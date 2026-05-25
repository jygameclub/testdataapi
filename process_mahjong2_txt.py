#!/usr/bin/env python3
"""Process Mahjong Ways 2 xxb capture files into URL replay data."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlsplit, urlunsplit


GITHUB_RAW_BASE = "https://raw.githubusercontent.com/jygameclub/testdataapi/main"
DEFAULT_TOKEN = "436475c81b51e6893c740657870f86b7"
DEFAULT_GAME_URL = (
    "https://fish-games.s3.amazonaws.com/MahjongWays2/index.html"
    "?env=ceshislot.osshaiwai.com&hasFloat=0"
    f"&token={DEFAULT_TOKEN}&language=en"
)
BIG_WIN_MULTIPLIER = 17
MEGA_WIN_MULTIPLIER = 35
SUPER_MEGA_WIN_MULTIPLIER = 50
FREE_SPIN_SCATTER_COUNT = 3
MAHJONG2_TITLE_ALIASES = (
    "mahjong2",
    "mahjongways2",
    "麻将2",
    "麻将ways2",
    "majianng2",
    "majiang2",
)


@dataclass(frozen=True)
class SplitSummary:
    files_written: int
    requests_written: int
    skipped_lines: int
    output_dir: Path


def is_mahjong2_title(title: str | None) -> bool:
    normalized = "".join((title or "").lower().split()).replace("-", "").replace("_", "")
    return any(alias in normalized for alias in MAHJONG2_TITLE_ALIASES)


def _with_query_params(url: str, params: dict[str, Any]) -> str:
    split = urlsplit(url)
    query = dict(parse_qsl(split.query, keep_blank_values=True))
    for key, value in params.items():
        if value is not None:
            query[key] = str(value)
    query_string = "&".join(f"{key}={value}" for key, value in query.items())
    return urlunsplit((split.scheme, split.netloc, split.path, query_string, split.fragment))


def _game_url_base(token: str | None = None) -> str:
    game_url = os.environ.get("MAHJONG2_GAME_URL_BASE", DEFAULT_GAME_URL)
    if "{token}" in game_url:
        game_url = game_url.format(token=token or DEFAULT_TOKEN)
    params: dict[str, Any] = {"debug": 1}
    if token:
        params["token"] = token
    return _with_query_params(game_url, params)


def build_url_lines(github_path: str, token: str | None = None, start: int = 1) -> list[str]:
    data_path = f"{GITHUB_RAW_BASE}/{github_path.strip('/')}"
    game_link = _with_query_params(
        _game_url_base(token),
        {"debugDataPath": data_path, "debugStart": max(1, start)},
    )
    return [data_path, f"{data_path}/manifest.json", "", game_link]


def _load_json_lines(source: Path) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    skipped = 0
    for line_no, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        text = line.strip().rstrip(",")
        if not text:
            continue
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            skipped += 1
            print(f"[process_mahjong2] skip line {line_no}: invalid JSON")
            continue
        if not isinstance(obj, dict):
            skipped += 1
            print(f"[process_mahjong2] skip line {line_no}: JSON root is not an object")
            continue
        rows.append(obj)
    return rows, skipped


def _extract_data(row: dict[str, Any]) -> dict[str, Any] | None:
    data = row.get("data")
    if data is None:
        dt = row.get("dt")
        if isinstance(dt, dict):
            data = dt.get("si")
    if data is None:
        data = row
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return None
    return data if isinstance(data, dict) else None


def _float_value(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _is_paid_bet(data: dict[str, Any]) -> bool:
    return data.get("st") in (1, 21) or _float_value(data.get("tb")) > 0


def _group_by_paid_bet(entries: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    groups: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []

    for entry in entries:
        if _is_paid_bet(entry) and current:
            groups.append(current)
            current = []
        current.append(entry)

    if current:
        groups.append(current)

    return groups


def _clean_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        for child in output_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        output_dir.mkdir(parents=True)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _manifest_group(file_name: str, entries: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(entries)
    first = rows[0] if rows else {}
    last = rows[-1] if rows else {}
    return {
        "file": file_name,
        "request_count": len(rows),
        "first_sid": first.get("sid"),
        "last_sid": last.get("sid"),
        "first_spinId": first.get("spinId"),
        "last_spinId": last.get("spinId"),
        "total_bet": first.get("tbb", first.get("tb", 0)),
        "start_balance": first.get("blb"),
        "end_balance": last.get("bl"),
        "total_win": last.get("ssaw", last.get("aw", last.get("tw", 0))),
    }


def _records_from_file(path: Path) -> list[dict[str, Any]]:
    try:
        token = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    raw_records = token if isinstance(token, list) else [token]
    records: list[dict[str, Any]] = []
    for raw in raw_records:
        if not isinstance(raw, dict):
            continue
        data = _extract_data(raw)
        if data is not None:
            records.append(data)
    return records


def _count_win_lines(record: dict[str, Any]) -> int:
    wp = record.get("wp")
    return len(wp) if isinstance(wp, dict) else 0


def _final_win(records: list[dict[str, Any]]) -> float:
    if not records:
        return 0.0
    last = records[-1]
    for key in ("ssaw", "aw", "tw", "ctw"):
        value = _float_value(last.get(key))
        if value > 0:
            return value
    return max((_float_value(record.get("ssaw")) for record in records), default=0.0)


def _bet_amount(records: list[dict[str, Any]]) -> float:
    if not records:
        return 0.0
    first = records[0]
    return _float_value(first.get("tbb")) or _float_value(first.get("tb"))


def _win_type(multiplier: float, total_win: float) -> str:
    if multiplier >= SUPER_MEGA_WIN_MULTIPLIER:
        return "Super Mega Win"
    if multiplier >= MEGA_WIN_MULTIPLIER:
        return "Mega Win"
    if multiplier >= BIG_WIN_MULTIPLIER:
        return "Big Win"
    if total_win > 0:
        return "普通中奖"
    return "未中奖"


def _has_free_spin(records: list[dict[str, Any]]) -> bool:
    for record in records:
        fs = record.get("fs")
        if _float_value(record.get("sc")) >= FREE_SPIN_SCATTER_COUNT:
            return True
        if isinstance(fs, dict) and (_float_value(fs.get("ts")) > 0 or _float_value(fs.get("s")) > 0):
            return True
    return False


def _has_gold_transform(records: list[dict[str, Any]]) -> bool:
    for record in records:
        if record.get("ptbr"):
            return True
        if record.get("rs") or record.get("rsc"):
            return True
    return False


def _summarize_replay_file(path: Path, github_path: str, token: str | None = None) -> dict[str, Any]:
    records = _records_from_file(path)
    file_index = int(path.stem) if path.stem.isdigit() else 1
    total_bet = _bet_amount(records)
    total_win = _final_win(records)
    multiplier = total_win / total_bet if total_bet > 0 else 0.0
    win_lines = [_count_win_lines(record) for record in records]
    scatter_count = max((_float_value(record.get("sc")) for record in records), default=0.0)
    debug_link = _with_query_params(
        _game_url_base(token),
        {
            "debugDataPath": f"{GITHUB_RAW_BASE}/{github_path.strip('/')}",
            "debugStart": file_index,
        },
    )
    cascade_count = max(0, len(records) - 1)
    has_continue_state = any(record.get("st") in (4, 22) or record.get("nst") in (4, 22) for record in records)
    win_type = _win_type(multiplier, total_win)

    reasons = []
    if win_type in {"Big Win", "Mega Win", "Super Mega Win"}:
        reasons.append(win_type)
    if cascade_count > 0 or has_continue_state:
        reasons.append(f"{len(records)}段连消/续转")
    if _has_free_spin(records):
        reasons.append("Scatter / Free Spin")
    if _has_gold_transform(records):
        reasons.append("金色符号/百搭转换")
    if max(win_lines, default=0) >= 3:
        reasons.append(f"多线中奖 {max(win_lines)}线")
    if total_win > 0 and not reasons:
        reasons.append("普通中奖覆盖")

    return {
        "file": path.name,
        "index": file_index,
        "request_count": len(records),
        "sid": records[0].get("sid") if records else "",
        "last_sid": records[-1].get("sid") if records else "",
        "spinId": records[0].get("spinId") if records else "",
        "total_bet": total_bet,
        "total_win": total_win,
        "multiplier": multiplier,
        "win_type": win_type,
        "max_win_lines": max(win_lines, default=0),
        "scatter_count": scatter_count,
        "has_free_spin": _has_free_spin(records),
        "has_gold_transform": _has_gold_transform(records),
        "cascade_count": cascade_count,
        "has_continue_state": has_continue_state,
        "start_balance": records[0].get("blb") if records else "",
        "end_balance": records[-1].get("bl") if records else "",
        "reasons": reasons,
        "debug_link": debug_link,
    }


def _priority_score(summary: dict[str, Any]) -> int:
    score = 0
    if summary["win_type"] == "Super Mega Win":
        score += 100
    elif summary["win_type"] == "Mega Win":
        score += 90
    elif summary["win_type"] == "Big Win":
        score += 80
    elif summary["total_win"] > 0:
        score += 20
    if summary["has_free_spin"]:
        score += 50
    if summary["cascade_count"] > 0 or summary["has_continue_state"]:
        score += 30
    if summary["has_gold_transform"]:
        score += 25
    if summary["max_win_lines"] >= 3:
        score += 15
    return score


def _money(value: Any) -> str:
    return f"{_float_value(value):.2f}"


def _multiplier(value: Any) -> str:
    return f"{_float_value(value):.2f}x"


def _link(label: str, url: str) -> str:
    return f"[{label}]({url})"


def _table_row(summary: dict[str, Any], include_reason: bool = True) -> str:
    reason = " / ".join(summary["reasons"]) if summary["reasons"] else "-"
    cells = [
        summary["file"],
        _link(f"从第{summary['index']}次开始", summary["debug_link"]),
        summary["win_type"],
        _money(summary["total_win"]),
        _multiplier(summary["multiplier"]),
        str(summary["request_count"]),
        str(summary["max_win_lines"]),
        str(int(summary["scatter_count"])),
        str(summary["sid"]),
        str(summary["last_sid"]),
    ]
    if include_reason:
        cells.append(reason)
    return "| " + " | ".join(cells) + " |"


def analyze_replay_dir(output_dir: Path | str, github_path: str, token: str | None = None) -> str:
    replay_dir = Path(output_dir)
    summaries = [
        _summarize_replay_file(path, github_path, token=token)
        for path in sorted(replay_dir.glob("*.json"))
        if path.name != "manifest.json"
    ]

    total_files = len(summaries)
    winning = [item for item in summaries if item["total_win"] > 0]
    big_wins = [item for item in summaries if item["win_type"] in {"Big Win", "Mega Win", "Super Mega Win"}]
    cascades = [item for item in summaries if item["cascade_count"] > 0 or item["has_continue_state"]]
    free_spins = [item for item in summaries if item["has_free_spin"]]
    gold_transforms = [item for item in summaries if item["has_gold_transform"]]
    top_replays = sorted(
        [item for item in summaries if _priority_score(item) > 0],
        key=lambda item: (_priority_score(item), item["total_win"], item["request_count"]),
        reverse=True,
    )

    lines = [
        "### Mahjong2 回放摘要",
        "",
        "依据代码阈值生成：`SuperBigWinReference` 中 Big Win = 17x、Mega Win = 35x、Super Mega Win = 50x；`WinningState` 在 `ssaw > 0` 时触发 Big/Mega/Super 与 Total Win 流程；`MatchingState` 会对 `wp` 中奖和 `st/nst=4` 的连消继续请求进行动画回放。",
        "",
        f"- 文件数: {total_files}",
        f"- 有中奖回合: {len(winning)}",
        f"- Big/Mega/Super 重点回合: {len(big_wins)}",
        f"- 连消/多段回放: {len(cascades)}",
        f"- Scatter / Free Spin 回放: {len(free_spins)}",
        f"- 金色符号/百搭转换回放: {len(gold_transforms)}",
    ]

    if top_replays:
        lines.extend([
            "",
            "### 重点测试回放建议",
            "",
            "| 文件 | 回放链接 | 类型 | 总赢 | 倍率 | 请求数 | 中奖线 | Scatter | 起始SID | 结束SID | 为什么要测 |",
            "|------|----------|------|------|------|--------|--------|---------|---------|---------|------------|",
        ])
        for summary in top_replays[:40]:
            lines.append(_table_row(summary))

    if big_wins:
        lines.extend([
            "",
            "### Big / Mega / Super Win",
            "",
            "| 文件 | 回放链接 | 类型 | 总赢 | 倍率 | 请求数 | 中奖线 | Scatter | 起始SID | 结束SID | 为什么要测 |",
            "|------|----------|------|------|------|--------|--------|---------|---------|---------|------------|",
        ])
        for summary in sorted(big_wins, key=lambda item: item["multiplier"], reverse=True):
            lines.append(_table_row(summary))

    if cascades:
        lines.extend([
            "",
            "### 连消/多段回放",
            "",
            "| 文件 | 回放链接 | 类型 | 总赢 | 倍率 | 请求数 | 中奖线 | Scatter | 起始SID | 结束SID | 为什么要测 |",
            "|------|----------|------|------|------|--------|--------|---------|---------|---------|------------|",
        ])
        for summary in sorted(cascades, key=lambda item: (item["request_count"], item["total_win"]), reverse=True)[:40]:
            lines.append(_table_row(summary))

    if free_spins:
        lines.extend([
            "",
            "### Scatter / Free Spin",
            "",
            "| 文件 | 回放链接 | 类型 | 总赢 | 倍率 | 请求数 | 中奖线 | Scatter | 起始SID | 结束SID | 为什么要测 |",
            "|------|----------|------|------|------|--------|--------|---------|---------|---------|------------|",
        ])
        for summary in sorted(free_spins, key=lambda item: (item["scatter_count"], item["total_win"]), reverse=True):
            lines.append(_table_row(summary))

    if gold_transforms:
        lines.extend([
            "",
            "### 金色符号 / 百搭转换",
            "",
            "| 文件 | 回放链接 | 类型 | 总赢 | 倍率 | 请求数 | 中奖线 | Scatter | 起始SID | 结束SID | 为什么要测 |",
            "|------|----------|------|------|------|--------|--------|---------|---------|---------|------------|",
        ])
        for summary in sorted(gold_transforms, key=lambda item: (item["request_count"], item["total_win"]), reverse=True)[:40]:
            lines.append(_table_row(summary))

    if winning:
        lines.extend([
            "",
            "### 全量中奖明细",
            "",
            "| 文件 | 回放链接 | 类型 | 总赢 | 倍率 | 请求数 | 中奖线 | Scatter | 起始SID | 结束SID | 为什么要测 |",
            "|------|----------|------|------|------|--------|--------|---------|---------|---------|------------|",
        ])
        for summary in sorted(winning, key=lambda item: item["index"]):
            lines.append(_table_row(summary))

    if not winning:
        lines.extend(["", "_未检测到中奖回合，可作为普通空转与余额扣费回归数据。_"])

    return "\n".join(lines) + "\n"


def split_capture(source: Path | str, output_dir: Path | str, mode: str = "bet") -> SplitSummary:
    source_path = Path(source)
    output_path = Path(output_dir)
    if mode not in {"bet", "request"}:
        raise ValueError("mode must be 'bet' or 'request'")

    rows, skipped = _load_json_lines(source_path)
    entries: list[dict[str, Any]] = []
    for row in rows:
        data = _extract_data(row)
        if data is None:
            skipped += 1
            continue
        entries.append(data)

    groups = [[entry] for entry in entries] if mode == "request" else _group_by_paid_bet(entries)
    _clean_output_dir(output_path)

    manifest_groups: list[dict[str, Any]] = []
    for index, group in enumerate(groups, 1):
        file_name = f"{index:03d}.json"
        value: Any = group[0] if mode == "request" else group
        _write_json(output_path / file_name, value)
        manifest_groups.append(_manifest_group(file_name, group))

    manifest = {
        "source": source_path.name,
        "mode": mode,
        "files_written": len(groups),
        "requests_written": len(entries),
        "skipped_lines": skipped,
        "groups": manifest_groups,
    }
    _write_json(output_path / "manifest.json", manifest)

    return SplitSummary(
        files_written=len(groups),
        requests_written=len(entries),
        skipped_lines=skipped,
        output_dir=output_path,
    )


def _write_url_file(output_dir: Path, github_path: str, token: str | None = None) -> Path:
    url_file = output_dir / "url.txt"
    url_file.write_text("\n".join(build_url_lines(github_path, token=token)) + "\n", encoding="utf-8")
    return url_file


def _write_analysis_file(output_dir: Path, github_path: str, token: str | None = None) -> str:
    analysis = analyze_replay_dir(output_dir, github_path, token=token)
    (output_dir / "analysis.md").write_text(analysis, encoding="utf-8")
    return analysis


def process_txt(
    txt_path: str | Path,
    token: str | None = None,
    mode: str = "bet",
    date_dir_name: str | None = None,
) -> tuple[str, str, int, str]:
    script_dir = Path(__file__).resolve().parent
    batch = date_dir_name or datetime.now().strftime("%m%d_%H%M")
    output_dir = script_dir / "mahjong2date" / batch
    print(f"create directory: mahjong2date/{batch}/")

    summary = split_capture(txt_path, output_dir, mode=mode)
    github_path = f"mahjong2date/{batch}"
    url_file = _write_url_file(output_dir, github_path, token=token)
    analysis = _write_analysis_file(output_dir, github_path, token=token)

    print(
        "[process_mahjong2] "
        f"files={summary.files_written} requests={summary.requests_written} "
        f"skipped={summary.skipped_lines} output=mahjong2date/{batch}/"
    )
    return batch, str(url_file), summary.files_written, analysis


def process_zip(
    zip_path: str | Path,
    token: str | None = None,
    mode: str = "bet",
    date_dir_name: str | None = None,
) -> tuple[str, str, int, str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as merged:
        merged_path = Path(merged.name)
        with zipfile.ZipFile(zip_path, "r") as zf:
            for info in sorted(zf.infolist(), key=lambda item: item.filename):
                if info.is_dir() or not info.filename.lower().endswith(".txt"):
                    continue
                data = zf.read(info.filename).decode("utf-8")
                merged.write(data.rstrip())
                merged.write("\n")

    try:
        return process_txt(merged_path, token=token, mode=mode, date_dir_name=date_dir_name)
    finally:
        merged_path.unlink(missing_ok=True)


def process_file(
    file_path: str | Path,
    token: str | None = None,
    mode: str = "bet",
    date_dir_name: str | None = None,
) -> tuple[str, str, int, str]:
    path = str(file_path)
    if path.lower().endswith(".zip"):
        return process_zip(path, token=token, mode=mode, date_dir_name=date_dir_name)
    return process_txt(path, token=token, mode=mode, date_dir_name=date_dir_name)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process Mahjong2 xxb capture txt/zip for URL replay.")
    parser.add_argument("file", nargs="?", help="Source .txt or .zip file. Defaults to update/mahjong2*.")
    parser.add_argument("--token", default=os.environ.get("CUSTOM_TOKEN") or None)
    parser.add_argument("--mode", choices=("bet", "request"), default="bet")
    parser.add_argument("--date-dir", help="Optional batch directory name, for example 0525_0910.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    script_dir = Path(__file__).resolve().parent
    file_path = args.file

    if not file_path:
        update_dir = script_dir / "update"
        files = [
            item for item in sorted(update_dir.iterdir())
            if item.name.lower().startswith("mahjong2") and item.suffix.lower() in {".txt", ".zip"}
        ]
        if not files:
            print("No mahjong2 txt/zip file found in update/.")
            return 0
        file_path = str(files[0])

    process_file(file_path, token=args.token, mode=args.mode, date_dir_name=args.date_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

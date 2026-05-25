#!/usr/bin/env python3
"""Process Mahjong Ways 2 xxb capture files into URL replay data."""

from __future__ import annotations

import argparse
import csv
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
REEL_COUNT = 5
REEL_HEIGHT = 7
BOARD_SIZE = REEL_COUNT * REEL_HEIGHT
WILD_SYMBOL = 0
SCATTER_SYMBOL = 1
HIDDEN_INDEXES = {0, 5, 6, 7, 13, 14, 20, 21, 27, 28, 33, 34}
RECOMMENDED_CSV_FILE = "recommended_replays.csv"
ALL_REPLAYS_CSV_FILE = "all_replays.csv"
ANALYSIS_TABLE_HEADER = "| 文件 | 特征标签 | 回放链接 | 类型 | 总赢 | 倍率 | 请求数 | 中奖线 | Scatter | 起始SID | 结束SID | 为什么要测 |"
ANALYSIS_TABLE_DIVIDER = "|------|----------|----------|------|------|------|--------|--------|---------|---------|---------|------------|"
CSV_COLUMNS = [
    "测试类型",
    "文件",
    "编号",
    "推荐分",
    "特征标签",
    "回放链接",
    "json绝对地址",
    "数据目录",
    "类型",
    "总赢",
    "倍率",
    "请求数",
    "掉落次数",
    "补牌总数",
    "消除位置总数",
    "wp中奖位置总数",
    "wild总数(可见盘面)",
    "单次最大wild数(可见盘面)",
    "是否免费旋转",
    "免费送胡",
    "是否金色百搭",
    "中奖线",
    "Scatter",
    "起始SID",
    "结束SID",
    "spinId",
    "起始余额",
    "结束余额",
    "为什么要测",
]
CSV_TYPE_ORDER = {
    "免费中大奖": 10,
    "Super Mega Win": 20,
    "Mega Win": 30,
    "Big Win": 40,
    "免费送胡": 50,
    "免费旋转": 60,
    "连消/掉落": 70,
    "金色/百搭": 80,
    "普通中奖": 90,
    "普通空转": 100,
}
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
    return [
        data_path,
        f"{data_path}/manifest.json",
        "",
        game_link,
        "",
        f"{data_path}/{RECOMMENDED_CSV_FILE}",
        f"{data_path}/{ALL_REPLAYS_CSV_FILE}",
    ]


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
    return _float_value(data.get("st")) == 1 or _float_value(data.get("tb")) > 0


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


def _int_value(value: Any, default: int | None = None) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _int_list(value: Any) -> list[int]:
    if not isinstance(value, list):
        return []

    result: list[int] = []
    for item in value:
        int_item = _int_value(item)
        if int_item is not None:
            result.append(int_item)
    return result


def _wp_positions(record: dict[str, Any]) -> dict[int, list[int]]:
    wp = record.get("wp")
    if not isinstance(wp, dict):
        return {}

    result: dict[int, list[int]] = {}
    for symbol, positions in wp.items():
        symbol_index = _int_value(symbol)
        if symbol_index is None:
            continue
        result[symbol_index] = _int_list(positions)
    return result


def _is_active_position(position: int) -> bool:
    return 0 <= position < BOARD_SIZE and position not in HIDDEN_INDEXES


def _reel_index(position: int) -> int:
    return position // REEL_HEIGHT


def _active_positions_for_reel(reel: int) -> list[int]:
    start = reel * REEL_HEIGHT
    return [
        position
        for position in range(start, start + REEL_HEIGHT)
        if _is_active_position(position)
    ]


def _record_has_win(record: dict[str, Any]) -> bool:
    return bool(_wp_positions(record))


def _possible_way_wins(rl: Any) -> dict[int, list[int]]:
    if not isinstance(rl, list) or len(rl) < BOARD_SIZE:
        return {}

    symbols = sorted({
        _int_value(rl[position])
        for position in range(BOARD_SIZE)
        if _is_active_position(position)
        and _int_value(rl[position]) not in (None, WILD_SYMBOL, SCATTER_SYMBOL)
    })
    wins: dict[int, list[int]] = {}

    for symbol in symbols:
        if symbol is None:
            continue

        positions: list[int] = []
        consecutive_reels = 0
        for reel in range(REEL_COUNT):
            reel_matches = [
                position
                for position in _active_positions_for_reel(reel)
                if _int_value(rl[position]) in (symbol, WILD_SYMBOL)
            ]
            if not reel_matches:
                break
            consecutive_reels += 1
            positions.extend(reel_matches)

        if consecutive_reels >= 3:
            wins[symbol] = positions

    return wins


def _debug_link_for_start(github_path: str, replay_start: int, token: str | None) -> str:
    return _with_query_params(
        _game_url_base(token),
        {
            "debugDataPath": f"{GITHUB_RAW_BASE}/{github_path.strip('/')}",
            "debugStart": replay_start,
        },
    )


def _markdown_cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def _majiang_issue(
    file_name: str,
    replay_start: int,
    github_path: str,
    token: str | None,
    entry_index: int,
    record: dict[str, Any],
    code: str,
    message: str,
    severity: str = "高危",
) -> dict[str, Any]:
    return {
        "file": file_name,
        "entry_index": entry_index,
        "sid": record.get("sid", ""),
        "severity": severity,
        "code": code,
        "message": message,
        "debug_link": _debug_link_for_start(github_path, replay_start, token),
        "replay_start_index": replay_start,
    }


def _validate_record_shape(
    file_name: str,
    replay_start: int,
    github_path: str,
    token: str | None,
    entry_index: int,
    record: dict[str, Any],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    rl = record.get("rl")

    if not isinstance(rl, list) or len(rl) != BOARD_SIZE:
        issues.append(_majiang_issue(
            file_name,
            replay_start,
            github_path,
            token,
            entry_index,
            record,
            "RL_LENGTH",
            f"rl长度应为{BOARD_SIZE}，当前={len(rl) if isinstance(rl, list) else 'null'}，客户端盘面可能无法和服务端数据对齐",
        ))
        return issues

    position_fields = {
        "ptbr": _int_list(record.get("ptbr")),
        "ssb": _int_list(record.get("ssb")),
        "ss": _int_list(record.get("ss")),
    }
    for field_name, positions in position_fields.items():
        for position in positions:
            if position < 0 or position >= BOARD_SIZE:
                issues.append(_majiang_issue(
                    file_name,
                    replay_start,
                    github_path,
                    token,
                    entry_index,
                    record,
                    "POSITION_RANGE",
                    f"{field_name}包含越界位置{position}，有效范围是0-{BOARD_SIZE - 1}",
                ))
            elif field_name == "ptbr" and position in HIDDEN_INDEXES:
                issues.append(_majiang_issue(
                    file_name,
                    replay_start,
                    github_path,
                    token,
                    entry_index,
                    record,
                    "HIDDEN_POSITION",
                    f"{field_name}包含隐藏格位置{position}，客户端不会把这个格子当作普通可消除盘面",
                ))

    wp_positions = _wp_positions(record)
    union_wp_positions: set[int] = set()
    for symbol, positions in wp_positions.items():
        union_wp_positions.update(positions)
        for position in positions:
            if position < 0 or position >= BOARD_SIZE:
                issues.append(_majiang_issue(
                    file_name,
                    replay_start,
                    github_path,
                    token,
                    entry_index,
                    record,
                    "WP_POSITION_RANGE",
                    f"wp[{symbol}]包含越界位置{position}，有效范围是0-{BOARD_SIZE - 1}",
                ))
                continue
            if position in HIDDEN_INDEXES:
                issues.append(_majiang_issue(
                    file_name,
                    replay_start,
                    github_path,
                    token,
                    entry_index,
                    record,
                    "WP_HIDDEN_POSITION",
                    f"wp[{symbol}]包含隐藏格位置{position}，客户端普通消除不会按可见格处理",
                ))
                continue

            board_symbol = _int_value(rl[position])
            if board_symbol not in (symbol, WILD_SYMBOL):
                issues.append(_majiang_issue(
                    file_name,
                    replay_start,
                    github_path,
                    token,
                    entry_index,
                    record,
                    "WP_BOARD_MISMATCH",
                    f"wp[{symbol}]位置{position}和当前盘面不一致：盘面符号={board_symbol}，期望={symbol}或Wild({WILD_SYMBOL})",
                ))

    ptbr_positions = set(_int_list(record.get("ptbr")))
    if wp_positions:
        missing_from_ptbr = sorted(union_wp_positions - ptbr_positions)
        extra_in_ptbr = sorted(ptbr_positions - union_wp_positions)
        if missing_from_ptbr:
            issues.append(_majiang_issue(
                file_name,
                replay_start,
                github_path,
                token,
                entry_index,
                record,
                "WP_NOT_IN_PTBR",
                f"wp中奖位置没有全部出现在ptbr中，缺少={missing_from_ptbr}，客户端消除会少消",
            ))
        if extra_in_ptbr:
            issues.append(_majiang_issue(
                file_name,
                replay_start,
                github_path,
                token,
                entry_index,
                record,
                "PTBR_NOT_IN_WP",
                f"ptbr包含不在wp中的位置={extra_in_ptbr}，客户端可能多消除普通麻将",
            ))
    else:
        visible_ptbr = sorted(position for position in ptbr_positions if _is_active_position(position))
        if visible_ptbr:
            issues.append(_majiang_issue(
                file_name,
                replay_start,
                github_path,
                token,
                entry_index,
                record,
                "PTBR_WITHOUT_WP",
                f"服务端没有wp中奖连接，但ptbr包含可见消除位置={visible_ptbr}",
            ))

    possible_wins = _possible_way_wins(rl)
    server_round_ended = _float_value(record.get("nst")) not in (4, 21, 22)
    if not _record_has_win(record) and server_round_ended and possible_wins:
        first_symbol, first_positions = next(iter(possible_wins.items()))
        issues.append(_majiang_issue(
            file_name,
            replay_start,
            github_path,
            token,
            entry_index,
            record,
            "FINAL_BOARD_STILL_WIN",
            f"服务端已结束但盘面仍可中奖：symbol={first_symbol}, positions={first_positions}",
        ))

    if _record_has_win(record) and not possible_wins:
        issues.append(_majiang_issue(
            file_name,
            replay_start,
            github_path,
            token,
            entry_index,
            record,
            "WP_WITHOUT_BOARD_WIN",
            "服务端给了wp中奖，但按当前rl盘面没有检测到从第1列开始的Ways中奖",
        ))

    return issues


def _non_gold_drop_positions(record: dict[str, Any]) -> list[int]:
    ssb = set(_int_list(record.get("ssb")))
    positions: list[int] = []
    for position in _int_list(record.get("ptbr")):
        if _is_active_position(position) and position not in ssb:
            positions.append(position)
    return positions


def _validate_record_transition(
    file_name: str,
    replay_start: int,
    github_path: str,
    token: str | None,
    previous_entry_index: int,
    previous_record: dict[str, Any],
    next_record: dict[str, Any],
) -> list[dict[str, Any]]:
    if not _record_has_win(previous_record):
        return []

    expected_by_reel: dict[int, list[int]] = {}
    for position in _non_gold_drop_positions(previous_record):
        expected_by_reel.setdefault(_reel_index(position), []).append(position)

    if not expected_by_reel:
        return []

    rs = next_record.get("rs")
    rns = rs.get("rns") if isinstance(rs, dict) else None
    issues: list[dict[str, Any]] = []
    for reel, positions in sorted(expected_by_reel.items()):
        actual_items = rns[reel] if isinstance(rns, list) and reel < len(rns) and isinstance(rns[reel], list) else []
        if len(actual_items) < len(positions):
            issues.append(_majiang_issue(
                file_name,
                replay_start,
                github_path,
                token,
                previous_entry_index + 1,
                next_record,
                "RNS_DROP_MISMATCH",
                f"上一条ptbr普通消除位置{positions}需要第{reel + 1}列补{len(positions)}个，当前rs.rns[{reel}]={actual_items}，补牌数量不足",
            ))

    return issues


def _majiang_error_checks_for_records(
    file_name: str,
    records: list[dict[str, Any]],
    github_path: str,
    token: str | None,
    replay_start: int,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for index, record in enumerate(records, 1):
        issues.extend(_validate_record_shape(file_name, replay_start, github_path, token, index, record))
        if index > 1:
            issues.extend(_validate_record_transition(
                file_name,
                replay_start,
                github_path,
                token,
                index - 1,
                records[index - 2],
                record,
            ))
    return issues


def _majiang_error_section(issues: list[dict[str, Any]]) -> list[str]:
    if not issues:
        return []

    lines = [
        "",
        "### majiangerrorcheck 数据异常优先检查",
        "",
        "| 文件 | 回放链接 | 严重度 | 位置/SID | 类型 | 说明 |",
        "|------|----------|--------|----------|------|------|",
    ]
    for issue in issues:
        location = f"entry={issue['entry_index']}, sid={issue['sid']}"
        message = f"majiangerrorcheck {issue['code']}: {issue['message']}"
        lines.append(
            "| "
            + " | ".join([
                _markdown_cell(issue["file"]),
                _link(f"从第{issue['replay_start_index']}次开始", issue["debug_link"]),
                _markdown_cell(issue["severity"]),
                _markdown_cell(location),
                _markdown_cell(issue["code"]),
                _markdown_cell(message),
            ])
            + " |"
        )
    return lines


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
        if _float_value(record.get("st")) in (21, 22) or _float_value(record.get("nst")) in (21, 22):
            return True
        if _float_value(record.get("sc")) >= FREE_SPIN_SCATTER_COUNT:
            return True
        if isinstance(fs, dict) and (_float_value(fs.get("ts")) > 0 or _float_value(fs.get("s")) > 0):
            return True
    return False


def _is_free_spin_round(record: dict[str, Any]) -> bool:
    fs = record.get("fs")
    if _float_value(record.get("st")) in (21, 22):
        return True
    return (
        _float_value(record.get("tb")) == 0
        and isinstance(fs, dict)
        and (_float_value(fs.get("ts")) > 0 or _float_value(fs.get("s")) > 0)
    )


def _has_free_spin_win(records: list[dict[str, Any]]) -> bool:
    for record in records:
        if not _is_free_spin_round(record):
            continue
        if _record_has_win(record) or _float_value(record.get("aw")) > 0 or _float_value(record.get("ssaw")) > 0:
            return True
    return False


def _rns_drop_symbol_count(records: list[dict[str, Any]]) -> int:
    count = 0
    for record in records:
        rs = record.get("rs")
        rns = rs.get("rns") if isinstance(rs, dict) else None
        if not isinstance(rns, list):
            continue
        for reel_symbols in rns:
            if isinstance(reel_symbols, list):
                count += len(reel_symbols)
    return count


def _ptbr_position_count(records: list[dict[str, Any]]) -> int:
    return sum(len(_int_list(record.get("ptbr"))) for record in records)


def _wp_position_count(records: list[dict[str, Any]]) -> int:
    count = 0
    for record in records:
        for positions in _wp_positions(record).values():
            count += len(positions)
    return count


def _visible_wild_count(record: dict[str, Any]) -> int:
    rl = record.get("rl")
    if not isinstance(rl, list):
        return 0

    if len(rl) >= BOARD_SIZE:
        positions = range(BOARD_SIZE)
        return sum(
            1
            for position in positions
            if _is_active_position(position) and _int_value(rl[position]) == WILD_SYMBOL
        )

    return sum(1 for value in rl if _int_value(value) == WILD_SYMBOL)


def _wild_counts(records: list[dict[str, Any]]) -> tuple[int, int]:
    counts = [_visible_wild_count(record) for record in records]
    return sum(counts), max(counts, default=0)


def _has_gold_transform(records: list[dict[str, Any]]) -> bool:
    for record in records:
        if record.get("ptbr"):
            return True
        if record.get("rs") or record.get("rsc"):
            return True
    return False


def _feature_tags(records: list[dict[str, Any]], win_type: str) -> list[str]:
    tags: list[str] = []
    has_free_spin = _has_free_spin(records)
    if has_free_spin:
        tags.append("免费旋转")
    if has_free_spin and win_type in {"Big Win", "Mega Win", "Super Mega Win"}:
        tags.append("免费中大奖")
    if _has_free_spin_win(records):
        tags.append("免费送胡")
    if _has_gold_transform(records):
        tags.append("金色/百搭")
    return tags


def _csv_test_type(summary: dict[str, Any]) -> str:
    tags = set(summary.get("feature_tags") or [])
    if "免费中大奖" in tags:
        return "免费中大奖"
    if summary["win_type"] in {"Super Mega Win", "Mega Win", "Big Win"}:
        return summary["win_type"]
    if "免费送胡" in tags:
        return "免费送胡"
    if "免费旋转" in tags:
        return "免费旋转"
    if summary["cascade_count"] > 0 or summary["has_continue_state"]:
        return "连消/掉落"
    if "金色/百搭" in tags:
        return "金色/百搭"
    if summary["total_win"] > 0:
        return "普通中奖"
    return "普通空转"


def _file_index(path: Path) -> int:
    return int(path.stem) if path.stem.isdigit() else 1


def _chain_key(records: list[dict[str, Any]]) -> str:
    if not records:
        return ""

    first = records[0]
    if _is_paid_bet(first):
        return str(first.get("sid") or first.get("psid") or first.get("spinId") or "")

    return str(first.get("psid") or first.get("sid") or first.get("spinId") or "")


def _build_replay_start_index_lookup(paths: list[Path]) -> dict[int, int]:
    records_by_path = {path: _records_from_file(path) for path in paths}
    earliest_by_chain: dict[str, int] = {}
    paid_start_by_chain: dict[str, int] = {}

    for path, records in records_by_path.items():
        if not records:
            continue
        index = _file_index(path)
        chain_key = _chain_key(records)
        if not chain_key:
            continue
        earliest_by_chain[chain_key] = min(index, earliest_by_chain.get(chain_key, index))
        if _is_paid_bet(records[0]):
            paid_start_by_chain[chain_key] = min(index, paid_start_by_chain.get(chain_key, index))

    lookup: dict[int, int] = {}
    for path, records in records_by_path.items():
        index = _file_index(path)
        chain_key = _chain_key(records)
        lookup[index] = paid_start_by_chain.get(chain_key, earliest_by_chain.get(chain_key, index))

    return lookup


def _summarize_replay_file(
    path: Path,
    github_path: str,
    token: str | None = None,
    replay_start_index: int | None = None,
) -> dict[str, Any]:
    records = _records_from_file(path)
    file_index = _file_index(path)
    replay_start = replay_start_index or file_index
    total_bet = _bet_amount(records)
    total_win = _final_win(records)
    multiplier = total_win / total_bet if total_bet > 0 else 0.0
    win_lines = [_count_win_lines(record) for record in records]
    scatter_count = max((_float_value(record.get("sc")) for record in records), default=0.0)
    data_dir_url = f"{GITHUB_RAW_BASE}/{github_path.strip('/')}"
    debug_link = _with_query_params(
        _game_url_base(token),
        {
            "debugDataPath": data_dir_url,
            "debugStart": replay_start,
        },
    )
    cascade_count = max(0, len(records) - 1)
    has_continue_state = any(record.get("st") in (4, 22) or record.get("nst") in (4, 22) for record in records)
    win_type = _win_type(multiplier, total_win)
    has_free_spin = _has_free_spin(records)
    has_free_spin_win = _has_free_spin_win(records)
    has_gold_transform = _has_gold_transform(records)
    wild_count, max_wild_count = _wild_counts(records)

    reasons = []
    if win_type in {"Big Win", "Mega Win", "Super Mega Win"}:
        reasons.append(win_type)
    if cascade_count > 0 or has_continue_state:
        reasons.append(f"{len(records)}段连消/续转")
    if has_free_spin:
        reasons.append("Scatter / Free Spin")
    if has_gold_transform:
        reasons.append("金色符号/百搭转换")
    if max(win_lines, default=0) >= 3:
        reasons.append(f"多线中奖 {max(win_lines)}线")
    if total_win > 0 and not reasons:
        reasons.append("普通中奖覆盖")

    feature_tags = _feature_tags(records, win_type)

    return {
        "file": path.name,
        "index": file_index,
        "replay_start_index": replay_start,
        "request_count": len(records),
        "sid": records[0].get("sid") if records else "",
        "last_sid": records[-1].get("sid") if records else "",
        "spinId": records[0].get("spinId") if records else "",
        "data_dir_url": data_dir_url,
        "json_url": f"{data_dir_url}/{path.name}",
        "total_bet": total_bet,
        "total_win": total_win,
        "multiplier": multiplier,
        "win_type": win_type,
        "max_win_lines": max(win_lines, default=0),
        "scatter_count": scatter_count,
        "has_free_spin": has_free_spin,
        "has_free_spin_win": has_free_spin_win,
        "has_gold_transform": has_gold_transform,
        "feature_tags": feature_tags,
        "cascade_count": cascade_count,
        "has_continue_state": has_continue_state,
        "drop_symbol_count": _rns_drop_symbol_count(records),
        "ptbr_position_count": _ptbr_position_count(records),
        "wp_position_count": _wp_position_count(records),
        "wild_count": wild_count,
        "max_wild_count": max_wild_count,
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
    feature_tags = " / ".join(summary.get("feature_tags") or []) or "-"
    cells = [
        summary["file"],
        feature_tags,
        _link(f"从第{summary['replay_start_index']}次开始", summary["debug_link"]),
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


def _yes_no(value: bool) -> str:
    return "是" if value else "否"


def _csv_sort_key(summary: dict[str, Any]) -> tuple[int, int, float, int, int]:
    test_type = _csv_test_type(summary)
    return (
        CSV_TYPE_ORDER.get(test_type, 999),
        -_priority_score(summary),
        -summary["total_win"],
        -summary["request_count"],
        summary["index"],
    )


def _summary_csv_row(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "测试类型": _csv_test_type(summary),
        "文件": summary["file"],
        "编号": summary["index"],
        "推荐分": _priority_score(summary),
        "特征标签": " / ".join(summary.get("feature_tags") or []),
        "回放链接": summary["debug_link"],
        "json绝对地址": summary["json_url"],
        "数据目录": summary["data_dir_url"],
        "类型": summary["win_type"],
        "总赢": f"{summary['total_win']:.2f}",
        "倍率": f"{summary['multiplier']:.2f}",
        "请求数": summary["request_count"],
        "掉落次数": summary["cascade_count"],
        "补牌总数": summary["drop_symbol_count"],
        "消除位置总数": summary["ptbr_position_count"],
        "wp中奖位置总数": summary["wp_position_count"],
        "wild总数(可见盘面)": summary["wild_count"],
        "单次最大wild数(可见盘面)": summary["max_wild_count"],
        "是否免费旋转": _yes_no(summary["has_free_spin"]),
        "免费送胡": _yes_no(summary["has_free_spin_win"]),
        "是否金色百搭": _yes_no(summary["has_gold_transform"]),
        "中奖线": summary["max_win_lines"],
        "Scatter": int(summary["scatter_count"]),
        "起始SID": summary["sid"],
        "结束SID": summary["last_sid"],
        "spinId": summary["spinId"],
        "起始余额": summary["start_balance"],
        "结束余额": summary["end_balance"],
        "为什么要测": " / ".join(summary["reasons"]) if summary["reasons"] else "",
    }


def _write_summary_csv(path: Path, summaries: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for summary in summaries:
            writer.writerow(_summary_csv_row(summary))


def _replay_summaries(output_dir: Path | str, github_path: str, token: str | None = None) -> list[dict[str, Any]]:
    replay_dir = Path(output_dir)
    replay_paths = [
        path
        for path in sorted(replay_dir.glob("*.json"))
        if path.name != "manifest.json"
    ]
    replay_start_lookup = _build_replay_start_index_lookup(replay_paths)
    return [
        _summarize_replay_file(
            path,
            github_path,
            token=token,
            replay_start_index=replay_start_lookup.get(_file_index(path)),
        )
        for path in replay_paths
    ]


def write_replay_csv_files(
    output_dir: Path | str,
    github_path: str,
    token: str | None = None,
) -> tuple[Path, Path]:
    replay_dir = Path(output_dir)
    summaries = _replay_summaries(replay_dir, github_path, token=token)
    sorted_summaries = sorted(summaries, key=_csv_sort_key)
    recommended = [summary for summary in sorted_summaries if _priority_score(summary) > 0]
    recommended_path = replay_dir / RECOMMENDED_CSV_FILE
    all_path = replay_dir / ALL_REPLAYS_CSV_FILE

    _write_summary_csv(recommended_path, recommended)
    _write_summary_csv(all_path, sorted_summaries)
    return recommended_path, all_path


def analyze_replay_dir(output_dir: Path | str, github_path: str, token: str | None = None) -> str:
    replay_dir = Path(output_dir)
    replay_paths = [
        path
        for path in sorted(replay_dir.glob("*.json"))
        if path.name != "manifest.json"
    ]
    replay_start_lookup = _build_replay_start_index_lookup(replay_paths)
    summaries = [
        _summarize_replay_file(
            path,
            github_path,
            token=token,
            replay_start_index=replay_start_lookup.get(_file_index(path)),
        )
        for path in replay_paths
    ]
    majiang_issues: list[dict[str, Any]] = []
    for path in replay_paths:
        file_index = _file_index(path)
        replay_start = replay_start_lookup.get(file_index, file_index)
        majiang_issues.extend(_majiang_error_checks_for_records(
            path.name,
            _records_from_file(path),
            github_path,
            token,
            replay_start,
        ))

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

    csv_base = f"{GITHUB_RAW_BASE}/{github_path.strip('/')}"
    lines.extend([
        "",
        "### CSV 下载",
        "",
        f"- 推荐测试 CSV（第一个 tab）: [{RECOMMENDED_CSV_FILE}]({csv_base}/{RECOMMENDED_CSV_FILE})",
        f"- 全部内容 CSV（第二个 tab）: [{ALL_REPLAYS_CSV_FILE}]({csv_base}/{ALL_REPLAYS_CSV_FILE})",
    ])

    lines.extend(_majiang_error_section(majiang_issues))

    if top_replays:
        lines.extend([
            "",
            "### 重点测试回放建议",
            "",
            ANALYSIS_TABLE_HEADER,
            ANALYSIS_TABLE_DIVIDER,
        ])
        for summary in top_replays[:40]:
            lines.append(_table_row(summary))

    if big_wins:
        lines.extend([
            "",
            "### Big / Mega / Super Win",
            "",
            ANALYSIS_TABLE_HEADER,
            ANALYSIS_TABLE_DIVIDER,
        ])
        for summary in sorted(big_wins, key=lambda item: item["multiplier"], reverse=True):
            lines.append(_table_row(summary))

    if cascades:
        lines.extend([
            "",
            "### 连消/多段回放",
            "",
            ANALYSIS_TABLE_HEADER,
            ANALYSIS_TABLE_DIVIDER,
        ])
        for summary in sorted(cascades, key=lambda item: (item["request_count"], item["total_win"]), reverse=True)[:40]:
            lines.append(_table_row(summary))

    if free_spins:
        lines.extend([
            "",
            "### Scatter / Free Spin",
            "",
            ANALYSIS_TABLE_HEADER,
            ANALYSIS_TABLE_DIVIDER,
        ])
        for summary in sorted(free_spins, key=lambda item: (item["scatter_count"], item["total_win"]), reverse=True):
            lines.append(_table_row(summary))

    if gold_transforms:
        lines.extend([
            "",
            "### 金色符号 / 百搭转换",
            "",
            ANALYSIS_TABLE_HEADER,
            ANALYSIS_TABLE_DIVIDER,
        ])
        for summary in sorted(gold_transforms, key=lambda item: (item["request_count"], item["total_win"]), reverse=True)[:40]:
            lines.append(_table_row(summary))

    if winning:
        lines.extend([
            "",
            "### 全量中奖明细",
            "",
            ANALYSIS_TABLE_HEADER,
            ANALYSIS_TABLE_DIVIDER,
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
    write_replay_csv_files(output_dir, github_path, token=token)
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

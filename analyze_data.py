"""
分析处理后的游戏数据文件，生成结构化的测试摘要（Markdown 格式）。

支持三款游戏：tiger / ox / anubis
每款游戏自动识别：免费旋转、大额/多线中奖、特殊动画等关键测试点。
"""

import json
import os
import urllib.parse

# 各游戏调试链接基础 URL（不含 token）
DEFAULT_TOKEN = "b3bb96ff1faef019504b83495ec3e45a"
GAME_URL_TEMPLATES = {
    "tiger": "https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token={token}&language=en&debug=1",
    "ox": "https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token={token}&language=en&debug=1",
    "anubis": "https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token={token}&language=en&debug=1",
}

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/jygameclub/testdataapi/main"


def _build_debug_link(game: str, data_url: str, start: int, token: str | None = None) -> str:
    """构建带 debugStart 的调试链接。"""
    t = token or DEFAULT_TOKEN
    base = GAME_URL_TEMPLATES[game].format(token=t)
    return f"{base}&debugDataUrl={data_url}&debugStart={start}"


def _parse_lines(filepath: str) -> list[dict]:
    """读取数据文件，返回解析后的 JSON 对象列表。"""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _count_win_lines(record: dict) -> int:
    """计算中奖线数。"""
    wp = record.get("wp")
    if wp and isinstance(wp, dict):
        return len(wp)
    return 0


def _describe_win(record: dict, game: str) -> str:
    """根据中奖情况生成说明文字。"""
    lines = _count_win_lines(record)
    aw = float(record.get("aw", 0))
    has_wild = False

    # 检查是否有 wild/百搭 (tiger: 0, ox: 99)
    rl = record.get("rl", [])
    if game == "tiger":
        has_wild = 0 in rl
    elif game == "ox":
        has_wild = 99 in rl

    parts = []
    if lines > 0:
        parts.append(f"{lines}线")
    if has_wild:
        parts.append("狂野")
    if lines >= 5:
        parts.append("全中")
    if aw > 0:
        parts.append(f"大奖")

    return " ".join(parts) if parts else f"{lines}线中奖"


def analyze_tiger(data_dir: str, github_path: str, token: str | None = None) -> str:
    """分析 Tiger 数据，返回 markdown 摘要。"""
    game = "tiger"
    free_spins = []   # (文件名, 起始编号, 轮次, 总赢, 说明)
    angry_list = []   # (文件名, 编号, 说明)
    big_wins = []     # (文件名, 编号, 金额, 说明)

    data_files = sorted([f for f in os.listdir(data_dir) if f.endswith(".txt") and f != "url.txt"])

    for filename in data_files:
        filepath = os.path.join(data_dir, filename)
        records = _parse_lines(filepath)
        data_url = f"{GITHUB_RAW_BASE}/{github_path}/{urllib.parse.quote(filename)}"

        i = 0
        while i < len(records):
            rec = records[i]
            line_num = i + 1  # 1-based

            # 检测免费旋转触发
            nst = rec.get("nst", 1)
            if nst != 1 and rec.get("st", 1) == 1:
                # 统计后续 st=4 的轮次
                rounds = 0
                total_win = float(rec.get("aw", 0))
                j = i + 1
                while j < len(records) and records[j].get("st") == 4:
                    rounds += 1
                    total_win += float(records[j].get("aw", 0))
                    j += 1
                desc = "免费旋转"
                if rounds >= 3:
                    desc = f"{rounds}轮免费旋转，验证多轮循环"
                elif total_win >= 100:
                    desc = "大额免费旋转"
                else:
                    desc = "免费旋转 基本流程"
                free_spins.append((filename, line_num, f"{rounds}轮", total_win, desc, data_url))
                i = j
                continue

            # 检测 isAngry
            ist = rec.get("ist", False)
            if ist:
                is_win = rec.get("wp") is not None
                desc = "有中奖的愤怒动画" if is_win else "无中奖的愤怒动画"
                angry_list.append((filename, line_num, desc, data_url))

            # 检测大额/多线中奖
            aw = float(rec.get("aw", 0))
            tbb = float(rec.get("tbb", 1))
            win_lines = _count_win_lines(rec)
            if (win_lines >= 3 or aw >= tbb * 10) and aw > 0:
                desc = _describe_win(rec, game)
                big_wins.append((filename, line_num, aw, desc, data_url))

            i += 1

    return _format_tiger_markdown(free_spins, angry_list, big_wins, token=token)


def _format_tiger_markdown(free_spins, angry_list, big_wins, token: str | None = None) -> str:
    """格式化 Tiger 分析结果为 markdown。"""
    sections = []

    if free_spins:
        lines = ["### 🎰 免费旋转测试", ""]
        lines.append("| 数据组 | 起始编号 | 轮次 | 总赢 | 测试要点 | 调试链接 |")
        lines.append("|--------|---------|------|------|---------|---------|")
        for fname, num, rounds, win, desc, data_url in free_spins:
            link = _build_debug_link("tiger", data_url, num, token=token)
            lines.append(f"| {fname} | #{num:03d} | {rounds} | {win:.0f} | {desc} | [点击测试]({link}) |")
        sections.append("\n".join(lines))

    if angry_list:
        lines = ["### 🐯 isAngry 老虎动画", ""]
        lines.append("| 数据组 | 编号 | 说明 | 调试链接 |")
        lines.append("|--------|------|------|---------|")
        for fname, num, desc, data_url in angry_list:
            link = _build_debug_link("tiger", data_url, num, token=token)
            lines.append(f"| {fname} | #{num:03d} | {desc} | [点击测试]({link}) |")
        sections.append("\n".join(lines))

    if big_wins:
        lines = ["### 💰 大额/多线中奖", ""]
        lines.append("| 数据组 | 编号 | 金额 | 说明 | 调试链接 |")
        lines.append("|--------|------|------|------|---------|")
        for fname, num, amount, desc, data_url in big_wins:
            link = _build_debug_link("tiger", data_url, num, token=token)
            lines.append(f"| {fname} | #{num:03d} | {amount:.0f} | {desc} | [点击测试]({link}) |")
        sections.append("\n".join(lines))

    if not sections:
        return "_未检测到特殊测试点_"

    return "\n\n".join(sections)


def analyze_ox(data_dir: str, github_path: str, token: str | None = None) -> str:
    """分析 Ox 数据，返回 markdown 摘要。"""
    game = "ox"
    free_spins = []
    big_wins = []
    multiplier_list = []  # 10x 倍率

    data_files = sorted([f for f in os.listdir(data_dir) if f.endswith(".txt") and f != "url.txt"])

    for filename in data_files:
        filepath = os.path.join(data_dir, filename)
        records = _parse_lines(filepath)
        data_url = f"{GITHUB_RAW_BASE}/{github_path}/{urllib.parse.quote(filename)}"

        i = 0
        while i < len(records):
            rec = records[i]
            line_num = i + 1

            # 检测免费旋转
            fs = rec.get("fs", False)
            nst = rec.get("nst", 1)
            if (fs or nst == 4) and rec.get("st", 1) == 1:
                rounds = 0
                total_win = float(rec.get("aw", 0))
                j = i + 1
                while j < len(records) and records[j].get("st") == 4:
                    rounds += 1
                    total_win += float(records[j].get("aw", 0))
                    j += 1
                desc = "免费旋转"
                if total_win >= 100:
                    desc = "大额免费旋转"
                elif rounds >= 3:
                    desc = f"{rounds}轮免费旋转"
                else:
                    desc = "免费旋转 基本流程"
                free_spins.append((filename, line_num, f"{rounds}轮", total_win, desc, data_url))
                i = j
                continue

            # 检测 10x 倍率
            im = rec.get("im", False)
            if im:
                aw = float(rec.get("aw", 0))
                multiplier_list.append((filename, line_num, aw, "10x 倍率触发", data_url))

            # 检测大额/多线中奖
            aw = float(rec.get("aw", 0))
            tbb = float(rec.get("tbb", 1))
            win_lines = _count_win_lines(rec)
            if (win_lines >= 3 or aw >= tbb * 10) and aw > 0:
                desc = _describe_win(rec, game)
                big_wins.append((filename, line_num, aw, desc, data_url))

            i += 1

    return _format_ox_markdown(free_spins, big_wins, multiplier_list, token=token)


def _format_ox_markdown(free_spins, big_wins, multiplier_list, token: str | None = None) -> str:
    """格式化 Ox 分析结果为 markdown。"""
    sections = []

    if free_spins:
        lines = ["### 🎰 免费旋转测试", ""]
        lines.append("| 数据组 | 起始编号 | 轮次 | 总赢 | 测试要点 | 调试链接 |")
        lines.append("|--------|---------|------|------|---------|---------|")
        for fname, num, rounds, win, desc, data_url in free_spins:
            link = _build_debug_link("ox", data_url, num, token=token)
            lines.append(f"| {fname} | #{num:03d} | {rounds} | {win:.0f} | {desc} | [点击测试]({link}) |")
        sections.append("\n".join(lines))

    if multiplier_list:
        lines = ["### ✨ 10x 倍率", ""]
        lines.append("| 数据组 | 编号 | 金额 | 说明 | 调试链接 |")
        lines.append("|--------|------|------|------|---------|")
        for fname, num, amount, desc, data_url in multiplier_list:
            link = _build_debug_link("ox", data_url, num, token=token)
            lines.append(f"| {fname} | #{num:03d} | {amount:.0f} | {desc} | [点击测试]({link}) |")
        sections.append("\n".join(lines))

    if big_wins:
        lines = ["### 💰 大额/多线中奖", ""]
        lines.append("| 数据组 | 编号 | 金额 | 说明 | 调试链接 |")
        lines.append("|--------|------|------|------|---------|")
        for fname, num, amount, desc, data_url in big_wins:
            link = _build_debug_link("ox", data_url, num, token=token)
            lines.append(f"| {fname} | #{num:03d} | {amount:.0f} | {desc} | [点击测试]({link}) |")
        sections.append("\n".join(lines))

    if not sections:
        return "_未检测到特殊测试点_"

    return "\n\n".join(sections)


def analyze_anubis(data_dir: str, github_path: str, token: str | None = None) -> str:
    """分析 Anubis 数据，返回 markdown 摘要。"""
    game = "anubis"
    free_spins = []
    scatter_list = []
    big_wins = []

    data_files = sorted([f for f in os.listdir(data_dir) if f.endswith(".txt") and f != "url.txt"])

    for filename in data_files:
        filepath = os.path.join(data_dir, filename)
        records = _parse_lines(filepath)
        data_url = f"{GITHUB_RAW_BASE}/{github_path}/{urllib.parse.quote(filename)}"

        i = 0
        while i < len(records):
            rec = records[i]
            line_num = i + 1

            # 检测免费旋转
            nst = rec.get("nst", 1)
            if nst != 1 and rec.get("st", 1) == 1:
                rounds = 0
                total_win = float(rec.get("aw", 0))
                j = i + 1
                while j < len(records) and records[j].get("st") == 4:
                    rounds += 1
                    total_win += float(records[j].get("aw", 0))
                    j += 1
                desc = "免费旋转"
                if rounds >= 5:
                    desc = f"{rounds}轮免费旋转"
                elif total_win >= 100:
                    desc = "大额免费旋转"
                else:
                    desc = "免费旋转 基本流程"
                free_spins.append((filename, line_num, f"{rounds}轮", total_win, desc, data_url))
                i = j
                continue

            # 检测 scatter 累积
            sc = rec.get("sc", 0)
            if sc and sc >= 3:
                desc = f"Scatter x{sc}"
                scatter_list.append((filename, line_num, desc, data_url))

            # 检测大额中奖
            aw = float(rec.get("aw", 0))
            tbb = float(rec.get("tbb", 1))
            if aw >= tbb * 5 and aw > 0:
                gm = rec.get("gm", 0)
                desc = f"大额中奖"
                if gm and gm > 1:
                    desc += f" ({gm}x 倍率)"
                big_wins.append((filename, line_num, aw, desc, data_url))

            i += 1

    return _format_anubis_markdown(free_spins, scatter_list, big_wins, token=token)


def _format_anubis_markdown(free_spins, scatter_list, big_wins, token: str | None = None) -> str:
    """格式化 Anubis 分析结果为 markdown。"""
    sections = []

    if free_spins:
        lines = ["### 🎰 免费旋转测试", ""]
        lines.append("| 数据组 | 起始编号 | 轮次 | 总赢 | 测试要点 | 调试链接 |")
        lines.append("|--------|---------|------|------|---------|---------|")
        for fname, num, rounds, win, desc, data_url in free_spins:
            link = _build_debug_link("anubis", data_url, num, token=token)
            lines.append(f"| {fname} | #{num:03d} | {rounds} | {win:.0f} | {desc} | [点击测试]({link}) |")
        sections.append("\n".join(lines))

    if scatter_list:
        lines = ["### 🔮 Scatter 累积", ""]
        lines.append("| 数据组 | 编号 | 说明 | 调试链接 |")
        lines.append("|--------|------|------|---------|")
        for fname, num, desc, data_url in scatter_list:
            link = _build_debug_link("anubis", data_url, num, token=token)
            lines.append(f"| {fname} | #{num:03d} | {desc} | [点击测试]({link}) |")
        sections.append("\n".join(lines))

    if big_wins:
        lines = ["### 💰 大额中奖", ""]
        lines.append("| 数据组 | 编号 | 金额 | 说明 | 调试链接 |")
        lines.append("|--------|------|------|------|---------|")
        for fname, num, amount, desc, data_url in big_wins:
            link = _build_debug_link("anubis", data_url, num, token=token)
            lines.append(f"| {fname} | #{num:03d} | {amount:.0f} | {desc} | [点击测试]({link}) |")
        sections.append("\n".join(lines))

    if not sections:
        return "_未检测到特殊测试点_"

    return "\n\n".join(sections)


def analyze(game: str, data_dir: str, github_path: str, token: str | None = None) -> str:
    """统一入口：根据游戏类型分析数据目录，返回 markdown 摘要。

    Args:
        game: 游戏类型 (tiger / ox / anubis)
        data_dir: 处理后的数据目录绝对路径
        github_path: GitHub 相对路径 (如 tigerdate/0316_0831)
        token: 自定义 token，为 None 时使用默认值

    Returns:
        markdown 格式的分析摘要
    """
    if game == "tiger":
        return analyze_tiger(data_dir, github_path, token=token)
    elif game == "ox":
        return analyze_ox(data_dir, github_path, token=token)
    elif game == "anubis":
        return analyze_anubis(data_dir, github_path, token=token)
    else:
        return f"_不支持的游戏类型: {game}_"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("用法: python analyze_data.py <game> <data_dir>")
        print("  game: tiger / ox / anubis")
        print("  data_dir: 数据目录路径 (如 tigerdate/0316_0831)")
        sys.exit(1)

    game = sys.argv[1]
    data_dir = sys.argv[2]
    github_path = data_dir.replace("\\", "/")
    # 只取相对路径部分
    for prefix in ("tigerdate/", "oxdate/", "anubisdate/"):
        if prefix in github_path:
            github_path = github_path[github_path.index(prefix.split("/")[0]):]
            break

    result = analyze(game, data_dir, github_path)
    print(result)

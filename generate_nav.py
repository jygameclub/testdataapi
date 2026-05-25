"""
扫描所有游戏批次目录，生成 README 历史数据导航章节。

读取每个批次的 url.txt 提取调试链接，更新 README.md 中
<!-- NAV_START --> 到 <!-- NAV_END --> 之间的内容。
"""

import os
import re
import urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 游戏配置：(目录名, 显示名, 游戏基础URL用于识别)
GAMES = [
    ("mahjong1date", "Mahjong Ways 1"),
    ("mahjong2date", "Mahjong Ways 2"),
    ("tigerdate", "Fortune-Tiger"),
    ("oxdate", "Fortune-Ox"),
    ("anubisdate", "Anubis"),
]


def _parse_date_dir(name: str) -> str:
    """将 0316_0831 格式转为 03-16 08:31 显示。"""
    if len(name) == 9 and name[4] == "_":
        return f"{name[0:2]}-{name[2:4]} {name[5:7]}:{name[7:9]}"
    return name


def _get_data_files(batch_dir: str) -> list[str]:
    """获取批次目录中的数据文件（排除 url.txt/manifest.json）。"""
    files = []
    for f in sorted(os.listdir(batch_dir)):
        if f == "url.txt" or f == "manifest.json":
            continue
        if f.endswith(".txt") or f.endswith(".json"):
            files.append(f)
    return files


def _get_debug_links(batch_dir: str) -> list[str]:
    """从 url.txt 读取调试链接。"""
    url_file = os.path.join(batch_dir, "url.txt")
    if not os.path.exists(url_file):
        return []
    links = []
    with open(url_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("https://fish-games"):
                links.append(line)
    return links


def _summarize_files(files: list[str]) -> str:
    """汇总文件列表为简短描述。"""
    if not files:
        return "-"
    if len(files) <= 3:
        return ", ".join(files)
    return f"{files[0]} ~ {files[-1]} ({len(files)}个文件)"


def generate_nav_markdown() -> str:
    """生成完整的导航 markdown 内容。"""
    sections = []

    for dir_name, display_name in GAMES:
        game_dir = os.path.join(SCRIPT_DIR, dir_name)
        if not os.path.isdir(game_dir):
            continue

        # 获取所有批次目录，按时间倒序
        batches = []
        for d in os.listdir(game_dir):
            full_path = os.path.join(game_dir, d)
            if os.path.isdir(full_path) and re.match(r"\d{4}_\d{4}", d):
                batches.append(d)
        batches.sort(reverse=True)

        if not batches:
            continue

        lines = [f"### {display_name}", ""]
        lines.append("| 批次 | 日期 | 数据文件 | 调试链接 |")
        lines.append("|------|------|---------|---------|")

        for batch in batches:
            batch_dir = os.path.join(game_dir, batch)
            date_str = _parse_date_dir(batch)
            data_files = _get_data_files(batch_dir)
            debug_links = _get_debug_links(batch_dir)
            files_summary = _summarize_files(data_files)

            # 生成调试链接列表
            if debug_links:
                link_parts = []
                for idx, link in enumerate(debug_links):
                    if "debugDataPath=" in link:
                        label = "批次回放"
                    elif idx < len(data_files):
                        label = data_files[idx].replace(".txt", "")
                    else:
                        label = f"文件{idx+1}"
                    link_parts.append(f"[{label}]({link})")
                links_str = " ".join(link_parts)
            else:
                links_str = "-"

            lines.append(f"| {batch} | {date_str} | {files_summary} | {links_str} |")

        sections.append("\n".join(lines))

    if not sections:
        return "_暂无历史数据_"

    return "\n\n".join(sections)


def update_readme():
    """更新 README.md 中的导航章节。"""
    readme_path = os.path.join(SCRIPT_DIR, "README.md")

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    nav_content = generate_nav_markdown()
    new_nav = f"<!-- NAV_START -->\n\n## 历史数据导航\n\n{nav_content}\n\n<!-- NAV_END -->"

    # 替换已有的导航区域，或追加到末尾
    pattern = r"<!-- NAV_START -->.*?<!-- NAV_END -->"
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, new_nav, content, flags=re.DOTALL)
    else:
        content = content.rstrip() + "\n\n" + new_nav + "\n"

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("README.md 导航已更新")


if __name__ == "__main__":
    update_readme()

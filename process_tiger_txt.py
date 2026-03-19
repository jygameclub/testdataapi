"""
处理上传的 tiger 数据 txt 文件，
创建日期+时间目录，转换数据并生成 url 文件。

支持两种输入:
  1. 单个 .txt 文件路径（支持单行JSONL和多行格式化JSON）
  2. .zip 文件路径（内含多个 .txt）

用法: python process_tiger_txt.py
"""

import json
import os
import zipfile
from datetime import datetime

# GitHub 仓库信息
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/jygameclub/testdataapi/main"
DEFAULT_TOKEN = "b3bb96ff1faef019504b83495ec3e45a"

def _game_url_base(token: str | None = None) -> str:
    t = token or DEFAULT_TOKEN
    return (
        "https://fish-games.s3.amazonaws.com/tiger/index.html"
        f"?env=ceshislot.osshaiwai.com&hasFloat=0&token={t}&language=en&debug=1"
    )

# 需要确保为 float 类型的字段（金额相关）
FLOAT_FIELDS = {
    "ssaw", "crtw", "twbm", "cs", "ctw", "aw",
    "blb", "blab", "bl", "tb", "tbb", "tw", "np",
}


def multiline_to_jsonl(content: str) -> list[str]:
    """将多行格式化JSON转换为单行JSONL列表。

    支持:
      - 已经是单行JSONL格式（每行一个JSON对象）
      - 单个或多个格式化（多行缩进）的JSON对象
    """
    content = content.strip()
    if not content:
        return []

    # 快速判断：如果第一个非空行本身就是完整JSON，按JSONL处理
    first_line = content.split("\n", 1)[0].strip()
    if first_line.startswith("{"):
        try:
            json.loads(first_line)
            return [line for line in content.split("\n") if line.strip()]
        except json.JSONDecodeError:
            pass

    # 多行JSON：用大括号计数法拆分出每个完整的JSON对象
    lines = []
    depth = 0
    current = []
    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        depth += stripped.count("{") - stripped.count("}")
        current.append(stripped)
        if depth == 0 and current:
            merged = " ".join(current)
            try:
                obj = json.loads(merged)
                lines.append(json.dumps(obj, separators=(",", ":"), ensure_ascii=False))
            except json.JSONDecodeError:
                pass
            current = []

    if current:
        merged = " ".join(current)
        open_b = merged.count("{")
        close_b = merged.count("}")
        if open_b > close_b:
            merged += "}" * (open_b - close_b)
        try:
            obj = json.loads(merged)
            lines.append(json.dumps(obj, separators=(",", ":"), ensure_ascii=False))
        except json.JSONDecodeError:
            pass

    return lines


def convert_line(line: str) -> str | None:
    """将一行 tiger 数据转换为目标格式。"""
    line = line.strip()
    if not line:
        return None

    # 尝试修复不完整的JSON（补全缺失的 } ）
    raw = line
    open_b = raw.count("{")
    close_b = raw.count("}")
    if open_b > close_b:
        raw = raw + "}" * (open_b - close_b)

    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None

    # Tiger 格式: {"code":200,"data":{...}}，data 直接就是 spin 数据
    if "data" in obj:
        si = obj["data"]                # {"code":200, "data":{...}}
    elif "dt" in obj:
        si = obj["dt"]["si"]            # {"dt":{"si":{...}}}
    else:
        return None

    # 金额字段转 float
    for key in FLOAT_FIELDS:
        if key in si and si[key] is not None and isinstance(si[key], int):
            si[key] = float(si[key])

    # 添加额外计算字段
    si["result"] = si["rl"]
    si["spinId"] = si["sid"]
    si["singleBet"] = float(si["tbb"])
    si["size"] = float(si["cs"])
    si["level"] = si["ml"]
    si["symbol"] = len(si["rl"])        # Tiger: rl 是 9 个位置 (3x3)
    si["preBetMoney"] = float(si["blb"])
    si["postBetMoney"] = float(si["blab"])
    si["postWinMoney"] = float(si["bl"])
    si["allgetmoney"] = float(si["aw"])
    si["iswin"] = 1 if si["wp"] is not None else 0

    return json.dumps(si, ensure_ascii=False)


def process_txt(txt_path: str, token: str | None = None) -> tuple[str, str, int, str]:
    """处理单个 tiger txt 文件，返回 (date_dir_name, url_file_path, file_count, analysis_md)。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 在 tigerdate/ 下创建日期+时间子目录
    now = datetime.now()
    date_dir_name = now.strftime("%m%d_%H%M")
    tigerdate_dir = os.path.join(script_dir, "tigerdate")
    output_dir = os.path.join(tigerdate_dir, date_dir_name)
    os.makedirs(output_dir, exist_ok=True)
    print(f"创建目录: tigerdate/{date_dir_name}/")

    # 读取并转换（支持多行格式化JSON和单行JSONL）
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    json_lines = multiline_to_jsonl(content)
    results = []
    for line in json_lines:
        result = convert_line(line)
        if result:
            results.append(result)

    basename = os.path.basename(txt_path)
    out_path = os.path.join(output_dir, basename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(results) + "\n")

    txt_filenames = [basename]
    print(f"  {basename}: {len(results)} 条记录")

    # 生成 url.txt
    github_path = f"tigerdate/{date_dir_name}"
    url_lines = []

    for name in txt_filenames:
        url_lines.append(f"{GITHUB_RAW_BASE}/{github_path}/{name}")

    url_lines.append("")  # 空行分隔

    game_base = _game_url_base(token)
    for name in txt_filenames:
        data_url = f"{GITHUB_RAW_BASE}/{github_path}/{name}"
        url_lines.append(f"{game_base}&debugDataUrl={data_url}&debugStart=1")

    url_file = os.path.join(output_dir, "url.txt")
    with open(url_file, "w", encoding="utf-8") as f:
        f.write("\n".join(url_lines) + "\n")

    print(f"\n完成！共处理 {len(txt_filenames)} 个文件")
    print(f"数据目录: tigerdate/{date_dir_name}/")
    print(f"URL 文件: tigerdate/{date_dir_name}/url.txt")

    # 数据分析
    from analyze_data import analyze
    github_path = f"tigerdate/{date_dir_name}"
    analysis_md = analyze("tiger", output_dir, github_path, token=token)

    # 将分析结果写入 analysis.md
    analysis_file = os.path.join(output_dir, "analysis.md")
    with open(analysis_file, "w", encoding="utf-8") as f:
        f.write(analysis_md)

    return date_dir_name, url_file, len(txt_filenames), analysis_md


def process_zip(zip_path: str, token: str | None = None) -> tuple[str, str, int, str]:
    """处理 tiger zip 文件，返回 (date_dir_name, url_file_path, file_count, analysis_md)。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    now = datetime.now()
    date_dir_name = now.strftime("%m%d_%H%M")
    tigerdate_dir = os.path.join(script_dir, "tigerdate")
    output_dir = os.path.join(tigerdate_dir, date_dir_name)
    os.makedirs(output_dir, exist_ok=True)
    print(f"创建目录: tigerdate/{date_dir_name}/")

    txt_filenames = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            if not info.filename.endswith(".txt"):
                continue

            basename = os.path.basename(info.filename)
            data = zf.read(info.filename).decode("utf-8")

            json_lines = multiline_to_jsonl(data)
            results = []
            for line in json_lines:
                result = convert_line(line)
                if result:
                    results.append(result)

            out_path = os.path.join(output_dir, basename)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(results) + "\n")

            txt_filenames.append(basename)
            print(f"  {basename}: {len(results)} 条记录")

    txt_filenames.sort()

    # 生成 url.txt
    github_path = f"tigerdate/{date_dir_name}"
    url_lines = []

    for name in txt_filenames:
        url_lines.append(f"{GITHUB_RAW_BASE}/{github_path}/{name}")

    url_lines.append("")

    game_base = _game_url_base(token)
    for name in txt_filenames:
        data_url = f"{GITHUB_RAW_BASE}/{github_path}/{name}"
        url_lines.append(f"{game_base}&debugDataUrl={data_url}&debugStart=1")

    url_file = os.path.join(output_dir, "url.txt")
    with open(url_file, "w", encoding="utf-8") as f:
        f.write("\n".join(url_lines) + "\n")

    print(f"\n完成！共处理 {len(txt_filenames)} 个文件")
    print(f"数据目录: tigerdate/{date_dir_name}/")
    print(f"URL 文件: tigerdate/{date_dir_name}/url.txt")

    # 数据分析
    from analyze_data import analyze
    github_path = f"tigerdate/{date_dir_name}"
    analysis_md = analyze("tiger", output_dir, github_path, token=token)

    # 将分析结果写入 analysis.md
    analysis_file = os.path.join(output_dir, "analysis.md")
    with open(analysis_file, "w", encoding="utf-8") as f:
        f.write(analysis_md)

    return date_dir_name, url_file, len(txt_filenames), analysis_md


def process_file(file_path: str, token: str | None = None) -> tuple[str, str, int, str]:
    """自动判断文件类型并处理。"""
    if file_path.lower().endswith(".zip"):
        return process_zip(file_path, token=token)
    else:
        return process_txt(file_path, token=token)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    update_dir = os.path.join(script_dir, "update")

    # 优先找 zip，再找 txt
    files = [f for f in os.listdir(update_dir)
             if f.lower().startswith("tiger") and (f.endswith(".zip") or f.endswith(".txt"))]
    if not files:
        print("在 update/ 目录下未找到 tiger 开头的 zip/txt 文件")
        return

    file_path = os.path.join(update_dir, files[0])
    print(f"找到文件: {files[0]}")
    process_file(file_path)


if __name__ == "__main__":
    main()

"""
从 update/ 目录读取 anubis 数据返回的 zip 文件，
创建日期+时间目录，转换数据并生成 url 文件。

用法: python process_anubis_zip.py
"""

import json
import os
import zipfile
from datetime import datetime

# GitHub 仓库信息
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/jygameclub/testdataapi/main"
GAME_URL_BASE = (
    "https://fish-games.s3.amazonaws.com/Anubis/index.html"
    "?env=ceshislot.osshaiwai.com&hasFloat=0"
    "&token=b3bb96ff1faef019504b83495ec3e45a"
    "&language=en&debug=1"
)

# 需要确保为 float 类型的字段（金额相关）
FLOAT_FIELDS = {
    "ssaw", "crtw", "twbm", "cs", "ctw", "aw",
    "blb", "blab", "bl", "tb", "tbb", "tw", "np",
}


def convert_line(line: str) -> str | None:
    """将一行 anubis 数据转换为目标格式。"""
    line = line.strip()
    if not line:
        return None

    raw = json.loads(line)

    # 支持两种源格式
    if "data" in raw:
        si = raw["data"]           # anubis0304 格式: {"code":200, "data":{...}}
    elif "dt" in raw:
        si = raw["dt"]["si"]       # anubis 格式: {"dt":{"si":{...}}}
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
    si["symbol"] = len(si["rl"])
    si["preBetMoney"] = float(si["blb"])
    si["postBetMoney"] = float(si["blab"])
    si["postWinMoney"] = float(si["bl"])
    si["allgetmoney"] = float(si["aw"])
    si["iswin"] = 1 if si["wp"] is not None else 0

    return json.dumps(si, ensure_ascii=False)


def process_zip(zip_path: str) -> tuple[str, str, int]:
    """处理 anubis zip 文件，返回 (date_dir_name, url_file_path, file_count)。

    可被 slack_bot.py 等外部调用。
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 在 anubisdate/ 下创建日期+时间子目录
    now = datetime.now()
    date_dir_name = now.strftime("%m%d_%H%M")
    anubisdate_dir = os.path.join(script_dir, "anubisdate")
    output_dir = os.path.join(anubisdate_dir, date_dir_name)
    os.makedirs(output_dir, exist_ok=True)
    print(f"创建目录: anubisdate/{date_dir_name}/")

    # 解压并转换
    txt_filenames = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            if not info.filename.endswith(".txt"):
                continue

            basename = os.path.basename(info.filename)
            data = zf.read(info.filename).decode("utf-8")
            lines = data.strip().split("\n")

            results = []
            for line in lines:
                result = convert_line(line)
                if result:
                    results.append(result)

            out_path = os.path.join(output_dir, basename)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(results) + "\n")

            txt_filenames.append(basename)
            print(f"  {basename}: {len(results)} 条记录")

    txt_filenames.sort()

    # 在 anubisdate/日期目录/ 下生成 url.txt
    github_path = f"anubisdate/{date_dir_name}"
    url_lines = []

    for name in txt_filenames:
        url_lines.append(f"{GITHUB_RAW_BASE}/{github_path}/{name}")

    url_lines.append("")  # 空行分隔

    for name in txt_filenames:
        data_url = f"{GITHUB_RAW_BASE}/{github_path}/{name}"
        url_lines.append(f"{GAME_URL_BASE}&debugDataUrl={data_url}&debugStart=1")

    url_file = os.path.join(output_dir, "url.txt")
    with open(url_file, "w", encoding="utf-8") as f:
        f.write("\n".join(url_lines) + "\n")

    print(f"\n完成！共处理 {len(txt_filenames)} 个文件")
    print(f"数据目录: anubisdate/{date_dir_name}/")
    print(f"URL 文件: anubisdate/{date_dir_name}/url.txt")

    return date_dir_name, url_file, len(txt_filenames)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    update_dir = os.path.join(script_dir, "update")

    zip_files = [f for f in os.listdir(update_dir)
                 if f.lower().startswith("anubis") and f.endswith(".zip")]
    if not zip_files:
        print("在 update/ 目录下未找到 anubis 开头的 zip 文件")
        return

    zip_path = os.path.join(update_dir, zip_files[0])
    print(f"找到 zip 文件: {zip_files[0]}")
    process_zip(zip_path)


if __name__ == "__main__":
    main()

"""
将 anubis/ 目录下的数据文件转换为 Anubistest1 格式。

源格式 (anubis/*.txt):
  {"dt": {"si": {...}}, "err": null}

目标格式 (Anubistest1):
  {... si 字段 ..., "result": [...], "spinId": "...", "singleBet": 12.0, ...}
"""

import json
import glob
import os

# 需要确保为 float 类型的字段（金额相关）
FLOAT_FIELDS = {
    "ssaw", "crtw", "twbm", "cs", "ctw", "aw",
    "blb", "blab", "bl", "tb", "tbb", "tw", "np",
}


def convert_line(line: str) -> str | None:
    """将一行 anubis 格式数据转换为 Anubistest1 格式。"""
    line = line.strip()
    if not line:
        return None

    raw = json.loads(line)
    si = raw["dt"]["si"]

    # 金额字段转 float
    for key in FLOAT_FIELDS:
        if key in si and si[key] is not None and isinstance(si[key], int):
            si[key] = float(si[key])

    # 添加额外计算字段
    si["result"] = si["rl"]
    si["spinId"] = si["sid"]
    si["singleBet"] = float(si["tbb"])      # 单注金额（用 tbb，respin 时 tb=0）
    si["size"] = float(si["cs"])
    si["level"] = si["ml"]
    si["symbol"] = len(si["rl"])
    si["preBetMoney"] = float(si["blb"])
    si["postBetMoney"] = float(si["blab"])
    si["postWinMoney"] = float(si["bl"])
    si["allgetmoney"] = float(si["aw"])
    si["iswin"] = 1 if si["wp"] is not None else 0

    return json.dumps(si, ensure_ascii=False)


def convert_file_inplace(file_path: str):
    """直接覆盖原文件，将其转换为 Anubistest1 格式。"""
    with open(file_path, "r", encoding="utf-8") as fin:
        lines = fin.readlines()

    results = []
    for line in lines:
        result = convert_line(line)
        if result:
            results.append(result)

    with open(file_path, "w", encoding="utf-8") as fout:
        fout.write("\n".join(results) + "\n")

    return len(results)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    anubis_dir = os.path.join(script_dir, "anubis")

    # 找到所有 txt 文件并按文件名数字排序
    txt_files = sorted(
        glob.glob(os.path.join(anubis_dir, "*.txt")),
        key=lambda f: int(os.path.splitext(os.path.basename(f))[0])
        if os.path.splitext(os.path.basename(f))[0].isdigit()
        else os.path.basename(f),
    )

    if not txt_files:
        print(f"在 {anubis_dir} 下未找到 txt 文件")
        return

    total = 0
    for f in txt_files:
        n = convert_file_inplace(f)
        print(f"  {os.path.basename(f)}: {n} 条记录")
        total += n

    print(f"\n转换完成！共 {total} 条记录已直接覆盖原文件")


if __name__ == "__main__":
    main()

import os
import json

ox_dir = os.path.join(os.path.dirname(__file__), "ox")

for filename in sorted(os.listdir(ox_dir)):
    if not filename.endswith(".txt"):
        continue
    filepath = os.path.join(ox_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    errors = 0
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # 尝试修复不完整的JSON（补全缺失的 } ）
        raw = line
        open_b = raw.count("{")
        close_b = raw.count("}")
        if open_b > close_b:
            raw = raw + "}" * (open_b - close_b)

        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"  {filename} line {i+1}: {e}")
            new_lines.append(line)
            errors += 1
            continue

        # 已经是目标格式的跳过
        if "dt" in obj:
            new_lines.append(raw)
            continue

        # {"code":200,"msg":"success","data":{...}} -> {"dt":{"si":{...}},"err":null}
        data = obj.get("data", {})
        new_obj = {"dt": {"si": data}, "err": None}
        new_lines.append(json.dumps(new_obj, ensure_ascii=False))

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")

    print(f"{filename}: {len(new_lines)} lines converted" + (f" ({errors} errors)" if errors else ""))

print("done")

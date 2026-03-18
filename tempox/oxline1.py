import json

# 读取 1.txt
with open('1.txt', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 写入 2.txt（一行）
with open('2.txt', 'w', encoding='utf-8') as f:
    json.dump(data, f, separators=(',', ':'))
# testdataapi

游戏测试数据自动处理工具，支持通过 GitHub Issue 或 Slack 上传数据文件，自动转换格式、生成调试链接。

目前支持的游戏：**Anubis**、**Fortune-Ox**、**Fortune-Tiger**

---

## 目录结构

```
testdataapi/
├── anubis/              # Anubis 静态数据文件
├── anubis0304/          # Anubis 备用格式数据
├── anubisdate/          # Anubis 按批次存放的转换结果
│   └── 0304_0631/       #   批次目录（格式: MMDD_HHMM）
│       ├── 1.txt        #     转换后的数据文件
│       └── url.txt      #     数据链接 + 游戏调试链接
├── ox/                  # Fortune-Ox 静态数据文件
├── oxdate/              # Fortune-Ox 按批次存放的转换结果
│   └── 0313_1530/       #   批次目录
│       ├── data.txt
│       └── url.txt
├── tigerdate/           # Fortune-Tiger 按批次存放的转换结果
│   └── 0316_1200/       #   批次目录
│       ├── data.txt
│       └── url.txt
├── update/              # 手动上传文件暂存目录
├── process_anubis_zip.py    # Anubis 数据处理核心
├── process_ox_txt.py        # Fortune-Ox 数据处理核心
├── process_tiger_txt.py     # Fortune-Tiger 数据处理核心
├── convert_anubis.py        # Anubis 格式转换（独立使用）
├── convert_anubis0304.py    # Anubis 0304格式转换
├── ox.PY                    # Fortune-Ox 格式转换（独立使用）
├── slack_bot.py             # Slack Bot 自动处理
└── .github/workflows/
    ├── process-anubis.yml   # Anubis GitHub Actions
    ├── process-ox.yml       # Fortune-Ox GitHub Actions
    └── process-tiger.yml    # Fortune-Tiger GitHub Actions
```

---

## Anubis

### 支持的数据格式

| 格式 | 结构 |
|------|------|
| 格式A | `{"dt": {"si": {...}}, "err": null}` |
| 格式B | `{"code": 200, "msg": "success", "data": {...}}` |

### 上传方式

#### 方式一：GitHub Issue（自动）

1. 在仓库创建新 Issue
2. **标题**包含 `anubis`（如：`上传 anubis 数据`）
3. **正文**中拖入 `.zip` 附件（zip 内含多个 .txt 数据文件）
4. 创建后 GitHub Actions 自动：
   - 下载 zip → 转换数据 → 提交到 `anubisdate/` → 评论返回链接 → 关闭 Issue

#### 方式二：Slack（自动）

1. 在 Slack 频道上传文件
2. 文件名包含 `anubis` 且以 `.zip` 结尾
3. Bot 自动处理并回复链接

#### 方式三：本地手动

```bash
# 将 zip 放入 update/ 目录，文件名以 anubis 开头
python process_anubis_zip.py
```

### 输出结果

处理后在 `anubisdate/{MMDD_HHMM}/` 生成：

- **数据文件** — 每行一个 JSON，包含转换后的 spin 数据
- **url.txt** — 包含两部分：
  - 原始数据链接：`https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/{批次}/{文件名}`
  - 游戏调试链接：`https://fish-games.s3.amazonaws.com/Anubis/index.html?...&debugDataUrl={数据链接}&debugStart=1`

---

## Fortune-Ox

### 支持的数据格式

与 Anubis 相同，支持两种源格式。同时自动修复不完整的 JSON（缺少 `}` 的情况）。

### 上传方式

#### 方式一：GitHub Issue（自动）

1. 在仓库创建新 Issue
2. **标题**包含 `ox`（如：`上传 ox 数据`）
3. **正文**中拖入 `.txt` 或 `.zip` 附件
4. 创建后 GitHub Actions 自动处理并返回链接

#### 方式二：Slack（自动）

1. 在 Slack 频道上传文件
2. 文件名包含 `ox` 且以 `.txt` 或 `.zip` 结尾
3. Bot 自动处理并回复链接

#### 方式三：本地手动

```bash
# 将 txt 或 zip 放入 update/ 目录，文件名以 ox 开头
python process_ox_txt.py
```

### 输出结果

处理后在 `oxdate/{MMDD_HHMM}/` 生成：

- **数据文件** — 转换后的 spin 数据
- **url.txt** — 包含：
  - 原始数据链接：`https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/{批次}/{文件名}`
  - 游戏调试链接：`https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?...&debugDataUrl={数据链接}&debugStart=1`

---

## Fortune-Tiger

### 支持的数据格式

| 格式 | 结构 |
|------|------|
| 格式A | `{"code": 200, "data": {...}}`（data 直接是 spin 数据，无 dt.si 嵌套） |
| 格式B | `{"dt": {"si": {...}}}` |

Tiger 的 `rl` 数组为 9 个位置（3x3 布局），与 Ox 的 12 个位置不同。同时自动修复不完整的 JSON。

### 上传方式

#### 方式一：GitHub Issue（自动）

1. 在仓库创建新 Issue
2. **标题**包含 `tiger`（如：`上传 tiger 数据`）
3. **正文**中拖入 `.txt` 或 `.zip` 附件
4. 创建后 GitHub Actions 自动处理并返回链接

#### 方式二：Slack（自动）

1. 在 Slack 频道上传文件
2. 文件名包含 `tiger` 且以 `.txt` 或 `.zip` 结尾
3. Bot 自动处理并回复链接

#### 方式三：本地手动

```bash
# 将 txt 或 zip 放入 update/ 目录，文件名以 tiger 开头
python process_tiger_txt.py
```

### 输出结果

处理后在 `tigerdate/{MMDD_HHMM}/` 生成：

- **数据文件** — 转换后的 spin 数据
- **url.txt** — 包含：
  - 原始数据链接：`https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/{批次}/{文件名}`
  - 游戏调试链接：`https://fish-games.s3.amazonaws.com/tiger/index.html?...&debugDataUrl={数据链接}&debugStart=1`

---

## 数据转换字段说明

转换过程会从原始 spin 数据中提取 `si` 对象，并添加以下计算字段：

| 字段 | 来源 | 说明 |
|------|------|------|
| `result` | `rl` | 轮盘结果 |
| `spinId` | `sid` | Spin ID |
| `singleBet` | `tbb` | 单注金额 |
| `size` | `cs` | 注码大小 |
| `level` | `ml` | 等级 |
| `symbol` | `len(rl)` | 符号数量 |
| `preBetMoney` | `blb` | 下注前余额 |
| `postBetMoney` | `blab` | 下注后余额 |
| `postWinMoney` | `bl` | 赢钱后余额 |
| `allgetmoney` | `aw` | 总赢金额 |
| `iswin` | `wp` | 是否赢（1/0） |

金额字段（`ssaw`, `crtw`, `twbm`, `cs`, `ctw`, `aw`, `blb`, `blab`, `bl`, `tb`, `tbb`, `tw`, `np`）会自动转为 float 类型。

---

## Slack Bot 配置

1. 复制 `.env.example` 为 `.env`，填入 Slack Token
2. 安装依赖：`pip install -r requirements.txt`
3. 启动：`python slack_bot.py`

Bot 同时监听 Anubis（`.zip`）、Fortune-Ox（`.txt` / `.zip`）和 Fortune-Tiger（`.txt` / `.zip`）文件上传。

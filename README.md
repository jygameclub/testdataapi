# testdataapi

游戏测试数据自动处理工具，通过 GitHub Issue 上传数据文件，自动转换格式、生成调试链接。

目前支持的游戏：**Anubis**、**Fortune-Ox**、**Fortune-Tiger**

---

## 快速开始：通过 GitHub Issue 上传数据

只需 3 步即可完成数据处理：

1. 在仓库中创建一个新 Issue
2. **标题**中包含游戏关键词（`anubis` / `ox` / `tiger`）
3. **正文**中拖入数据文件附件

创建后 GitHub Actions 会自动处理数据并在 Issue 评论中返回调试链接。

---

## 详细 Issue 使用教程

### 第一步：进入仓库 Issue 页面

打开仓库页面，点击顶部的 **Issues** 标签，然后点击右上角的 **New issue** 按钮。

### 第二步：填写 Issue 标题

标题中必须包含对应游戏的关键词，系统根据标题自动识别游戏类型：

| 游戏 | 标题关键词 | 示例标题 |
|------|-----------|---------|
| Anubis | `anubis` | `上传 anubis 数据` |
| Fortune-Ox | `ox` | `上传 ox 数据` |
| Fortune-Tiger | `tiger` | `上传 tiger 数据` |

### 第三步：上传数据文件

在 Issue 正文区域，直接**拖拽文件**到编辑框中（或点击编辑框底部的 "Attach files by dragging & dropping" 区域）。GitHub 会自动上传文件并生成附件链接。

**各游戏支持的文件格式：**

| 游戏 | 支持格式 |
|------|---------|
| Anubis | `.zip`（zip 内含多个 .txt 文件） |
| Fortune-Ox | `.txt` 或 `.zip` |
| Fortune-Tiger | `.txt` 或 `.zip` |

### 第四步：提交 Issue

点击 **Submit new issue** 按钮提交。GitHub Actions 会自动触发，通常在 1-2 分钟内完成处理。

### 第五步：查看处理结果

处理完成后，系统会自动在 Issue 下方评论返回结果：

- **成功** — 评论中包含原始数据链接和游戏调试链接，可直接点击调试链接在浏览器中测试
- **失败** — 评论中会说明错误原因和正确的数据格式说明
- **未找到附件** — 提示正确的文件上传方式

### 第六步：Issue 状态流转

数据处理成功后，Issue 会被自动打上 `待修复` 标签，进入以下工作流程：

```
上传数据 → [待修复] → 开发修复 → [待验证] → 测试验证 → [已验证/关闭]
                                       ↑                    |
                                       └── 验证不通过 ──────┘
```

| 步骤 | 操作人 | 在 Issue 中回复 | 效果 |
|------|--------|----------------|------|
| 1 | 开发 | `程序已修复` | 标签变为 `待验证` |
| 2a | 测试 | `测试已经验证` | 标签变为 `已验证`，Issue 自动关闭 |
| 2b | 测试 | `验证不通过` | 标签回退为 `待修复`，等待开发再次修复 |

> 直接在 Issue 下方回复对应关键词即可触发状态流转，无需手动修改标签。

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
└── .github/workflows/
    ├── process-anubis.yml   # Anubis GitHub Actions
    ├── process-ox.yml       # Fortune-Ox GitHub Actions
    ├── process-tiger.yml    # Fortune-Tiger GitHub Actions
    └── issue-lifecycle.yml  # Issue 状态流转自动化
```

---

## Anubis

### 支持的数据格式

| 格式 | 结构 |
|------|------|
| 格式A | `{"dt": {"si": {...}}, "err": null}` |
| 格式B | `{"code": 200, "msg": "success", "data": {...}}` |

### 上传方式

#### 方式一：GitHub Issue（推荐）

1. 在仓库创建新 Issue
2. **标题**包含 `anubis`（如：`上传 anubis 数据`）
3. **正文**中拖入 `.zip` 附件（zip 内含多个 .txt 数据文件）
4. 创建后 GitHub Actions 自动：
   - 下载 zip → 转换数据 → 提交到 `anubisdate/` → 评论返回链接

#### 方式二：本地手动

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

#### 方式一：GitHub Issue（推荐）

1. 在仓库创建新 Issue
2. **标题**包含 `ox`（如：`上传 ox 数据`）
3. **正文**中拖入 `.txt` 或 `.zip` 附件
4. 创建后 GitHub Actions 自动处理并返回链接

#### 方式二：本地手动

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

#### 方式一：GitHub Issue（推荐）

1. 在仓库创建新 Issue
2. **标题**包含 `tiger`（如：`上传 tiger 数据`）
3. **正文**中拖入 `.txt` 或 `.zip` 附件
4. 创建后 GitHub Actions 自动处理并返回链接

#### 方式二：本地手动

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

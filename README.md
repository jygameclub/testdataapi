# testdataapi

游戏测试数据自动处理工具，通过 GitHub Issue 上传数据文件，自动转换格式、生成调试链接。

目前支持的游戏：**Anubis**、**Fortune-Ox**、**Fortune-Tiger**、**Mahjong Ways 2**

---

## 快速开始：通过 GitHub Issue 上传数据

只需 3 步即可完成数据处理：

1. 在仓库中创建一个新 Issue
2. **标题**中包含游戏关键词（`anubis` / `ox` / `tiger` / `mahjong2` / `麻将2` / `MahjongWays2`）
3. **正文**中拖入数据文件附件
4. （可选）正文中添加 `token: 你的自定义token` 指定调试 token

创建后 GitHub Actions 会自动处理数据并在 Issue 评论中返回调试链接。

> 不指定 token 时使用默认值。处理完成后的评论中会显示当前 token 和替换方法。

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
| Mahjong Ways 2 | `mahjong2` / `麻将2` / `majianng2` / `MahjongWays2` | `上传 麻将2 数据` |

### 第三步：上传数据文件

在 Issue 正文区域，直接**拖拽文件**到编辑框中（或点击编辑框底部的 "Attach files by dragging & dropping" 区域）。GitHub 会自动上传文件并生成附件链接。

**各游戏支持的文件格式：**

| 游戏 | 支持格式 |
|------|---------|
| Anubis | `.zip`（zip 内含多个 .txt 文件） |
| Fortune-Ox | `.txt` 或 `.zip` |
| Fortune-Tiger | `.txt` 或 `.zip` |
| Mahjong Ways 2 | `.txt` 或 `.zip` |

### 第四步：提交 Issue

点击 **Submit new issue** 按钮提交。GitHub Actions 会自动触发，通常在 1-2 分钟内完成处理。

### 第五步：查看处理结果

处理完成后，系统会自动在 Issue 下方评论返回结果：

- **成功** — 评论中包含原始数据链接和游戏调试链接，可直接点击调试链接在浏览器中测试
- **失败** — 评论中会说明错误原因和正确的数据格式说明
- **未找到附件** — 提示正确的文件上传方式
- **Mahjong2 格式咨询** — 在 Mahjong2 Issue 下回复 `这样的数据`，系统会返回支持格式、处理逻辑和 URL 参数说明

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
├── mahjong2date/        # Mahjong Ways 2 按批次存放的回放结果
│   └── 0525_0910/       #   批次目录
│       ├── 001.json
│       ├── manifest.json
│       └── url.txt
├── update/              # 手动上传文件暂存目录
├── process_anubis_zip.py    # Anubis 数据处理核心
├── process_ox_txt.py        # Fortune-Ox 数据处理核心
├── process_tiger_txt.py     # Fortune-Tiger 数据处理核心
├── process_mahjong2_txt.py  # Mahjong Ways 2 数据处理核心
├── convert_anubis.py        # Anubis 格式转换（独立使用）
├── convert_anubis0304.py    # Anubis 0304格式转换
├── ox.PY                    # Fortune-Ox 格式转换（独立使用）
└── .github/workflows/
    ├── process-anubis.yml   # Anubis GitHub Actions
    ├── process-ox.yml       # Fortune-Ox GitHub Actions
    ├── process-tiger.yml    # Fortune-Tiger GitHub Actions
    ├── process-mahjong2.yml # Mahjong Ways 2 GitHub Actions
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

## Mahjong Ways 2

### 支持的数据格式

支持 `xxbet_capture_*.txt` 这类 JSONL 抓包文件，每行一个 JSON 对象。脚本会提取 `data` 或 `dt.si` 中的 spin 数据，并按“每次实际扣费 bet”拆成 `001.json`、`002.json` 等回放文件。`st=21/22` 且 `tb=0` 属于免费旋转/续转链，不会当成新的下单起点。

批次目录会额外生成 `manifest.json`，WebGL 可通过 `debugDataPath` 读取目录并按 manifest 顺序回放。

### 上传方式

#### 方式一：GitHub Issue（推荐）

1. 在仓库创建新 Issue
2. **标题**包含 `mahjong2` / `麻将2` / `majianng2` / `MahjongWays2`（如：`上传 麻将2 数据`）
3. **正文**中拖入 `.txt` 或 `.zip` 附件
4. 创建后 GitHub Actions 自动处理并返回链接
5. 如果只是咨询格式，在 Issue 下回复 `这样的数据` 会自动返回支持格式说明

#### 方式二：本地手动

```bash
# 指定文件处理
python process_mahjong2_txt.py /path/to/xxbet_capture.txt

# 或将 txt/zip 放入 update/ 目录，文件名以 mahjong2 开头
python process_mahjong2_txt.py
```

### 输出结果

处理后在 `mahjong2date/{MMDD_HHMM}/` 生成：

- **数据文件** — `001.json`、`002.json`，默认每个文件是一轮扣费 bet 及其后续 cascade/continue 数据
- **manifest.json** — 文件顺序与摘要，供 WebGL URL 回放读取
- **validation_summary.json** — 机器可读校验结果，供 GitHub Actions 判断是否允许提交
- **url.txt** — 包含：
  - 数据目录基址：`https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/{批次}`
  - manifest 链接：`https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/{批次}/manifest.json`
  - 生产调试链接：`https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath={数据目录链接}&debugStart=1`

### 重点测试说明

`analysis.md` 会根据 Mahjong2 代码阈值自动生成测试说明：

- Big Win：总赢 >= 17 倍下注
- Mega Win：总赢 >= 35 倍下注
- Super Mega Win：总赢 >= 50 倍下注
- 连消/多段回放：同一 bet 内存在多个请求或 `st/nst=4`
- Scatter / Free Spin：`sc >= 3` 或 `fs` 中存在免费旋转状态
- 金色符号/百搭转换：`ptbr`、`rs`、`rsc` 等字段有内容
- 数据高危异常：`majiangerrorcheck` 会优先列出 `wp/ptbr/rl/rs.rns` 等客户端表现风险；GitHub Actions 会阻断这类批次提交，避免坏数据进入主回放目录

---

## Anubis / Ox / Tiger 数据转换字段说明

Anubis / Ox / Tiger 转换过程会从原始 spin 数据中提取 `si` 对象，并添加以下计算字段。Mahjong2 数据保持原始 spin 字段，只按 bet 拆分回放文件。

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

<!-- NAV_START -->

## 历史数据导航

### Mahjong Ways 2

| 批次 | 日期 | 数据文件 | 调试链接 |
|------|------|---------|---------|
| 0525_1407 | 05-25 14:07 | 001.json ~ 999.json (6003个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=6937d51c78fce0f2d29f93346f8c0f6e&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_1407&debugStart=1) |
| 0525_0921 | 05-25 09:21 | 001.json ~ 100.json (100个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0921&debugStart=1) |
| 0525_0910 | 05-25 09:10 | 001.json ~ 100.json (100个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0910&debugStart=1) |
| 0525_0603 | 05-25 06:03 | 001.json ~ 100.json (100个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0603&debugStart=1) |
| 0525_0526 | 05-25 05:26 | 001.json ~ 100.json (100个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0526&debugStart=1) |
| 0525_0523 | 05-25 05:23 | 001.json ~ 999.json (1000个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0523&debugStart=1) |
| 0525_0433 | 05-25 04:33 | 001.json ~ 999.json (1000个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0433&debugStart=1) |
| 0525_0416 | 05-25 04:16 | 001.json ~ 999.json (1000个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0416&debugStart=1) |
| 0525_0226 | 05-25 02:26 | 001.json ~ 999.json (1000个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0226&debugStart=1) |
| 0525_0220 | 05-25 02:20 | 001.json ~ 100.json (100个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0220&debugStart=1) |
| 0525_0219 | 05-25 02:19 | 001.json ~ 999.json (1000个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0219&debugStart=1) |
| 0525_0205 | 05-25 02:05 | 001.json ~ 999.json (1000个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0205&debugStart=1) |
| 0525_0204 | 05-25 02:04 | 001.json ~ 100.json (100个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0204&debugStart=1) |
| 0525_0202 | 05-25 02:02 | 001.json ~ 999.json (1000个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0202&debugStart=1) |
| 0525_0159 | 05-25 01:59 | 001.json ~ 100.json (100个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0159&debugStart=1) |
| 0525_0112 | 05-25 01:12 | 001.json ~ 291.json (291个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0112&debugStart=1) |
| 0525_0110 | 05-25 01:10 | 001.json ~ 311.json (311个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0110&debugStart=1) |
| 0525_0055 | 05-25 00:55 | 001.json ~ 311.json (311个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0055&debugStart=1) |
| 0525_0050 | 05-25 00:50 | 001.json ~ 100.json (100个文件) | [批次回放](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=436475c81b51e6893c740657870f86b7&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0050&debugStart=1) |

### Fortune-Tiger

| 批次 | 日期 | 数据文件 | 调试链接 |
|------|------|---------|---------|
| 0427_0623 | 04-27 06:23 | tiger_upload.txt | [tiger_upload](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0427_0623/tiger_upload.txt&debugStart=1) |
| 0427_0611 | 04-27 06:11 | tiger_upload.txt | [tiger_upload](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0427_0611/tiger_upload.txt&debugStart=1) |
| 0427_0606 | 04-27 06:06 | tiger_upload.txt | [tiger_upload](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0427_0606/tiger_upload.txt&debugStart=1) |
| 0427_0559 | 04-27 05:59 | tiger_upload.txt | [tiger_upload](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0427_0559/tiger_upload.txt&debugStart=1) |
| 0427_0513 | 04-27 05:13 | tiger_upload.txt | [tiger_upload](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0427_0513/tiger_upload.txt&debugStart=1) |
| 0410_0604 | 04-10 06:04 | tiger_upload.txt | [tiger_upload](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0410_0604/tiger_upload.txt&debugStart=1) |
| 0410_0600 | 04-10 06:00 | tiger_upload.txt | [tiger_upload](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0410_0600/tiger_upload.txt&debugStart=1) |
| 0318_0516 | 03-18 05:16 | 虎80-1.txt ~ 虎80-9.txt (10个文件) | [虎80-1](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0318_0516/虎80-1.txt&debugStart=1) [虎80-10](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0318_0516/虎80-10.txt&debugStart=1) [虎80-2](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0318_0516/虎80-2.txt&debugStart=1) [虎80-3](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0318_0516/虎80-3.txt&debugStart=1) [虎80-4](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0318_0516/虎80-4.txt&debugStart=1) [虎80-5](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0318_0516/虎80-5.txt&debugStart=1) [虎80-6](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0318_0516/虎80-6.txt&debugStart=1) [虎80-7](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0318_0516/虎80-7.txt&debugStart=1) [虎80-8](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0318_0516/虎80-8.txt&debugStart=1) [虎80-9](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0318_0516/虎80-9.txt&debugStart=1) |
| 0316_0831 | 03-16 08:31 | 虎80-1.txt ~ 虎80-9.txt (10个文件) | [虎80-1](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0831/虎80-1.txt&debugStart=1) [虎80-10](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0831/虎80-10.txt&debugStart=1) [虎80-2](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0831/虎80-2.txt&debugStart=1) [虎80-3](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0831/虎80-3.txt&debugStart=1) [虎80-4](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0831/虎80-4.txt&debugStart=1) [虎80-5](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0831/虎80-5.txt&debugStart=1) [虎80-6](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0831/虎80-6.txt&debugStart=1) [虎80-7](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0831/虎80-7.txt&debugStart=1) [虎80-8](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0831/虎80-8.txt&debugStart=1) [虎80-9](https://fish-games.s3.amazonaws.com/tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0831/虎80-9.txt&debugStart=1) |
| 0316_0828 | 03-16 08:28 | 虎80-1.txt ~ 虎80-9.txt (10个文件) | [虎80-1](https://fish-games.s3.amazonaws.com/Fortune-Tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0828/虎80-1.txt&debugStart=1) [虎80-10](https://fish-games.s3.amazonaws.com/Fortune-Tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0828/虎80-10.txt&debugStart=1) [虎80-2](https://fish-games.s3.amazonaws.com/Fortune-Tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0828/虎80-2.txt&debugStart=1) [虎80-3](https://fish-games.s3.amazonaws.com/Fortune-Tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0828/虎80-3.txt&debugStart=1) [虎80-4](https://fish-games.s3.amazonaws.com/Fortune-Tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0828/虎80-4.txt&debugStart=1) [虎80-5](https://fish-games.s3.amazonaws.com/Fortune-Tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0828/虎80-5.txt&debugStart=1) [虎80-6](https://fish-games.s3.amazonaws.com/Fortune-Tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0828/虎80-6.txt&debugStart=1) [虎80-7](https://fish-games.s3.amazonaws.com/Fortune-Tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0828/虎80-7.txt&debugStart=1) [虎80-8](https://fish-games.s3.amazonaws.com/Fortune-Tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0828/虎80-8.txt&debugStart=1) [虎80-9](https://fish-games.s3.amazonaws.com/Fortune-Tiger/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/tigerdate/0316_0828/虎80-9.txt&debugStart=1) |

### Fortune-Ox

| 批次 | 日期 | 数据文件 | 调试链接 |
|------|------|---------|---------|
| 0326_0629 | 03-26 06:29 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0326_0629/ox_upload.txt&debugStart=1) |
| 0326_0228 | 03-26 02:28 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0326_0228/ox_upload.txt&debugStart=1) |
| 0323_0631 | 03-23 06:31 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0323_0631/ox_upload.txt&debugStart=1) |
| 0323_0559 | 03-23 05:59 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0323_0559/ox_upload.txt&debugStart=1) |
| 0323_0541 | 03-23 05:41 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0323_0541/ox_upload.txt&debugStart=1) |
| 0323_0457 | 03-23 04:57 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0323_0457/ox_upload.txt&debugStart=1) |
| 0323_0452 | 03-23 04:52 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0323_0452/ox_upload.txt&debugStart=1) |
| 0323_0435 | 03-23 04:35 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0323_0435/ox_upload.txt&debugStart=1) |
| 0318_0515 | 03-18 05:15 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0318_0515/ox_upload.txt&debugStart=1) |
| 0318_0145 | 03-18 01:45 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0318_0145/ox_upload.txt&debugStart=1) |
| 0318_0143 | 03-18 01:43 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0318_0143/ox_upload.txt&debugStart=1) |
| 0318_0142 | 03-18 01:42 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0318_0142/ox_upload.txt&debugStart=1) |
| 0318_0141 | 03-18 01:41 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0318_0141/ox_upload.txt&debugStart=1) |
| 0318_0116 | 03-18 01:16 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0318_0116/ox_upload.txt&debugStart=1) |
| 0318_0045 | 03-18 00:45 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0318_0045/ox_upload.txt&debugStart=1) |
| 0316_0423 | 03-16 04:23 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0316_0423/ox_upload.txt&debugStart=1) |
| 0316_0235 | 03-16 02:35 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0316_0235/ox_upload.txt&debugStart=1) |
| 0316_0215 | 03-16 02:15 | 普通旋转80次-1.txt ~ 普通旋转80次-9.txt (10个文件) | [普通旋转80次-1](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0316_0215/普通旋转80次-1.txt&debugStart=1) [普通旋转80次-10](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0316_0215/普通旋转80次-10.txt&debugStart=1) [普通旋转80次-2](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0316_0215/普通旋转80次-2.txt&debugStart=1) [普通旋转80次-3](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0316_0215/普通旋转80次-3.txt&debugStart=1) [普通旋转80次-4](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0316_0215/普通旋转80次-4.txt&debugStart=1) [普通旋转80次-5](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0316_0215/普通旋转80次-5.txt&debugStart=1) [普通旋转80次-6](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0316_0215/普通旋转80次-6.txt&debugStart=1) [普通旋转80次-7](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0316_0215/普通旋转80次-7.txt&debugStart=1) [普通旋转80次-8](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0316_0215/普通旋转80次-8.txt&debugStart=1) [普通旋转80次-9](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0316_0215/普通旋转80次-9.txt&debugStart=1) |
| 0313_0442 | 03-13 04:42 | ox_upload.txt | [ox_upload](https://fish-games.s3.amazonaws.com/Fortune-Ox/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/oxdate/0313_0442/ox_upload.txt&debugStart=1) |

### Anubis

| 批次 | 日期 | 数据文件 | 调试链接 |
|------|------|---------|---------|
| 0327_0632 | 03-27 06:32 | 1.txt | [1](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=67433bab6631c6c8930165641056773&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0327_0632/1.txt&debugStart=1) |
| 0327_0631 | 03-27 06:31 | 1.txt | [1](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0327_0631/1.txt&debugStart=1) |
| 0304_1503 | 03-04 15:03 | 1.txt ~ 9.txt (10个文件) | [1](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1503/1.txt&debugStart=1) [10](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1503/10.txt&debugStart=1) [2](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1503/2.txt&debugStart=1) [3](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1503/3.txt&debugStart=1) [4](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1503/4.txt&debugStart=1) [5](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1503/5.txt&debugStart=1) [6](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1503/6.txt&debugStart=1) [7](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1503/7.txt&debugStart=1) [8](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1503/8.txt&debugStart=1) [9](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1503/9.txt&debugStart=1) |
| 0304_1447 | 03-04 14:47 | 80_41.txt ~ 80_50.txt (10个文件) | [80_41](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1447/80_41.txt&debugStart=1) [80_42](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1447/80_42.txt&debugStart=1) [80_43](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1447/80_43.txt&debugStart=1) [80_44](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1447/80_44.txt&debugStart=1) [80_45](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1447/80_45.txt&debugStart=1) [80_46](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1447/80_46.txt&debugStart=1) [80_47](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1447/80_47.txt&debugStart=1) [80_48](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1447/80_48.txt&debugStart=1) [80_49](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1447/80_49.txt&debugStart=1) [80_50](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1447/80_50.txt&debugStart=1) |
| 0304_1446 | 03-04 14:46 | 80_41.txt ~ 80_50.txt (10个文件) | [80_41](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1446/80_41.txt&debugStart=1) [80_42](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1446/80_42.txt&debugStart=1) [80_43](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1446/80_43.txt&debugStart=1) [80_44](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1446/80_44.txt&debugStart=1) [80_45](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1446/80_45.txt&debugStart=1) [80_46](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1446/80_46.txt&debugStart=1) [80_47](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1446/80_47.txt&debugStart=1) [80_48](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1446/80_48.txt&debugStart=1) [80_49](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1446/80_49.txt&debugStart=1) [80_50](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_1446/80_50.txt&debugStart=1) |
| 0304_0637 | 03-04 06:37 | 80_41.txt ~ 80_50.txt (10个文件) | [80_41](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0637/80_41.txt&debugStart=1) [80_42](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0637/80_42.txt&debugStart=1) [80_43](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0637/80_43.txt&debugStart=1) [80_44](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0637/80_44.txt&debugStart=1) [80_45](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0637/80_45.txt&debugStart=1) [80_46](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0637/80_46.txt&debugStart=1) [80_47](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0637/80_47.txt&debugStart=1) [80_48](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0637/80_48.txt&debugStart=1) [80_49](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0637/80_49.txt&debugStart=1) [80_50](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0637/80_50.txt&debugStart=1) |
| 0304_0633 | 03-04 06:33 | 1.txt ~ 9.txt (10个文件) | [1](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0633/1.txt&debugStart=1) [10](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0633/10.txt&debugStart=1) [2](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0633/2.txt&debugStart=1) [3](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0633/3.txt&debugStart=1) [4](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0633/4.txt&debugStart=1) [5](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0633/5.txt&debugStart=1) [6](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0633/6.txt&debugStart=1) [7](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0633/7.txt&debugStart=1) [8](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0633/8.txt&debugStart=1) [9](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0633/9.txt&debugStart=1) |
| 0304_0631 | 03-04 06:31 | 1.txt ~ 9.txt (10个文件) | [1](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0631/1.txt&debugStart=1) [10](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0631/10.txt&debugStart=1) [2](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0631/2.txt&debugStart=1) [3](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0631/3.txt&debugStart=1) [4](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0631/4.txt&debugStart=1) [5](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0631/5.txt&debugStart=1) [6](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0631/6.txt&debugStart=1) [7](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0631/7.txt&debugStart=1) [8](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0631/8.txt&debugStart=1) [9](https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0304_0631/9.txt&debugStart=1) |

<!-- NAV_END -->

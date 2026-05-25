# Mahjong Ways 2 0525_1407 批次说明

## 数据来源

- 本地源文件: `/Users/yang/work/git/sun/har/麻将2/xxbet_capture_mahjong2_10000_20260525_133609.txt`
- 采集目标: Mahjong2 服务端 bet 接口返回数据
- 原始响应数: `10000`
- 拆分模式: `bet`
- 生成回放文件数: `6003`
- 跳过行数: `0`
- 批次目录: `mahjong2date/0525_1407`

## 处理结果

- 回放目录: [mahjong2date/0525_1407](https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_1407)
- manifest: [manifest.json](https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_1407/manifest.json)
- 推荐测试 CSV: [recommended_replays.csv](https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_1407/recommended_replays.csv)
- 全量内容 CSV: [all_replays.csv](https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_1407/all_replays.csv)
- 自动分析: [analysis.md](./analysis.md)
- URL 汇总: [url.txt](./url.txt)

## 摘要统计

| 项目 | 数量 |
|------|------|
| 文件数 | 6003 |
| 服务端响应数 | 10000 |
| 有中奖回合 | 1857 |
| Big/Mega/Super 重点回合 | 46 |
| 连消/多段回放 | 1857 |
| Scatter / Free Spin 回放 | 65 |
| 金色符号/百搭转换回放 | 1857 |
| 推荐测试 CSV 行数 | 1857 |
| 全量 CSV 行数 | 6003 |

## majiangerrorcheck 预检查

本批次生成 `analysis.md` 时没有检出 majiangerrorcheck 数据异常记录。

已覆盖的预检查包括 `rl` 长度、`ptbr/ssb/ss/wp` 位置范围、`wp` 和当前盘面符号匹配、`ptbr` 和 `wp` 一致性、上一轮普通消除后的下一轮 `rs.rns` 补牌数量，以及服务端结束后最终盘面是否仍存在明显可继续中奖组合。

## 重点回放入口

| 回放 | 类型 | 说明 | 链接 |
|------|------|------|------|
| `001.json` | Super Mega Win | 92 段连消/续转，Scatter/Free Spin，金色/百搭，总赢 7408.00，倍率 185.20x。 | [从第 1 次开始](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=6937d51c78fce0f2d29f93346f8c0f6e&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_1407&debugStart=1) |
| `2107.json` | Super Mega Win | 27 段连消/续转，Scatter/Free Spin，多线中奖 3 线，总赢 5384.00，倍率 134.60x。 | [从第 2107 次开始](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=6937d51c78fce0f2d29f93346f8c0f6e&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_1407&debugStart=2107) |
| `4111.json` | Super Mega Win | 38 段连消/续转，Scatter/Free Spin，总赢 5408.00，倍率 135.20x。 | [从第 4111 次开始](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=6937d51c78fce0f2d29f93346f8c0f6e&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_1407&debugStart=4111) |
| `5637.json` | Mega Win | 41 段连消/续转，Scatter/Free Spin，多线中奖 3 线，总赢 1788.00，倍率 44.70x。 | [从第 5637 次开始](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=6937d51c78fce0f2d29f93346f8c0f6e&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_1407&debugStart=5637) |
| `6001.json` | Big Win | 靠近批次尾部的 26 段连消/续转，Scatter/Free Spin，总赢 696.00，倍率 17.40x。 | [从第 6001 次开始](https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=6937d51c78fce0f2d29f93346f8c0f6e&language=en&debug=1&debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_1407&debugStart=6001) |

## 可复制 Issue 描述

```markdown
### Mahjong Ways 2 10000 条服务端回放数据

本批次已直接放入 testdataapi 仓库，不再通过 Issue 附件上传。

- 批次目录: `mahjong2date/0525_1407`
- 原始响应数: `10000`
- bet 回放文件数: `6003`
- 有中奖回合: `1857`
- Big/Mega/Super 重点回合: `46`
- Scatter / Free Spin 回放: `65`
- 金色符号/百搭转换回放: `1857`
- majiangerrorcheck: 未检出数据异常记录

推荐先看：

- `analysis.md`: 自动分析和重点测试回放建议
- `recommended_replays.csv`: 推荐测试 CSV
- `all_replays.csv`: 全量回放 CSV
- `url.txt`: 回放目录和调试链接

重点回放：

- `001.json`: Super Mega Win，92 段连消/续转，debugStart=1
- `2107.json`: Super Mega Win，27 段连消/续转，debugStart=2107
- `4111.json`: Super Mega Win，38 段连消/续转，debugStart=4111
- `5637.json`: Mega Win，41 段连消/续转，debugStart=5637
- `6001.json`: Big Win，26 段连消/续转，debugStart=6001
```

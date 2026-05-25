# Mahjong Ways 2 测试数据

本目录保存 Mahjong Ways 2 的 Debug Bet Replay 测试数据。每个批次目录是一组可直接通过 `debugDataPath=<目录URL>` 回放的数据。

## 最新重点批次

| 批次 | 说明 | 入口 |
|------|------|------|
| `0525_1407` | 通过服务端接口抓取的 10000 条响应，已拆成 6003 组 bet 回放；包含推荐测试 CSV、全量 CSV 和分析说明。 | [查看批次说明](./0525_1407/README.md) |

## 使用方式

进入批次目录后优先查看：

- `README.md`: 本批次说明、Issue 描述、关键统计和推荐回放入口。
- `analysis.md`: 自动分析出的重点测试回放建议、Big/Mega/Super Win、连消、Free Spin、金色/百搭等明细。
- `recommended_replays.csv`: 推荐测试清单，适合 QA 优先回归。
- `all_replays.csv`: 全量回放清单，适合筛选指定类型数据。
- `url.txt`: raw 数据目录、manifest、CSV 和默认调试链接。
- `manifest.json`: 每个回放 JSON 的请求数、SID、spinId、余额和总赢摘要。

## 回放 URL 规则

Mahjong Ways 2 只保留目录回放模式：

```text
debug=1&debugDataPath=<目录URL>&debugStart=<bet开始下标>
```

不要使用旧的 `debugDataUrl` 或 `debugbetreplay` 单文件模式。

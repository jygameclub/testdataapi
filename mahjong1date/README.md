# Mahjong Ways 1 测试数据

本目录保存 Mahjong Ways 1 的 Debug Bet Replay 测试数据。每个批次目录是一组可直接通过 `debugDataPath=<目录URL>` 回放的数据。

## 输出文件

- `001.json`、`002.json`...：按实际下注 bet 拆分后的回放数据。
- `manifest.json`：WebGL 目录回放入口，记录文件顺序、请求数、SID 和余额摘要。
- `analysis.md`：人可读测试建议和 `majiangerrorcheck` 高危错误。
- `recommended_replays.csv`：建议优先测试的回放清单。
- `all_replays.csv`：全部回放清单。
- `validation_summary.json`：GitHub Actions 用于阻断高危数据提交的机器可读结果。
- `url.txt`：数据目录、manifest、调试链接和 CSV 下载链接。

## Mahjong1 规则

- 盘面为 5 列 x 6 格，`rl` 长度必须是 30。
- 隐藏格为 `0,5,6,11,12,17,18,23,24,29`。
- `st=1` 是新的实际下注起点；`st=4/21/22` 属于连消或免费旋转续转链。
- 最后一条仍为 `iswin=1`、带 `wp` 或带 `lw` 时，会被标记为 `TRUNCATED_CONTINUE_STATE`。

## 本地处理

```bash
python process_mahjong1_txt.py /path/to/xxbet_capture.txt
```

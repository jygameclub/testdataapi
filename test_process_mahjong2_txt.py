import json
import tempfile
import unittest
from pathlib import Path

from process_mahjong2_txt import analyze_replay_dir, build_url_lines, is_mahjong2_title, split_capture


class Mahjong2ProcessTests(unittest.TestCase):
    def test_split_capture_groups_by_paid_bet(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "mahjong2_upload.txt"
            output = Path(tmp) / "out"
            rows = [
                {"data": {"sid": "1", "spinId": "a", "st": 1, "tb": 40, "tbb": 40, "blb": 1000, "bl": 960, "aw": 0}},
                {"data": {"sid": "2", "spinId": "b", "st": 4, "tb": 0, "tbb": 40, "blb": 960, "bl": 980, "aw": 20}},
                {"data": {"sid": "3", "spinId": "c", "st": 1, "tb": 40, "tbb": 40, "blb": 980, "bl": 940, "aw": 0}},
            ]
            source.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

            summary = split_capture(source, output, mode="bet")

            self.assertEqual(summary.files_written, 2)
            self.assertEqual(summary.requests_written, 3)
            first_group = json.loads((output / "001.json").read_text(encoding="utf-8"))
            second_group = json.loads((output / "002.json").read_text(encoding="utf-8"))
            self.assertEqual(len(first_group), 2)
            self.assertEqual(second_group[0]["sid"], "3")
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual([group["file"] for group in manifest["groups"]], ["001.json", "002.json"])

    def test_split_capture_keeps_free_spin_chain_with_paid_bet_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "mahjong2_upload.txt"
            output = Path(tmp) / "out"
            rows = [
                {"data": _record("100", 40, 24, st=1, nst=4)},
                {"data": _record("101", 0, 184, st=4, nst=21, psid="100")},
                {"data": _record("102", 0, 580, st=21, nst=21, psid="100")},
                {"data": _record("103", 0, 944, st=22, nst=21, psid="100")},
                {"data": _record("104", 0, 944, st=21, nst=1, psid="100")},
                {"data": _record("200", 40, 0, st=1, nst=1)},
            ]
            source.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

            summary = split_capture(source, output, mode="bet")

            self.assertEqual(summary.files_written, 2)
            first_group = json.loads((output / "001.json").read_text(encoding="utf-8"))
            second_group = json.loads((output / "002.json").read_text(encoding="utf-8"))
            self.assertEqual([entry["sid"] for entry in first_group], ["100", "101", "102", "103", "104"])
            self.assertEqual(second_group[0]["sid"], "200")

    def test_analysis_links_mid_chain_file_to_paid_bet_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.mkdir()
            _write_json(output / "001.json", [_record("100", 40, 24, st=1, nst=4)])
            _write_json(output / "002.json", [_record("101", 0, 580, st=21, nst=21, psid="100")])
            _write_json(output / "003.json", [_record("102", 0, 944, st=22, nst=1, psid="100")])

            analysis = analyze_replay_dir(output, "mahjong2date/test_batch", token="custom-token")

            self.assertIn("003.json", analysis)
            self.assertIn("- Scatter / Free Spin 回放: 2", analysis)
            self.assertIn("debugStart=1", analysis)
            self.assertNotIn("debugStart=3", analysis)

    def test_build_url_lines_uses_debug_data_path_for_directory_replay(self):
        lines = build_url_lines("mahjong2date/0525_0910", token="custom-token")

        self.assertEqual(
            lines[0],
            "https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0910",
        )
        self.assertEqual(
            lines[1],
            "https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0910/manifest.json",
        )
        self.assertIn("https://fish-games.s3.amazonaws.com/MahjongWays2/index.html", lines[3])
        self.assertIn("token=custom-token", lines[3])
        self.assertIn("debug=1", lines[3])
        self.assertIn("debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong2date/0525_0910", lines[3])
        self.assertIn("debugStart=1", lines[3])

    def test_build_url_lines_defaults_to_production_mahjong2_token(self):
        lines = build_url_lines("mahjong2date/0525_0910")

        self.assertIn(
            "https://fish-games.s3.amazonaws.com/MahjongWays2/index.html?env=ceshislot.osshaiwai.com",
            lines[3],
        )
        self.assertIn("token=436475c81b51e6893c740657870f86b7", lines[3])

    def test_issue_title_aliases_match_mahjong2(self):
        for title in ("上传 麻将2 数据", "majianng2 数据", "MahjongWays2 replay", "mahjong2 upload"):
            with self.subTest(title=title):
                self.assertTrue(is_mahjong2_title(title))

        self.assertFalse(is_mahjong2_title("上传 tiger 数据"))

    def test_analysis_marks_code_based_priority_replays(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            source = Path(tmp) / "mahjong2_upload.txt"
            rows = [
                {"data": _record("1", 10, 180, wp_count=2)},
                {"data": _record("2", 10, 360, wp_count=3)},
                {"data": _record("3", 10, 520, wp_count=4, sc=3, fs={"s": 10, "ts": 10, "as": 0})},
                {"data": _record("4", 10, 5, wp_count=1, nst=4, ptbr=[1, 2, 3])},
                {"data": _record("5", 0, 35, wp_count=2, st=4, nst=4, ptbr=[4, 5])},
                {"data": _record("6", 0, 80, wp_count=2, st=4, nst=1)},
            ]
            source.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
            split_capture(source, output, mode="bet")

            analysis = analyze_replay_dir(output, "mahjong2date/test_batch", token="custom-token")

            self.assertIn("依据代码阈值", analysis)
            self.assertIn("Super Mega Win", analysis)
            self.assertIn("Mega Win", analysis)
            self.assertIn("Big Win", analysis)
            self.assertIn("连消/多段回放", analysis)
            self.assertIn("Scatter / Free Spin", analysis)
            self.assertIn("debugStart=3", analysis)
            self.assertIn("debugStart=4", analysis)
            self.assertIn("custom-token", analysis)

    def test_analysis_puts_majiangerrorcheck_first_for_ptbr_rns_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.mkdir()
            first = _full_record("100", st=1, nst=4)
            first["wp"] = {"4": [2, 4, 8, 15]}
            first["ptbr"] = [2, 4, 8, 15]
            first["ssb"] = None
            for position in first["ptbr"]:
                first["rl"][position] = 4
            second = _full_record("101", st=4, nst=1, psid="100")
            second["rl"][15] = 0
            second["wp"] = {"4": [1, 8, 12, 15, 24]}
            second["ptbr"] = [1, 8, 12, 15, 24]
            for position in second["ptbr"]:
                second["rl"][position] = 4
            second["rl"][15] = 0
            second["rs"] = {"rns": [[2, 4], [9], [], [], []]}
            _write_json(output / "001.json", [first, second])

            analysis = analyze_replay_dir(output, "mahjong2date/test_batch", token="custom-token")

            self.assertIn("majiangerrorcheck", analysis)
            self.assertIn("rs.rns[2]", analysis)
            self.assertIn("15", analysis)
            self.assertLess(
                analysis.index("### majiangerrorcheck 数据异常优先检查"),
                analysis.index("### 重点测试回放建议"),
            )

    def test_analysis_flags_final_board_with_possible_win_when_server_ended(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.mkdir()
            record = _full_record("200", st=1, nst=1)
            record["wp"] = None
            record["ptbr"] = []
            record["rl"][1] = 4
            record["rl"][8] = 4
            record["rl"][15] = 4
            _write_json(output / "001.json", [record])

            analysis = analyze_replay_dir(output, "mahjong2date/test_batch")

            self.assertIn("majiangerrorcheck", analysis)
            self.assertIn("服务端已结束但盘面仍可中奖", analysis)

    def test_analysis_flags_wp_position_that_does_not_match_board_symbol(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.mkdir()
            record = _full_record("300", st=1, nst=4)
            record["wp"] = {"4": [1, 8, 15]}
            record["ptbr"] = [1, 8, 15]
            record["rl"][1] = 4
            record["rl"][8] = 4
            record["rl"][15] = 7
            _write_json(output / "001.json", [record])

            analysis = analyze_replay_dir(output, "mahjong2date/test_batch")

            self.assertIn("majiangerrorcheck", analysis)
            self.assertIn("wp[4]", analysis)
            self.assertIn("盘面符号=7", analysis)

    def test_analysis_does_not_flag_hidden_ss_or_ssb_as_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.mkdir()
            record = _full_record("400", st=1, nst=1)
            record["ssb"] = [13, 20, 21]
            record["ss"] = [13, 20, 21]
            _write_json(output / "001.json", [record])

            analysis = analyze_replay_dir(output, "mahjong2date/test_batch")

            self.assertNotIn("majiangerrorcheck", analysis)


def _full_record(
    sid: str,
    st: int = 1,
    nst: int = 1,
    psid: str | None = None,
) -> dict:
    rl = []
    for reel in range(5):
        rl.extend([2 + reel] * 7)
    hidden = {0, 5, 6, 7, 13, 14, 20, 21, 27, 28, 33, 34}
    for index in hidden:
        rl[index] = 1
    return {
        "sid": sid,
        "psid": psid or sid,
        "spinId": f"spin-{sid}",
        "st": st,
        "nst": nst,
        "tb": 40 if st == 1 else 0,
        "tbb": 40.0,
        "cs": 2.0,
        "ml": 1,
        "aw": 0,
        "ssaw": 0,
        "tw": 0,
        "ctw": 0,
        "blb": 1000.0,
        "blab": 960.0,
        "bl": 960.0,
        "wp": None,
        "lw": None,
        "rl": rl,
        "sc": 0,
        "fs": None,
        "ptbr": [],
        "ssb": [],
        "ss": [],
    }


def _record(
    sid: str,
    bet: float,
    win: float,
    wp_count: int = 0,
    st: int = 1,
    nst: int = 1,
    sc: int = 0,
    fs: dict | None = None,
    ptbr: list[int] | None = None,
    psid: str | None = None,
) -> dict:
    wp = {str(index): [index, index + 1] for index in range(1, wp_count + 1)} if wp_count else None
    lw = {str(index): float(win / wp_count) for index in range(1, wp_count + 1)} if wp_count else None
    return {
        "sid": sid,
        "psid": psid or sid,
        "spinId": f"spin-{sid}",
        "st": st,
        "nst": nst,
        "tb": bet,
        "tbb": 10.0,
        "cs": 1.0,
        "ml": 1,
        "aw": win,
        "ssaw": win,
        "tw": win,
        "ctw": win,
        "blb": 1000.0,
        "blab": 1000.0 - bet,
        "bl": 1000.0 - bet + win,
        "wp": wp,
        "lw": lw,
        "rl": [1, 2, 3],
        "sc": sc,
        "fs": fs,
        "ptbr": ptbr or [],
    }


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

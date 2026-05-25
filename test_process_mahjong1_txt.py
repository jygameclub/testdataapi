import json
import shutil
import tempfile
import unittest
from pathlib import Path

from process_mahjong1_txt import (
    analyze_replay_dir,
    build_url_lines,
    is_mahjong1_title,
    process_txt,
    split_capture,
)


class Mahjong1ProcessTests(unittest.TestCase):
    def test_issue_title_aliases_match_mahjong1(self):
        for title in ("上传 麻将1 数据", "majiang1 数据", "MahjongWays1 replay", "mahjong1 upload"):
            with self.subTest(title=title):
                self.assertTrue(is_mahjong1_title(title))

        self.assertFalse(is_mahjong1_title("上传 麻将2 数据"))

    def test_build_url_lines_uses_mahjong1_directory_replay(self):
        lines = build_url_lines("mahjong1date/0525_0910", token="custom-token")

        self.assertEqual(
            lines[0],
            "https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong1date/0525_0910",
        )
        self.assertEqual(
            lines[1],
            "https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong1date/0525_0910/manifest.json",
        )
        self.assertIn("https://fish-games.s3.amazonaws.com/MahjongWays1/index.html", lines[3])
        self.assertIn("token=custom-token", lines[3])
        self.assertIn("debug=1", lines[3])
        self.assertIn("debugDataPath=https://raw.githubusercontent.com/jygameclub/testdataapi/main/mahjong1date/0525_0910", lines[3])
        self.assertIn("debugStart=1", lines[3])

    def test_split_capture_groups_mahjong1_by_st_paid_bet_without_tb(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "mahjong1_upload.txt"
            output = Path(tmp) / "out"
            rows = [
                {"data": _record("1", st=1, win=20)},
                {"data": _record("2", st=4, win=40, psid="1")},
                {"data": _record("3", st=1, win=0)},
            ]
            source.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

            summary = split_capture(source, output, mode="bet")

            self.assertEqual(summary.files_written, 2)
            first_group = json.loads((output / "001.json").read_text(encoding="utf-8"))
            second_group = json.loads((output / "002.json").read_text(encoding="utf-8"))
            self.assertEqual([entry["sid"] for entry in first_group], ["1", "2"])
            self.assertEqual(second_group[0]["sid"], "3")

    def test_analysis_uses_mahjong1_board_shape_for_wp_ways_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.mkdir()
            record = _full_record("500", st=1)
            record["iswin"] = 1
            record["wp"] = {"4": [1, 7, 13]}
            record["ptbr"] = [1, 7, 13]
            record["rl"][1] = 4
            record["rl"][2] = 4
            record["rl"][7] = 4
            record["rl"][13] = 4
            record["rl"][14] = 5
            record["rl"][15] = 5
            record["rl"][16] = 5
            (output / "001.json").write_text(json.dumps([record]), encoding="utf-8")

            analysis = analyze_replay_dir(output, "mahjong1date/test_batch")

            self.assertIn("WP_WAYS_MISMATCH", analysis)
            self.assertIn("expected=[1, 2, 7, 13]", analysis)

    def test_analysis_flags_mahjong1_next_rl_restore_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.mkdir()
            first = _full_record("600", st=1)
            first["iswin"] = 1
            first["wp"] = {"4": [1, 7, 13]}
            first["ptbr"] = [1, 7, 13]
            for position in first["ptbr"]:
                first["rl"][position] = 4

            second = _full_record("601", st=4, psid="600")
            second["rs"] = {"rns": [[9], [9], [9], [], []]}
            second["rl"][13] = 0
            (output / "001.json").write_text(json.dumps([first, second]), encoding="utf-8")

            analysis = analyze_replay_dir(output, "mahjong1date/test_batch")

            self.assertIn("NEXT_RL_RESTORE_MISMATCH", analysis)
            self.assertIn("previous entry 1", analysis)

    def test_analysis_flags_last_mahjong1_winning_entry_as_truncated(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.mkdir()
            record = _full_record("700", st=1)
            record["iswin"] = 1
            record["wp"] = {"4": [1, 7, 13]}
            record["ptbr"] = [1, 7, 13]
            for position in record["ptbr"]:
                record["rl"][position] = 4
            (output / "001.json").write_text(json.dumps([record]), encoding="utf-8")

            analysis = analyze_replay_dir(output, "mahjong1date/test_batch")

            self.assertIn("TRUNCATED_CONTINUE_STATE", analysis)
            self.assertIn("iswin=1", analysis)

    def test_process_txt_writes_mahjong1_validation_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "mahjong1_upload.txt"
            batch = "unit_mahjong1_validation_summary"
            output = Path(__file__).resolve().parent / "mahjong1date" / batch
            record = _full_record("800", st=1)
            record["iswin"] = 1
            record["wp"] = {"4": [1, 7, 13]}
            record["ptbr"] = [1, 7, 13]
            record["rl"][1] = 4
            record["rl"][7] = 4
            record["rl"][13] = 7
            source.write_text(json.dumps({"data": record}) + "\n", encoding="utf-8")
            shutil.rmtree(output, ignore_errors=True)

            try:
                process_txt(source, token="custom-token", date_dir_name=batch)

                self.assertTrue((output / "manifest.json").exists())
                self.assertTrue((output / "analysis.md").exists())
                self.assertTrue((output / "recommended_replays.csv").exists())
                self.assertTrue((output / "all_replays.csv").exists())
                summary = json.loads((output / "validation_summary.json").read_text(encoding="utf-8"))
                self.assertTrue(summary["has_errors"])
                self.assertEqual(summary["max_severity"], "高危")
                self.assertEqual(summary["issues"][0]["code"], "WP_BOARD_MISMATCH")
            finally:
                shutil.rmtree(output, ignore_errors=True)


def _record(sid: str, st: int = 1, win: float = 0, psid: str | None = None) -> dict:
    record = _full_record(sid, st=st, psid=psid)
    record["aw"] = win
    record["ssaw"] = win
    record["tw"] = win
    record["ctw"] = win
    record["iswin"] = 1 if win > 0 else 0
    if win > 0:
        record["wp"] = {"4": [1, 7, 13]}
        record["lw"] = {"4": win}
        record["ptbr"] = [1, 7, 13]
        for position in record["ptbr"]:
            record["rl"][position] = 4
    return record


def _full_record(
    sid: str,
    st: int = 1,
    psid: str | None = None,
) -> dict:
    rl = []
    for reel in range(5):
        rl.extend([2 + reel] * 6)
    hidden = {0, 5, 6, 11, 12, 17, 18, 23, 24, 29}
    for index in hidden:
        rl[index] = 1
    return {
        "sid": sid,
        "psid": psid or sid,
        "spinId": f"spin-{sid}",
        "st": st,
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
        "rs": {"rns": [[], [], [], [], []]},
        "iswin": 0,
    }


if __name__ == "__main__":
    unittest.main()

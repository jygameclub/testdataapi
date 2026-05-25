# Mahjong1 Data Error Check Strengthening

Date: 2026-05-25

## Conclusion

Mahjong1 now has the same upload-time blocking pattern as Mahjong2, but the validator is adapted to Mahjong1's 5 x 6 board. High-risk `majiangerrorcheck` issues are written to both `analysis.md` and `validation_summary.json`; GitHub Actions stops before commit/push when the JSON summary reports errors.

## Current Flow

- Upload path: `.github/workflows/process-mahjong1.yml`.
- Processing entry: `process_mahjong1_txt.py::process_file`.
- Output directory: `mahjong1date/<batch>/`.
- Existing human report: `analysis.md`.
- Existing checker section: `majiangerrorcheck 数据异常优先检查`.

Checks cover:

- `rl` length must be 30.
- Hidden indexes are `0,5,6,11,12,17,18,23,24,29`.
- `ptbr`, `ssb`, `ss`, and `wp` positions must be in range.
- `ptbr` and `wp` must not point to hidden visible-play positions.
- `wp` positions must match the requested symbol or Wild.
- `ptbr` and `wp` must agree on visible elimination positions.
- A final no-win board must not still contain an obvious Ways win.
- A win response must have at least one Ways win on the board.
- The next response must contain enough `rs.rns` symbols for normal eliminated positions.
- `wp[symbol]` must equal the exact Ways positions derived from `rl`.
- The next `rl` must be reconstructable from:

```text
previous rl + previous ptbr + previous ssb/ss gold-to-Wild conversion + next rs.rns
```

- A bet file whose last response is still a Mahjong1 winning response (`iswin=1`, `wp`, or `lw`) is reported as `TRUNCATED_CONTINUE_STATE`.

## Strengthening Design

### Python Validation

The directory-level validation helper returns structured issues. The script keeps the existing `analysis.md` section and also writes:

```text
mahjong1date/<batch>/validation_summary.json
```

Suggested JSON shape:

```json
{
  "has_errors": true,
  "error_count": 3,
  "max_severity": "高危",
  "issues": [
    {
      "file": "079.json",
      "entry_index": 3,
      "sid": "672639",
      "severity": "高危",
      "code": "WP_BOARD_MISMATCH",
      "message": "wp[8]位置12和当前盘面不一致：盘面符号=1，期望=8或Wild(0)",
      "replay_start_index": 79,
      "debug_link": "https://..."
    }
  ]
}
```

Primary high-risk issue codes:

- `WP_WAYS_MISMATCH`
- `NEXT_RL_RESTORE_MISMATCH`
- `TRUNCATED_CONTINUE_STATE`

### Workflow Gate

After `process_file(...)`, `.github/workflows/process-mahjong1.yml` reads `validation_summary.json`.

- If `has_errors == false`: continue current success path.
- If `has_errors == true`: set `success=false`, post the validation failure, and do not commit or push generated replay data.

### Test Strategy

Add failing tests before implementation:

- A board where `wp` is a legal subset but not the complete Ways set must report `WP_WAYS_MISMATCH`.
- A transition with enough `rs.rns` count but a mismatched next `rl` must report `NEXT_RL_RESTORE_MISMATCH`.
- A final Mahjong1 winning response (`iswin=1`, `wp`, or `lw`) with no next entry must report `TRUNCATED_CONTINUE_STATE`.
- Processing a bad upload must write `validation_summary.json` with `has_errors=true`.

## Adversarial Review

### Concern: Full Ways comparison may false-positive on current good data.

Check: no existing `mahjong1date` batches were present at implementation time, so the safety check is covered by unit tests and real-upload `/tmp` reruns.

Decision: keep the rule high-risk because it matches Mahjong1 client board logic and prevents publishing broken replay batches.

### Concern: Blocking uploads may hide useful broken samples.

Broken samples are useful for investigation, but publishing them into the main replay dataset makes normal QA links unsafe. The workflow should block commits while still posting enough issue detail for the uploader to reproduce and fix the capture.

Decision: block high-risk data commits. If deliberately uploading broken samples is needed later, add an explicit override workflow or separate quarantine directory.

### Concern: Exact cascade restore may disagree with Unity runtime behavior around gold tiles.

Unity behavior shows that matched gold symbols turn into Wild and do not drop as normal tiles. The restore model uses `ssb` and `ss` the same way: gold positions in `ssb` but not in `ss` become Wild; non-gold `ptbr` positions are removed and filled by `rs.rns`.

Decision: use exact restore as a high-risk validator because it models the client-visible board transition.

### Concern: Workflow should not parse Markdown.

Markdown is for people. Gate decisions should read `validation_summary.json`.

Decision: add JSON output and use it in GitHub Actions.

## Implementation Plan

1. Add failing unit tests for the three new validator rules and JSON summary output.
2. Implement helpers in `process_mahjong1_txt.py`:
   - exact Ways set comparison,
   - exact next-`rl` restoration,
   - Mahjong1 `iswin/wp/lw` truncated continue-state check,
   - validation summary writer.
3. Reuse the same issue list in `analysis.md` and `validation_summary.json`.
4. Update `process-mahjong1.yml` so validation errors set `success=false` before commit/push.
5. Verify with unit tests, `py_compile`, and `git diff --check`.

## Acceptance Criteria

- A malformed Mahjong1 sample reports validation failure and does not pass the upload gate.
- Valid Mahjong1 batches can still generate `manifest.json`, `analysis.md`, CSV files, `url.txt`, and `validation_summary.json`.
- Human report still starts with `majiangerrorcheck` when issues exist.
- Workflow can block bad data without parsing Markdown.
- Unity consumes the generated batch through `debugDataPath` and `manifest.json`.

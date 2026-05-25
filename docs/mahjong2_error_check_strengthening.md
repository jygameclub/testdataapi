# Mahjong2 Data Error Check Strengthening

Date: 2026-05-25

## Conclusion

The current Mahjong2 upload flow can detect obvious data defects such as `wp` pointing to a board position whose symbol is neither the winning symbol nor Wild. However, detection is only reported in `analysis.md`; GitHub Actions still treats the upload as successful and commits the generated replay data.

The strengthened flow should keep generating human-readable analysis, but also produce a machine-readable validation summary and block upload commits when high-risk data errors are found.

## Current Flow

- Upload path: `.github/workflows/process-mahjong2.yml`.
- Processing entry: `process_mahjong2_txt.py::process_file`.
- Output directory: `mahjong2date/<batch>/`.
- Existing human report: `analysis.md`.
- Existing checker section: `majiangerrorcheck 数据异常优先检查`.

Current checks already cover:

- `rl` length must be 35.
- `ptbr`, `ssb`, `ss`, and `wp` positions must be in range.
- `ptbr` and `wp` must not point to hidden visible-play positions.
- `wp` positions must match the requested symbol or Wild.
- `ptbr` and `wp` must agree on visible elimination positions.
- A final no-win board must not still contain an obvious Ways win.
- A win response must have at least one Ways win on the board.
- The next response must contain enough `rs.rns` symbols for normal eliminated positions.

## Gaps

### 1. Upload Gate

`process-mahjong2.yml` currently marks processing as successful when `count > 0`. It does not fail the upload when `analysis.md` contains `majiangerrorcheck`.

Risk: bad data is committed and published even though the analysis already reported high-risk defects.

### 2. Exact `wp` vs Ways Set

The checker verifies each `wp` position independently, but it does not require the full `wp[symbol]` set to equal the Ways positions derived from `rl`.

Risk: a response can omit a valid winning position or include only a partial winning set while each listed position is individually legal.

### 3. Exact Cascade Board Restore

The checker verifies that `rs.rns` has enough symbols for normal dropped positions. It does not reconstruct the next `rl` exactly from:

```text
previous rl + previous ptbr + previous ssb/ss gold-to-Wild conversion + next rs.rns
```

Risk: `rs.rns` count is sufficient, but symbols or board order still produce a client board that differs from the server `rl`.

### 4. Truncated Continue State

The checker does not flag a bet file whose last response still has `nst` in `{4, 21, 22}`.

Risk: replay ends in a continue state and the client requests another response that does not exist in that bet chain.

### 5. Machine-Readable Result

The only validation result is embedded in Markdown.

Risk: workflow logic must parse text or ignore the result. A JSON summary is safer and simpler.

## Strengthening Design

### Python Validation

Add a reusable directory-level validation helper that returns structured issues. Keep the existing `analysis.md` section, but also write:

```text
mahjong2date/<batch>/validation_summary.json
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

Add these issue codes:

- `WP_WAYS_MISMATCH`
- `NEXT_RL_RESTORE_MISMATCH`
- `TRUNCATED_CONTINUE_STATE`

### Workflow Gate

After `process_file(...)`, read `validation_summary.json`.

- If `has_errors == false`: continue current success path.
- If `has_errors == true`: set `success=false`, post the validation failure, and do not commit or push generated replay data.

### Test Strategy

Add failing tests before implementation:

- A board where `wp` is a legal subset but not the complete Ways set must report `WP_WAYS_MISMATCH`.
- A transition with enough `rs.rns` count but a mismatched next `rl` must report `NEXT_RL_RESTORE_MISMATCH`.
- A final response with `nst=4`, `21`, or `22` and no next entry must report `TRUNCATED_CONTINUE_STATE`.
- Processing a bad upload must write `validation_summary.json` with `has_errors=true`.

## Adversarial Review

### Concern: Full Ways comparison may false-positive on current good data.

Check: a strict scan over existing `mahjong2date` data covered 14,616 files and 25,140 responses. It found zero `WP_WAYS_MISMATCH` and zero exact restore mismatches.

Decision: safe to add as high-risk validation.

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
2. Implement helpers in `process_mahjong2_txt.py`:
   - exact Ways set comparison,
   - exact next-`rl` restoration,
   - truncated continue-state check,
   - validation summary writer.
3. Reuse the same issue list in `analysis.md` and `validation_summary.json`.
4. Update `process-mahjong2.yml` so validation errors set `success=false` before commit/push.
5. Verify with unit tests, `py_compile`, and `git diff --check`.

## Acceptance Criteria

- The manually modified `0 -> 1` sample reports validation failure and does not pass the upload gate.
- Existing good Mahjong2 batches still produce zero validation issues.
- Human report still starts with `majiangerrorcheck` when issues exist.
- Workflow can block bad data without parsing Markdown.
- No Unity files are modified by this change.

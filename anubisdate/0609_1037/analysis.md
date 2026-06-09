# AU duplicate sid fault-injection replay

Purpose: reproduce/debug Anubis multiplier-board desync around free-spin start #207 by injecting one duplicate sid.

## Change

Based on `anubisdate/0609_0910/au_upload.txt`.

Only one field is changed:

| Record | Original sid | New sid | Reason |
|---:|---|---|---|
| #215 | 4575351210 | 4575351121 | Make #215 duplicate #214 so the client duplicate-sid guard can skip #215. |

## Key sequence

| Record | sid | psid | st -> nst | fs.s | aw | ssaw | tw | twbm | ttmrl | ihttmrl |
|---:|---|---|---|---:|---:|---:|---:|---:|---|---|
| #214 | 4575351121 | 4575350157 | 21 -> 21 | 8 | 0.0 | 0.0 | 0.0 | 0.0 | [5, 6, 3, 4, 4] | [False, False, False, False, False] |
| #215 | 4575351121 | 4575350157 | 21 -> 22 | 8 | 0.0 | 200.0 | 200.0 | 0.0 | [3, 3, 4, 3, 3] | [True, False, False, False, False] |
| #216 | 4575351245 | 4575350157 | 22 -> 21 | 7 | 1200.0 | 1200.0 | 1000.0 | 200.0 | [3, 3, 4, 3, 3] | [True, True, False, False, False] |

## Test links

- Start at #207: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1037/au_dup_sid_214_215_upload.txt&debugStart=207
- Start at #214: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1037/au_dup_sid_214_215_upload.txt&debugStart=214

# AU FS7 previous-spin top 5/6/4 replay

Base file: `anubisdate/0609_0910/au_upload.txt`.

Purpose: reproduce the reported FS remaining 7 frame using the actual client path: top multiplier text is written on `StopSpin(#215)`, then #216 only updates gold/active flags during cascade.

## Change

Only one field is changed:

| Record | Field | Original | New |
|---:|---|---|---|
| #215 | ttmrl | [3, 3, 4, 3, 3] | [5, 6, 4, 3, 3] |

Critical #216 fields are unchanged:

| Record | sid | psid | st -> nst | fs.s | aw | ssaw | tw | twbm | gm | pgm | ttmrl | ihttmrl |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| #215 | 4575351210 | 4575350157 | 21 -> 22 | 8 | 0.0 | 200.0 | 200.0 | 0.0 | 0 | 3 | [5, 6, 4, 3, 3] | [True, False, False, False, False] |
| #216 | 4575351245 | 4575350157 | 22 -> 21 | 7 | 1200.0 | 1200.0 | 1000.0 | 200.0 | 6 | 0 | [3, 3, 4, 3, 3] | [True, True, False, False, False] |

Expected visual relation at #216:

- Top multiplier text remains from #215: `x5 x6 x4 x3 x3`.
- #216 lights only first two flags: `ihttmrl=[true,true,false,false,false]`.
- The third `x4` appears in the top strip but should not light.
- The side/middle multiplier added during the #216 cascade can still be `x6` because only the second newly active slot is added at that moment.

## Links

- Raw: https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1050/au_fs7_prevspin_top_564_total_6_upload.txt
- Start #207: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1050/au_fs7_prevspin_top_564_total_6_upload.txt&debugStart=207
- Start #215: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1050/au_fs7_prevspin_top_564_total_6_upload.txt&debugStart=215
- Start #216: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1050/au_fs7_prevspin_top_564_total_6_upload.txt&debugStart=216

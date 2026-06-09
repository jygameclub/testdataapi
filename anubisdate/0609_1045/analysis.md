# AU FS7 top 5/6/4 visual mismatch replay

Base file: `anubisdate/0609_0910/au_upload.txt`.

Purpose: reproduce the reported remaining-free-spins-7 frame where top multipliers look like stale `5,6,4`, while the center/side total remains `6x` and the third `4x` is not lit.

## Change

Only one field is changed:

| Record | Field | Original | New |
|---:|---|---|---|
| #216 | ttmrl | [3, 3, 4, 3, 3] | [5, 6, 4, 3, 3] |

All these #216 fields remain unchanged:

| Record | sid | psid | st -> nst | fs.s | aw | ssaw | tw | twbm | gm | pgm | ihttmrl |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| #216 | 4575351245 | 4575350157 | 22 -> 21 | 7 | 1200.0 | 1200.0 | 1000.0 | 200.0 | 6 | 0 | [True, True, False, False, False] |

Expected visual relation:

- Top multiplier text: `x5 x6 x4 x3 x3`
- Lit/active flags: first two only (`ihttmrl=[true,true,false,false,false]`)
- Side/middle total multiplier should still be `x6` because `gm=6` remains unchanged.

## Links

- Raw: https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1045/au_fs7_top_564_total_6_upload.txt
- Start #207: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1045/au_fs7_top_564_total_6_upload.txt&debugStart=207
- Start #215: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1045/au_fs7_top_564_total_6_upload.txt&debugStart=215
- Start #216: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1045/au_fs7_top_564_total_6_upload.txt&debugStart=216

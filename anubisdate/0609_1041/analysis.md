# AU targeted fault-injection replay variants

Base file: `anubisdate/0609_0910/au_upload.txt`.

## Variant A: duplicate sid on #215/#216

File: `au_dup_sid_215_216_upload.txt`

| Record | sid | psid | st -> nst | fs.s | aw | ssaw | tw | twbm | ttmrl | ihttmrl |
|---:|---|---|---|---:|---:|---:|---:|---:|---|---|
| #215 | 4575351210 | 4575350157 | 21 -> 22 | 8 | 0.0 | 200.0 | 200.0 | 0.0 | [3, 3, 4, 3, 3] | [True, False, False, False, False] |
| #216 | 4575351210 | 4575350157 | 22 -> 21 | 7 | 1200.0 | 1200.0 | 1000.0 | 200.0 | [3, 3, 4, 3, 3] | [True, True, False, False, False] |
| #217 | 4575351489 | 4575350157 | 21 -> 21 | 6 | 1200.0 | 0.0 | 0.0 | 1200.0 | [4, 7, 5, 3, 4] | [False, False, False, False, False] |

Change: only #216 `sid` is changed from `4575351245` to `4575351210`, duplicating #215.

Expected client path: #215 enters MatchingState, #216 is fetched as next response, duplicate-sid guard may skip #216.

## Variant B: multiplier mismatch on #216 1200 response

File: `au_multiplier_mismatch_216_upload.txt`

| Record | sid | psid | st -> nst | fs.s | aw | ssaw | tw | twbm | ttmrl | ihttmrl |
|---:|---|---|---|---:|---:|---:|---:|---:|---|---|
| #214 | 4575351121 | 4575350157 | 21 -> 21 | 8 | 0.0 | 0.0 | 0.0 | 0.0 | [5, 6, 3, 4, 4] | [False, False, False, False, False] |
| #215 | 4575351210 | 4575350157 | 21 -> 22 | 8 | 0.0 | 200.0 | 200.0 | 0.0 | [3, 3, 4, 3, 3] | [True, False, False, False, False] |
| #216 | 4575351245 | 4575350157 | 22 -> 21 | 7 | 1200.0 | 1200.0 | 1000.0 | 200.0 | [5, 6, 3, 4, 4] | [True, True, False, False, False] |

Change: only #216 `ttmrl` is changed from `[3,3,4,3,3]` to `[5,6,3,4,4]`; #216 board/win/free-spin fields remain unchanged.

## Links

### au_dup_sid_215_216_upload.txt
- Raw: https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1041/au_dup_sid_215_216_upload.txt
- Start #207: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1041/au_dup_sid_215_216_upload.txt&debugStart=207
- Start #215: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1041/au_dup_sid_215_216_upload.txt&debugStart=215
- Start #216: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1041/au_dup_sid_215_216_upload.txt&debugStart=216

### au_multiplier_mismatch_216_upload.txt
- Raw: https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1041/au_multiplier_mismatch_216_upload.txt
- Start #207: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1041/au_multiplier_mismatch_216_upload.txt&debugStart=207
- Start #215: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1041/au_multiplier_mismatch_216_upload.txt&debugStart=215
- Start #216: https://fish-games.s3.amazonaws.com/Anubis/index.html?env=ceshislot.osshaiwai.com&hasFloat=0&token=b3bb96ff1faef019504b83495ec3e45a&language=en&debug=1&debugDataUrl=https://raw.githubusercontent.com/jygameclub/testdataapi/main/anubisdate/0609_1041/au_multiplier_mismatch_216_upload.txt&debugStart=216

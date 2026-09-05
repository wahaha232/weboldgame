# 檔案 Inventory — 《楚漢之爭》原始 DOS 檔案 (Phase 1 FILE FORENSICS)

> 產出工具: `reverse/tools/inventory.py` | 資料來源: `reverse/extracted/`
> 所有判讀僅為 binary evidence 之初步觀察；正式結論標記於 hypotheses/。

## 總表

| 檔案 | 大小 | SHA-256 | MD5 | CRC32 | MZ |
|---|---|---|---|---|---|
| `分享說明.txt` | 47 | `6b0afe996a5ea235d8d7956b1fd072e6ca363c18f99f8e032ade2d701c311f12` | `9e686a3a205da24998add8393125ea56` | `20D7907E` | 否 |
| `攻略.txt` | 1019 | `029ea2c7f817d173361e9d14f6fdc8b33172879961e7c445dd8ccc18b6843596` | `848e252361f08da86a3fe3c5346f0ee8` | `3E7E878A` | 否 |
| `說明.txt` | 130 | `424d7cac33921b7b20e516f218a9a917d47c50ece486d92c043abcd91e40d904` | `6fbb0d30e4bd85ab2208f4670d7755fd` | `44838AC9` | 否 |
| `讀我.txt` | 14 | `eb3eade8a3ccdfd58958d2184b0cdf511f769e1ce015f126dc9bf3bdc9ae8478` | `e270a355010c3edbcb335c5d671371ac` | `F0736768` | 否 |
| `han\BASEDATA.001` | 11376 | `c40883cb89fa1ad2e12819e83d13369de3c3d82a079d2c12ce31a4481ac881d3` | `1cddcaa429ff639d9662a378d967f367` | `03061BF9` | 否 |
| `han\FACE.GRP` | 180024 | `3f57bd9c80f69004f86a51320068a4d74b91a2ecc5751465750984e67b7d73b4` | `5e23639710c1437aa90ef37aa4cfd246` | `133FD0FD` | 否 |
| `han\HAN.EXE` | 133424 | `e13c0e370124b646bf2c1b7206821668fc08bd44175a5b942f4e6394700b8796` | `221569350c5e27daf8547c6e460549e4` | `A7463EE1` | MZ/DOS-EXE(valid header) |
| `han\HANSAVE.DAT` | 45760 | `db4514bf3e87ed66a72d5b20a37a795bddf87b98c77c77ae1f590771bb135491` | `13295102b1a0ef304860a5b4d88e2716` | `0909E803` | 否 |
| `han\INSTALL.BAT` | 339 | `2d0faa07106dba4ec4b013057f5c7771f8154431cc5b5ecf891c0a498e04c320` | `de703f8871a25cb564c46a8e54cdf230` | `FB2FB061` | 否 |
| `han\PICS.GRP` | 290344 | `cb7735adb073f48e1bf46ce3b20b53f33f6c81a4d685a76985b92e5ecb5e689b` | `7bd7843092985692dde57dd150c0ad61` | `174C8EF5` | 否 |
| `han\PICS.IDX` | 136 | `9fc4b5c3ba3cb86f00c8c64e17c28fabadb81cd31814ebd1aec4a111c78e81bf` | `cc52ae06f427047c9aeac38375237e01` | `1D9D093C` | 否 |
| `han\PLAY.BAT` | 29 | `341d613a0feb49feeb98d2026968db8b06b834d84be42e22df4dbf8125c9fe64` | `265d6128d2dc40e1bd39027cfd8d90e9` | `DB0B5AFD` | 否 |
| `han\SONGS.GRP` | 13265 | `7a33835fe286036a37dbeb767b6bee5747430e0760552188869fbae2b5ba341e` | `9006a07fd7f48e7cbfc4a0db9e74592b` | `D2B8681C` | 否 |
| `han\SONGS.IDX` | 12 | `a6e3dc027815a545d6ee9b28e585b8544a45f9769130b5d6828fe6fa1f8ea65c` | `b8a991d900113de3a2ce45dd5a09d4a9` | `755D47E5` | 否 |
| `han\SOUND.EXE` | 7163 | `37389c499579debb8017ce041a89cabdfae6ced2ee30e79e4ac8488eb53bd757` | `40159e342d51bd14a46ccf9fe69e272b` | `C2E10BF6` | MZ/DOS-EXE(valid header) |
| `han\STANDARD.BNK` | 1024 | `6f9a77a8e3c183b9f0cca97a3b0089c8dc179f234da6d05d8da38c48ff43535a` | `d5f1a6631302952afabbbe85a583cdea` | `C35A046E` | 否 |
| `han\YING.PAT` | 2048 | `79f1c8bf4510f267fc40d60036a401737dd3492996b279cb1a753dd58dc7ceb1` | `cac63316e286248e92c647b4ab920a5f` | `EA96E2E0` | 否 |
| `han\ZHONG.COD` | 1182 | `a81d3cffcb6a02cc4f63e3945ee8149f66cc22178029d9727c383455c74860d4` | `8d8af0ab88da5ed35ef8707c924e2a01` | `513A55F3` | 否 |
| `han\ZHONG.PAT` | 18912 | `51eb00e5a8ce7bdf83efa311a98fcf67899e06241dbc296b3b1ffa6de0af49b0` | `dca0ea2206c2765b3f84a30cc99394eb` | `28A84418` | 否 |


### 初步分類判讀表 (依 binary evidence, 皆為 Phase 1 觀察)

| 檔案 | 判讀 | 證據 | 信心 |
|---|---|---|---|
| HAN.EXE | 可執行 (16-bit DOS MZ) | `MZ` magic、MZ header 欄位合理;含 C runtime 字串、`SOUND-DRIVER-AD-LIB` | VERIFIED(MZ) |
| SOUND.EXE | 可執行 (16-bit DOS MZ,疑 LZ 壓縮殼) | `MZ` magic;檔頭後 0x1C 處有 `LZ91` 標記;entropy 7.68 | VERIFIED(MZ) / PROBABLE(殼) |
| BASEDATA.001 | 遊戲靜態資料檔 | 內含郡名中文(Big5:遼東/會稽/…)、數值表、開頭區塊結構 | PROBABLE |
| HANSAVE.DAT | 存檔 | 重複多個「郡名+數值」區塊結構(與 BASEDATA 字串重疊) | PROBABLE |
| PICS.GRP | 圖形 (8-bit indexed raw) | 17 張圖皆 `u16 w + u16 h + raw`, len=w*h+4 完全吻合 | VERIFIED(結構) |
| PICS.IDX | 圖形索引 | 17 筆 × 8B, (start,end) uint32 單調、與 GRP 內容吻合 | VERIFIED(結構) |
| FACE.GRP | 圖形 (頭像) | 開頭 `30 00 30 00` 疑似 w/h=48×48;資料為索引色 | HYPOTHESIS |
| SONGS.GRP | 音樂/音效資料 | 含 `\roll\default` ASCII;low entropy 3.63 | UNKNOWN |
| SONGS.IDX | 音樂索引 | 12B = 3×uint32(0,0x196D,0x267E) | HYPOTHESIS |
| STANDARD.BNK | AdLib 音色庫 | 含 `ADLIB-` ASCII 簽名 | VERIFIED(簽名)/PROBABLE(用途) |
| ZHONG.PAT | 中文字型 | 18912=591×32 (16×16 bitmap @32B) | PROBABLE(數字)/HYPOTHESIS(格式) |
| YING.PAT | 英文字型 | 2048=128×16 (8×16 bitmap @16B) | PROBABLE(數字)/HYPOTHESIS(格式) |
| ZHONG.COD | 中文碼表/對照資料 | 1182=591×2,與 ZHONG.PAT 數量一致 | HYPOTHESIS |
| INSTALL.BAT / PLAY.BAT | 批次檔 (ASCII) | 內容為 DOS 指令 | VERIFIED |
| 攻略.txt 等 4 個 .txt | 附加說明文件 (非遊戲原始資料) | 檔名/內容為繁中文字;時間戳 2002–2005 晚於遊戲檔 | VERIFIED(附加) |

> 註:文件時間戳:遊戲檔 1990-11~1994-10;HAN.EXE/PLAY.BAT 1998-11;txt 檔 2002–2005。HAN.EXE/SOUND.EXE 之 MZ header 特性(reloc=0、標記)疑曾被加工,列為待 Phase 2 驗證項目。

---

## 分享說明.txt

- 副檔名: `TXT` | 大小: 47 bytes
- SHA-256: `6b0afe996a5ea235d8d7956b1fd072e6ca363c18f99f8e032ade2d701c311f12`
- MD5: `9e686a3a205da24998add8393125ea56`
- CRC32: `20D7907E`
- 前 64 bytes HEX:

  `6B 69 6C 6C 70 65 6F 70 6C 65 A4 C0 A8 C9 A9 F3 `
  `73 68 61 72 65 67 65 74 2E 63 79 6E 64 69 2E 74 `
  `77 65 64 32 6B 2E 65 61 73 74 73 68 61 72 65`

- MZ 檢查: 否 (前2 bytes = `6B69`)
- ASCII strings (2 筆, 顯示前 2):
  - `killpeople`
  - `shareget.cyndi.twed2k.eastshare`
- Big5/中文 strings (1 筆, 顯示前 1):
  - `分享於`

---

## 攻略.txt

- 副檔名: `TXT` | 大小: 1019 bytes
- SHA-256: `029ea2c7f817d173361e9d14f6fdc8b33172879961e7c445dd8ccc18b6843596`
- MD5: `848e252361f08da86a3fe3c5346f0ee8`
- CRC32: `3E7E878A`
- 前 64 bytes HEX:

  `A6 57 BA D9 A1 47 B7 A1 BA 7E A4 A7 AA A7 20 28 `
  `A4 A4 A4 E5 AA A9 29 0A C2 B2 A4 B6 A1 47 B4 BC `
  `AB 61 31 39 39 30 A6 7E A5 58 AB 7E AA BA B5 A6 `
  `B2 A4 B9 43 C0 B8 A1 41 A5 48 AF B3 B4 C2 A5 BD`

- MZ 檢查: 否 (前2 bytes = `A657`)
- ASCII strings (10 筆, 顯示前 10):
  - `a1990`
  - `      `
  - `\HAN`
  - `SOUND`
  - `MCGA`
  - `      HAN.EXE (`
  - `COPYLOCK)`
  - `        3B 06 60 37 74 11`
  - `        -- -- -- -- EB --`
  - `        3B 06 60 37 74 0E`
- Big5/中文 strings (21 筆, 顯示前 21):
  - `名稱：楚漢之爭`
  - `中文版`
  - `簡介：智冠`
  - `年出品的策略遊戲，以秦朝末年為背景，但並未細分時期，因`
  - `此只有一種勢力分佈而已。玩家可挑選秦朝（胡亥）以外的劉邦、項梁、`
  - `武臣、韓廣、魏咎、田儋、東勝、吳芮等１～８人，進行勢力攻防。不`
  - `過本遊戲可用的策略並不多，除了軍事以外，其餘如內政、外交等用途`
  - `均不大。在戰爭方面，係採用直接對戰方式，其中智將效能遠優於武將。`
  - `兵力分佈並不以將領帶兵方式進行，而是以郡縣兵力為主，每個郡縣最`
  - `大兵力一律為１５００００，因此低能力的降將可說幾無用處。此外，`
  - `玩家能下命令的也只有君主所在郡縣，其餘領地均委由電腦控管，而且`
  - `控管的並不是很好，因此在調兵遣將上常感到不是很得心應手。整體而`
  - `言，這款遊戲做得並不是很好，想玩的玩家還不如再玩玩其後出品的三`
  - `國演義。`
  - `限制：必須安裝在根目錄`
  - `目錄下。`
  - `備註：若執行時會當機，先將執行批次檔中的`
  - `命令拿掉，然後進遊戲時`
  - `試試。`
  - `保護：數字密碼，破解碼：`
  - `先剝掉`

---

## 說明.txt

- 副檔名: `TXT` | 大小: 130 bytes
- SHA-256: `424d7cac33921b7b20e516f218a9a917d47c50ece486d92c043abcd91e40d904`
- MD5: `6fbb0d30e4bd85ab2208f4670d7755fd`
- CRC32: `44838AC9`
- 前 64 bytes HEX:

  `64 6F 73 62 6F 78 30 2E 36 33 0D 0A 0D 0A B6 69 `
  `A4 4A 62 6F 73 62 6F 78 AB E1 2C A8 CC B7 D3 A4 `
  `55 AD B1 BF E9 A4 4A B0 F5 A6 E6 B9 43 C0 B8 0D `
  `0A 6D 6F 75 6E 74 20 63 20 63 3A 5C 0D 0A 63 3A`

- MZ 檢查: 否 (前2 bytes = `646F`)
- ASCII strings (6 筆, 顯示前 6):
  - `dosbox0.63`
  - `Jbosbox`
  - `mount c c:\`
  - `cd han`
  - `play (`
  - `enter`
- Big5/中文 strings (6 筆, 顯示前 6):
  - `進入`
  - `依照下面輸入執行遊戲`
  - `要用右方數字控制方向`
  - `空白鍵確定`
  - `有時`
  - `也會用到`

---

## 讀我.txt

- 副檔名: `TXT` | 大小: 14 bytes
- SHA-256: `eb3eade8a3ccdfd58958d2184b0cdf511f769e1ce015f126dc9bf3bdc9ae8478`
- MD5: `e270a355010c3edbcb335c5d671371ac`
- CRC32: `F0736768`
- 前 64 bytes HEX:

  `A5 B2 B6 B7 B8 D1 A8 EC 63 3A 5C 48 41 4E`

- MZ 檢查: 否 (前2 bytes = `A5B2`)
- ASCII strings (1 筆, 顯示前 1):
  - `c:\HAN`
- Big5/中文 strings (1 筆, 顯示前 1):
  - `必須解到`

---

## han\BASEDATA.001

- 副檔名: `001` | 大小: 11376 bytes
- SHA-256: `c40883cb89fa1ad2e12819e83d13369de3c3d82a079d2c12ce31a4481ac881d3`
- MD5: `1cddcaa429ff639d9662a378d967f367`
- CRC32: `03061BF9`
- 前 64 bytes HEX:

  `41 43 1A 00 02 01 04 06 05 07 03 09 08 00 FF FF `
  `FF FF FF FF 01 0A 00 00 00 00 00 00 00 00 00 00 `
  `00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 `
  `00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00`

- MZ 檢查: 否 (前2 bytes = `4143`)
- ASCII strings (60 筆, 顯示前 60):
  - `        `
  - `||||||||`
  - `        88888888XXXXXXXX((((((((XXXXXXXX88888888XXXXXXXX((((((((XXXXXXXX`
  - `        H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(`
  - `        fffffffff`
  - `ffff`
  - `fffffffff`
  - `(((((((`
  - `        X(X(X(X(((((((((X(X(X(X(((((((((X(X(X(X(((((((((X(X(X(X(((((((((`
  - `HHHH`
  - `((((((((`
  - `        XXXXXXXXXXX`
  - `XXXXX`
  - `XXXXXXXXXXX`
  - `xGS'`
  - ` IP[`
  - `vXZ_`
  - `tMPZ`
  - `]PFZ`
  - ` B^Z`
  - `>a! `
  - `d?5&dd`
  - `RQV4T?`
  - ` -LRA5P=`
  - ` (IX5"ME`
  - ` -7W:3 H`
  - `V=6*VZ`
  - `U)C"OI`
  - ` .AT;3`
  - `FSS1'C`
  - `  Q.4"BK`
  - `D;<P`
  - ` &T%>"JT`
  - `AB62`
  - ` !Y#P"CH`
  - `+@D^`
  - ` '@LH:`
  - `AZNL B`
  - `:CKR`
  - `U'W DK`
  - `Q,B!QF`
  - `  bV\M_c`
  - `*8OT$&`
  - `/CRT%`
  - `3_IU:=`
  - `U[H=SW`
  - `"S'O"MS`
  - `cEP/bb`
  - `ENF1`
  - `c7@'[R`
  - `W%R BS`
  - `W.<!SH`
  - `LD:T`
  - `KCUR`
  - `k "Y0Q!GL`
  - `W*4Z,1`
  - `I2UR""`
  - `X(;"GP`
  - `W'K!NN`
  - `e 'S+T`
- Big5/中文 strings (32 筆, 顯示前 32):
  - `虜虜虜虜`
  - `虜虜虜`
  - `虜虜虜`
  - `虜虜虜`
  - `遼東`
  - `遼西`
  - `北平`
  - `漁陽`
  - `上谷`
  - `雁門`
  - `九原`
  - `鉅鹿`
  - `太原`
  - `北地`
  - `琅琊`
  - `邯鄲`
  - `上黨`
  - `河東`
  - `內史`
  - `隴西`
  - `九江`
  - `泗水`
  - `三川`
  - `會稽`
  - `穎川`
  - `南陽`
  - `漢中`
  - `閩中`
  - `黔中`
  - `南海`
  - `桂林`
  - `食其`

---

## han\FACE.GRP

- 副檔名: `GRP` | 大小: 180024 bytes
- SHA-256: `3f57bd9c80f69004f86a51320068a4d74b91a2ecc5751465750984e67b7d73b4`
- MD5: `5e23639710c1437aa90ef37aa4cfd246`
- CRC32: `133FD0FD`
- 前 64 bytes HEX:

  `30 00 30 00 14 14 14 14 14 14 14 14 14 14 14 14 `
  `14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 `
  `14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 14 `
  `14 14 14 14 14 40 40 40 40 40 40 40 40 40 40 40`

- MZ 檢查: 否 (前2 bytes = `3000`)
- ASCII strings (60 筆, 顯示前 60):
  - `@@@@@@@@@@@@@@@@@@@@@`
  - `@@@@@@@@@@@@@@@@@@@@`
  - `@@@@@@@@@@@@@@@@`
  - `@@@@@@@@@@@@@@@@@`
  - `@@@@@@@@@@@@@@@`
  - `@@@@@@@@@@@@`
  - `@@@@@@@@@@@@@`
  - `@@@@@@@@@@@`
  - `@@@@@@@@@@`
  - `@@@@@@@@@`
  - `@@@@@@@@`
  - `@@@@@@@`
  - `@@@@@`
  - `@@@@`
  - `@@@@@@`
  - `GGGGG`
  - `GGGGGGGG`
  - `GGGGGG`
  - `GGGG`
  - `GGGGGGG`
  - `@@@@WWW`
  - `W@@@@@@@@@@@@@@@@@@@`
  - `@@@@@WW`
  - `@@@@@@WW`
  - `@@@@@@@WW`
  - `WWWW`
  - `WWWWWWW@@@@@@@@@@@@@@@@@@@`
  - `WWWWW`
  - `@@@@@@@@W`
  - `@@@@@@@@WWWW`
  - `@@@@@@@@@WW`
  - `@@@@@@@@@W`
  - `@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@`
  - `@@@@@@@@@@@@@@@@@@@@@@@@@@@@`
  - `@@@@@@@@@@@@@@@@@@@@@@@@@@`
  - `@@@@@@@@@@@@@@@@@@@@@@@@`
  - `@@@@@@@@@@@@@@`
  - `uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu`
  - `uuuuuuuuuuuuuuuuuu`
  - `uuuuuuuuuuuuuuuuuuuuuuuuuu`
  - `uuuuuuuuuuuu`
  - `uuuuuuuuuu`
  - `uuuuuuuuuuuuuuuuuuuuuuuuuuu`
  - `uuuuuu`
  - `uuuuuuuuuuuuuuuuuuuuuuuuuuuu`
  - `uuuu`
  - `uuuuuuuuuuuuuuuuuuuuuuuuu`
  - `uuuuuuuuuuuuuuuuuuuuuuuu`
  - `uuuuuuuuuuuuuuuuuuuuuu`
  - `uuuuuuuuuuuuuuuuuuuuu`
  - `uuuuuuuuuuuuuuuu`
  - `uuuuuuuuuuuuuu`
  - `uuuuuuuuu`
  - `uuuuuuuuuuu`
  - `uuuuuuuu`
  - `uuuuuuu`
  - `uuuuu`
  - `uuuuuuuuuuuuu`
  - `uuuuuuuuuuuuuuu`
  - `@@@@@@@@@@@@@@@@@@@@@@@@@@@`
- Big5/中文 strings (80 筆, 顯示前 80):
  - `戌戌戌`
  - `戌戌`
  - `戌戌戌戌戌戌`
  - `戌戌`
  - `戌戌`
  - `戌戌`
  - `戌戌`
  - `戌戌`
  - `戌戌戌戌`
  - `戌戌戌`
  - `戌戌戌`
  - `戌戌戌`
  - `戌戌`
  - `戌戌`
  - `擬擬擬擬擬擬擬擬`
  - `擬擬擬擬擬擬擬擬擬`
  - `戌戌戌`
  - `擬擬擬擬擬擬擬擬擬擬`
  - `戌戌`
  - `擬擬擬擬擬擬擬擬擬擬擬`
  - `擬擬擬擬擬擬擬擬擬`
  - `擬擬擬擬擬擬`
  - `戌戌`
  - `擬擬擬`
  - `擬擬擬擬`
  - `擬擬擬`
  - `擬擬擬擬`
  - `擬擬`
  - `戌戌`
  - `擬擬擬`
  - `擬擬`
  - `擬擬`
  - `擬擬`
  - `擬擬`
  - `擬擬擬擬擬擬擬擬擬擬擬擬`
  - `戌戌`
  - `擬擬擬擬擬擬擬擬擬擬擬擬`
  - `戌戌`
  - `擬擬擬擬擬擬擬擬擬擬擬擬`
  - `擬擬擬擬擬擬擬擬擬擬擬擬`
  - `擬擬擬擬擬`
  - `擬擬擬`
  - `擬擬`
  - `擬擬擬擬擬`
  - `擬擬擬`
  - `擬擬擬擬擬擬擬擬擬擬擬`
  - `擬擬擬擬擬擬擬擬擬擬擬`
  - `擬擬擬擬擬擬`
  - `擬擬`
  - `斐斐`
  - `擬擬擬擬`
  - `擬擬`
  - `擬擬`
  - `斐斐斐`
  - `擬擬擬擬`
  - `擬擬`
  - `斐斐`
  - `擬擬擬擬`
  - `擬擬`
  - `斐斐`
  - `擬擬擬擬擬擬擬擬`
  - `斐斐`
  - `斐斐斐斐`
  - `擬擬擬擬擬擬擬`
  - `斐斐`
  - `擬擬擬擬`
  - `擬擬`
  - `順超`
  - `順超`
  - `壯壯壯`
  - `壯壯壯壯壯`
  - `壯壯壯壯壯劬`
  - `壯壯壯`
  - `藤藤藤藤`
  - `藤藤藤藤`
  - `藤藤藤藤`
  - `藤藤藤藤`
  - `藤藤藤藤`
  - `藤藤藤藤藤`
  - `藤藤藤藤藤`

---

## han\HAN.EXE

- 副檔名: `EXE` | 大小: 133424 bytes
- SHA-256: `e13c0e370124b646bf2c1b7206821668fc08bd44175a5b942f4e6394700b8796`
- MD5: `221569350c5e27daf8547c6e460549e4`
- CRC32: `A7463EE1`
- 前 64 bytes HEX:

  `4D 5A 6B 01 E8 00 00 00 20 00 00 00 FF FF 94 1E `
  `80 00 00 00 12 00 DD 1B 1E 00 00 00 01 00 00 00 `
  `00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 `
  `00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00`

- MZ 檢查: **MZ/DOS-EXE(valid header)**
  - `e_cblp=363 e_cp=232 reloc_items=0 header_paras=32 minalloc=0 maxalloc=65535 SS=1E94 SP=0080 IP=0012 CS=1BDD lfarlc=001E ovno=0 e_lfanew=0`
- ASCII strings (60 筆, 顯示前 60):
  - `=87u`
  - `<C&8`
  - `t"R3`
  - `9>H&`
  - `7>J&R`
  - `;.J&`
  - `7>J&3`
  - `R&->@3`
  - `7.J&Z`
  - `5>H&`
  - `5.H&`
  - `I,"t`
  - `"<\u`
  - `Stack overflow!`
  - `X-@=`
  - `Z-+F`
  - `YYRP`
  - `&.;F`
  - `2:YY3`
  - `;F(|`
  - `  RP`
  - `XZ&+G`
  - `X&:G`
  - `<5|%`
  - `,5RP`
  - `05RP`
  - `,5RP3`
  - `05RP3`
  - `(5;V`
  - `XZ&;W`
  - `>V7(~`
  - `>T7(~`
  - `:7;F`
  - `T7;F`
  - `'5+F`
  - `9>X;`
  - `\6uM`
  - `616G6]6s6`
  - `D5RP`
  - `'5RP`
  - `\6u `
  - `^6u `
  - `\7@P`
  - `9&((w`
  - `:YY;F`
  - `69&((w`
  - `@@RP`
  - `SOUND-DRIVER-AD-LIB`
  - `$0<HT'lx`
  - `@}Y;`
  - `_[r?`
  - `x$Nt`
  - `@}7;`
  - `@}C@=`
  - `@}>=`
  - `t4+^`
  - `$"""""`
  - `WUUUUUU`
  - `23333`
  - `VWVWV`
- Big5/中文 strings (80 筆, 顯示前 80):
  - `佫婷`
  - `燧謧`
  - `燧謧蒯`
  - `禓艫`
  - `燧藎`
  - `碫聘`
  - `顥雥`
  - `碬聘`
  - `釨栝`
  - `顲鳺`
  - `欏鎝`
  - `跿繪`
  - `嬁芓`
  - `獲柴`
  - `鶱穄`
  - `壧劙`
  - `壧劙`
  - `蒑虥`
  - `娮侉`
  - `鞦懂`
  - `戃彏`
  - `戁戄`
  - `鼱隒眒笤`
  - `豽錤`
  - `戃彏`
  - `蘼麶`
  - `寔隑碢`
  - `歜獍`
  - `桄韞`
  - `嬁汭`
  - `栜栜`
  - `栜栜`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `桏桏`
  - `天隒`
  - `桏桏`
  - `嬁汭`
  - `栜栜`
  - `桏桏`
  - `栜栜`
  - `螈孽`
  - `蕀孽`
  - `豻孽`
  - `嬁汭`
  - `桏桏`
  - `嬁汭`
  - `桏桏`
  - `嬁汭`
  - `豻孽`
  - `嬁汭`
  - `嬁汭`
  - `髲饟`
  - `魴饟`
  - `骳饟`
  - `嬁汭`
  - `桏桏`
  - `桏桏`
  - `優澣`

---

## han\HANSAVE.DAT

- 副檔名: `DAT` | 大小: 45760 bytes
- SHA-256: `db4514bf3e87ed66a72d5b20a37a795bddf87b98c77c77ae1f590771bb135491`
- MD5: `13295102b1a0ef304860a5b4d88e2716`
- CRC32: `0909E803`
- 前 64 bytes HEX:

  `20 20 20 BC 42 20 20 A8 B9 20 20 A6 62 20 20 E4 `
  `68 20 20 20 00 20 20 20 BC 42 20 20 A8 B9 20 20 `
  `A6 62 20 AA 72 A4 F4 20 20 00 20 20 20 BC 42 20 `
  `20 A8 B9 20 20 A6 62 20 AA 72 A4 F4 20 20 00 20`

- MZ 檢查: 否 (前2 bytes = `2020`)
- ASCII strings (60 筆, 顯示前 60):
  - `h   `
  - `        `
  - `||||||||`
  - `        88888888XXXXXXXX((((((((XXXXXXXX88888888XXXXXXXX((((((((XXXXXXXX`
  - `        H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(H(`
  - `        fffffffff`
  - `ffff`
  - `fffffffff`
  - `(((((((`
  - `        X(X(X(X(((((((((X(X(X(X(((((((((X(X(X(X(((((((((X(X(X(X(((((((((`
  - `HHHH`
  - `((((((((`
  - `        XXXXXXXXXXX`
  - `XXXXX`
  - `XXXXXXXXXXX`
  - `Hd_0`
  - `;ddY`
  - `N &dd`
  - `&dds`
  - ` -dd`
  - `/ddG`
  - `W ?dd`
  - `a?ddL`
  - `xKdc`
  - ` Mdd`
  - `F -D\`
  - `X?dd`
  - `F>Ud`
  - `vYFd`
  - ` 5b'h`
  - `tUdd`
  - `]XddH`
  - `h )dd`
  - `tHdb`
  - ` 0db`
  - ` FR+`
  - `n .dd]`
  - `>a! `
  - `d?5&dd`
  - `RQV4T?`
  - ` 4LRA5P=`
  - ` 0IX5"ME`
  - ` 37W:3 H`
  - `V=6*VZ`
  - `U)C"OI`
  - ` 6AT;3`
  - `l #FSS1'C`
  - ` !W)I`
  - ` (Q.4"BK`
  - `D;<P`
  - `v %V(:`
  - ` "X/V`
  - ` -T%>"JT`
  - ` %AB62`
  - ` )Y#P"CH`
  - `{ #+@D^`
  - ` /@LH:`
  - `AZNL B`
  - `:CKR`
  - `s "R&L`
- Big5/中文 strings (80 筆, 顯示前 80):
  - `泗水`
  - `泗水`
  - `泗水`
  - `三川`
  - `虜虜虜虜`
  - `虜虜虜`
  - `虜虜虜`
  - `虜虜虜`
  - `遼東`
  - `遼西`
  - `北平`
  - `漁陽`
  - `上谷`
  - `雁門`
  - `九原`
  - `鉅鹿`
  - `太原`
  - `北地`
  - `琅琊`
  - `邯鄲`
  - `上黨`
  - `河東`
  - `內史`
  - `隴西`
  - `九江`
  - `泗水`
  - `三川`
  - `會稽`
  - `穎川`
  - `南陽`
  - `漢中`
  - `閩中`
  - `黔中`
  - `南海`
  - `桂林`
  - `食其`
  - `虜虜虜虜`
  - `虜虜虜`
  - `虜虜虜`
  - `虜虜虜`
  - `遼東`
  - `遼西`
  - `北平`
  - `漁陽`
  - `上谷`
  - `雁門`
  - `九原`
  - `鉅鹿`
  - `太原`
  - `北地`
  - `琅琊`
  - `邯鄲`
  - `上黨`
  - `河東`
  - `內史`
  - `隴西`
  - `九江`
  - `泗水`
  - `三川`
  - `會稽`
  - `穎川`
  - `南陽`
  - `漢中`
  - `閩中`
  - `黔中`
  - `南海`
  - `桂林`
  - `食其`
  - `虜虜虜虜`
  - `虜虜虜`
  - `虜虜虜`
  - `虜虜虜`
  - `遼東`
  - `遼西`
  - `北平`
  - `漁陽`
  - `上谷`
  - `雁門`
  - `九原`
  - `鉅鹿`

---

## han\INSTALL.BAT

- 副檔名: `BAT` | 大小: 339 bytes
- SHA-256: `2d0faa07106dba4ec4b013057f5c7771f8154431cc5b5ecf891c0a498e04c320`
- MD5: `de703f8871a25cb564c46a8e54cdf230`
- CRC32: `FB2FB061`
- 前 64 bytes HEX:

  `0D 0A 65 63 68 6F 20 6F 66 66 0D 0A 65 63 68 6F `
  `20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 `
  `49 6E 73 74 61 6C 6C 20 74 6F 20 64 72 69 76 65 `
  `20 43 3A 0D 0A 0D 0A 65 63 68 6F 20 20 20 20 20`

- MZ 檢查: 否 (前2 bytes = `0D0A`)
- ASCII strings (11 筆, 顯示前 11):
  - `echo off`
  - `echo                Install to drive C:`
  - `echo            *** Insert Han Disk #1 in Drive A: ***`
  - `pause`
  - `md han`
  - `cd han`
  - `copy a:*.*`
  - `echo            *** Insert Han Disk #2 in Drive A: ***`
  - `echo To play type:       c: `
  - `echo                     cd\han `
  - `echo                     play `
- Big5/中文 strings: (無)

---

## han\PICS.GRP

- 副檔名: `GRP` | 大小: 290344 bytes
- SHA-256: `cb7735adb073f48e1bf46ce3b20b53f33f6c81a4d685a76985b92e5ecb5e689b`
- MD5: `7bd7843092985692dde57dd150c0ad61`
- CRC32: `174C8EF5`
- 前 64 bytes HEX:

  `A0 00 20 01 00 00 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C `
  `1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C `
  `1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C `
  `1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C 1C`

- MZ 檢查: 否 (前2 bytes = `A000`)
- ASCII strings (60 筆, 顯示前 60):
  - `eeeej`
  - `jiijj`
  - `ijjiiji`
  - `jiiijihi`
  - `jjiiiiiiieeiiiiiiiiiiieediiiiiiiijijj`
  - `edeeeee`
  - `jjjjjjjjiiijjijjjiiiiiiii`
  - `iiijj`
  - `ieeee`
  - `jjjjjj`
  - `iijjiiiijjjij`
  - `nnjnnn`
  - `nnnnnnn`
  - `jjjj`
  - `nnnnnj`
  - `jjjjj`
  - `jjnnnnnnnnn`
  - `nnnn`
  - `nE8[`
  - `jiiij`
  - `jnEE8`
  - `mnmmn`
  - `d?EE9`
  - `^**%%%`
  - `nnnnnjii`
  - `?8-V`
  - `lhc0`
  - `*///0`
  - `**%%%%*5`
  - `jnnjnnjnnnnnnnnnm`
  - `imni`
  - `hb0*`
  - `b/*+05h`
  - `njnmi`
  - `jjnnn`
  - `nnnmnnnnnnn`
  - `nm?8,&`
  - `''"R`
  - `h6**`
  - `hgcdim`
  - `njmjnnnimn`
  - `nmnn`
  - `mm?8`
  - `"""!!`
  - `hc6*`
  - `jnnniinnj`
  - `9?99-!`
  - `"#"""&&",8`
  - `767h0%%`
  - `**%***b`
  - `innjmmmmimmimmm`
  - `nnnnnn`
  - `mE>8`
  - `hg656=h`
  - `Y%%%`
  - `******b`
  - `nnnmimimmmmmmmimmmm`
  - `mFEE8&`
  - `hggh`
  - `*%%**`
- Big5/中文 strings (80 筆, 顯示前 80):
  - `公蝸匱`
  - `牧牧牧`
  - `牧牧牧牧牧牧`
  - `牧牧牧牧牧`
  - `牧牧`
  - `妒藥鏽秉藤謠`
  - `膜蝸`
  - `牧牧`
  - `帚牧爸牧牧牧`
  - `牧狎牧秉牧牧牧牧牧牧秉牧牧牧牧牧`
  - `壯藤藤藤藤謠`
  - `壯豕豕`
  - `公蝸蝸`
  - `牧爸牧牧牧牧`
  - `牧牧牧藤牧藤牧`
  - `牧牧`
  - `牧牧秉牧秉礙穩蘆孩鏽牧礙牧礙牧牧`
  - `牧秉藤`
  - `尾擠擠蝸蝸膜`
  - `帘版`
  - `牧牧牧牧`
  - `牧牧版牧牧牧牧秉秉牧牧牧牧牧牧牧牧藤藤礙礙秉怵礙牧牧`
  - `牧牧牧帚`
  - `版牧`
  - `公擬蝗蝸蝗壑`
  - `牧牧牧牧帘`
  - `牧牧牧牧牧牧牧牧牧牧牧牧牧牧牧牧礙牧牧酊牧牧牧`
  - `壯夾`
  - `中蝸蝸蝸蝸謊中`
  - `牧牧牧牧`
  - `牧牧牧礙牧牧牧礙牧牧牧`
  - `牧牧牧秉牧牧牧牧牧牧牧`
  - `牧牧牧`
  - `爸豕豕豕豕豕`
  - `公公擬謠謗擱祣坐`
  - `牧牧`
  - `牧牧`
  - `牧牧牧牧牧`
  - `牧牧牧牧牧牧牧`
  - `豕豕豕豕豕豆豆`
  - `中擠蝸蝗蝌祣謠薛`
  - `牧牧牧牧`
  - `牧牧`
  - `牧牧`
  - `牧牧`
  - `赤牧阪豕阪赤豆豆豕`
  - `壯蝸蝸畛擱笱祫謊坐`
  - `壯妝`
  - `牧帘`
  - `牧爸`
  - `牧牧`
  - `牧牧`
  - `牧牧牧牧牧`
  - `牧牧牧牧`
  - `豕爸牧豕赤豕豕`
  - `壯分擠蝗笱笱輿祫壑`
  - `牧牧`
  - `牧牧`
  - `牧牧牧牧`
  - `秉礙牧秉牧豕`
  - `豕牧`
  - `擬擬擬擬輿笱笱笱謗`
  - `牧牧`
  - `牧牧`
  - `牧牧牧`
  - `秈蘆牧牧牧`
  - `牧爸`
  - `尾謊擬謊氈笱笱笱祫`
  - `牧牧`
  - `牧牧`
  - `牧牧`
  - `豕豕`
  - `牧牧牧牧牧`
  - `牧牧秉牧牧牧牧`
  - `牧牧`
  - `擱謠祫擱輿笱笱碻`
  - `牧牧`
  - `牧牧`
  - `牧牧`
  - `壯妒赤赤赤豕豕夾`

---

## han\PICS.IDX

- 副檔名: `IDX` | 大小: 136 bytes
- SHA-256: `9fc4b5c3ba3cb86f00c8c64e17c28fabadb81cd31814ebd1aec4a111c78e81bf`
- MD5: `cc52ae06f427047c9aeac38375237e01`
- CRC32: `1D9D093C`
- 前 64 bytes HEX:

  `00 00 00 00 04 B4 00 00 08 0E 01 00 0C B6 01 00 `
  `B0 B7 01 00 B4 6B 02 00 38 70 02 00 BC 74 02 00 `
  `40 79 02 00 C4 7D 02 00 48 82 02 00 CC 86 02 00 `
  `50 8B 02 00 D4 8F 02 00 58 94 02 00 DC 98 02 00`

- MZ 檢查: 否 (前2 bytes = `0000`)
- ASCII strings: (無)
- Big5/中文 strings: (無)

---

## han\PLAY.BAT

- 副檔名: `BAT` | 大小: 29 bytes
- SHA-256: `341d613a0feb49feeb98d2026968db8b06b834d84be42e22df4dbf8125c9fe64`
- MD5: `265d6128d2dc40e1bd39027cfd8d90e9`
- CRC32: `DB0B5AFD`
- 前 64 bytes HEX:

  `40 65 63 68 6F 20 6F 66 66 0D 0A 73 6F 75 6E 64 `
  `20 62 37 30 30 30 0D 0A 68 61 6E 0D 0A`

- MZ 檢查: 否 (前2 bytes = `4065`)
- ASCII strings (2 筆, 顯示前 2):
  - `@echo off`
  - `sound b7000`
- Big5/中文 strings: (無)

---

## han\SONGS.GRP

- 副檔名: `GRP` | 大小: 13265 bytes
- SHA-256: `7a33835fe286036a37dbeb767b6bee5747430e0760552188869fbae2b5ba341e`
- MD5: `9006a07fd7f48e7cbfc4a0db9e74592b`
- CRC32: `D2B8681C`
- 前 64 bytes HEX:

  `00 00 04 00 5C 72 6F 6C 6C 5C 64 65 66 61 75 6C `
  `74 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 `
  `00 00 00 00 00 00 00 00 00 00 00 00 04 00 04 00 `
  `48 00 46 00 00 00 20 01 1E 01 1E 01 1E 01 A0 00`

- MZ 檢查: 否 (前2 bytes = `0000`)
- ASCII strings (60 筆, 顯示前 60):
  - `\roll\default`
  - `Tempo`
  - `?Voix  0`
  - `Timbre  0`
  - `trumpet1`
  - `Volume  0`
  - `Timbr`
  - `Y?Pitch  0`
  - `?Voix  1`
  - `Timbre  1`
  - `piano1`
  - `Volume  1`
  - `@?Pitch  1`
  - `?Voix  2`
  - `Timbre  2`
  - `Volume  2`
  - `@?Pitch  2`
  - `?Voix  3`
  - `Timbre  3`
  - `Volume  3`
  - `@?Pitch  3`
  - `?Voix  4`
  - `Timbre  4`
  - `Volume  4`
  - `@?Pitch  4`
  - `?Voix  5`
  - `Timbre  5`
  - `Volume  5`
  - `@?Pitch  5`
  - `?Voix  6`
  - `Timbre  6`
  - `bdrum1`
  - `Volume  6`
  - `L?Pitch  6`
  - `?Voix  7`
  - `Timbre  7`
  - `snare1`
  - `Volume  7`
  - `333?0`
  - `ff&?8`
  - `333?:`
  - `ff&?H`
  - `333?`
  - `ff&?`
  - `Y?Pitch  7`
  - `?Voix  8`
  - `Timbre  8`
  - `tom1`
  - `Volume  8`
  - `fff?Pitch  8`
  - `?Voix  9`
  - `Timbre  9`
  - `cymbal1`
  - `Volume  9`
  - `@?Pitch  9`
  - `?Voix 10`
  - `Timbre 10`
  - `hihat1`
  - `Volume 10`
  - `?Pitch 10`
- Big5/中文 strings: (無)

---

## han\SONGS.IDX

- 副檔名: `IDX` | 大小: 12 bytes
- SHA-256: `a6e3dc027815a545d6ee9b28e585b8544a45f9769130b5d6828fe6fa1f8ea65c`
- MD5: `b8a991d900113de3a2ce45dd5a09d4a9`
- CRC32: `755D47E5`
- 前 64 bytes HEX:

  `00 00 00 00 6D 19 00 00 7E 26 00 00`

- MZ 檢查: 否 (前2 bytes = `0000`)
- ASCII strings: (無)
- Big5/中文 strings: (無)

---

## han\SOUND.EXE

- 副檔名: `EXE` | 大小: 7163 bytes
- SHA-256: `37389c499579debb8017ce041a89cabdfae6ced2ee30e79e4ac8488eb53bd757`
- MD5: `40159e342d51bd14a46ccf9fe69e272b`
- CRC32: `C2E10BF6`
- 前 64 bytes HEX:

  `4D 5A FB 01 0E 00 00 00 02 00 89 0E FF FF 66 03 `
  `80 00 00 00 0E 00 A8 01 1C 00 00 00 4C 5A 39 31 `
  `FF FF FA B8 BA 25 05 10 00 B1 04 D3 E8 8C CB 03 `
  `C3 FF FF 8E D8 8E D0 BC 20 0F FB B4 30 CD 21 0A`

- MZ 檢查: **MZ/DOS-EXE(valid header)**
  - `e_cblp=507 e_cp=14 reloc_items=0 header_paras=2 minalloc=3721 maxalloc=65535 SS=0366 SP=0080 IP=000E CS=01A8 lfarlc=001C ovno=0 e_lfanew=169987376`
- ASCII strings (34 筆, 顯示前 34):
  - `LZ91`
  - `SOUND-DRIVE`
  - `CR-A`
  - `Soun`
  - `?d-driver: Bad f`
  - `ction numb`
  - `?F;F=v`
  - `3?:v`
  - `>L#r`
  - `Tuo.`
  - `ugSQR`
  - `BY[X`
  - `ta>r`
  - `0>?1`
  - `Rk8l`
  - `s(k{`
  - `SAJ2`
  - `b=-_`
  - `Invalid `
  - `stack`
  - `I/O redi`
  - `sufficient?`
  - ` memory`
  - ` STACK OVERFLOW `
  - `drive`
  - `r V1.51 (C) A`
  - `nc. 1987`
  - `too lar+`
  - `dy iZ1ll@`
  - `Ccces`
  - `d evn`
  - ` LIST`
  - `E FULL`
  - `*FAB*`
- Big5/中文 strings (80 筆, 顯示前 80):
  - `鐖髀`
  - `轉暨`
  - `湛崏`
  - `奠籫`
  - `頏鏸`
  - `殧鯽`
  - `錝燽`
  - `疘侳箜儗`
  - `腜ｃ`
  - `匱謾蟳`
  - `駌筘`
  - `蕦鬎`
  - `橶嫙`
  - `瓕鼉`
  - `董蜣粺`
  - `玁讓`
  - `詳簅`
  - `撣獿`
  - `駉麻豵盹`
  - `轍蕆`
  - `譝礗`
  - `鱵躦`
  - `墆癌`
  - `僦鑴`
  - `嗹識`
  - `鶡遻`
  - `鷘釐`
  - `蝞僔鍎`
  - `闌薍鏸`
  - `藱粹`
  - `芷鋼`
  - `逡釪`
  - `慥蜧搆堽`
  - `輗麃`
  - `襴僵`
  - `迤聖`
  - `祡睌`
  - `毃齘`
  - `窉鶋`
  - `俛朄聶`
  - `稔佻`
  - `琭蹺`
  - `觴踔閷巃`
  - `揨摙`
  - `綻鴀`
  - `筵橪`
  - `情條`
  - `蹪盞`
  - `稠跤`
  - `蛭阿`
  - `芄綱`
  - `谹彄`
  - `薏硞`
  - `閫鸇`
  - `檁噎`
  - `枙眄`
  - `誠儅輴`
  - `鎳憀`
  - `摠認`
  - `難詣`
  - `矔涀`
  - `棋禴劊`
  - `鱣丌`
  - `慔雝`
  - `麃衊`
  - `匴昶`
  - `勱騖孃`
  - `鍪譏`
  - `慏綧`
  - `臏懁`
  - `酕硃椓`
  - `篘桑`
  - `鳲訹嚲`
  - `驖眚`
  - `縕嵃`
  - `樸滘湉譨`
  - `螔齘`
  - `榱後`
  - `蕛迋銵`
  - `齘薃`

---

## han\STANDARD.BNK

- 副檔名: `BNK` | 大小: 1024 bytes
- SHA-256: `6f9a77a8e3c183b9f0cca97a3b0089c8dc179f234da6d05d8da38c48ff43535a`
- MD5: `d5f1a6631302952afabbbe85a583cdea`
- CRC32: `C35A046E`
- 前 64 bytes HEX:

  `01 00 41 44 4C 49 42 2D 07 00 20 00 1C 00 00 00 `
  `9C 01 00 00 00 00 00 00 00 00 00 00 03 00 01 42 `
  `44 52 55 4D 31 00 00 00 05 00 01 43 59 4D 42 41 `
  `4C 31 00 00 06 00 01 48 49 48 41 54 31 00 00 00`

- MZ 檢查: 否 (前2 bytes = `0100`)
- ASCII strings (8 筆, 顯示前 8):
  - `ADLIB-`
  - `BDRUM1`
  - `CYMBAL1`
  - `HIHAT1`
  - `PIANO1`
  - `SNARE1`
  - `TOM1`
  - `TRUMPET1`
- Big5/中文 strings: (無)

---

## han\YING.PAT

- 副檔名: `PAT` | 大小: 2048 bytes
- SHA-256: `79f1c8bf4510f267fc40d60036a401737dd3492996b279cb1a753dd58dc7ceb1`
- MD5: `cac63316e286248e92c647b4ab920a5f`
- CRC32: `EA96E2E0`
- 前 64 bytes HEX:

  `00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 `
  `00 00 00 00 20 30 38 3C 3E 3C 38 30 20 00 00 00 `
  `00 00 00 00 7E FF DB FF FF C3 E7 FF 7E 00 00 00 `
  `00 00 00 00 00 36 7F 7F 7F 7F 3E 1C 08 00 00 00`

- MZ 檢查: 否 (前2 bytes = `0000`)
- ASCII strings (57 筆, 顯示前 57):
  - ` 08<><80 `
  - `<fBBf<`
  - `<fff<`
  - `?3?000p`
  - `cccg`
  - `@'p|`
  - `|p'@`
  - `333333`
  - `6cc6`
  - `""""`
  - `>UTTT>`
  - `"RT$`
  - `8DN@ .BAAA>`
  - `>AAAAAAAAA>`
  - `@@@@~`
  - `>@@@@~AAAA>`
  - `>AAAA>AAAA>`
  - `>AAAA?`
  - `@'px|~|xp'@`
  - `>AIUUUUQN@?`
  - `"">AAAA`
  - `|BBBB~AAAA~`
  - `>A@@@@@@@A>`
  - `|BAAAAAAAB|`
  - `@@@@~@@@@`
  - `@@@@~@@@@@`
  - `>A@@@GAAAA>`
  - `AAAAA`
  - `ABDHP'PHDBA`
  - `@@@@@@@@@@`
  - `AcUIAAAAAAA`
  - `AaQIECAAAAA`
  - `~AAAA~@@@@@`
  - `>AAAAAIIIE>`
  - `~AAAA~PHDBA`
  - `>A@@@>`
  - `AAAAAAAAAA>`
  - `AAA"""`
  - `AAAAAAAIUcA`
  - `AA""`
  - `?AAAA?`
  - `@@@@@~AAAA~`
  - `>A@@A>`
  - `    >     `
  - `<BBB>`
  - `@@@@@~AAAAA`
  - `@@@@@ABDLRa`
  - `~IIIII`
  - `~AAAAA`
  - `>AAAA>`
  - `~AAA~@@`
  - `?AAA?`
  - `CLP'@@`
  - `     ~    `
  - `AAAAA?`
  - `AAIUcA`
  - `AAAA?`
- Big5/中文 strings (2 筆, 顯示前 2):
  - `褌醮`
  - `詗萑`

---

## han\ZHONG.COD

- 副檔名: `COD` | 大小: 1182 bytes
- SHA-256: `a81d3cffcb6a02cc4f63e3945ee8149f66cc22178029d9727c383455c74860d4`
- MD5: `8d8af0ab88da5ed35ef8707c924e2a01`
- CRC32: `513A55F3`
- 前 64 bytes HEX:

  `B8 A1 F1 BF 46 AA E8 A6 5F A5 AD A5 AE BA A7 B6 `
  `57 A4 A6 A8 4E A5 AD B6 F9 AA 45 A4 EC AD F4 BB `
  `64 B9 C0 B3 D3 A4 61 A6 77 B2 78 B2 A7 C1 D5 CD `
  `58 E8 D2 C4 65 AA BA A4 76 A5 F7 C3 BF A6 72 AA`

- MZ 檢查: 否 (前2 bytes = `B8A1`)
- ASCII strings: (無)
- Big5/中文 strings (2 筆, 顯示前 2):
  - `腹鬵`
  - `芾囝平幼漣超丹沐平嫁枕木哥蜿嘛勝兀安琊異轅炂骳攙的己份藩字邱止槊川弋愍篁鄤膳軟品漱夭說斟濠冗載桂夏玥剷冰撕函排醇剛弁貌執孝植責吱摩蒂鬨敕奸銲芳佛者譫薯餾髮周帖由必賜賢孔廾魺捐匹裶團梟艱良齈處旱末鄴虫敗袂埃剌妨哥疋劊嬛姒巨訑迎桂抹晁伍跾綜鋪簷歲綏篾蝕癒魂匝秦級嫡毓佔蹦乎冀且叉烈剷昆舵蛹吳珠座嬉首玬刊裸硎愀頜吸髡醋腌貶苦漿尹戌必陘芋跚偏逸冉吼詻讓父鮮澤砭隄爐奉幀集饜來馬殿斡氿齵亭氈幢友糊屍仿鼯全產逕同`

---

## han\ZHONG.PAT

- 副檔名: `PAT` | 大小: 18912 bytes
- SHA-256: `51eb00e5a8ce7bdf83efa311a98fcf67899e06241dbc296b3b1ffa6de0af49b0`
- MD5: `dca0ea2206c2765b3f84a30cc99394eb`
- CRC32: `28A84418`
- 前 64 bytes HEX:

  `00 00 01 00 02 80 02 80 04 40 04 40 FC 7E 40 04 `
  `20 08 10 10 08 20 09 20 12 90 14 50 28 28 30 18 `
  `00 00 40 20 37 FF 12 52 01 8C 79 04 0A FA 14 89 `
  `20 F8 10 88 08 F8 18 70 10 A8 29 24 47 FF 00 00`

- MZ 檢查: 否 (前2 bytes = `0000`)
- ASCII strings (60 筆, 顯示前 60):
  - `P((0`
  - `""""""$`
  - `B"2"`
  - `$I(I`
  - `j%TI@`
  - `AAAA`
  - `@"H$FIB`
  - `@"@A@>`
  - `$0E!`
  - `IrM$J`
  - `"D>(!`
  - `!B""$`
  - `J(j/S`
  - `B/B)Bo`
  - `@ 0 `
  - `%%<I`
  - `BQ@ `
  - `~?B!~?B!~?@`
  - ` * )`
  - `AAIIzI`
  - `JBI(`
  - `%\=T$`
  - `'uL#`
  - `"?"!>!"!"!"?"!J`
  - `z"I$K`
  - `I"z!I`
  - `H"HBH`
  - `!B?~?~!B?~`
  - ` *$I&`
  - `$!,J"`
  - `!A*A$A A `
  - `|TH(|`
  - `?QQ `
  - `#*"J>`
  - `""B@`
  - `>"D"`
  - `IBIB`
  - `RIJIB`
  - `BUFUB`
  - ` ( K`
  - `%%%%=`
  - `%!%!-eF"`
  - `!?BB`
  - `(&D@`
  - `"*"J"`
  - `)$I$`
  - ` ("O`
  - `("D"DB`
  - `8~ D>D"D>`
  - ` D>D"("`
  - `*($GA`
  - `))**`
  - `($/'4@?`
  - ` %@C`
  - `~(B(B(B(~IB`
  - `@0@PD`
  - `TRTTT`
  - `$8$T$`
  - ` "$"$">J`
  - `%E%+!`
- Big5/中文 strings (2 筆, 顯示前 2):
  - `躥襼呢臡`
  - `榎＠`

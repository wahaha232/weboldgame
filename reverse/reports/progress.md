# Phase 1 — FILE FORENSICS 進度報告 (progress.md)

**專案**: 《楚漢之爭》DOS 原始遊戲逆向解析
**工作區**: `D:\VS CODE\PROJECT\hanwebgame`
**本階段目標**: 完成 Phase 1 FILE FORENSICS 並停止(不進入 Phase 2 / 不開始任何 Web 開發)

---

## 1. 原始檔案定位與驗證

| 項目 | 結果 |
|---|---|
| 預期位置 `original/han.rar` | 不存在 |
| 實際位置 | **`D:\VS CODE\PROJECT\hanwebgame\han.rar`**(工作區根目錄) |
| 檔案大小 | 186,634 bytes |
| Magic | `52 61 72 21 1A 07 00` → **RAR 4.x**([VERIFIED]) |
| SHA-256 | `f52eacb6ee809d2888af628b6b4c66abe5d4411dd495b8bbc6a831ece6ff5895` |
| MD5 | `694b50bcc6ce7acffad0f0907813a436` |
| CRC32 | `62B14349` |
| 解壓工具 | 7-Zip 26.02(本機 `C:\Users\wahah\Desktop\7-Zip\7z.exe`) |

> 原始 han.rar 未做任何修改;所有分析產物位於 `reverse/`。自製 header parser:
> `reverse/tools/list_rar.py`(不依賴外部工具的 RAR4 唯讀解析)。

## 2. Archive 內容(19 檔,解壓至 `reverse/extracted/han/`)

| 檔案 | 大小 | 初步判讀 |
|---|---|---|
| HAN.EXE | 133,424 | DOS MZ 可執行(核心) |
| SOUND.EXE | 7,163 | DOS MZ 可執行,疑 LZ91 壓縮殼 |
| PICS.GRP | 290,344 | 圖形(raw bitmap) |
| PICS.IDX | 136 | 圖形索引(17 筆) |
| FACE.GRP | 180,024 | 頭像圖形(格式未解) |
| BASEDATA.001 | 11,376 | 遊戲靜態資料(郡名等) |
| HANSAVE.DAT | 45,760 | 存檔 |
| SONGS.GRP | 13,265 | 音樂資料(?含 `\roll\default`) |
| SONGS.IDX | 12 | 索引(3×uint32) |
| STANDARD.BNK | 1,024 | AdLib 音色庫(含 `ADLIB-` 簽名) |
| ZHONG.PAT | 18,912 | 中文字型(16×16, 591 glyph) |
| ZHONG.COD | 1,182 | 中文對照(591×2) |
| YING.PAT | 2,048 | 英文字型(8×16, 128 glyph) |
| INSTALL.BAT / PLAY.BAT | 339 / 29 | 安裝/啟動批次檔 |
| 攻略.txt 等 4 個 txt | — | **附加文件**(2002–2005 加入,非原始遊戲檔) |

完整 per-file 紀錄(hash/MD5/CRC32/first64 HEX/ASCII/Big5 strings/MZ 檢查):
→ `reverse/reports/file_inventory.md`

## 3. Phase 1 工作清單狀態

- [x] 找到原始檔案、顯示路徑與大小、算 SHA-256 / MD5 / CRC32、判斷 RAR 版本、列出內容
- [x] 解壓縮至 `reverse/extracted/han/`(未動原始檔)
- [x] 完整檔案 Inventory(每檔 hash、first64 HEX、ASCII/Big5 strings、MZ 檢查)
- [x] Magic Bytes / 檔案分類初步判讀
- [x] Hex Dump → `reverse/dumps/hex/*.txt`(含全文 dump:SONGS.IDX、PICS.IDX、BASEDATA.001、STANDARD.BNK、ZHONG.COD、YING.PAT 等)
- [x] Strings / Big5 Strings(郡縣名、`SOUND-DRIVER-AD-LIB`、`ADLIB-`、`Stack overflow!` 等)
- [x] MZ Header 檢查(HAN.EXE / SOUND.EXE)→ `reverse/reports/han_exe_analysis.md`
- [x] BAT 分析(INSTALL.BAT / PLAY.BAT / `sound b7000`)→ `reverse/reports/bat_analysis.md`
- [x] 建立初步 Hypothesis → `reverse/hypotheses/`
- [x] 建立 progress.md(本檔)

## 4. Phase 1 重要發現(依證據分級)

1. **[VERIFIED]** PICS.GRP = 17 張 8-bit indexed raw 圖;每張 `u16 w + u16 h + w×h pixels`,len=w×h+4 全數吻合。
2. **[VERIFIED]** PICS.IDX = 17 × (uint32 start, uint32 end);與 GRP 內容一致。
3. **[PROBABLE]** STANDARD.BNK 為 AdLib 音色庫(`ADLIB-` 簽名 + 配套字串)。
4. **[PROBABLE]** ZHONG.PAT / YING.PAT / ZHONG.COD 為字型檔(數量:591/128/591,與 16×16@32B、8×16@16B、2B/字 吻合),尚待字形繪製驗證。
5. **[HYPOTHESIS]** 聲音系統以 AdLib 為主(SOUND.EXE 疑 LZ91 殼、`sound b7000` 語意未定,禁止臆測)。
6. **[HYPOTHESIS]** HAN.EXE / SOUND.EXE 之 MZ header 異常(reloc=0、`LZ91`、0x200 起 stub)疑受加工(保護/破解),Phase 2 需先驗證。
7. **[PROBABLE]** BASEDATA.001 / HANSAVE.DAT 含郡縣名資料(HANSAVE 為重複郡縣狀態區塊)。
8. **[REJECTED — 初版自製 parser]** list_rar.py 首次版本解析偏移錯誤 → 修正 unp_ver/欄位後驗證;最終以 7-Zip listing 為準。

## 5. Phase 1 產出清單

```
reverse/
├─ extracted/han/                     (解壓原始檔, 唯讀不動)
├─ reports/
│  ├─ file_inventory.md               (每檔 hash/hex/strings/MZ + 初步分類)
│  ├─ han_exe_analysis.md             (Phase1: MZ header)
│  ├─ bat_analysis.md                 (啟動流程)
│  └─ progress.md                     (本檔)
├─ dumps/
│  ├─ hex/…                           (hex dumps)
│  └─ text/…                          (附加 txt 轉 UTF-8 副本)
├─ tools/
│  ├─ list_rar.py                     (RAR4 唯讀解析)
│  ├─ inventory.py                    (檔案鑑識 inventory 產生器)
│  └─ hex_dump.py                     (hex dump 工具)
└─ hypotheses/                        (初步假設資料庫)
```

## 6. 下一步(Phase 2 建議,待指示後才執行)

1. SOUND.EXE 之 LZ91 格式鑑別與解壓(輸出至 dumps)。
2. HAN.EXE / SOUND.EXE 反組譯:分段表、interrupt 使用、I/O、entry 流程。
3. HAN.EXE 對 BASEDATA.001 / PICS.* / FACE.GRP / HANSAVE.DAT / SONGS.* 的讀取邏輯追蹤。
4. 調色盤定位與圖片/字型 PNG 驗證輸出。
5. 依照 hypotheses/ 的 Next Test 逐項驗證。


# Phase 2 — 程式與資料格式深入分析 進度 (進度追加)

> 本節記錄「繼續」後執行之 Phase 2 進度。

## Phase 2 已完成項目

### 工具/環境
- 安裝 Python `capstone`(16-bit x86 反組譯用);`Pillow` 已有。

### 圖形 (reports/graphics_analysis.md)
- [VERIFIED] PICS.GRP 17 圖(容器 `u16 w/u16 h + raw`);FACE.GRP **78 × (4+48×48)**。
- 解出 PNG 灰階預覽:`dumps/pics/*`、`dumps/face/*`。
- 調色盤定位:`HAN.EXE` **0x1B40F** 起 768B 全為 6-bit 值(候選);緊鄰字串表 → [PROBABLE] 調色盤,待 code trace。

### 字型 (reports/font_analysis.md)
- [PROBABLE] ZHONG.PAT 591×32(16×16)、YING.PAT 128×16(8×16)、ZHONG.COD 591×2。
- 字形 sheet 輸出 `dumps/font/*.png`。

### 聲音 (reports/sound_analysis.md)
- [VERIFIED] STANDARD.BNK:`ADLIB-` + 7 具名打擊樂器(DRUM1…TRUMPET1);+0x0C=28。
- [PROBABLE] SOUND.EXE 0x1C 處 `LZ91` 壓縮標記。
- [HYPOTHESIS] HAN.EXE 以名稱(`_SoundCall` 等)向音效 TSR 取服務。

### 遊戲資料 (reports/basedata_analysis.md)
- [VERIFIED] BASEDATA.001:城市表 39×0x30 @0x540;人物表 255×0x20 @0xC90(項羽…范增…)。
- 輸出:`dumps/basedata/cities.txt`、`characters.txt`。

### 存檔 (reports/save_analysis.md)
- HANSAVE.DAT 含重複郡名區塊與圖示區;版型待多存檔差分。

### 本輪新增結果
- [VERIFIED] SONGS.IDX = 3×uint32 三首歌起點;SONGS.GRP = 3 首 AdLib 多軌譜
  (文字標記 `Tempo/Voix/Timbre/Volume/Pitch`,11 軌,樂器名對應 STANDARD.BNK)。
- [VERIFIED] STANDARD.BNK 樂器名 = BDRUM1/CYMBAL1/HIHAT1/PIANO1/SNARE1/TOM1/TRUMPET1。
- [VERIFIED] HAN.EXE 主 code 區約 0x1278E–0x17798(內含唯一 `AH=3Dh` fopen 包裝於 0x168AA、
  MS-C 16-bit 大模式,handle 表在 `[bx+0x2ACC]`);固定段呼叫(`lcall 0x16AE,0x0D`、DS=0x19CB)→
  檔案疑為依賴特定載入位址之加工版,entry 定錨需動態驗證。
- [VERIFIED] 檔名表/候選調色盤(0x1B40F)/Sound API 名稱表等資料內嵌位置標記完畢。
- 產物: `tools/sound_analyzer.py`、`dumps/sound/songs_overview.txt`;
  reports 更新:`han_exe_analysis.md`、`sound_analysis.md`。

### 本輪新增結果(SOUND.EXE 定性 + 規格草稿)
- [PROBABLE] SOUND.EXE = `LZ91` 自定位 loader(LZEXE 0.91 系)+ LZ 壓縮本體;
  loader 以 `FF FF` 段值佔位執行期自 patch(故 MZ reloc=0);0x1AB0 起為多段式 LZ 解壓器。
- [VERIFIED] loader 區含命令列/驅動字串(`SOUND-DRIVE`、`CR-A`、`Sound driver: Bad function number`…),
  故 `b7000` 為此 loader 解析之參數(語意仍 [UNKNOWN],需解壓後驗證)。
- [VERIFIED] 新增 `reports/reverse_engineering_spec.md`(規格草稿 v0.2,彙整所有已確認格式與未知區)。
- SOUND.EXE 完整解壓改列「需 DOSBox 動態擷取或實作 LZEXE 解壓」。

### 本輪新增結果(HANSAVE.DAT 版面)
- [VERIFIED] HANSAVE.DAT = header(勢力文字行+`AC`+圖示位元區) + **4 份世界狀態副本**
  @ 0x640 / 0x32B0 / 0x5F20 / 0x8B90(間距 = 0x2C70 = BASEDATA 大小)。
- [VERIFIED] 每份狀態 ≈ BASEDATA[0x540:0x2C70];現況副本差 1794B,其餘三份各差 ~300B。
- 例:遼東 uint32 值 5000/2500(BASEDATA)→ 3226/762(存檔現況) → 疑兵力/資源。
- 更新:`reports/save_analysis.md`、`hypotheses/save_format.md`、`reverse_engineering_spec.md`。

### 本輪新增結果(顯示/調色盤 + 字型 + SOUND/SONGS 再確認)
- [VERIFIED] HAN.EXE 視訊初始化(0x11B30):模式 13h(MCGA 320×200×256);
  INT 10h AX=1012h BX=0 CX=256 由固定資料段 0x19CB 之 **0x1F4E / 0x224E** 載入兩組調色盤。
- [VERIFIED] YING.PAT **glyph index = ASCII code**('A'@0x41、'a'@0x61 標準字形)。
- [VERIFIED] ZHONG.COD 591×u16 全唯一(值域 A1B8–F97D),但與遊戲文字重疊 <3% → 語意仍 [UNKNOWN]。
- 更新:`reports/han_exe_analysis.md`、`reverse_engineering_spec.md`。

### 本輪新增結果(SOUND.EXE 解壓)
- [VERIFIED] 以 `tools/lzexe_unpack.py`(移植 mywave82/unlzexe 0.9;src 在 `tools/src/`)解出
  SOUND.EXE = **LZEXE 0.91** 包裝之 **Ad Lib「Sound Driver V1.51」TSR**(13,792B)。
- [VERIFIED] TSR 掛 **INT 65h**,簽名 `SOUND-DRIVER-AD-LIB`;OPL 寫入 0x388/0x389(base 變數)。
- [VERIFIED] `b7000` 解析:'b' 選項 + hex 7000 = 0x7000 寫入參數槽(預設 0xFFA,min 0x3E8;語意待證)。
- 產物:`dumps/SOUND_unpacked.exe`、`tools/lzexe_unpack.py`、`tools/src/*`(來源註明);
  reports/spec/hypotheses 更新。

### 本輪新增結果(規格深化)
- [VERIFIED] HANSAVE 四份狀態區塊在 +0x750 各含 255 人人物表(與 BASEDATA 版面一致)。
- 產出 `dumps/basedata/persons.csv`(255 人)、`cities.csv`(39 城)。
- `reverse_engineering_spec.md`:更新 §10/11;新增附錄 A(位元組級版面速查)、B(數值欄位觀察)、C(Web 轉製注意事項)。
- DOSBox 動態嘗試結果已記錄於 `reports/dynamic_attempt.md`(自動環境內 DOSBox-X ~20s 自退,待互動環境)。

### 本輪新增結果(圖形色彩全定案)
- [VERIFIED] palA 適用 **FACE 78 張 + PICS 全部 17 張**(使用者目視正常)→ 圖形調色盤定案。
- canonical:`dumps/face_final/`、`dumps/pics_final/`(含 palette_8bit.bin、CONTACT 對照)。
- 更新:`reports/graphics_analysis.md`、`reverse_engineering_spec.md` §2。

### 收尾(2026-09)— 規格 v1 出爐
- 新增 **`reports/remake_spec_v1.md`**《可玩重製規格 v1》:素材產出清單、圖形/字型/BASEDATA/HANSAVE/聲音/EXE 規格、規則現況與缺口、建議。
- 動態測試暫停;DOSBox 已關閉。原始檔未修改。













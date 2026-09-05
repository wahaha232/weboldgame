# 《楚漢之爭》Reverse Engineering Specification — 草稿 v0.2 (Phase 1+2 匯整)

> 狀態:進行中。所有事實標記證據等級。
> 產生來源:原始 RAR `han.rar`(SHA-256 f52eacb6…)解壓之 `reverse/extracted/han/`。
> 此文件目標:成為日後重製 Web Game 的主要技術規格。內容會隨 Phase 持續更新。

---

## 0. 證據等級
[VERIFIED] 直接 binary/assembly 證據 | [PROBABLE] 多重支持未全證 | [HYPOTHESIS] 合理推測
| [UNKNOWN] 無法判斷 | [REJECTED] 已被推翻

## 1. File Inventory(摘要)
| 檔 | 大小 | 角色 | 狀態 |
|---|---|---|---|
| HAN.EXE | 133,424 | 主程式(含 loader) | 部分分析(見 §9) |
| SOUND.EXE | 7,163 | 音效驅動(TSR)loader+LZ | 見 §7 |
| PICS.GRP / PICS.IDX | 290,344 / 136 | 圖形 + 索引 | [VERIFIED] 結構 |
| FACE.GRP | 180,024 | 78 張 48×48 頭像 | [VERIFIED] 結構 |
| BASEDATA.001 | 11,376 | 靜態世界/單位資料 | [VERIFIED] 版面,欄位語意未定 |
| HANSAVE.DAT | 45,760 | 存檔 | 初步,多存檔差分未做 |
| ZHONG.PAT / YING.PAT / ZHONG.COD | 18,912 / 2,048 / 1,182 | 中文/英文/對照 字型 | [PROBABLE] 見 §6 |
| SONGS.GRP / SONGS.IDX | 13,265 / 12 | 3 首 AdLib 樂譜 + 索引 | [VERIFIED] 見 §7 |
| STANDARD.BNK | 1,024 | AdLib 樂器庫 | [VERIFIED] 簽名/樂器名 |
| INSTALL.BAT / PLAY.BAT | — | 安裝/啟動 | [VERIFIED] |
| 4 × 附加 .txt | — | 非遊戲資料(2002+) | 僅參考 |

## 2. 圖形格式(Graphics Format)
### PICS.GRP(圖片容器)[VERIFIED]
- 每張 = `uint16le width | uint16le height | w×h bytes 8-bit palette index`。
- PICS.IDX = 17 × (uint32le start, uint32le end),start 對應 GRP 檔內起點。
- GRP 檔內另有**未索引**圖片區間(例如 32×24 額外 1 張、80×128 額外 1 張等)。
- 尺寸範例:160×288(title/背景)、168×256、48×24、32×24、80×128。

### FACE.GRP [VERIFIED]
- 78 × (4+48×48)=180,024;容器同上。每張僅用 5–13 個調色盤索引。

### 調色盤 [VERIFIED — 視覺確認]
- 由 DOSBox 0.74 runtime 記憶體提取兩張調色盤;使用者目視確認 **palA** 正確,且
  **FACE 78 張 + PICS 17 張全部以 palA 呈現正常** → 圖形色彩定案。
- palA:768B、6-bit(≤63);來源 guest 記憶體(host 0x13A1FBE1 / 映像複本 0x47521D7)。
- canonical 輸出:`dumps/face_final/`(78 頭像)、`dumps/pics_final/`(17 圖)+ `palette_8bit.bin` + CONTACT 對照。
- palB(另一 runtime 表)保留於 `dumps/pics/palB_8bit.bin`,用途未定。



## 3. Font Format(字型)
- YING.PAT:128 glyph × 16B = 8×16;**[VERIFIED] glyph index = ASCII code(identity)**:
  index 0x41/0x42/0x43/0x61/0x30/0x38/0x3F 分別為標準 A/B/C/a/0/8/? 字形;index 0x20 = space。
- ZHONG.PAT:591 glyph × 32B = 16×16(每列 2B)。排序假設與 ZHONG.COD 對應(未證)。
- ZHONG.COD:591 × 2B;值域 A1B8–F97D 且 591 值全唯一,但與遊戲文字(BASEDATA/HAN.EXE)重疊極少(3%)→
  角色/排序 [UNKNOWN](非一般 Big5 字表)。
- 字形 sheet:`dumps/font/*.png`。

## 4. Game Data Format(BASEDATA.001)[VERIFIED 版面]
```
0x0000  header(~0x44,含 "AC" 1A 00 與位元組清單,語意 UNKNOWN)
0x0540  城市表 39 × 0x30: name(4B,Big5,空白補足)| 狀態欄位(多組 uint32;語意待解)
0x0C90  人物表 255 × 0x20: name(8B,Big5,空白補足)| 24B 屬性(語意/編碼待解)
```
- 城市名:遼東/遼西/北平/漁陽/上谷/雁門/九原/鉅鹿/太原/北地/琅琊/邯鄲/上黨/河東/內史/隴西/九江/泗水/三川/會稽/穎川/南陽/漢中/閩中/黔中/南海/桂林(+單字城如代/齊/薛/東/楚/南/巴/蜀…)共 39 槽。
- 人物:項羽、劉邦、項梁、嬴胡亥、趙高、李斯、陳勝、吳廣、葛嬰、張耳、陳餘、武臣、邵騷、襄疆、鄧宗、周市、李由、蔡賜、周文、孔鮒、徐公、蒯徹、張敖、韓廣、李良、張黶、章邯、劉伯、劉仲、蕭何、曹參、夏侯嬰、呂重、任敖、樊噲、呂三、曹咎…(255 筆,含空)。
- 工具:`tools/basedata_analyzer.py` → `dumps/basedata/{cities,characters}.txt`。

## 5. Save Format(HANSAVE.DAT)
- 45,760B。
- 版面(可驗證):
  - 0x0000–0x063F:header(勢力「君主 在 城」文字行、`AC` 標記、圖示位元區)
  - 4 份「世界狀態」副本 @ 0x0640 / 0x32B0 / 0x5F20 / 0x8B90(間距 0x2C70)
  - 每份狀態 ≈ BASEDATA[0x540:0x2C70](城市表 39×0x30 + 人物表 255×0x20),內容與預設差:
    現況副本差 1794B,其餘三份各差 ~300B(每城記錄旗標)。
- 例:遼東 uint32 值 BASEDATA=5000/2500,存檔現況=3226/762 → 疑兵力/資源動態值。
- header/version/checksum/回合等欄位 → [UNKNOWN];4 副本意義待 runtime。
- 工具:`tools/parse_save.py`、差集分析(見 `dumps/save/save_overview.txt`、`reports/save_analysis.md`)。

## 6. Sound Format
### STANDARD.BNK [VERIFIED 部分]
- 簽名 `ADLIB-`;+0x0C=28;具名樂器:BDRUM1, CYMBAL1, HIHAT1, PIANO1, SNARE1, TOM1, TRUMPET1。
- 詳細 instrument 欄位(疑 OPL2 register 參數)→ [UNKNOWN] 待 SOUND.EXE 驗證。

### SONGS.IDX / SONGS.GRP [VERIFIED 結構]
- IDX=3×uint32(0,0x196D,0x267E)=三首歌。
- 每首歌:`00 00 04 00` + `\roll\default` 檔頭、`Tempo`、11 軌 `Voix 0..10`;
  軌道含 `Timbre n`+樂器名、`Volume n`、`Pitch n`(含 float)與音高事件序列。
- 事件語意(時值/音高排列)→ [UNKNOWN]。

### SOUND.EXE [VERIFIED — 已解壓]
- 本體 = **LZEXE 0.91** 包裝的 Ad Lib「Sound Driver V1.51」TSR(解壓 13,792B → `dumps/SOUND_unpacked.exe`)。
- 掛 **INT 65h**;簽名 19B `SOUND-DRIVER-AD-LIB`。HAN.EXE 以名稱呼叫(`_SoundCall` 等)。
- OPL 寫入:base 變數(預設 **0x388**)/資料 **0x389**,OUT+IN 延時。
- 命令列選項:b/B→槽0xFFA(min 0x3E8,疑 buffer),p/P→槽0x388(疑 I/O base),w/W→第三槽。
  `b7000` = 0x7000 寫入 0xFFA 槽(語意待證)。
- 工具:`tools/lzexe_unpack.py`(演算法/參數自 `tools/src/unlzexe.c`,mywave82/unlzexe 0.9 移植)。

## 7. 啟動流程(BAT)
- INSTALL.BAT → `C:\han`;PLAY.BAT:`sound b7000` 後 `han`。
- `b7000` 語意 [UNKNOWN](疑 loader 參數,可能=TSR 載入位址;禁止臆測)。

## 8. HAN.EXE 主程式結構
- 內嵌資料(檔案 offset):檔名表 0x19EB0、0x1BA11;Sound API 名表 ~0x1F023
  (`_SoundCall`、`_GetSoundDrvVersion`、`_m_sound_eff`、`_sound`、`_nosound`…);
  候選調色盤 0x1B40F。
- `int 21h` 使用區:stub 0x200–0x9C0;主 code ~0x1278E–0x17798(fopen 包裝於 0x168AA;
  MS-C 16-bit large model;handle 表 `[bx+0x2ACC]`)。
- 大量固定段常數(`lcall 0x16AE,0x0D` 等)與自定位 stub(DS=0x19CB 清 BSS)→
  [HYPOTHESIS] 依賴特定載入位址之加工版;真實 entry 需動態驗證。

## 9. 遊戲規則(Game Logic)
- 尚未從程式驗證。第三方文字(攻略.txt,非 binary)提供以下**參考**:
  智冠 1990 策略;8 勢力;郡縣制兵力(每郡最大 150,000);君主所在郡可直接下令等。
- 全部規則標記:需由 HAN.EXE 反組譯或 runtime 驗證,目前皆 [UNKNOWN]。

## 10. Important Algorithms / 已確認
- 圖形:PICS/FACE = 無壓縮 raw 8-bit(VERIFIED);PICS.IDX = (start,end)。
- 字型:YING 128×16B identity;ZHONG 591×32B(排序待解);無壓縮。
- 存檔/BASEDATA:無壓縮固定表格。
- SOUND.EXE:`LZEXE 0.91` 包裝 → 已解壓(Ad Lib Sound Driver V1.51 TSR)。
- 音樂:SONGS 3 首多軌譜(事件語意待解)。

## 11. Unknown Areas / Remaining Tasks
1. HAN.EXE runtime entry / 固定段 mapping(0x19CB)→ 調色盤正式檔案位址與重渲(需動態)。
2. SONGS 事件語意、STANDARD.BNK 欄位↔OPL 對照、ZHONG.COD 排序。
3. BASEDATA/HANSAVE 屬性欄位語意與編碼。
4. 遊戲規則(回合/戰鬥/內政/勝利)由程式還原。
5. DOSBox 互動環境動態驗證(嘗試紀錄: reports/dynamic_attempt.md)。


---

# 附錄 A — 位元組級版面速查(皆以 16 進位 file offset)

## BASEDATA.001
| 區段 | offset | 結構 |
|---|---|---|
| header | 0x0000 | `41 43 1A 00` + 位元組清單/FF 填補至 ~0x53F |
| 城市表 | 0x0540 | 39 × 0x30:名稱 4–8B(Big5,空白補足)、+0x09 旗標、+0x0C/+0x10/+0x14/+0x18/+0x1C 五個 u16 動態值、FF 填補 |
| 人物表 | 0x0C90 | 255 × 0x20:名稱 8B(Big5,空白補足)+ 24B 屬性/資料(編碼未解) |

## HANSAVE.DAT
| 區段 | offset |
|---|---|
| header/資訊(勢力文字行、`AC`、圖示) | 0x0000–0x063F |
| 狀態副本#0(城市 39×0x30 + 人物 255×0x20) | 0x0640 |
| 副本#1 | 0x32B0 |
| 副本#2 | 0x5F20 |
| 副本#3(至檔尾) | 0x8B90 |

副本間距 = 0x2C70;人物表在 副本+0x750。

## SONGS.IDX / SONGS.GRP
- SONGS.IDX = 3 × u32:0x0000 / 0x196D / 0x267E(三首歌起點)。
- 每首歌:「Voix n / Timbre n / Volume n / Pitch n」多軌譜,檔頭 `00 00 04 00` + `\roll\default`。

## STANDARD.BNK
- +0x02 `ADLIB-`;+0x0C u32=28;樂器名 BDRUM1/CYMBAL1/HIHAT1/PIANO1/SNARE1/TOM1/TRUMPET1;
  資料區 ~0x19C–0x270(疑似 11-byte OPL 參數組,未定案)。

## HAN.EXE 內嵌資料(參考)
- 檔名表 ~0x19EB0、~0x1BA11;Sound API 名 ~0x1F023;候選調色盤 0x1B40F(6-bit)。
- 視訊初始化 code 0x11B30(模式 13h、INT10 AX=1012 調色盤 0x19CB:0x1F4E / 0x224E)。
- fopen 包裝 ~0x168AA;主 code int21 區 ~0x1278E–0x17798。

# 附錄 B — 數值欄位觀察(未定語意)
- 城市 +0x0C..(+0x10/+0x14/+0x18/+0x1C):存檔現況 vs BASEDATA 預設會變動(例 遼東 5000→3226、2500→762)→ 疑兵力/資源。
- 人物屬性 24B:值域 0x00–0x7F,含 0xFF 分隔;與高位置位解碼為亂碼 → 判為數值/旗標類,非 7-bit 文字(REJECTED 該假說)。

# 附錄 C — Web 轉製注意事項(規格,非實作)
1. 圖形:可直接以「IDX(start,end)→ u16 w/h + raw」讀取;調色盤需由 EXE(0x19CB:0x1F4E)提取或視覺校正後內建。
2. 字型:ASCII 用 YING(identity);中文需先解 ZHONG.COD→ZHONG.PAT 對應(未解,勿臆測編碼)。
3. 遊戲資料:BASEDATA 提供城市/人物名稱與初始數值;存檔格式與「回合/年」欄位未定位,須 runtime 或第二存檔。
4. 音樂:Songs 樂譜格式與樂器欄位未完全解碼;轉 MIDI 前需完成事件語意。
5. 規則面(勝利/內政/戰鬥)尚未由程式驗證,僅第三方文字可參考。


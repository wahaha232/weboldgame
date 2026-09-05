# 《楚漢之爭》可玩重製規格 v1(Web 重製依據)

> 版本:2026-09(由 Phase 1/2 逆向成果整理,含 DOSBox 動態驗證)
> 性質:**規格文件**(不是 Web 實作)。目的:提供日後重製成 Web 版的格式與素材依據。
> 證據標記:[VERIFIED] binary/動態/目視確認 | [PROBABLE] 多證據支持 | [HYPOTHESIS] 推測 | [UNKNOWN] 未知
> 原始檔來源:`han.rar`(SHA-256 f52eacb6…);分析產物均在 `reverse/`(原始檔未修改)。

---

## 0. 一句話結論
圖形(畫面/頭像/調色盤)、字型(ASCII)、靜態資料(39 城/255 人/3 首樂譜結構)、
聲音驅動(AdLib TSR)、存檔「4 格」佈局都已逆向清楚,可直接做成**資源/資料型** Web 內容;
但**遊戲規則(回合流程/內政/戰爭/AI/勝利)**尚未由程式完整還原,「可玩」層面需再補。

---

## 1. 素材可直接使用(產出路徑)
| 素材 | 位置 | 說明 |
|---|---|---|
| 17 張畫面圖(彩色) | `reverse/dumps/pics_final/*.png` | 160×288 / 168×256 / 80×128 / 48×24 / 32×24;palA 上色已目視正常 |
| 78 張武將頭像 | `reverse/dumps/face_final/*.png` | 48×48;含網格 `faces_grid.png` |
| 調色盤(可直接內建) | `reverse/dumps/pics_final/palette_8bit.bin` | 768B,6-bit×4(RGB 8-bit) |
| ASCII 8×16 字型 | `reverse/dumps/font/ying_8x16.png`(樣張)/ YING.PAT | index=ASCII code [VERIFIED] |
| 中文 16×16 字形樣張 | `reverse/dumps/font/zhong_16x16.png` | 字碼對應未解(見 §3) |
| 39 城清單 | `reverse/dumps/basedata/cities.csv` | 名稱+槽位 |
| 255 人清單 | `reverse/dumps/basedata/persons.csv` | 名稱+索引 |
| 樂譜結構/hex | `reverse/dumps/sound/song0..2_hex.txt` | AdLib 多軌譜(事件語意未解) |
| 存檔樣本 | `reverse/dumps/save/save_turn0_newgame.dat`、`save_turn1_slot1.dat` | 用於差分 |

---

## 2. 圖形規格(Graphics)[VERIFIED]
- **容器**:每張圖 = `uint16le width | uint16le height | width×height bytes(8-bit 調色盤索引)`,無壓縮。
- **PICS.IDX**:17 筆 × `uint32le start,end`,指向 PICS.GRP 內區間。
- **FACE.GRP**:78 × (4 + 48×48)。
- **調色盤**:runtime palA(已目視確認適用全部圖與頭像);對應「HAN.EXE 資料區 0x1B40F 起 6-bit 表」內容。
- **畫面模式**:MCGA 320×200×256(INT 10 AX=13h)+ INT10 AX=1012h 載入調色盤。

## 3. 字型規格(Font)
- YING.PAT = 128 glyph × 16B = **8×16;glyph index = ASCII code**[VERIFIED](A/a/0/? 位置標準)。
- ZHONG.PAT = 591 × 32B = 16×16(排序與碼表未解);ZHONG.COD = 591×2B,**語意 [UNKNOWN]**(與遊戲文字重疊 <3%,非一般 Big5 表)。
- 建議:Web 版可先用系統字型顯示中文;若要原版點陣字需先解 ZHONG.COD 對應(見 §9)。

## 4. 靜態資料 BASEDATA.001[VERIFIED 版面]
- 0x0540 起 39×0x30 城市:名(4-8B Big5)+ 旗標(+0x09 疑存在)+ 5×u16(+0x0C/10/14/18/1C 疑兵力/資源類)。
- 0x0C90 起 255×0x20 人物:名(8B)+ 24B 屬性(編碼未解)。
- 與 HANSAVE 表單一致(見 §5)。

## 5. 存檔 HANSAVE.DAT[VERIFIED 佈局]
- 0x0000–0x063F:共用 header(勢力「君主 在 城」文字、`AC` 標記、圖示/tile 區)。
- **4 個存檔格**(0x2C70 間距):格1=0x640、格2=0x32B0、格3≈0x5F20、格4≈0x8B90(動態確認格1/格2)。
- 每格含:城市表 39×0x30(位於格起點)+ 人物表 255×0x20(格+0x750)。
- 每回合變動:該格城市/人物動態欄位;玩家目視「回合結束=月份+1」;候選計數 u16 `0x0C5C` 隨新回合存檔+1(需再驗)。
- 樣本:三份開局/回合1 存檔已存於 `dumps/save/`。

## 6. 聲音規格(Sound)
- SOUND.EXE = **Ad Lib「Sound Driver V1.51」TSR**(LZEXE 0.91 包裝,已解壓 13,792B)。
- 掛 **INT 65h**,簽名 19B `SOUND-DRIVER-AD-LIB`;OPL 寫入:base 變數(預設 **0x388**)→ reg、+1(0x389)→ data。
- `PLAY.BAT: sound b7000` → 參數 'b'、hex 7000 → **0x7000**(槽預設 0xFFA);語意疑 buffer 大小,[HYPOTHESIS]。
- STANDARD.BNK:`ADLIB-`、28、樂器名 BDRUM1/CYMBAL1/HIHAT1/PIANO1/SNARE1/TOM1/TRUMPET1;資料區疑 11-byte OPL 參數組(欄位對應未驗)。
- SONGS.IDX=3×u32 三首歌;每首含 `Voix 0..10`(11 軌)+ Tempo/Timbre/Volume/Pitch 標記;**事件語意未解**。

## 7. HAN.EXE 主程式(節錄)
- MS-C 16-bit large model;fopen 包裝 0x168AA;主 code INT21 區 ~0x1278E–0x17798。
- 視訊初始化 0x11B30(模式13 + 調色盤載入,來源 runtime 段 0x19CB:0x1F4E/0x224E)。
- 檔案在 DOSBox 可啟動(SOUND→HAN 流程可行);採「固定段/自載」設計;entry 之靜態解讀與動態事實需再研究。
- 內嵌資料:檔名表 0x19EB0/0x1BA11、Sound API 名 0x1F023、候選調色盤 0x1B40F。

## 8. 規則現況(Game Logic)
- 已由玩家目視確認(動態):
  - 主選單:新遊戲 / 舊遊戲 / 結束。
  - 新遊戲:可選 8 位君主(預設 劉邦);確定後進入開場白→主地圖。
  - 主指令:內政 / 軍事 / 外交 / 其他;結束回合=月份+1。
- 第三方文字(攻略.txt,非 binary):8 勢力、郡縣兵力制(單郡上限 150,000)、君主所在郡才可直接下指令等。
- **其餘規則(內政/戰爭/外交/徵兵/AI/勝利)程式層未還原 → [UNKNOWN]。**

## 9. 剩餘缺口與建議
1. ZHONG.COD↔中文字碼對應(需 HAN.EXE 繪字邏輯或實驗)。
2. SONGS 事件語意(時值/音高)→ 才能轉 MIDI。
3. 存檔「年/月/回合」欄位定案(一次正確「結束回合→存檔」的差分即可)。
4. 遊戲規則還原:建議 DOSBox 互動配合畫面文字,或程式級反組譯。
5. 調色盤 palB 用途(供其它畫面)待查。
6. 正式 Web 實作前,請另行授權(本文件不含 Web 實作)。

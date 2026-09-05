# 《楚漢之爭》Reverse Engineering — 產物索引

> 原始檔:`han.rar`(SHA-256 f52eacb6…,未修改)。全部分析產物在本目錄。

## 目錄
- `reports/` — 分析報告
  - **`remake_spec_v1.md`**《可玩重製規格 v1》(Web 重製依據;素材/格式/規則缺口)
  - `reverse_engineering_spec.md`(技術規格草稿,含附錄 A/B/C)
  - `file_inventory.md` / `bat_analysis.md` / `han_exe_analysis.md`
  - `graphics_analysis.md` / `font_analysis.md` / `sound_analysis.md`
  - `basedata_analysis.md` / `save_analysis.md` / `progress.md`
  - `dynamic_attempt.md`(DOSBox 動態嘗試與調色盤提取紀錄)
- `hypotheses/` — 逐格式假設(含 Evidence/Test/Result/Confidence/Next)
- `dumps/` — 資料傾印
  - `hex/` 各檔 hex;`text/` 附加 txt(UTF-8);`face|face_color/` `pics|pics_color/` 圖形 PNG
  - `font/` 字形 sheet;`basedata/` 城市/人物表;`save/` 存檔概觀;`sound/` 歌曲 hex/overview
  - `SOUND_unpacked.exe`(LZEXE 解壓之原始 SOUND driver)
- `tools/` — 自製唯讀工具(含 `src/` 引用來源)

## 主要已驗證事實(詳見 spec)
- PICS/FACE 圖形:raw 8-bit + `u16 w/h`,PICS.IDX=(start,end)×17,FACE=78×48×48。
- 字型:YING glyph=ASCII code;ZHONG 591;ZHONG.COD 語意未定。
- BASEDATA:城市 39×0x30(名+欄位)、人物 255×0x20(名+屬性)。
- HANSAVE:header + 4 份世界狀態副本(0x640/0x32B0/0x5F20/0x8B90)。
- SOUND.EXE=Ad Lib Sound Driver V1.51 TSR(INT 65h,簽名 SOUND-DRIVER-AD-LIB)。
- SONGS=3 首 AdLib 譜(11 軌/首);STANDARD.BNK 樂器庫。
- HAN.EXE:MCGA 13h;兩組調色盤於 runtime 0x19CB:0x1F4E/0x224E;固定段自載(entry 待動態驗證)。

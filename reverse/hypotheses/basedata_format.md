# basedata_format.md — BASEDATA.001 遊戲資料

## H1: BASEDATA.001 是遊戲靜態主資料庫(地圖/郡縣/人名等)

- **Evidence**:
  - 內含大量連續 Big5 郡縣名:遼東、遼西、北平、漁陽、上谷、雁門、九原、鉅鹿、太原、北地、琅琊、邯鄲、上黨、河東、內史、隴西、九江、泗水、三川、會稽、穎川、南陽、漢中、閩中、黔中、南海、桂林、…(另見 `食其`)
  - 開頭為結構化數值:`41 43 1A 00 02 01 04 06 05 07 03 09 08 00 FF FF FF FF FF FF 01 0A 00…`
  - 大小 11,376;entropy 5.52(半結構化)
- **Tests Performed**: Phase 1 Big5 strings、hex、entropy
- **Result**: 確認為中文資料檔;細部格式未解
- **Confidence**: PROBABLE(用途)
- **Next Test**: 找 HAN.EXE 讀取 BASEDATA.001 的 INT 21h open/read/lseek 與其長度;以 fixed-size record 搜尋重複結構

## H2: 包含固定長度 record(郡/勢力/武將)與字串表

- **Evidence**: 字串(郡名)長度不一 → 後端應有 string table;但尚未定位
- **Tests Performed**: 目視
- **Result**: 未解
- **Confidence**: HYPOTHESIS
- **Next Test**: 分析 0x41 0x43 開頭是否為 header/version/偏移表;對齊試算 record size

## Phase 2 Update(2026-09)
- [VERIFIED] 版面:
  - 城市表: `0x0540` 起,39 筆 × 0x30,名 4B(Big5,空白補足)。
  - 人物表: `0x0C90` 起,255 筆 × 0x20,名 8B(Big5,空白補足)→ 項羽、劉邦、…、張良、范增…。
- [VERIFIED] 工具: `basedata_analyzer.py`;輸出 `dumps/basedata/cities.txt`、`characters.txt`。
- [UNKNOWN] 屬性欄位語意(需 EXE 讀檔/計算邏輯交叉)。
- 分析報告: `reports/basedata_analysis.md`。

## 待辦 (Next)
1. HAN.EXE 內定位 BASEDATA.001 之 open/read/lseek 與長度常數(0x2C70?),對齊欄位語意。
2. 解屬性編碼(疑含對稱/簡易加密或位元欄位)。


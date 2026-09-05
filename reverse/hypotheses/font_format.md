# font_format.md — 字型格式初步假設

## H1: YING.PAT = 128 glyph × 16 bytes = 8×16 bitmap 字型

- **Evidence**: YING.PAT 大小 2048 = 128 × 16;16 bytes = 8px寬(每列 1 byte)× 16 列;檔頭前幾列全 0(空白字元)+ 後續出現筆畫 pattern
- **Tests Performed**: Phase 1 檔長分解與 hex(head dump YING_PAT.txt)
- **Result**: 數字吻合
- **Confidence**: PROBABLE(數字)/待圖形驗證
- **Next Test**: 依 8×16 解碼繪製 ASCII 0x20–0x7F,確認字型形狀與排列

## H2: ZHONG.PAT = 591 glyph × 32 bytes = 16×16 bitmap 中文字型

- **Evidence**: 18912 = 591 × 32;32 bytes = 每列 2 bytes × 16 列;檔頭可見筆畫位元型態(如 `02 80 02 80 04 40…` 具對稱筆畫)
- **Tests Performed**: 檔長分解;hex(ZHONG_PAT.txt head)
- **Result**: 數字吻合
- **Confidence**: PROBABLE(數字)/待圖形驗證
- **Next Test**: 用 16×16@32B 解碼輸出 PNG,比對是否為中文字形(含 Big5 常用字)

## H3: ZHONG.COD = 與 ZHONG.PAT 對應的對照資料(591 × 2 bytes)

- **Evidence**: 1182 = 591 × 2,glyph 數與 ZHONG.PAT 相同;內容為 2-byte 序列(候選:Big5 code 或內部字碼)
- **Tests Performed**: 檔長分解;Big5 掃描結果混亂、無法直接當文字讀
- **Result**: 未確認語意
- **Confidence**: HYPOTHESIS
- **Next Test**: 逐 2-byte 與 Big5 編碼範圍(lead 0x81–0xFE)比對;與 YING/ZHONG.PAT glyph 順序、HAN.EXE 字串繪製呼叫交叉驗證

## Phase 2 Update(2026-09)
- [PROBABLE] 檔案大小分解確認:ZHONG.PAT=591×32、YING.PAT=128×16、ZHONG.COD=591×2。
- [VERIFIED] 工具已可輸出字形 sheet PNG(`dumps/font/ying_8x16.png`、`zhong_16x16.png`)。
- [HYPOTHESIS] ZHONG.COD 為 2B/字之對照資料,非純 Big5 字串(語意未定)。

## Phase 2 Update #2(2026-09)— 字形對應
- [VERIFIED] YING.PAT glyph index = ASCII code:index 0x41/0x42/0x61/0x30/0x38/0x3F = 標準 A/B/a/0/8/?;
  index 0x20 = space(空白)。
- [VERIFIED] ZHONG.COD 591×u16 值全唯一(0xA1B8–0xF97D),但與 BASEDATA/HAN.EXE 文字重疊 <3% →
  其角色與 ZHONG.PAT 排序之對應仍 [UNKNOWN]。

## 待辦 (Next)
1. 目視驗證字形輸出。
2. 自 HAN.EXE 文字繪製函式反推字碼 → glyph 對應。
3. 確認 16×16 位元組序與 glyph 排序。



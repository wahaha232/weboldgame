# 字型分析 — ZHONG.PAT / YING.PAT / ZHONG.COD (Phase 2)

## 檔案分解(全為整除關係)

| 檔案 | 大小 | 分解 | 假設 |
|---|---|---|---|
| ZHONG.PAT | 18,912 | 591 × 32 B | 中文 16×16 bitmap;每 glyph 32B = 16列 × 2B/列(MSB-first 尚未定) |
| YING.PAT | 2,048 | 128 × 16 B | ASCII 8×16 bitmap;每 glyph 16B = 16列 × 1B/列 |
| ZHONG.COD | 1,182 | 591 × 2 B | 與 ZHONG.PAT 對應的 2B/字資料(語意未定) |

[PROBABLE] ZHONG.PAT 與 ZHONG.COD 的 591 = 相同數量;YING.PAT 128 glyph 正好是 ASCII 8-bit 數。

## 解碼結果(工具 `reverse/tools/font_render.py`)
- 依 16×16@32B 與 8×16@16B 解出並輸出 contact sheet PNG:
  - `dumps/font/ying_8x16.png`
  - `dumps/font/zhong_16x16.png`
- YING.PAT 開頭為空字元(0x00 為空白),字形有「邊框」規則(每字外框留白)→ 與 8×16 文字字型行為一致。

## ZHONG.COD 觀察
- 內容前 64 bytes:
  `B8 A1 F1 BF 46 AA E8 A6 5F A5 AD A5 AE BA A7 B6 57 A4 A6 A8 4E …`
- 以 2-byte 讀出之值並非等差/等距,亦非完整合法 Big5 序列 → 非「glyph offset」表;可能為
  內部字碼對照/索引(需以 HAN.EXE 繪字流程驗證)。[HYPOTHESIS]

## 待辦 (Next)
1. 目視驗證 PNG 字形是否為中文字形。
2. 找 HAN.EXE 文字輸出函式:如何由字碼 → ZHONG.COD → ZHONG.PAT。
3. 確認 16×16 位元組序(MSB/LSB)與直/橫向排列。

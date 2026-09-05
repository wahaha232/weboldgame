# 圖形分析 — PICS.GRP / PICS.IDX / FACE.GRP (Phase 2)

## 結論摘要

### PICS.IDX / PICS.GRP [VERIFIED]
- `PICS.IDX` = **17 筆 × 8 bytes**,每筆 = `uint32 start, uint32 end`(小端)。
- `PICS.GRP` = 17 張圖依序存放。每張圖容器格式相同:
  `uint16 width | uint16 height | width×height bytes 8-bit 索引色像素`
- 每張 `len = w×h + 4` 全數吻合(Phase 1 已驗證;Phase 2 再次確認)。

| # | w | h | offset | length | 推測用途(待驗證) |
|---|---|---|---|---|---|
| 0 | 160 | 288 | 0x000000 | 46084 | 背景/大圖 |
| 1 | 168 | 256 | 0x010E08 | 43012 | 背景/大圖 |
| 2 | 160 | 288 | 0x01B7B0 | 46084 | 背景/大圖 |
| 3–7 | 48 | 24 | 0x027038… | 1156×5 | 小 UI 圖 |
| 8–11 | 32 | 24 | 0x029BE0… | 772×4 | 小 UI 圖 |
| 12–16 | 80 | 128 | 0x02D900… | 10244×5 | 選單/畫面 |

### FACE.GRP [VERIFIED]
- 180,024 bytes = **78 × (4 + 48×48)** 恰整除;每張頭 `uint16 w(=48), uint16 h(=48)` + raw 索引色。
- 每張臉僅用 5–13 個色索引 → 共用調色盤、色塊風格。

### 調色盤 [VERIFIED — 定案]
- 自 DOSBox runtime 記憶體提取調色盤,經使用者目視確認 **palA** 正確:
  `dumps/pics/palA_8bit.bin`(6-bit ×4)。
- **FACE 78 張頭像與全部 17 張 PICS 均使用 palA 且目視正常 → 圖形色彩定案**。
- canonical 彩色輸出:`dumps/face_final/`、`dumps/pics_final/`(附 palette_8bit.bin、CONTACT_palA/palB 對照)。
- 原「0x1B40F 候選」與 runtime palA 內容一致(灰階漸層→彩表),現已定案。
- palB 用途未定(留檔 `dumps/pics/palB_8bit.bin`)。


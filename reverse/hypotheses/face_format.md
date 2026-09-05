# face_format.md — FACE.GRP 頭像格式

## H1: FACE.GRP 起點 `30 00 30 00` 為 width=48, height=48(u16le)

- **Evidence**: 檔頭前 4 bytes `30 00 30 00` = 48,48;其後連續 0x14(20)值像背景/邊框色索引
- **Tests Performed**: Phase 1 hex dump(dumps/hex/FACE_GRP_head.txt)
- **Result**: 未確認
- **Confidence**: HYPOTHESIS
- **Next Test**: 搜尋檔內重複的 48×48 區塊間距;找是否有內部索引表;比對人物頭像數與 HAN.EXE/BASEDATA 人名數

## Phase 2 Update(2026-09)
- [VERIFIED] FACE.GRP = **78 × (4 + 48×48)**,每張 `u16 w=48, u16 h=48 + raw 2304px`;無內部索引、無調色盤。
- 工具 `extract_face.py` 輸出 78 PNG(灰階 `dumps/face/`,候選彩 `dumps/face_color/`)。

## Phase 2 Update #3(2026-09)— 調色盤定案 [VERIFIED]
- DOSBox runtime 提取 + 使用者目視確認:**palA 正確**。
- canonical:`dumps/face_final/`、`dumps/pics_final/`;調色盤 `palA_8bit.bin`。
- 原 0x1B40F 候選與 runtime palA 內容一致 → 舊 H1(候選)升級為 VERIFIED。



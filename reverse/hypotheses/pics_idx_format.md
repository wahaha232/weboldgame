# pics_idx_format.md — PICS.IDX 索引格式

## H1: PICS.IDX = 17 × { uint32 start, uint32 end }(小端)

- **Evidence**:
  - PICS.IDX 大小 136 = 17×8
  - 每 8 bytes 內兩個 uint32 LE 值皆**單調遞增**;後值−前值 = 對應圖片長度
  - 每段長度與圖片 w×h+4 完全一致(見 graphics_format.md H1)
  - 最後一筆 end=0x44124 仍在 PICS.GRP 檔長(0x46E28)內
- **Tests Performed**: Phase 1 Python 全數比對
- **Result**: 成立
- **Confidence**: VERIFIED(內部一致);待與 EXE 讀檔邏輯交叉驗證
- **Next Test**: HAN.EXE 中尋找「開啟 PICS.IDX → 讀 N 筆 8 bytes」的 INT 21h 追蹤;測試是否為(offset,length)但 length 之語意由他處定義(暫以 end 解釋最一致)

## H2: 無獨立 palette/flag/width/height 欄位

- **Evidence**: 每筆恰 8 bytes,而 w/h 直接存在 GRP 圖片起點
- **Tests Performed**: 8-byte stride 全解
- **Result**: 與 GRP 內容吻合
- **Confidence**: PROBABLE(尚未由 EXE 驗證)
- **Next Test**: 反組譯確認讀取方式

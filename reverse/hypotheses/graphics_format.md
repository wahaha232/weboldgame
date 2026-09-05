# graphics_format.md — 圖形格式初步假設

## H1: PICS.GRP 為 8-bit palette-indexed raw bitmap,每張 = `u16le w + u16le h + raw w*h`

- **Evidence**: PICS.IDX 17 筆;從每筆起點讀 `u16 w/h`:
  - img00 w=160 h=288;img01 168×256;img02 160×288;img03-07 48×24;img08-11 32×24;img12-16 80×128
  - 每張 **len = w×h + 4 完全吻合**(46084=4+160×288 等),表示無 RLE/壓縮,純 raw pixels
- **Tests Performed**: Python 逐一比對 PICS.IDX 區間長度與 w×h(見 dumps/hex/PICS_GRP_head.txt、PICS_IDX.txt)
- **Result**: 全部 17 張吻合;為 **8-bit indexed、每像素 1 byte**
- **Confidence**: VERIFIED(結構)
- **Next Test**: 找出調色盤來源(GRP 尾段 11524 bytes 或 EXE 內建);確認每張圖對應的 palette index;輸出測試 PNG

## H2: PICS.GRP 尾部(off 0x44124–EOF, 11524 bytes)與各區間間隙含調色盤/未索引資料

- **Evidence**: EOF 至 0x46E28 剩 11524 = 4 + 15×768(768 = 256色×3)的候選;img0/1/2/11 之後存在間隙(0x5A04、0x5A4、0x2804 bytes)
- **Tests Performed**: 計算各區間起訖(Phase 1)
- **Result**: 未判定內容
- **Confidence**: HYPOTHESIS
- **Next Test**: 檢查這些區域是否為 768B×N 的 RGB(或 BGR)調色盤資料;與圖內容分布比對

## H3: 圖形為 VGA 256 色(可能 MCGA/13h 或 Mode X)

- **Evidence**: raw 每像素 1 byte 的格式、16-bit DOS 年代;附加說明 txt 提及「選 MCGA」
- **Tests Performed**: 無(Phase 1 僅觀察)
- **Result**: 未確認
- **Confidence**: HYPOTHESIS
- **Next Test**: HAN.EXE 反組譯找 VGA mode set(INT 10h AX=0013h 等)與調色盤寫入(INT 10h AX=1010h / 3C8h/3C9h)

## Phase 2 Update(2026-09)
- [VERIFIED] FACE.GRP = **78 × (4 + 48×48)**,容器同 PICS:`u16 w,u16 h,raw 8-bit`。每張僅用 5–13 色。
- [VERIFIED] PICS.GRP/FACE.GRP 檔內無調色盤。
- [PROBABLE] HAN.EXE file offset **0x1B40F 起 768B 全為 6-bit(0–63)值(灰階漸層→色彩表)**,緊鄰 `\HAN\STANDARD.BNK` 字串表之前;候選 VGA 調色盤,待 EXE code trace 確認並對應每張圖。
- 工具:`extract_pics.py`、`extract_face.py`;PNG 預覽在 `dumps/pics|face`。

## Phase 2 Update #2(2026-09)— 調色盤載入碼 [VERIFIED]
- 0x11B30 起:HAN.EXE 設 **模式 13h(MCGA 320×200×256)**,然後 INT 10h AX=1012h
  BX=0 CX=256 ES=0x19CB DX=**0x1F4E** 寫入調色盤;第二組於 DX=**0x224E**(相距 0x300)。
- 0x11B66 起:直接操作 VGA 0xA000(填色 cx=0xFA00=320×200)。
- 待辦:以 runtime 段映射把 0x19CB:0x1F4E 對回 file offset,正式重渲。


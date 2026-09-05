# save_format.md — HANSAVE.DAT 存檔格式

## H1: HANSAVE.DAT 含重複的「郡縣狀態」區塊

- **Evidence**:
  - 檔頭即為重複模式:`20 20 20 BC 42 20 20 A8 B9 20 20 A6 62 20 20 E4 68 20 20 20 00` 再三重複
    (空白分隔 + 2-byte Big5 字,疑似郡名欄位;後隨 `00`)
  - 檔案中段含與 BASEDATA.001 相同的郡名序列(泗水/三川/遼東…重複多輪)
  - 大小 45,760 = 可能是固定大小存檔(header + 郡縣/勢力表)
- **Tests Performed**: Phase 1 hex/strings
- **Result**: 確認含重複文字區塊;詳細版型未解
- **Confidence**: PROBABLE(存檔用途,依檔名與內容)
- **Next Test**: 比對多個存檔(若可得)找差異欄位;對齊 record size;找 HAN.EXE 寫檔呼叫(INT 21h AH=3Ch/40h 追蹤)與長度常數

## Phase 2 Update #2(2026-09)
- [VERIFIED] HANSAVE.DAT 含 **4 份世界狀態副本**(0x640/0x32B0/0x5F20/0x8B90,間距 0x2C70);
  每份 ≈ BASEDATA[0x540:0x2C70](城市+人物表)。
- [VERIFIED] 現況副本(#0)與 BASEDATA 差 1794B;其餘三份各差 ~300B(每城小旗標,如 +9:00→04)。
- 例:遼東 5000/2500 → 現況 3226/762(uint32 疑兵力/資源)。[HYPOTHESIS]
- 4 副本語意(#0=現況;其餘=?)、header/回合欄位 → [UNKNOWN],待 runtime。

## 待辦 (Next)
1. 第二份存檔差分。
2. HAN.EXE 寫檔 code(AH=40h @ ~0x16733)追蹤對齊欄位。
3. 4 副本意義確認。


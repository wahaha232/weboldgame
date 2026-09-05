# sound_format.md — 聲音系統初步假設

## H1: 遊戲音效系統以 AdLib FM 合成為主(待程式碼驗證)

- **Evidence**:
  - `STANDARD.BNK` 含 ASCII 簽名 **"ADLIB-"**([VERIFIED] 字串存在);大小 1024;開頭 `01 00` 後接簽名
  - `HAN.EXE` 內含 ASCII **`SOUND-DRIVER-AD-LIB`**([VERIFIED])
  - `SOUND.EXE` 內含 `SOUND-DRIVE`、`CR-A`([VERIFIED])
  - PLAY.BAT 先載 `sound b7000` 再執行 `han`
- **Tests Performed**: Phase 1 strings / magic 掃描
- **Result**: 線索一致但尚未見 `IN/OUT 0x388/0x389` 指令證據
- **Confidence**: HYPOTHESIS(傾向強)
- **Next Test**: 脫 LZ91 殼 → SOUND.EXE 反組譯找 OUT 0x388/0x389、INT 2Fh/15h hook;檢查 STANDARD.BNK 是否為標準 AdLib instrument bank 結構(每樂器 12 或 14 bytes 等);找出 HAN.EXE 對 TSR 的呼叫協定

## H2: SOUND.EXE 為 LZ 壓縮的小型常駐驅動

- **Evidence**: MZ header 後 0x1C 有 `LZ91` 標記;entropy 高(≈7.68);header 僅 2 paragraphs
- **Tests Performed**: Phase 1 header/entropy
- **Result**: 疑似
- **Confidence**: PROBABLE(需解壓確認)
- **Next Test**: 鑑別 LZ91 格式與參數(可能為自訂/商用 LZ 殼),撰寫解壓器

## H3: SONGS.GRP / SONGS.IDX 為音樂序列資料

- **Evidence**: SONGS.GRP 含 ASCII `\roll\default`(路徑/內部名?);low entropy 3.63;SONGS.IDX = 3×uint32(0, 0x196D, 0x267E)
- **Tests Performed**: Phase 1 掃描
- **Result**: 內容未定
- **Confidence**: UNKNOWN(用途猜測)
- **Next Test**: 檢查 SONGS.GRP 是否有 CMF/ROL/RDO 等音樂容器特徵;以 IDX 值切段檢視段頭;與 STANDARD.BNK 樂器數交叉比對

## Phase 2 Update(2026-09)
- [VERIFIED] STANDARD.BNK 內含 7 個具名 OPL 打擊樂器(DRUM1/CYMBAL1/HIHAT1/PIANO1/SNARE1/TOM1/TRUMPET1);+0x0C 值 28(樂器數?)。
- [PROBABLE] SOUND.EXE 含 `LZ91` 壓縮標記於 file offset 0x1C;entropy 7.68。
- [HYPOTHESIS] HAN.EXE 以名稱解析取得音效驅動服務(`_SoundCall`、`_GetSoundDrvVersion`…),並直接讀 `STANDARD.BNK`/`songs.grp`/`songs.idx`。
- [UNKNOWN] SONGS 內容格式未定(切點 0/0x196D/0x267E 待驗證)。

## Phase 2 Update #2(2026-09)— SONGS/BNK 結構
- [VERIFIED] SONGS.IDX = 3×uint32(0x0000/0x196D/0x267E)=三首歌起點,恰蓋滿。
- [VERIFIED] SONGS.GRP 每首歌含 `Tempo` + 11 軌 `Voix 0..10`,軌道樂器名與 BNK 相同
  (trumpet1/piano1/bdrum1/snare1/tom1/cymbal1/hihat1);含 IEEE float 參數。
- [UNKNOWN] 軌道音高事件之欄位語意與時值單位 → 需 SOUND.EXE 播放器。
- [VERIFIED] STANDARD.BNK 樂器名 BDRUM1/…/TRUMPET1。
- 工具:`sound_analyzer.py` → `dumps/sound/songs_overview.txt`。

## Phase 2 Update #3(2026-09)— SOUND.EXE 已解壓
- [VERIFIED] SOUND.EXE = **LZEXE 0.91** 包裝之 **Ad Lib「Sound Driver V1.51」TSR**;
  解壓 13,792B(`dumps/SOUND_unpacked.exe`;工具 `lzexe_unpack.py`)。
- [VERIFIED] TSR 掛 **INT 65h**,簽名 `SOUND-DRIVER-AD-LIB`(19B)。
- [VERIFIED] OPL 寫入副程式:base 變數(預設 0x388)→ reg/data 兩 port + IN 延遲。
- [VERIFIED] 參數選項:`b/B` 寫入 0xFFA 槽(hex 值);`p/P` 寫入 0x388 槽(疑 I/O base);`w/W` 寫入第三槽。
  `b7000`→0x7000 入 0xFFA 槽;該槽語意(buffer 大小?) [HYPOTHESIS]。
- 待辦:0x9AA 安裝邏輯解析 `[bp+4]` 語意;SONGS 事件語意仍待播放器。




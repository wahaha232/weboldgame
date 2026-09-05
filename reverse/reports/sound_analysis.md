# 聲音系統分析 — SOUND.EXE / SONGS.* / STANDARD.BNK (Phase 2 初版)

## 啟動方式([VERIFIED], 見 bat_analysis.md)
`PLAY.BAT`: `sound b7000` 然後 `han`。SOUND.EXE 為先行載入的常駐驅動。

## SOUND.EXE
- 大小 7,163;MZ header 僅 2 paragraphs;`e_crlc=0`。
- **file offset 0x1C 起有 `LZ91` 標記**,後接可辨識之 8086 stub 指令序列(計算段落、`mov ah,30h/int 21h` 等)→ [PROBABLE] 以 LZ 壓縮殼包裝的真程式。
- 內含字串 `SOUND-DRIVE`、`CR-A`;entropy ≈ 7.68。
- **待辦**: 鑑別 `LZ91` 格式並解壓(反組譯 stub 逆向解壓演算法,或查表實作)。

## STANDARD.BNK(1,024 bytes)
- 結構(已確認部分):
  - +0x02: `"ADLIB-"` 簽名([VERIFIED])
  - +0x0C: `1C 00 00 00` = 28(可能樂器數)
  - +0x10 起有 **7 個具名樂器**:`DRUM1, CYMBAL1, HIHAT1, PIANO1, SNARE1, TOM1, TRUMPET1`(皆 OPL 打擊樂名)
  - +0x1A0 起為大量小數值區(疑似 FM operator 參數);後半 ~0x270–0x3FF 為 0
- [PROBABLE] 這是 AdLib 鼓組/樂器定義檔(標準 AdLib BNK 衍生格式),詳細欄位待與 SOUND.EXE 解壓碼比對。

## SONGS.GRP / SONGS.IDX
- SONGS.IDX = 12 bytes = 三個 uint32 LE: `0x00000000, 0x0000196D, 0x0000267E`(切點候選)。
- SONGS.GRP = 13,265 bytes;含 ASCII `\roll\default`;entropy 低(3.63)。
- 以 idx 切出兩段:`[0,0x196D)` 與 `[0x196D,0x267E)`,檔尾尚有 0x0D53 bytes 未索引。
- 格式未定(可能為自訂 FM 序列;非標準 CMF/ROL 的證據待驗)。[UNKNOWN]

## HAN.EXE 側線索
- HAN.EXE 內含字串:`SOUND-DRIVER-AD-LIB`、`STANDARD.BNK`、`songs.grp`、`songs.idx`、
  `_SoundCall`、`_GetSoundDrvVersion`、`_m_sound_eff`、`_sound`、`_nosound`。
- 推測 HAN.EXE 以「名稱解析」方式向常駐音效驅動(SOUND.EXE)取得服務函式(類似
  driver API table),並直接載入 `STANDARD.BNK`/SONGS 播放。[HYPOTHESIS]

## Phase 2 Update(2026-09)— SONGS.GRP/IDX 結構已解出

- SONGS.IDX = 3 × uint32 LE = **歌曲起點**:0x0000 / 0x196D / 0x267E;
  三首歌曲長度 = 6509 / 3345 / 3411,恰蓋滿全檔。
- SONGS.GRP 每首歌 = 文字標記式 AdLib 多軌譜:
  - 檔頭 `00 00 04 00` + `\roll\default`
  - `Tempo` 標記(後接速度參數)
  - **11 軌** `Voix 0..10`,每軌含 `Timbre n`(後接樂器名)、`Volume n`、`Pitch n`
    等標記與參數(含 IEEE float,如 `00 00 80 3F`=1.0)
  - 軌道樂器名與 STANDARD.BNK 一致:`trumpet1、piano1、bdrum1、snare1、tom1、cymbal1、hihat1`
  - 音高序列:一串 u16 小端 token(候選:duration/pitch 對),事件欄位**順序語意未定** → 不臆測,
    待 SOUND.EXE 播放器 code 確認後再解碼樂譜。([UNKNOWN])
- STANDARD.BNK 具名樂器更正為 **BDRUM1/CYMBAL1/HIHAT1/PIANO1/SNARE1/TOM1/TRUMPET1**
  (前次讀取 DRUM1 為錯位誤讀)。
- 工具:`sound_analyzer.py`,輸出 `dumps/sound/songs_overview.txt`。

## Phase 2 Update #3(2026-09)— SOUND.EXE 解壓成功(LZEXE 0.91)

### 解壓
- 以自製 `tools/lzexe_unpack.py`(移植自 mywave82/unlzexe 0.9,參照 `tools/src/unlzexe.c`)解壓成功:
  **13,792 bytes**(load module 13,280;relocs 0)→ `dumps/SOUND_unpacked.exe`。
- 驗證:字串完整乾淨 → 確認為 **Ad Lib Inc.「Sound Driver V1.51」**(1987/1989)TSR。

### 內部結構 [VERIFIED]
- **TSR 掛 INT 65h**,以 19 bytes 簽名 `SOUND-DRIVER-AD-LIB` 識別(0x388 起 set/get INT 65h + 簽名比對)→ HAN.EXE 透過名稱/INT 65h 呼叫驅動(對應 HAN.EXE 內 `_SoundCall`、`_GetSoundDrvVersion` 等)。
- **OPL 暫存器寫入副程式**(0x7CE 起):`mov dx,[0x6F6]`→`out dx,al`(reg index, 預設 **0x388**)→`inc dx`→`out dx,al`(data → **0x389**);以大量 `in al,dx` 延時 → 典型 OPL2 寫法。
- base I/O 存於變數 `[0x6F6]`(0x21D8 處由 AX 寫入)。
- driver API 為中斷處理程式(0x3EE 起),函式表於 cs+0x213/0x243,依函式編號複製參數並呼叫。

### `b7000` 參數解析 [VERIFIED 語法 / UNKNOWN 語意]
- 主程式(0x471 起)解析至多 3 個命令列參數;`0x5ED` 為 **hex 字串轉 16-bit**('0-9','a-f','A-F')。
- 選項表:`'p'/'P'`→mov `[bp+6]`(預設 **0x388**,AdLib I/O base)、`'w'/'W'`→`[bp+8]`、
  `'b'/'B'`→mov `[bp+4]`(預設 **0xFFA**,且最小值 0x3E8=1000;超上限印「buffer too large」)。
- 故 `PLAY.BAT: sound b7000` → 選項 b、值 hex `7000` = **0x7000** 寫入參數 `[bp+4]`。
- `[bp+4]` 語意(疑 buffer/配置大小)→ [HYPOTHESIS],需由 0x9AA 安裝邏輯進一步確認。

### 其他字串(行為證據)
`Sound driver already installed.` / `successfully installed.` / `buffer too large!` /
`Bad eventType!` / `Bad function number.` / `Invalid option.` / `*** STACK OVERFLOW ***`。



## Phase 2 Update #4(2026-09)— STANDARD.BNK 觀察(保守)
- 0x0C 處 u32 = 28(疑筆數);檔頭含 7 筆具名樂器目錄(前綴索引值 03/05/06/04/02…依序)。
- 資料區 0x19C–0x270 含規則性 11-byte 參數組(例 `2F 0D 04 00 06 0F 00 00 00 00 00` 出現於 0x1CB/0x225/0x243)→
  疑為 OPL2 雙 operator 參數(20/40/60/80/E0 ×2 + C0 = 11 regs),**但欄位↔暫存器對應未驗證 → 不宣稱**。
- 待辦:以 HAN.EXE 樂器載入邏輯(INT 65h 呼叫)或 SOUND 播放器確認對應。


# HAN.EXE / SOUND.EXE — Phase 1 MZ Header 分析

> 本文件是 Phase 1 (FILE FORENSICS) 對兩個 DOS 可執行檔的**起始**分析,
> 只涵蓋 MZ header、magic、初始觀察與假設。完整程式逆向(分段表、反組譯、
> interrupt/port I/O、overlay、遊戲邏輯)屬於後續 Phase。
> 資料來源: `reverse/extracted/han/HAN.EXE`、`reverse/extracted/han/SOUND.EXE`。

## 1. HAN.EXE

- 大小: **133,424 bytes**; SHA-256 `e13c0e37…8796`;CRC32 `A7463EE1`。
- MZ header 欄位([VERIFIED],檔頭 byte 0x00–0x27):

| 欄位 | 值 | 說明 |
|---|---|---|
| e_magic | `4D 5A` | "MZ" |
| e_cblp | 0x016B (363) | 最後一頁位元組數 |
| e_cp | 0x00E8 (232) | 總頁數(512B) → 232×512=118,784 ≈ 檔長合理 |
| e_crlc | **0** | 重定位項目數 = 0 |
| e_cparhdr | 0x0020 (32) | 檔頭 32 paragraphs = 512 bytes |
| e_minalloc | 0 | |
| e_maxalloc | 0xFFFF | |
| e_ss | 0x1E94 | stack segment(相對) |
| e_sp | 0x0080 | stack pointer |
| e_ip | 0x0012 | entry IP(相對) |
| e_cs | 0x1BDD | entry CS(相對) |
| e_lfarlc | 0x001E (30) | relocation table 位於 0x1E(但項目數=0) |
| e_ovno | 0 | 非 overlay |

- 檔頭 0x28–0x1FF 全為 0x00;第一個非零程式碼在 **file offset 0x200**:
  `BA CB 19 | 2E 89 16 C7 01 | B4 30 | CD 21` …(mov dx,19CBh; mov cs:[01C7h],dx; mov ah,30h; int 21h …)→ 開頭即 DOS version call,典型 runtime stub 型態。
- 內嵌 ASCII(節錄):`SOUND-DRIVER-AD-LIB`、`Stack overflow!`。
  `Stack overflow!` 為 C 編譯器 runtime 訊息(常見於 Borland/Turbo C 之 `_emit__`/`__chkstk` 鏈)**[PROBABLE: 以 C 語言(可能 Borland)撰寫]**;待 Phase 2 反組譯確認 CRT 特徵(如 `__turbo`、`_8087`…)。

### HAN.EXE 異常點(Phase 1 觀察)

1. e_crlc(重定位數)=0,但 e_lfarlc 指向 0x1E(在檔頭內),非典型連結產物。
2. e_cparhdr=512 bytes 而多數 1990 年 16-bit 遊戲連結器輸出為 0x20~0x200;此處頭後大片 0。
3. e_csum = 0, e_ovno = 0。
4. 檔案時間戳 1998-11-28(與同 RAR 內 1990 年代檔案不同)。

以上與附加攻略.txt 所言「HAN.EXE 曾有 COPYLOCK 保護、有人提供破解 patch」可互相對照,但**不可直接當結論**。
[HYPOTHESIS] HAN.EXE 可能經加殼/保護或破解加工(移除重定位、填入 stub);Phase 2 需驗證:載入段配置、0x200 起 stub 是否為解壓/解碼迴圈、entry 流程,並判斷真實程式區塊位置。

## 2. SOUND.EXE

- 大小: **7,163 bytes**; SHA-256 `37389c49…bd757`;CRC32 `C2E10BF6`。
- MZ header 欄位([VERIFIED]):

| 欄位 | 值 | 說明 |
|---|---|---|
| e_magic | `4D 5A` | "MZ" |
| e_cblp | 0x01FB (507) | 最後一頁位元組數 |
| e_cp | 0x000E (14) | 14 頁 |
| e_crlc | **0** | 重定位數 0 |
| e_cparhdr | **0x0002 (2)** | 檔頭僅 32 bytes |
| e_minalloc | 0x0E89 | |
| e_maxalloc | 0xFFFF | |
| e_ss | 0x0366 | |
| e_sp | 0x0080 | |
| e_ip | 0x000E | entry IP |
| e_cs | 0x01A8 | entry CS |
| e_lfarlc | 0x001C (28) | relocation table 位置(項目數=0) |

- file offset **0x1C** 起 4 bytes = `4C 5A 39 31` = **"LZ91"**([VERIFIED] 標記存在)。
- 其後緊接看似 8086 指令序列:`B8 BA 25 | 05 10 00 | B1 04 | D3 E8 | 8C CB | 03 C3 | 8E D8 | 8E D0 | BC 20 0F | FB | B4 30 | CD 21`…(mov ax,25BAh; add ax,10h; shr ax,4; mov bx,cs; add ax,bx; mov ds,ax; mov ss,ax; mov sp,0F20h; sti; mov ah,30h; int 21h …)→ 解壓 stub 正在計算/設定解壓後 segment。
- 內嵌 ASCII(節錄):`SOUND-DRIVE`、`CR-A`。
- entropy ≈ 7.68(接近隨機,高)。

[HYPOTHESIS/PROBABLE] SOUND.EXE 是以 **LZ 壓縮殼("LZ91")包裝的小型 TSR(常駐音效驅動)**,真實音效程式需解壓後才可見。
Phase 2 待辦:辨識 LZ91 格式 → 寫解壓器(保留到 `reverse/dumps/`)→ 反組譯 → 找 `IN/OUT` 0x388/0x389、INT 2Fh/INT 15h hook、參數 `b7000` 的解析程式碼。

## Phase 2 Update(2026-09)— 程式結構關鍵發現

### 1. 檔案 I/O 包裝已定位
- **0x168AA 起為 fopen 包裝函式**(16-bit MS-C 大模式):
  - 0x1643F 起:`'r'/'w'/'a'/'+'` 開檔模式字串解析器
  - 0x168AA:`lds dx,[bp+6]; mov ah,3Dh; int 21h`(唯一 `AH=3Dh` 位置)
  - handle 表位於 `[bx + 0x2ACC]`(0x2ACC 起,每 handle 1 word)
- `int 21h` 集中於兩區:stub 0x200–0x9C0 與主程式 **0x1278E–0x17798**。
- AH=40h(寫檔)於 0x9BE、0x16733;對應 save 寫出邏輯。

### 2. 固定段落常數(重要異常)
- stub 中 `mov dx,0x19CB; mov cs:[0x1C7],dx` → `mov ds,dx`(DS=0x19CB)並對 `[0x77..0x91]` 寫入 PSP 資訊;
  之後 `mov es, cs:[0x1c7]` 清 BSS → 表示**假定資料段落位於固定絕對段 0x19CB**。
- 主程式到處 `lcall 0x16AE,0x0D`、`lcall 0x175E,1`、`lcall 0x15D7,7` 等固定段呼叫。
- entry CS:IP=0x1BDD:0x0012 對應 file offset 0x1BDE2 反組譯不成 code(疑為資料/被竄改)。
- 結論[HYPOTHESIS]:本 HAN.EXE 為「破解/加工版」,大量位址以固定段寫死,依賴特定載入位置;
  **靜態無法可靠定錨真實 entry**,需:獲得未加工版、或 DOSBox 動態除錯(紀錄 CS:IP 起始)、
  或逆向小 stub(0x200)以推導實際基底。

### Phase 2 Update #2(2026-09)— 顯示/調色盤程式碼已定位

### 視訊初始化(0x11B30 起)[VERIFIED]
- 0x11B34 `mov ax,0x13; int 10h` → **模式 13h (MCGA 320×200×256)**。
- 0x11B39-0x11B4A:
  `mov ax,0x19CB; mov es,ax; mov ax,0x1012; mov bx,0; mov cx,0x100; mov dx,0x1F4E; int 10h`
  → INT 10h AX=1012h 寫入 **256 色調色盤**,資料位址 = **ES:0x19CB:DX=0x1F4E**。
- 第二組調色盤於 **DS(0x19CB):0x224E**(與 0x1F4E 相距 0x300=768 bytes);切換函式在 0x11EE1。
- 0x11B4C..:以 320(=0x140) 步進填 200 列(螢幕線性位址計算,0xA000)。
- 0x11B66..:`es=0xA000, di=0, cx=0xFA00(=320×200)` 整頁填色 → 直接操作 VGA memory。
- 0xC25E 另有 AX=1010h(單一 DAC 寫入)之包裝(以間接 int 呼叫)。

### 解讀
- 遊戲以 **MCGA 256 色直接寫 VGA**(0xA000),印證 攻略/說明.txt 所述「選 MCGA」。
- 調色盤資料位於 runtime「固定資料段 0x19CB」內 offset 0x1F4E 與 0x224E(各 768B)。
- 因該 EXE 採「固定段自載」配置,上述段 offset **無法直接換算 file offset**;
  目前靜態候選調色盤(0x1B40F 起之 6-bit 表)與此相符程度待 runtime 映射驗證。
### 3. 資料段內嵌(檔案 offset)
- 檔名表:0x19EB0 起(`ying.pat/zhong.pat/zhong.cod/PICS.IDX/PICS.GRP/FACE.GRP/hansave.dat/basedata.001`…)
  與 0x1BA11 起(`\HAN\STANDARD.BNK`、`songs.grp`、`songs.idx`)。
- Sound API 名稱表 ~0x1F023 起(`_save_game`、`_hum_save_game`、`_SoundCall`、
  `_GetSoundDrvVersion`、`_m_sound_eff`、`_sound`、`_nosound`、`_ffsave`、`_fpicsidx`)。
- 候選調色盤 0x1B40F 起(768B 6-bit)。
- 檔尾(超過 MZ 宣告長度 0x1CF6B 之 0x1CF6B–0x20930 段)→ 可能為遊戲自行讀取的附加資料/overlay;待查。




# BAT / 啟動流程分析 —《楚漢之爭》(Phase 1)

> 資料來源: `reverse/extracted/han/INSTALL.BAT`、`reverse/extracted/han/PLAY.BAT`
> 以及附加檔 `reverse/dumps/text/說明.txt`(DOSBox 執行說明,非遊戲原始檔)。
> 證據分級: [VERIFIED] [PROBABLE] [HYPOTHESIS] [UNKNOWN] [REJECTED]

## 1. INSTALL.BAT

- 大小: 339 bytes; DOS CRLF 行尾;純 ASCII(Big5 字元未出現)。
- 檔案實際內容(逐位元組讀出):

```bat

echo off
echo                Install to drive C:

echo            *** Insert Han Disk #1 in Drive A: ***
pause
c:
cd\
md han
cd han
copy a:*.*

echo            *** Insert Han Disk #2 in Drive A: ***
pause
copy a:*.*

echo To play type:       c:
echo                     cd\han
echo                     play

```

[VERIFIED] 結論:
- 此遊戲發行時為**多磁片**(至少 Disk #1 / Disk #2),安裝目的固定為 **`C:\han`**(根目錄下的 han 目錄,非任意子目錄)。
- 安裝只做 `md han` + `copy a:*.*`,未做任何記憶體、音效卡或 EMM/XMS 設定。
- 最後提示啟動指令: `c:` → `cd\han` → `play`(即執行 `PLAY.BAT`)。

## 2. PLAY.BAT

- 大小: 29 bytes;內容(逐位元組):

```bat
@echo off
sound b7000
han
```

[VERIFIED] 結論:
- 啟動順序: **先執行 `SOUND.EXE`(呼叫檔名縮寫 `sound`)帶參數 `b7000`,再執行 `HAN.EXE`**。
- 沒有 himem.sys / emm386 / memmaker / 任何環境變數設定;`HAN.EXE` 直接在 DOS 常規記憶體中啟動。

### 「sound b7000」參數的意義 — 目前狀態 [UNKNOWN]

依規則不得直接假設 `b7000` 是記憶體位址。Phase 1 的觀察與待辦:
- [VERIFIED] `SOUND.EXE` 是 DOS MZ 可執行檔;檔案很小(7163 bytes),且檔頭後 0x1C 起有 `LZ91` 標記(疑為 LZ 壓縮/自解殼),原始程式需先脫殼才可見。
- [VERIFIED] `SOUND.EXE` 內含 ASCII:`SOUND-DRIVE`、`CR-A`。
- [VERIFIED] `HAN.EXE` 內含 ASCII:`SOUND-DRIVER-AD-LIB` 與 C runtime 訊息 `Stack overflow!`。
- [HYPOTHESIS] `b7000` 可能是要求 SOUND.EXE(TSR 型音效驅動)載入到某記憶體段(如 B700h),或設定其 I/O/中斷參數。此假設**尚未驗證**,Phase 2 需:脫殼 SOUND.EXE → 反組譯參數解析 → 找 `IN/OUT`(0x388/0x389 AdLib 或 0x220…SB)與 INT 21h/INT 2Fh hook → 交叉比對 HAN.EXE 對該 TSR 的呼叫協定。
- [HYPOTHESIS] `SOUND-DRIVER-AD-LIB` 字串與 `ADLIB-` 音色庫(`STANDARD.BNK`)互相呼應,可能整套聲音系統以 **AdLib FM 合成**為主;待用程式碼證據確認。

## 3. 執行環境需求(來自附加說明,非 binary evidence)

`說明.txt`(Big5)內容為 DOSBox 0.63 的操作說明:
```
mount c c:\
c:
cd han
play
```
`讀我.txt` 寫「必須解到 c:\HAN」。這些與 INSTALL.BAT 的 `C:\han` 目標一致 [PROBABLE]。

## 4. 其他觀察

- HAN.EXE / PLAY.BAT 的 RAR 內時間戳為 **1998-11-28**,其餘遊戲檔為 1990-11 ~ 1994-10;附加 txt 檔為 2002–2005。
- 攻略.txt(附加,非原始遊戲檔)提到「若當機先拿掉 SOUND 指令再進遊戲選 MCGA 及 N」以及 COPYLOCK/破解位元組(`3B 06 60 37 74 11 → EB`)。此為**第三方文字**,Phase 1 不採信為程式事實,但保留為待驗證線索,並可解釋為何 HAN.EXE/SOUND.EXE 的 MZ header 呈現異常(見 han_exe_analysis.md)。

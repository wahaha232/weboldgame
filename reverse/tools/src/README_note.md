# src 來源說明

- `unlzexe.c` / `unlzexe_README.md`:由 **mywave82/unlzexe (Ver 0.9)** 取得
  (GitHub, https://github.com/mywave82/unlzexe),用於本專案解 LZEXE 0.90/0.91 壓縮檔。
  原作者註記為 freeware(v0.5 PC-VAN UTJ44266 Kou, 歷經 v0.6-0.9 多位作者)。
- `tools/lzexe_unpack.py` 為上述程式碼之 Python 移植,僅用於 SOUND.EXE 分析(靜態、唯讀)。
- 解壓結果以 binary 內容自行驗證(MZ header、字串 `SOUND-DRIVER-AD-LIB`、`Sound driver V1.51 (C) Ad Lib Inc.` 等)。

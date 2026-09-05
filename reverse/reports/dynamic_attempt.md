# DOSBox 動態驗證嘗試紀錄

日期:2026-09 | 工具:DOSBox-X 2026.09.01(`C:\DOSBox-X\dosbox-x.exe`,winget 安裝)

## 作法
1. 遊戲複製至 `reverse/work/han/`(避免寫入 extracted 原始檔)。
2. `auto.conf`:`mount c <work>` → `cd han` → `play`。
3. 背景啟動 + 12–20 s 後以 `scan_dosbox_mem*.py` 掃描行程記憶體找已知簽名
   (`basedata.001`、`PICS.GRP`、`hansave.dat`、`SOUND-DRIVER-AD-LIB`、郡名 big5、`AC\x1A`…)。

## 結果(誠實記錄)
- DOSBox-X 在 8 s 時存活;~20 s 內自行結束(即使 autoexec 尾接無限迴圈批次,
  且 `play` 從未返回(無 `done.txt` 標記))→ 退出為模擬器/視窗環境層面,非遊戲完成。
- 存活期間掃描 4.4 億 bytes:未見任何遊戲資料檔名/內容/聲音驅動字串於 guest 記憶體;
  唯一重複命中為 `41 43 1A 00` 三處(位址間距 0x1F9,疑為 DOSBox 內部資料,非 BASEDATA)。
- 未取得遊戲畫面/文字(視窗內容無法於此自動環境讀取)。

## 更新 #1(DOSBox 0.74 動態,2026-09)
- 改用 **DOSBox 0.74-3**(`C:\Program Files (x86)\DOSBox-0.74-3\`)。它能穩定持續執行(不像 DOSBox-X ~20s 自退)。
- 讀取 guest 記憶體(ReadProcessMemory)發現:
  - SOUND driver 已常駐(host 0x139c6c19 起可見 `SOUND-DRIVER-AD-LIB` 簽名與程式碼、`Sound driver V1.51…` 字串)。
  - HAN.EXE 正開啟資料檔:記憶體含 `\han\basedata.001\0rb\0A:basedata.001\0rb\0`、`BASEDATA.001`、`PICS.GRP`、`FACE.GRP`、`ZHONG.PAT`、`YING.PAT`、`hansave.dat` 等檔名與檔案物件頭。
  - 宿主 0x4756FC0 起含**整份 HAN.EXE 映像副本**:檔案 offset X ↔ host R+X 完全吻合(例 basedata.001@0x1A06B→0x477102B;候選調色盤@0x1B40F→0x47723CF)。
  - **結論**:此 HAN.EXE 在 DOSBox 0.74 可正常啟動(SOUND→HAN 流程可行);先前「MZ entry 指向資料 ⇒ 無法啟動」之靜態推論與動態事實矛盾 → 須再研究 DOS 載入細節(DOSBox 對 e_cs/e_ip 的處理或 PSP 基準)。
  - 調色盤簽名(2,2,2,4,…)另現於 0x139ECBE1(疑 guest conventional 區);guest conventional 基底 B 尚未定出,故「DS=0x19CB:0x1F4E ↔ file offset」仍未映射。
- 待辦(動態):定出 B → 直接讀取 runtime 調色盤與 DS 區;送鍵推進遊戲到載入 BASEDATA/圖形畫面;以 B8000/畫面內容校正。


## 更新 #2(2026-09)— Runtime 調色盤已提取
- 於 DOSBox 0.74 guest 記憶體(host 0x13A1FBE1;另檔案映像複本 0x47521D7)找到兩組連續調色盤表:
  - **palA**(疑 DS:0x1F4E):768B 全為 6-bit(≤63);idx0=(2,2,2)、idx0x14=(16,16,63) 藍、idx0xA6 膚色 → 疑頭像/主要調色盤。
  - **palB**(疑 DS:0x224E):另一張(idx0=(17,17,13) 等)。
- 輸出:`dumps/pics/palA_8bit.bin`、`palB_8bit.bin`、`runtime_pal_a/b_1.bin`。
- 重渲:`dumps/face_runtimeA/`、`dumps/pics_runtimeA/`、`dumps/pics_runtimeB/`(供目視確認)。
- 待辦:目視比對 A/B 於各圖的正確性 → 定案每圖調色盤後正式渲染。


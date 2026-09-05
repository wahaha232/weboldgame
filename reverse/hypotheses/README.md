# Hypotheses —《楚漢之爭》Phase 1 初步假設資料庫

> 本目錄記錄所有「格式/機制」層面的假設。每項記錄依循:
> **Hypothesis → Evidence → Tests → Result → Confidence → Next Test**
>
> 證據分級([定義] 依任務規則):
> - **[VERIFIED]** 有直接 binary / assembly / runtime 證據
> - **[PROBABLE]** 多項證據支持,尚未完全確認
> - **[HYPOTHESIS]** 目前合理推測
> - **[UNKNOWN]** 無法判斷
> - **[REJECTED]** 原先假設經分析證明錯誤

| 文件 | 主題 | 狀態 |
|---|---|---|
| [graphics_format.md](graphics_format.md) | PICS.GRP/PICS.IDX/FACE.GRP 圖形格式 | PICS/FACE 結構已驗證;調色盤候選 |
| [pics_idx_format.md](pics_idx_format.md) | PICS.IDX 索引格式 | (start,end)×17 已驗證 |
| [face_format.md](face_format.md) | FACE.GRP 頭像格式 | 78×(4+48×48) 已驗證 |
| [font_format.md](font_format.md) | ZHONG.PAT/YING.PAT/ZHONG.COD 字型 | 大小分解 PROBABLE |
| [sound_format.md](sound_format.md) | SOUND.EXE/SONGS.*/STANDARD.BNK | BNK/SONGS 結構已驗證;LZ91 待解壓 |
| [basedata_format.md](basedata_format.md) | BASEDATA.001 | 城市/人物表版面已驗證 |
| [save_format.md](save_format.md) | HANSAVE.DAT 存檔 | 初步 |
| [game_logic.md](game_logic.md) | 遊戲規則/流程 | 僅第三方參考(未驗證) |

> 完整匯整見 `reports/reverse_engineering_spec.md`(規格草稿)。


各文件內含欄位:Hypothesis | Evidence | Tests Performed | Result | Confidence | Next Test。

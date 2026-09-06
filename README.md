# DOS CLASSIC GAMES — Retro DOS Web Platform

「1990～2000 年代 DOS 經典遊戲 Web 平台」。
透過 Browser-based DOS Emulator（WebAssembly + Canvas）在瀏覽器中執行合法取得的原版 DOS 遊戲。

> The platform is designed for legally obtained classic DOS software and games.

## 已整合功能
- `index.html` — Retro DOS 首頁(Header / DOS Emulator / Available Games / Footer)
- `style.css` — Windows 95/98 + MS-DOS 風格(bevel 框、深藍標題列、CRT 輕量 scanline)
- `js/i18n.js` + `js/main.js` — 三語切換(繁體中文 / English / Español)
- **js-dos v7 Emulator 整合**(`js-dos@7.1.3`)
  - Emulator loader/css 來自 jsdelivr CDN(版本固定)
  - `wdosbox.js` / `wdosbox.wasm` 為 js-dos 7.1.3 dist 的本機副本(js-dos runtime 以頁面相對路徑載入,GitHub Pages 子路徑可用)
  - 遊戲 bundle 為 `.jsdos`(zip,含 `.jsdos/dosbox.conf` + `.jsdos/jsdos.json`),由 `games/*.jsdos` 提供
- 控制列:PLAY / FULLSCREEN / SOUND / RESET(PLAY 於執行中切換 PAUSE/RESUME)
- Emulator lifecycle:IDLE → LOADING → RUNNING/PAUSED → ERROR,單一 instance,切換遊戲時完整釋放
- 錯誤處理:`GAME LIST ERROR` / `DOS GAME ERROR` / `EMULATOR ERROR` 顯示於 overlay,console 留下 `console.error`

## 遊戲清單(資料驅動)
新增遊戲時 **只需要**:
1. 放入遊戲 bundle:`games/<name>.jsdos`
2. 於 `games/games.json` 增加一筆 entry

```json
{
  "games": [
    {
      "id": "han",
      "title": "楚漢相爭",
      "titles": { "zh": "楚漢相爭", "en": "Chu-Han Contest", "es": "La Disputa Chu-Han" },
      "bundle": "games/han_v4.jsdos",
      "status": "available"
    }
  ]
}
```

不需要修改 `index.html` / `js/main.js`。

## 遊戲檔案原則
- 遊戲維持原始 DOS 程式,不重寫、不轉 HTML5、不反編譯。
- 放入遊戲前需確認合法使用權。

## 本機執行
```
cd D:\VS CODE\PROJECT\weboldgame
python -m http.server 8000
```
開啟 http://127.0.0.1:8000/

## GitHub Pages
- 靜態站,資源皆以相對路徑引用,可在 `/weboldgame/` 子路徑運作。
- `robots.txt`、`sitemap.xml`、SEO/OG meta 已保留。


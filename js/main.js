/* js/main.js - DOS CLASSIC GAMES web platform
 * language switch, data-driven game list, js-dos v7 emulator lifecycle.
 * Emulator stack:
 *   js-dos.js      -> https://cdn.jsdelivr.net/npm/js-dos@7.1.3/dist/js-dos.js
 *   js-dos.css     -> https://cdn.jsdelivr.net/npm/js-dos@7.1.3/dist/js-dos.css
 *   wdosbox.js/wasm -> local copies of js-dos 7.1.3 dist (fetched by js-dos at runtime)
 *   .jsdos bundles -> games/<game>.jsdos (loaded through emulators pathPrefix="")
 */
(function () {
  "use strict";

  var KEY = "dosclassic-lang";
  var JS_URL = "https://cdn.jsdelivr.net/npm/js-dos@7.1.3/dist/js-dos.js";
  var CSS_URL = "https://cdn.jsdelivr.net/npm/js-dos@7.1.3/dist/js-dos.css";
  var GAMES_URL = "games/games.json";

  /* ---------------- emulator session state ----------------
   * idle -> booting -> running -> (paused) -> running
   * any of the above can fall to error.
   */
  var state = "idle";       // idle | booting | running | paused | error
  var selected = null;      // current selected / loaded game object
  var gamesCache = [];      // parsed games.json list
  var player = null;        // single DosInstance
  var ci = null;            // CommandInterface of running session
  var soundOn = true;
  var assetsPromise = null; // cached emulator asset loader promise
  var bootOverlay = null;
  var currentGame = null;   // game object of the running session
  var busyToken = 0;

  /* ---------------- small dom helpers ---------------- */
  function $(id) { return document.getElementById(id); }

  function setText(el, txt) { if (el) el.textContent = txt; }

  function langOf() {
    try { var v = localStorage.getItem(KEY); if (v && I18N[v]) return v; } catch (e) {}
    var h = (navigator.language || "zh").toLowerCase();
    if (h.indexOf("es") === 0) return "es";
    if (h.indexOf("en") === 0) return "en";
    return "zh";
  }

  function tr(lang, k) { var d = I18N[lang] || I18N.zh; return d[k] || I18N.zh[k] || k; }

  function gameTitle(g, lang) { return (g.titles && g.titles[lang]) || g.title || g.id || ""; }

  /* ---------------- lazy emulator assets (once) ---------------- */
  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = function () { reject(new Error("script load fail: " + src)); };
      document.head.appendChild(s);
    });
  }

  function loadCss(href) {
    return new Promise(function (resolve, reject) {
      var l = document.createElement("link");
      l.rel = "stylesheet";
      l.href = href;
      l.onload = resolve;
      l.onerror = function () { reject(new Error("css load fail: " + href)); };
      document.head.appendChild(l);
    });
  }

  function ensureEmulatorAssets() {
    if (!assetsPromise) {
      assetsPromise = Promise.all([loadScript(JS_URL), loadCss(CSS_URL)])
        .then(function () {
          if (typeof window.Dos !== "function") throw new Error("Dos global not found");
          if (window.emulators) window.emulators.pathPrefix = "";
          return window.Dos;
        })
        .catch(function (err) {
          assetsPromise = null; // allow retry on next user action
          throw err;
        });
    }
    return assetsPromise;
  }

  /* ---------------- screen / status UI ---------------- */
  function screenEl() { return $("screen"); }

  function idleArtVisible(show) {
    var s = screenEl();
    if (!s) return;
    if (show) s.classList.remove("dos-active");
    else s.classList.add("dos-active");
  }

  function buildScreenHost() {
    var s = screenEl();
    if (!s) return null;
    s.innerHTML = "";
    idleArtVisible(false);
    var host = document.createElement("div");
    host.id = "emulatorHost";
    s.appendChild(host);
    return host;
  }

  function setBootStatus(lines) {
    var s = screenEl();
    if (!s) return;
    if (bootOverlay) { bootOverlay.remove(); bootOverlay = null; }
    if (!lines || !lines.length) return;
    var ov = document.createElement("div");
    ov.className = "bootOverlay";
    var pre = document.createElement("pre");
    pre.className = "bootLines";
    pre.textContent = lines.join("\n");
    ov.appendChild(pre);
    s.appendChild(ov);
    bootOverlay = ov;
  }

  function hideBootStatus() {
    if (bootOverlay) { bootOverlay.remove(); bootOverlay = null; }
  }

  function focusEmulator() {
    var host = document.getElementById("emulatorHost");
    var s = screenEl();
    var el = host || s;
    if (el && el.focus) { try { el.setAttribute("tabindex", "-1"); el.focus({ preventScroll: true }); } catch (e) {} }
  }

  /* ---------------- error overlay ---------------- */
  function showError(code, detail) {
    state = "error";
    hideBootStatus();
    var err = $("errorScreen");
    if (!err) { console.error("[dos] " + code + " " + detail); return; }
    err.classList.remove("hidden");
    var pre = $("errCode");
    if (pre) pre.textContent = code + "\n|\nUnable to start game.\nPossible causes:\nGame files missing / Emulator failed";
    var det = $("errDetail");
    if (det) det.textContent = detail || "";
    console.error("[weboldgame]", code, detail);
    updateControls();
  }

  function hideError() {
    var err = $("errorScreen");
    if (err) err.classList.add("hidden");
    if (state === "error") { state = "idle"; updateControls(); }
  }


  /* ---------------- emulator lifecycle ---------------- */
  function disposeSession() {
    busyToken++;
    if (bootOverlay) { bootOverlay.remove(); bootOverlay = null; }
    var oldPlayer = player;
    var oldCi = ci;
    player = null;
    ci = null;
    currentGame = null;
    if (oldPlayer && oldPlayer.stop) {
      try { oldPlayer.stop().catch(function () {}); } catch (e) {}
    } else if (oldCi && oldCi.exit) {
      try { oldCi.exit().catch(function () {}); } catch (e) {}
    }
    var s = screenEl();
    if (s) {
      var host = document.getElementById("emulatorHost");
      if (host) host.remove();
    }
  }

  function resetScreenToIdle(lang) {
    disposeSession();
    var s = screenEl();
    if (!s) return;
    s.innerHTML = "";
    idleArtVisible(true);
    var p = document.createElement("div");
    p.className = "prompt";
    p.textContent = tr(lang, "prompt_line1");
    s.appendChild(p);
    var g = document.createElement("div");
    g.className = "game";
    g.textContent = tr(lang, "prompt_line2");
    s.appendChild(g);
    var n = document.createElement("div");
    n.id = "emulatorNote";
    n.className = "note hidden";
    s.appendChild(n);
  }

  function startGame(game, lang) {
    if (!game || !game.bundle) {
      showError(tr(lang, "err_dos_game"), "game config is missing a bundle field");
      return;
    }
    if (state === "booting") return; // already starting
    disposeSession();
    selected = game;
    state = "booting";
    updateControls();

    var s = screenEl();
    if (!s) { showError(tr(lang, "err_emulator"), "screen element missing"); return; }
    var host = buildScreenHost();
    setBootStatus([tr(lang, "status_init"), tr(lang, "status_emu")]);

    var myToken = busyToken;

    ensureEmulatorAssets()
      .then(function () {
        if (myToken !== busyToken) throw new Error("aborted");
        setBootStatus([tr(lang, "status_init"), tr(lang, "status_emu"), tr(lang, "status_game")]);
        var host2 = document.getElementById("emulatorHost") || host;
        var options = {
          style: "none",
          emulatorFunction: "dosboxDirect"
        };
        var inst = window.Dos(host2, options);
        player = inst;
        setBootStatus([tr(lang, "status_init"), tr(lang, "status_emu"), tr(lang, "status_game"), tr(lang, "status_boot")]);
        return inst.run(game.bundle);
      })
      .then(function (cmd) {
        if (myToken !== busyToken) { try { cmd.exit(); } catch (e) {} throw new Error("aborted"); }
        ci = cmd;
        currentGame = game;
        if (!soundOn) { try { cmd.mute(); } catch (e) {} }
        state = "running";
        hideBootStatus();
        updateControls();
        focusEmulator();
        var frameDone = false;
        if (cmd && cmd.events && cmd.events().onFrame) {
          try {
            cmd.events().onFrame(function () {
              if (!frameDone) { frameDone = true; hideBootStatus(); updateControls(); }
            });
          } catch (e) {}
        }
      })
      .catch(function (err) {
        if (myToken !== busyToken) return; // superseded by a newer action
        console.error("[weboldgame] emulator error:", err);
        if (typeof window.Dos !== "function") {
          showError(tr(lang, "err_emulator"), String(err && err.message ? err.message : err));
        } else {
          showError(tr(lang, "err_dos_game"), String(err && err.message ? err.message : err));
        }
      });
  }


  /* ---------------- pause / resume / reset / sound / fullscreen ---------------- */
  function doPause() {
    if (state !== "running" || !ci) return;
    try { ci.pause(); } catch (e) { console.error(e); }
    state = "paused";
    updateControls();
  }

  function doResume() {
    if (state !== "paused" || !ci) return;
    try { ci.resume(); } catch (e) { console.error(e); }
    state = "running";
    updateControls();
  }

  function doReset() {
    var g = currentGame || selected;
    if (!g || state === "booting") return;
    var lang = langOf();
    startGame(g, lang);
  }

  function toggleSound() {
    soundOn = !soundOn;
    if (ci) {
      try { if (soundOn) ci.unmute(); else ci.mute(); } catch (e) { console.error(e); }
    }
    updateControls();
  }

  function isFullscreen() {
    return !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement);
  }

  function exitFullscreen() {
    if (document.exitFullscreen) return document.exitFullscreen();
    if (document.webkitExitFullscreen) return document.webkitExitFullscreen();
    if (document.mozCancelFullScreen) return document.mozCancelFullScreen();
    if (document.msExitFullscreen) return document.msExitFullscreen();
    return Promise.resolve();
  }

  function toggleFullscreen() {
    var lang = langOf();
    if (isFullscreen()) {
      exitFullscreen().catch(function (e) { console.error(e); });
      return;
    }
    var el = $("screen");
    if (!el) return;
    var req = el.requestFullscreen || el.webkitRequestFullscreen || el.mozRequestFullScreen || el.msRequestFullscreen;
    if (!req) {
      showError(tr(lang, "err_fullscreen"), "Fullscreen API is not supported by this browser.");
      return;
    }
    try {
      var r = req.call(el);
      if (r && r.catch) r.catch(function (e) { console.error("[weboldgame] fullscreen denied:", e); });
    } catch (e) {
      console.error("[weboldgame] fullscreen denied:", e);
    }
  }

  /* ---------------- i18n apply / controls ---------------- */
  function updateControls() {
    var lang = langOf();
    var bPlay = $("btnPlay"), bReset = $("btnReset"),
        bFull = $("btnFull"), bSound = $("btnSound");
    if (bPlay) {
      if (state === "running") setText(bPlay, tr(lang, "btn_pause"));
      else if (state === "paused") setText(bPlay, tr(lang, "btn_resume"));
      else setText(bPlay, tr(lang, "btn_play"));
      bPlay.disabled = (state === "booting");
    }
    if (bReset) {
      bReset.disabled = !(state === "running" || state === "paused");
      setText(bReset, tr(lang, "btn_reset"));
    }
    if (bSound) setText(bSound, soundOn ? tr(lang, "btn_sound") : tr(lang, "btn_mute"));
    if (bFull) setText(bFull, isFullscreen() ? tr(lang, "btn_full_exit") : tr(lang, "btn_full"));
  }

  function apply(lang) {
    var d = I18N[lang] || I18N.zh;
    var nodes = document.querySelectorAll("[data-i18n]");
    for (var i = 0; i < nodes.length; i++) {
      var k = nodes[i].getAttribute("data-i18n");
      if (d[k]) nodes[i].textContent = d[k];
    }
    var btns = document.querySelectorAll("[data-lang]");
    for (var j = 0; j < btns.length; j++) {
      btns[j].classList.toggle("on", btns[j].getAttribute("data-lang") === lang);
    }
    document.documentElement.lang = lang;
    var h1 = document.querySelector("h1");
    if (h1) h1.textContent = d.brand;
    if (state === "idle") resetScreenToIdle(lang);
    if (gamesCache.length) renderGames(gamesCache, lang);
    updateControls();
  }

  function saveLang(l) {
    try { localStorage.setItem(KEY, l); } catch (e) {}
    apply(l);
  }


  /* ---------------- game list (data driven, XSS safe) ---------------- */
  function renderGames(list, lang) {
    gamesCache = list || [];
    var box = $("gameList");
    if (!box) return;
    box.innerHTML = "";
    var valid = gamesCache.filter(function (g) { return g && g.id && g.bundle; });
    if (!valid.length) {
      var em = document.createElement("p");
      em.className = "errMsg";
      em.textContent = tr(lang, "err_game_list") + " — " + tr(lang, "err_load_fail");
      box.appendChild(em);
      return;
    }
    valid.forEach(function (g) {
      var card = document.createElement("div");
      card.className = "gameCard";

      var t = document.createElement("div");
      t.className = "gameTitle";
      t.textContent = gameTitle(g, lang);
      card.appendChild(t);

      var meta = document.createElement("div");
      meta.className = "gameMeta";
      meta.textContent = tr(lang, "dos_classic") + " · " + (g.status || "available");
      card.appendChild(meta);

      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "playBtn";
      btn.textContent = tr(lang, "play_now");
      btn.addEventListener("click", function () {
        startGame(g, langOf());
      });
      card.appendChild(btn);
      box.appendChild(card);
    });
  }

  function showGameListError(detail) {
    var box = $("gameList");
    if (!box) return;
    box.innerHTML = "";
    var p = document.createElement("p");
    p.className = "errMsg";
    p.textContent = I18N[langOf()].err_game_list + " — " + I18N[langOf()].err_load_fail;
    box.appendChild(p);
    console.error("[weboldgame] " + I18N[langOf()].err_game_list, detail);
  }

  function loadGames() {
    var box = $("gameList");
    var lang = langOf();
    if (box) { box.innerHTML = ""; var pl = document.createElement("p"); pl.textContent = tr(lang, "loading"); box.appendChild(pl); }
    var req = new XMLHttpRequest();
    req.open("GET", GAMES_URL, true);
    req.timeout = 15000;
    req.onreadystatechange = function () {
      if (req.readyState !== 4) return;
      if (req.status === 200) {
        try {
          var data = JSON.parse(req.responseText);
          if (!data || !Array.isArray(data.games)) throw new Error("bad games.json schema");
          renderGames(data.games, lang);
        } catch (e) {
          console.error("[weboldgame] games.json parse error:", e);
          showGameListError(e && e.message);
        }
      } else {
        showGameListError("HTTP " + req.status);
      }
    };
    req.onerror = function () { showGameListError("network error"); };
    req.ontimeout = function () { showGameListError("timeout"); };
    req.send();
  }

  /* ---------------- wiring ---------------- */
  function firstPlayableGame() {
    var list = gamesCache.filter(function (g) { return g && g.bundle; });
    return list[0] || null;
  }

  function onBtnPlay() {
    var lang = langOf();
    if (state === "running") { doPause(); return; }
    if (state === "paused") { doResume(); return; }
    if (state === "booting") return;
    var target = selected || firstPlayableGame();
    if (target) startGame(target, lang);
    else showError(tr(lang, "err_dos_game"), "no playable game in games.json");
  }

  document.addEventListener("DOMContentLoaded", function () {
    var lang = langOf();
    apply(lang);
    loadGames();

    var btns = document.querySelectorAll("[data-lang]");
    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener("click", function () {
        saveLang(this.getAttribute("data-lang"));
      });
    }

    var bPlay = $("btnPlay");
    if (bPlay) bPlay.addEventListener("click", onBtnPlay);
    var bReset = $("btnReset");
    if (bReset) bReset.addEventListener("click", function () { doReset(); });
    var bFull = $("btnFull");
    if (bFull) bFull.addEventListener("click", function () { toggleFullscreen(); });
    var bSound = $("btnSound");
    if (bSound) bSound.addEventListener("click", function () { toggleSound(); });

    var bRetry = $("btnRetry");
    if (bRetry) bRetry.addEventListener("click", function () { hideError(); });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        var err = $("errorScreen");
        if (err && !err.classList.contains("hidden")) { hideError(); e.preventDefault(); return; }
        if (isFullscreen()) { exitFullscreen(); }
      }
    });
    document.addEventListener("fullscreenchange", function () { updateControls(); });
    document.addEventListener("webkitfullscreenchange", function () { updateControls(); });
  });

  /* small diagnostic hook (not required by the UI) */
  window.__weboldgame = {
    getState: function () { return state; },
    getSelected: function () { return selected; },
    getCi: function () { return ci; },
    getSound: function () { return soundOn; }
  };
})();


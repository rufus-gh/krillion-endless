// Multiplayer: rooms, lobby, synced rounds and scoreboards, backed by Supabase.
// Room state lives in Postgres; every write goes through a database function (see supabase/schema.sql).
(() => {
  "use strict";
  const K = window.Krill;
  const cfg = window.KRILLION_CONFIG;
  const PROMPTS = window.KRILLION_PROMPTS;
  const $ = (id) => document.getElementById(id);
  const esc = K.escapeHtml;
  const ACTIVE_MS = 25000;
  const TIER_RANK = { gem: 6, deepCut: 5, rare: 4, schooler: 3, tooClever: 2, plankton: 1 };

  const ui = {
    mpBtn: $("mpBtn"),
    home: $("screenMp"), lobby: $("screenLobby"), board: $("screenBoard"), final: $("screenFinal"),
    name: $("mpName"), linkJoin: $("linkJoin"), linkJoinCode: $("linkJoinCode"),
    joinForm: $("joinCodeForm"), joinCode: $("joinCode"), createForm: $("createForm"), roomName: $("roomName"), roomPass: $("roomPass"),
    roomList: $("roomList"), refreshRooms: $("refreshRooms"), error: $("mpError"), back: $("mpBackBtn"),
    lobbyEyebrow: $("lobbyEyebrow"), lobbyName: $("lobbyName"), shareLink: $("shareLink"), copyLink: $("copyLink"), shareHint: $("shareHint"),
    lobbyCount: $("lobbyCount"), lobbyPlayers: $("lobbyPlayers"), start: $("mpStartBtn"), lobbyWait: $("lobbyWait"), lobbyLeave: $("lobbyLeave"),
    progress: $("mpProgress"), resultWait: $("resultWait"),
    boardEyebrow: $("boardEyebrow"), boardPrompt: $("boardPrompt"), boardBest: $("boardBest"), boardList: $("boardList"), boardNext: $("boardNext"), boardWait: $("boardWait"),
    finalWinner: $("finalWinner"), finalStandings: $("finalStandings"), finalLog: $("finalLog"), again: $("mpAgainBtn"), finalLeave: $("finalLeave"), finalWait: $("finalWait"),
    pwDialog: $("pwDialog"), pwInput: $("pwInput"), mates: $("mates"),
    lobbyModes: $("lobbyModes"), lobbyModeNote: $("lobbyModeNote"), finalModes: $("finalModes"), finalEyebrow: $("finalEyebrow"), finalRace: $("finalRace"),
  };

  const ERRORS = {
    name_required: "Pick a name first.",
    room_not_found: "There's no room with that code.",
    wrong_passcode: "Wrong password.",
    room_full: "That room is full.",
    host_only: "Only the host can do that.",
    already_playing: "The dive has already started.",
    round_closed: "Too late, that prompt has closed.",
    not_in_room: "You're no longer in that room.",
    passcode_too_long: "Passwords can be up to 32 characters.",
    bad_mode: "That mode doesn't exist.",
  };
  const errText = (e) => ERRORS[e && e.message] || "Couldn't reach the server. Try again.";

  const sb = window.supabase && cfg ? window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey, { auth: { persistSession: false } }) : null;

  // Room seat is per tab (so two tabs can be two players); a refresh keeps it.
  const seat = {
    get() { try { return JSON.parse(sessionStorage.getItem("krillion.mp")); } catch { return null; } },
    set(v) { try { v ? sessionStorage.setItem("krillion.mp", JSON.stringify(v)) : sessionStorage.removeItem("krillion.mp"); } catch {} },
  };

  async function rpc(fn, args) {
    const { data, error } = await sb.rpc(fn, args || {});
    if (error) throw new Error(error.message);
    return data;
  }

  // ---------- State ----------
  let me = null;            // { code, player_id, token, pw }
  let room = null, players = [], answers = [];
  let offset = 0;           // server clock minus local clock (ms)
  let channel = null, refreshTimer = 0, pollTimer = 0, hbTimer = 0, tickTimer = 0, browserTimer = 0, pendingPhase = 0;
  let phaseKey = "", compiled = null, landingUntil = 0, lastNudge = 0, linkPw = "";

  const MP = (window.KrillMP = { active: false, onSubmit, confirmLeave, dig: () => isDig(), tunnel: () => tunnelOf(myPlayer()) });
  const serverNow = () => Date.now() + offset;
  const isHost = () => room && me && room.host_id === me.player_id;
  const isActive = (p) => p.id === me.player_id || (!p.left_at && serverNow() - Date.parse(p.last_seen) < ACTIVE_MS);
  const activePlayers = () => players.filter(isActive);
  const myPlayer = () => players.find((p) => p.id === me.player_id);
  const answerFor = (pid, round = room.round) => answers.find((a) => a.player_id === pid && a.round === round);
  const hue = (id) => [...id].reduce((h, c) => (h * 31 + c.charCodeAt(0)) % 360, 7);

  // Dig to China race: each player's tunnel (banked by the server at the start of every dive)
  // carries over, and the first to reach the far surface wins. Totals are in points.
  const GOAL = Scene.END;
  const isDig = () => !!room && room.mode === "dig";
  const tunnelOf = (p) => (isDig() && p ? p.tunnel_pts || 0 : 0);
  const totalOf = (p) => tunnelOf(p) + p.score;
  const depthText = (pts) => K.depthLabel(isDig() ? Math.min(GOAL, pts) : pts);
  const pctOf = (pts) => Math.min(100, Math.floor((pts / GOAL) * 100));
  const nameOf = (id) => (players.find((p) => p.id === id) || {}).name;
  // Players past the far surface, furthest first (ties: who answered this prompt first).
  function brokeThrough() {
    if (!isDig()) return [];
    const at = (p) => { const a = answerFor(p.id); return a ? Date.parse(a.submitted_at) : Infinity; };
    return players.filter((p) => totalOf(p) >= GOAL).sort((a, b) => totalOf(b) - totalOf(a) || at(a) - at(b));
  }

  function showError(msg) { ui.error.textContent = msg || ""; }

  function shareUrl() {
    const u = new URL(location.href);
    u.search = "";
    u.hash = "";
    u.searchParams.set("room", me.code);
    if (me.pw) u.searchParams.set("pw", me.pw);
    return u.toString();
  }

  // ---------- Home / room browser ----------
  function openHome({ code = "", pw = "" } = {}) {
    if (!sb) { alert("Multiplayer isn't configured (see config.js)."); return; }
    linkPw = pw;
    ui.name.value = K.store.get("name", "");
    ui.joinCode.value = code;
    ui.linkJoin.classList.toggle("hidden", !code);
    ui.linkJoinCode.textContent = code;
    showError("");
    K.show(ui.home);
    (ui.name.value ? (code ? $("joinCodeBtn") : ui.joinCode) : ui.name).focus({ preventScroll: true });
    loadRooms();
    clearInterval(browserTimer);
    browserTimer = setInterval(() => { if (!ui.home.classList.contains("hidden")) loadRooms(); else clearInterval(browserTimer); }, 5000);
  }

  async function loadRooms() {
    try {
      const rooms = await rpc("list_rooms");
      if (!rooms.length) { ui.roomList.innerHTML = `<li class="muted">No open rooms right now. Create one!</li>`; return; }
      ui.roomList.innerHTML = rooms.map((r) => {
        const state = r.status === "lobby" ? "in lobby"
          : r.status === "finished" ? "between dives"
          : `prompt ${Math.min(r.round + 1, r.total_rounds)} of ${r.total_rounds}`;
        return `<li>
          <div class="room-main">
            <b>${esc(r.name)}</b>${r.locked ? ` <span class="pill">LOCKED</span>` : ""}${r.mode === "dig" ? ` <span class="pill dig">DIG RACE</span>` : ""}
            <span class="muted">${esc(r.host_name || "?")} · ${r.players} diver${r.players === 1 ? "" : "s"} · ${state} · ${r.code}</span>
          </div>
          <button class="small-btn" data-code="${r.code}" data-locked="${r.locked}">JOIN</button>
        </li>`;
      }).join("");
    } catch (e) {
      ui.roomList.innerHTML = `<li class="muted">${esc(errText(e))}</li>`;
    }
  }

  function getName() {
    const n = ui.name.value.trim();
    if (!n) { showError(ERRORS.name_required); ui.name.focus(); return null; }
    K.store.set("name", n);
    return n;
  }

  function askPassword() {
    return new Promise((resolve) => {
      ui.pwInput.value = "";
      ui.pwDialog.returnValue = "";
      ui.pwDialog.showModal();
      ui.pwInput.focus();
      ui.pwDialog.addEventListener("close", () => resolve(ui.pwDialog.returnValue === "ok" ? ui.pwInput.value : null), { once: true });
    });
  }

  async function join(code, pw, locked) {
    const name = getName();
    if (!name) return;
    code = code.trim().toUpperCase();
    if (!code) { showError("Enter a room code."); return; }
    if (locked && !pw) { pw = await askPassword(); if (pw == null) return; }
    showError("");
    busy(true);
    try {
      const res = await rpc("join_room", { p_code: code, p_passcode: pw || "", p_player_name: name });
      enterRoom({ code: res.code, player_id: res.player_id, token: res.token, pw: pw || "" });
    } catch (e) {
      if (e.message === "wrong_passcode") {
        if (pw) showError(ERRORS.wrong_passcode);
        const again = await askPassword();
        if (again != null) return join(code, again, true);
        return;
      }
      showError(errText(e));
    } finally {
      busy(false);
    }
  }

  function busy(on) {
    for (const b of ui.home.querySelectorAll("button")) b.disabled = on;
  }

  async function create() {
    const name = getName();
    if (!name) return;
    const pw = ui.roomPass.value.trim();
    showError("");
    busy(true);
    try {
      const res = await rpc("create_room", { p_room_name: ui.roomName.value.trim(), p_passcode: pw, p_player_name: name });
      enterRoom({ code: res.code, player_id: res.player_id, token: res.token, pw });
    } catch (e) {
      showError(errText(e));
    } finally {
      busy(false);
    }
  }

  // ---------- Room connection ----------
  async function syncClock() {
    try {
      const t0 = Date.now();
      const s = await rpc("server_now");
      offset = Date.parse(s) - (t0 + Date.now()) / 2;
    } catch {}
  }

  async function enterRoom(creds) {
    me = creds;
    seat.set(me);
    MP.active = true;
    phaseKey = "";
    clearInterval(browserTimer);
    history.replaceState(null, "", shareUrl());
    K.el.ocean.classList.add("mp");

    channel = sb.channel("room-" + me.code)
      .on("postgres_changes", { event: "*", schema: "public", table: "rooms", filter: `code=eq.${me.code}` }, scheduleRefresh)
      .on("postgres_changes", { event: "*", schema: "public", table: "players", filter: `room_code=eq.${me.code}` }, scheduleRefresh)
      .on("postgres_changes", { event: "*", schema: "public", table: "answers", filter: `room_code=eq.${me.code}` }, scheduleRefresh)
      .subscribe();

    await Promise.all([syncClock(), heartbeat()]);
    await refresh();
    pollTimer = setInterval(refresh, 3000);    // backstop in case a realtime event is missed
    hbTimer = setInterval(heartbeat, 5000);
    tickTimer = setInterval(tick, 500);
  }

  async function heartbeat() {
    if (!me) return;
    try {
      await rpc("heartbeat", { p_player_id: me.player_id, p_token: me.token });
    } catch (e) {
      if (e.message === "not_in_room") { const code = me.code; cleanup(); openHome({ code }); showError(ERRORS.not_in_room); }
    }
  }

  function scheduleRefresh() {
    clearTimeout(refreshTimer);
    refreshTimer = setTimeout(refresh, 120);
  }

  async function refresh() {
    if (!me) return;
    const code = me.code;
    const [r, p, a] = await Promise.all([
      sb.from("rooms").select("*").eq("code", code).maybeSingle(),
      sb.from("players").select("id,name,score,tunnel_pts,joined_at,last_seen,left_at").eq("room_code", code).order("joined_at"),
      sb.from("answers").select("round,player_id,answer,tier,pts,submitted_at").eq("room_code", code),
    ]);
    if (!me || me.code !== code) return;
    if (r.error || p.error || a.error) return;
    if (!r.data) { cleanup(); openHome(); showError("That room has closed."); return; }
    room = r.data; players = p.data; answers = a.data;
    applyShared();
    render();
  }

  // Shared answers (like in Stop): once a prompt is revealed, everyone who gave the same
  // answer gets half points. The server stores full points; every client applies the
  // halving to the same answers table, so everyone sees the same scores.
  function revealed(round) {
    return round < room.round || room.status === "reveal" || room.status === "finished";
  }
  function applyShared() {
    const groups = {};
    for (const a of answers) {
      a.full = a.full ?? a.pts;
      a.sharedWith = [];
      a.pts = a.full;
      if (a.tier && a.answer && revealed(a.round)) (groups[a.round + "|" + a.answer.toLowerCase()] ||= []).push(a);
    }
    for (const g of Object.values(groups)) {
      if (g.length < 2) continue;
      for (const a of g) {
        a.pts = Math.ceil(a.full / 2);
        a.sharedWith = g.filter((b) => b !== a).map((b) => (players.find((p) => p.id === b.player_id) || {}).name).filter(Boolean);
      }
    }
    for (const p of players) {
      p.score = answers.filter((a) => a.player_id === p.id).reduce((s, a) => s + a.pts, 0);
    }
  }

  // Server phases advance when any client nudges them; nudge as soon as a deadline passes.
  function tick() {
    if (!room) return;
    const ends = room.phase_ends_at ? Date.parse(room.phase_ends_at) : 0;
    if ((room.status === "playing" || room.status === "reveal") && ends && serverNow() > ends && Date.now() - lastNudge > 1500) {
      lastNudge = Date.now();
      heartbeat();
    }
    if (room.status === "reveal" && !ui.board.classList.contains("hidden")) renderBoardTimer();
  }

  function render() {
    const key = [room.status, room.round, room.round_started_at, room.mode].join("|");
    if (key !== phaseKey) {
      // Let your own descent finish before jumping to the scoreboard.
      const wait = landingUntil - performance.now();
      if (wait > 0 && room.status !== "playing") {
        clearTimeout(pendingPhase);
        pendingPhase = setTimeout(render, wait);
        renderLive();
        return;
      }
      // Answers load on demand; fetch this game's prompts before entering a round.
      if (room.status !== "lobby" && (room.prompt_ids || []).some((id) => PROMPTS[id] && !PROMPTS[id].answers)) {
        K.loadPrompts(room.prompt_ids).then(render, (e) => { console.error(e); setTimeout(render, 2000); });
        renderLive();
        return;
      }
      phaseKey = key;
      if (room.status === "lobby") enterLobby();
      else if (room.status === "playing") enterRound();
      else if (room.status === "reveal") enterBoard();
      else if (room.status === "finished") enterFinal();
    }
    renderLive();
  }

  // Things that change within a phase: player lists, answered counts, host controls, ruler markers.
  function renderLive() {
    if (room.status === "lobby") renderLobby();
    if (room.status === "playing") {
      const act = activePlayers();
      const done = act.filter((p) => answerFor(p.id)).length;
      ui.progress.textContent = `${done} / ${act.length} divers answered`;
      const left = act.length - done;
      ui.resultWait.textContent = left > 0 ? `Waiting for ${left} more diver${left === 1 ? "" : "s"}…` : "Everyone's in!";
    }
    if (room.status === "reveal") renderBoard();
    if (room.status === "finished") renderFinal();
    if (room.status === "lobby" || room.status === "finished") renderModes();
    renderPips();
    renderMates();
  }

  function myScoreBeforeRound() {
    const mine = myPlayer();
    if (!mine) return 0;
    const a = room.status === "playing" ? answerFor(me.player_id) : null;
    return mine.score - (a ? a.pts : 0);
  }

  function setHud(score) {
    K.setDepthVisual(score * K.METRES_PER_POINT);
    K.animateCounters(score, score, 1);
  }

  // ---------- Lobby ----------
  function enterLobby() {
    compiled = null;
    K.stopTimer();
    setHud(0);
    K.show(ui.lobby);
    ui.shareLink.value = shareUrl();
  }

  function renderModes() {
    for (const box of [ui.lobbyModes, ui.finalModes]) {
      for (const b of box.querySelectorAll("button")) {
        b.classList.toggle("on", b.dataset.mode === room.mode);
        b.disabled = !isHost();
      }
    }
    ui.finalModes.classList.toggle("hidden", !isHost());
    ui.lobbyModeNote.textContent = isDig()
      ? `Race to China: your tunnel carries over from dig to dig, and the first to dig out the far side (${GOAL.toLocaleString()} pts) wins.`
      : "Classic: every dive starts at the surface, and the deepest dive wins.";
  }

  async function setMode(mode) {
    if (!isHost() || !room || mode === room.mode) return;
    const dug = isDig() && players.some((p) => p.tunnel_pts > 0);
    if (dug && !confirm("Switching modes fills in everyone's tunnel. Switch anyway?")) return;
    try { await rpc("set_room_mode", { p_player_id: me.player_id, p_token: me.token, p_mode: mode }); scheduleRefresh(); }
    catch (e) { alert(errText(e)); }
  }

  function renderLobby() {
    const act = activePlayers();
    ui.lobbyEyebrow.textContent = `ROOM ${room.code}${room.locked ? " · PRIVATE" : ""}`;
    ui.lobbyName.textContent = room.name;
    ui.shareHint.textContent = room.locked
      ? "This link includes the password, so friends can join straight away."
      : `Or have friends enter code ${room.code}, or find the room in the browser.`;
    ui.lobbyCount.textContent = `Divers (${act.length})`;
    ui.lobbyPlayers.innerHTML = act.map(playerRow).join("");
    const host = players.find((p) => p.id === room.host_id);
    ui.start.classList.toggle("hidden", !isHost());
    ui.start.disabled = false;
    ui.lobbyWait.textContent = isHost()
      ? (act.length < 2 ? "You can start solo, or wait for others to join." : "Everyone here? Start the dive!")
      : `Waiting for ${host ? host.name : "the host"} to start the dive…`;
  }

  function playerRow(p) {
    return `<li style="--c:hsl(${hue(p.id)} 80% 68%)"><span class="dot"></span><span class="pname">${esc(p.name)}</span>${p.id === me.player_id ? `<span class="pill you">YOU</span>` : ""}${p.id === room.host_id ? `<span class="pill host">HOST</span>` : ""}</li>`;
  }

  async function startGame() {
    ui.start.disabled = true; ui.again.disabled = true;
    try {
      await rpc("start_game", { p_player_id: me.player_id, p_token: me.token, p_prompt_ids: K.drawPrompts(K.PROMPTS_PER_DIVE) });
      scheduleRefresh();
    } catch (e) {
      alert(errText(e));
    } finally {
      ui.start.disabled = false; ui.again.disabled = false;
    }
  }

  // ---------- Rounds ----------
  function enterRound() {
    const p = PROMPTS[room.prompt_ids[room.round]];
    compiled = { ...p, ...K.buildIndex(p) };
    const el = K.el;
    const mine = answerFor(me.player_id);
    setHud(myScoreBeforeRound());
    if (mine) { // e.g. after a refresh mid-round
      showMyVerdict(mine.tier ? { display: mine.answer, tier: mine.tier } : null, false);
      return;
    }
    el.eyebrow.textContent = `PROMPT ${room.round + 1} OF ${room.prompt_ids.length}`;
    el.promptText.textContent = p.prompt;
    K.clearSuggestion();
    el.feedback.textContent = "";
    el.feedback.className = "feedback";
    el.input.value = "";
    el.input.disabled = false;
    el.diveBtn.disabled = false;
    ui.progress.classList.remove("hidden");
    K.show(el.play);
    el.input.focus();
    const msLeft = Date.parse(room.phase_ends_at) - 500 - serverNow();
    K.startTimer(performance.now() + Math.min(msLeft, K.SECONDS_PER_PROMPT * 1000), () => submit(null));
  }

  function onSubmit(raw) {
    if (!compiled || !room || room.status !== "playing") return;
    K.judge(compiled, raw, submit);
  }

  async function submit(hit) {
    if (!room || room.status !== "playing" || answerFor(me.player_id)) return;
    const round = room.round;
    const before = myScoreBeforeRound();
    // Optimistic: record locally and start sinking right away.
    answers.push({ round, player_id: me.player_id, answer: hit ? hit.display : null, tier: hit ? hit.tier : null, pts: hit ? K.TIERS[hit.tier].pts : 0, submitted_at: new Date(serverNow()).toISOString() });
    showMyVerdict(hit, true, before);
    renderLive();
    try {
      await rpc("submit_answer", { p_player_id: me.player_id, p_token: me.token, p_round: round, p_answer: hit ? hit.display : null, p_tier: hit ? hit.tier : null });
    } catch (e) {
      ui.resultWait.textContent = errText(e);
    }
    scheduleRefresh();
  }

  function showMyVerdict(hit, animate, before = myScoreBeforeRound()) {
    const pts = hit ? K.TIERS[hit.tier].pts : 0;
    const dur = K.showVerdict(hit, before, before + pts, null);
    landingUntil = animate ? performance.now() + dur + 900 : 0;
    ui.resultWait.classList.remove("hidden");
  }

  // ---------- Scoreboard ----------
  function enterBoard() {
    K.stopTimer();
    K.endDescent();
    const mine = myPlayer();
    setHud(mine ? mine.score : 0);
    ui.resultWait.classList.add("hidden");
    K.show(ui.board);
  }

  function roundRows(round) {
    const ids = new Set([...activePlayers().map((p) => p.id), ...answers.filter((a) => a.round === round).map((a) => a.player_id)]);
    return players.filter((p) => ids.has(p.id)).map((p) => ({ p, a: answerFor(p.id, round) })).sort((x, y) => {
      const rx = x.a && x.a.tier ? TIER_RANK[x.a.tier] : 0, ry = y.a && y.a.tier ? TIER_RANK[y.a.tier] : 0;
      if (rx !== ry) return ry - rx;
      if (x.a && y.a) return Date.parse(x.a.submitted_at) - Date.parse(y.a.submitted_at);
      return x.a ? -1 : y.a ? 1 : 0;
    });
  }

  function renderBoard() {
    const p = PROMPTS[room.prompt_ids[room.round]];
    const total = room.prompt_ids.length;
    ui.boardEyebrow.textContent = `PROMPT ${room.round + 1} OF ${total} · RESULTS`;
    ui.boardPrompt.textContent = p.prompt;
    const rows = roundRows(room.round);
    const topTier = rows[0] && rows[0].a && rows[0].a.tier;
    if (topTier) {
      const best = rows.filter((r) => r.a && r.a.tier === topTier);
      ui.boardBest.style.setProperty("--tier", K.tierColor(topTier));
      ui.boardBest.innerHTML = `<span class="label">BEST ANSWER</span> ${best.map((r) => `<b>${esc(r.p.name)}</b> “${esc(r.a.answer)}”`).join(" · ")} <span class="tag">${K.TIERS[topTier].name}</span>`;
    } else {
      ui.boardBest.style.setProperty("--tier", "var(--t-miss)");
      ui.boardBest.innerHTML = `<span class="label">NOBODY SCORED</span> Lost at sea, all of you.`;
    }
    ui.boardList.innerHTML = rows.map(({ p: pl, a }) => {
      const tier = a && a.tier;
      const c = tier ? K.tierColor(tier) : "var(--t-miss)";
      return `<li style="--tier:${c};--c:hsl(${hue(pl.id)} 80% 68%)" class="${pl.id === me.player_id ? "me" : ""}">
        <span class="dot"></span>
        <span class="who">${esc(pl.name)}${pl.id === me.player_id ? " (you)" : ""}</span>
        <span class="ans">${a && a.answer ? `“${esc(a.answer)}”` : `<i>no answer</i>`}${a && a.sharedWith && a.sharedWith.length ? `<span class="shared">½ shared with ${a.sharedWith.map(esc).join(", ")}</span>` : ""}</span>
        <span class="tier">${tier ? K.TIERS[tier].name : K.MISS.name}</span>
        <span class="pts">+${a ? a.pts : 0}<small>${depthText(totalOf(pl))} total</small></span>
      </li>`;
    }).join("");
    const last = room.round + 1 >= total || brokeThrough().length > 0;
    ui.boardNext.textContent = last ? "FINAL RESULTS ▼" : "NEXT PROMPT ▼";
    ui.boardNext.classList.toggle("hidden", !isHost());
    renderBoardTimer();
  }

  function renderBoardTimer() {
    const secs = Math.max(0, Math.ceil((Date.parse(room.phase_ends_at) - serverNow()) / 1000));
    const through = brokeThrough();
    const last = room.round + 1 >= room.prompt_ids.length || through.length > 0;
    const what = last ? "Final results" : "Next prompt";
    const host = players.find((p) => p.id === room.host_id);
    ui.boardWait.textContent = (through.length ? `${through[0].id === me.player_id ? "You" : through[0].name} dug out the other side! ` : "") + (isHost()
      ? `${what} in ${secs}s, or skip ahead.`
      : `${what} in ${secs}s${host ? ` (or when ${host.name} continues)` : ""}.`);
  }

  async function nextRound() {
    ui.boardNext.disabled = true;
    try { await rpc("next_round", { p_player_id: me.player_id, p_token: me.token, p_round: room.round }); scheduleRefresh(); }
    catch (e) { alert(errText(e)); }
    finally { ui.boardNext.disabled = false; }
  }

  // ---------- Final standings ----------
  function enterFinal() {
    K.stopTimer();
    const mine = myPlayer();
    setHud(mine ? mine.score : 0);
    K.show(ui.final);
  }

  function renderFinal() {
    const ids = new Set([...activePlayers().map((p) => p.id), ...answers.map((a) => a.player_id)]);
    const dig = isDig();
    if (dig) for (const p of players) if (p.tunnel_pts > 0) ids.add(p.id);
    const ranked = players.filter((p) => ids.has(p.id)).sort((a, b) => totalOf(b) - totalOf(a));
    const top = ranked[0];
    const winners = ranked.filter((p) => top && totalOf(p) === totalOf(top));
    const winner = dig && room.winner_id ? players.find((p) => p.id === room.winner_id) : null;
    ui.final.classList.toggle("breakthrough", !!winner);
    ui.finalEyebrow.textContent = winner ? "BREAKTHROUGH!" : dig ? "DIG COMPLETE · THE RACE IS ON" : "DIVE COMPLETE";
    if (winner) {
      ui.finalWinner.textContent = winner.id === me.player_id ? "You dug through to the other side!" : `${winner.name} dug through to the other side!`;
      ui.finalRace.textContent = "First out of the hole, into the Indian Ocean. Not China, but close enough. The next dig starts a new race.";
    } else if (dig) {
      ui.finalWinner.textContent = !top ? "" : winners.length > 1 ? `Neck and neck at ${depthText(totalOf(top))}!` : `${top.name} leads the race!`;
      ui.finalRace.textContent = top ? `${pctOf(totalOf(top))}% of the way through. Tunnels carry over to the next dig.` : "";
    } else {
      ui.finalWinner.textContent = !top ? "" : winners.length > 1 ? `It's a tie at ${(top.score * 10).toLocaleString()}m!` : `${top.name} dives deepest!`;
      ui.finalRace.textContent = "";
    }
    let rank = 0, prev = null;
    ui.finalStandings.innerHTML = ranked.map((p, i) => {
      const t = totalOf(p);
      if (t !== prev) { rank = i + 1; prev = t; }
      const depth = p.score * K.METRES_PER_POINT;
      const detail = dig ? `${K.placeName(Math.min(GOAL, t))} · ${pctOf(t)}% · +${p.score} this dig` : `${K.zoneFor(depth).name} · ${p.score} pts`;
      return `<li style="--c:hsl(${hue(p.id)} 80% 68%)" class="${p.id === me.player_id ? "me" : ""}">
        <span class="rank">${rank}</span><span class="dot"></span>
        <span class="who">${esc(p.name)}${p.id === me.player_id ? " (you)" : ""}</span>
        <span class="depth">${dig ? depthText(t) : depth.toLocaleString() + "m"}<small>${detail}</small></span>
      </li>`;
    }).join("");
    // A dig race can end mid-dive, so only list the prompts that were played.
    ui.finalLog.innerHTML = room.prompt_ids.slice(0, room.round + 1).map((pid, round) => {
      const p = PROMPTS[pid];
      const gem = p.gem || "";
      const finders = answers.filter((a) => a.round === round && a.tier === "gem").map((a) => (players.find((x) => x.id === a.player_id) || {}).name).filter(Boolean);
      const mine = answerFor(me.player_id, round);
      const c = mine && mine.tier ? K.tierColor(mine.tier) : "var(--t-miss)";
      return `<li style="--tier:${c}">
        <span class="q">${esc(p.prompt)}</span>
        <span class="a">you: ${mine && mine.answer ? esc(mine.answer) : "<i>no answer</i>"}${mine && mine.sharedWith && mine.sharedWith.length ? ` <span class="shared">½ shared with ${mine.sharedWith.map(esc).join(", ")}</span>` : ""}</span>
        <span class="pts">+${mine ? mine.pts : 0}<small>${mine && mine.tier ? K.TIERS[mine.tier].name : K.MISS.name}</small></span>
        <span class="g">${esc(K.TIERS.gem.name.toLowerCase())}: <b>${esc(gem)}</b>${finders.length ? ` · found by ${finders.map(esc).join(", ")}` : ""}</span>
      </li>`;
    }).join("");
    const host = players.find((p) => p.id === room.host_id);
    ui.again.textContent = winner ? "▼ NEW RACE ▼" : dig ? "▼ KEEP DIGGING ▼" : "▼ DIVE AGAIN ▼";
    ui.again.classList.toggle("hidden", !isHost());
    ui.finalWait.textContent = isHost() ? "" : `Waiting for ${host ? host.name : "the host"} to start ${winner ? "a new race" : dig ? "another dig" : "another dive"}…`;
  }

  // ---------- HUD + ruler ----------
  function renderPips() {
    if (!room || room.status === "lobby") return;
    const total = room.prompt_ids.length;
    K.el.pips.innerHTML = Array.from({ length: total }, (_, i) => {
      const a = answerFor(me.player_id, i);
      if (a) return `<div class="pip" style="background:${a.tier ? K.tierColor(a.tier) : "var(--t-miss)"}"></div>`;
      return `<div class="pip${i === room.round && room.status === "playing" ? " current" : ""}"></div>`;
    }).join("");
    K.el.hudPrompt.textContent = room.status === "finished" ? (isDig() ? "DIG COMPLETE" : "DIVE COMPLETE") : `PROMPT ${room.round + 1} OF ${total}`;
  }

  // Other divers ride the depth ruler beside you. During a prompt they stay at their
  // depth from before it, so nobody's answer is given away until the scoreboard.
  function renderMates() {
    if (!MP.active || !room || room.status === "lobby") { ui.mates.innerHTML = ""; Scene.setMates([]); return; }
    const myPts = tunnelOf(myPlayer()) + K.depth / K.METRES_PER_POINT;
    const base = innerHeight * 0.52;
    const px = K.RULER_PX_PER_M * K.METRES_PER_POINT;
    const stack = {};
    const others = activePlayers().filter((p) => p.id !== me.player_id).map((p) => {
      const a = room.status === "playing" ? answerFor(p.id) : null;
      return { p, a, pts: totalOf(p) - (a ? a.pts : 0) };
    });
    Scene.setMates(isDig() ? others.map(({ p, pts }) => ({ pts: Math.min(GOAL, pts), color: `hsl(${hue(p.id)} 80% 68%)` })) : []);
    ui.mates.innerHTML = others.map(({ p, a, pts }) => {
      let y = base + (pts - myPts) * px;
      const min = 150, max = innerHeight - 150;
      const off = y < min ? "up" : y > max ? "down" : "";
      y = Math.max(min, Math.min(max, y));
      const slot = Math.round(y / 18);
      const n = (stack[slot] = (stack[slot] || 0) + 1) - 1;
      if (Math.abs(pts - myPts) < 1) y += 20 + n * 20; else y += n * 20;
      const done = room.status === "playing" && a ? " ✓" : "";
      return `<div class="mate ${off}" style="top:${y}px;--c:hsl(${hue(p.id)} 80% 68%)">
        <span>${off === "up" ? "▲ " : off === "down" ? "▼ " : ""}${esc(p.name)} · ${depthText(pts)}${done}</span>
      </div>`;
    }).join("");
  }

  // ---------- Leaving ----------
  function confirmLeave() {
    if (confirm("Leave this room?")) leave();
  }

  async function leave() {
    const creds = me;
    cleanup();
    K.goHome();
    if (creds) { try { await rpc("leave_room", { p_player_id: creds.player_id, p_token: creds.token }); } catch {} }
  }

  function cleanup() {
    MP.active = false;
    for (const t of [pollTimer, hbTimer, tickTimer]) clearInterval(t);
    clearTimeout(refreshTimer); clearTimeout(pendingPhase);
    if (channel) { sb.removeChannel(channel); channel = null; }
    K.stopTimer();
    me = null; room = null; players = []; answers = []; compiled = null; phaseKey = "";
    seat.set(null);
    ui.mates.innerHTML = "";
    Scene.setMates([]);
    ui.final.classList.remove("breakthrough");
    ui.progress.classList.add("hidden");
    ui.resultWait.classList.add("hidden");
    K.el.next.classList.remove("hidden");
    K.el.ocean.classList.remove("mp");
    history.replaceState(null, "", location.pathname);
  }

  // ---------- Wire up ----------
  ui.mpBtn.addEventListener("click", () => openHome());
  ui.back.addEventListener("click", () => { clearInterval(browserTimer); history.replaceState(null, "", location.pathname); K.goHome(); });
  ui.refreshRooms.addEventListener("click", loadRooms);
  ui.joinForm.addEventListener("submit", (e) => { e.preventDefault(); join(ui.joinCode.value, ui.joinCode.value.trim().toUpperCase() === ui.linkJoinCode.textContent ? linkPw : ""); });
  ui.joinCode.addEventListener("input", () => { ui.joinCode.value = ui.joinCode.value.toUpperCase().replace(/[^A-Z0-9]/g, ""); });
  ui.createForm.addEventListener("submit", (e) => { e.preventDefault(); create(); });
  ui.roomList.addEventListener("click", (e) => {
    const b = e.target.closest("button[data-code]");
    if (b) join(b.dataset.code, "", b.dataset.locked === "true");
  });
  ui.copyLink.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(ui.shareLink.value); } catch { ui.shareLink.select(); document.execCommand("copy"); }
    ui.copyLink.textContent = "COPIED";
    setTimeout(() => (ui.copyLink.textContent = "COPY"), 1500);
  });
  ui.start.addEventListener("click", startGame);
  ui.again.addEventListener("click", startGame);
  ui.boardNext.addEventListener("click", nextRound);
  for (const box of [ui.lobbyModes, ui.finalModes]) {
    box.addEventListener("click", (e) => { const b = e.target.closest("button[data-mode]"); if (b) setMode(b.dataset.mode); });
  }
  ui.lobbyLeave.addEventListener("click", confirmLeave);
  ui.finalLeave.addEventListener("click", confirmLeave);
  document.addEventListener("krill:depth", () => requestAnimationFrame(renderMates));
  addEventListener("resize", renderMates);

  // Arriving via a share link, or refreshing while in a room.
  const params = new URLSearchParams(location.search);
  const linkCode = (params.get("room") || "").toUpperCase();
  if (linkCode && sb) {
    const saved = seat.get();
    if (saved && saved.code === linkCode) {
      rpc("heartbeat", { p_player_id: saved.player_id, p_token: saved.token })
        .then(() => enterRoom(saved))
        .catch(() => { seat.set(null); openHome({ code: linkCode, pw: params.get("pw") || "" }); });
    } else {
      openHome({ code: linkCode, pw: params.get("pw") || "" });
    }
  }
})();

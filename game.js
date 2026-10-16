(() => {
  "use strict";

  // ---------- Config ----------
  const PROMPTS_PER_DIVE = 7;
  const SECONDS_PER_PROMPT = 25;
  const METRES_PER_POINT = 10;
  const MAX_DEPTH = 7000;
  const RULER_PX_PER_M = 2; // matches the real game's ruler: 100 m ≈ 200 px

  const TIERS = {
    plankton:  { name: "Plankton",          pts: 10,  flavor: "Everyone's down here. Barely a ripple." },
    tooClever: { name: "Too Clever",        pts: 15,  flavor: "The obscure pick… that everyone else picked too." },
    schooler:  { name: "Schooler",          pts: 30,  flavor: "Swimming with the school. Solid." },
    rare:      { name: "Rare",              pts: 60,  flavor: "Genuinely uncommon. Nice pull." },
    deepCut:   { name: "Deep Cut",          pts: 85,  flavor: "Very few divers ever reach this one." },
    gem:       { name: "One in a Krillion", pts: 100, flavor: "The hidden gem. Truly one in a krillion." },
  };
  const TIER_ORDER = ["plankton", "tooClever", "schooler", "rare", "deepCut", "gem"];
  const MISS = { name: "Lost at Sea", pts: 0, flavor: "Out of air. The clock ran dry." };

  const ZONES = [
    { to: 200,  name: "Sunlight Zone", color: "#1d5f8f" },
    { to: 1000, name: "Twilight Zone", color: "#123f66" },
    { to: 4000, name: "Midnight Zone", color: "#0b2038" },
    { to: 6000, name: "Abyssal Zone",  color: "#08131f" },
    { to: 7000, name: "Hadal Zone",    color: "#060b13" },
  ];
  const DEPTH_COLORS = [[0, "#1d5f8f"], [200, "#164c78"], [1000, "#0e2b48"], [4000, "#0a1626"], [7000, "#04070d"]];
  const LANDMARKS = [
    { m: 332,  name: "Deepest scuba dive" },
    { m: 1000, name: "Midnight zone" },
    { m: 1857, name: "Grand Canyon depth" },
    { m: 3800, name: "Titanic wreck" },
    { m: 4000, name: "Abyssal plain" },
    { m: 6000, name: "Hadal zone" },
    { m: 7000, name: "Trench floor" },
  ];

  // ---------- Answer matching ----------
  function normalize(s) {
    return s
      .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/&/g, " and ")
      .replace(/['’`.!?]/g, "")
      .replace(/[^a-z0-9]+/g, " ")
      .trim()
      .replace(/^(the|a|an) /, "")
      .split(" ")
      .map((w) => (w.length > 3 && w.endsWith("s") && !w.endsWith("ss") ? w.slice(0, -1) : w))
      .join("");
  }

  function levenshtein(a, b, max) {
    if (Math.abs(a.length - b.length) > max) return max + 1;
    let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
    for (let i = 1; i <= a.length; i++) {
      const cur = [i];
      let rowMin = i;
      for (let j = 1; j <= b.length; j++) {
        cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
        rowMin = Math.min(rowMin, cur[j]);
      }
      if (rowMin > max) return max + 1;
      prev = cur;
    }
    return prev[b.length];
  }

  const typoAllowance = (len) => (len < 5 ? 0 : len < 9 ? 1 : 2);

  function buildIndex(p) {
    const index = new Map();
    let gem = null;
    for (const tier of TIER_ORDER) {
      for (const entry of p.answers[tier] || []) {
        const variants = entry.split("|");
        const display = variants[0];
        if (tier === "gem" && !gem) gem = display;
        for (const v of variants) {
          const key = normalize(v);
          if (!key) continue;
          if (index.has(key)) {
            if (index.get(key).display !== display) console.warn(`[${p.prompt}] duplicate answer "${v}" (already ${index.get(key).tier})`);
            continue;
          }
          index.set(key, { display, tier });
        }
      }
    }
    return { index, gem };
  }

  function match(compiled, input) {
    const key = normalize(input);
    if (!key) return null;
    if (compiled.index.has(key)) return compiled.index.get(key);
    let best = null, bestD = Infinity;
    for (const [k, v] of compiled.index) {
      const max = typoAllowance(Math.min(k.length, key.length));
      if (max === 0) continue;
      const d = levenshtein(key, k, max);
      if (d <= max && d < bestD) { best = v; bestD = d; }
    }
    return best;
  }

  // ---------- Storage (best effort) ----------
  const store = {
    get(k, fallback) { try { const v = localStorage.getItem("krillion." + k); return v == null ? fallback : JSON.parse(v); } catch { return fallback; } },
    set(k, v) { try { localStorage.setItem("krillion." + k, JSON.stringify(v)); } catch {} },
  };

  function shuffle(a) {
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  }

  // Shuffle bag so you cycle through the whole bank before seeing repeats.
  function drawPrompts(n) {
    const total = window.KRILLION_PROMPTS.length;
    n = Math.min(n, total);
    let bag = store.get("bag", []).filter((i) => i < total);
    const picked = [];
    while (picked.length < n) {
      if (!bag.length) bag = shuffle([...Array(total).keys()].filter((i) => !picked.includes(i)));
      picked.push(bag.shift());
    }
    store.set("bag", bag);
    return picked;
  }

  // ---------- DOM ----------
  const $ = (id) => document.getElementById(id);
  const el = {
    ocean: $("ocean"), fauna: $("fauna"), bubbles: $("bubbles"), rulerTrack: $("rulerTrack"),
    hud: $("hud"), hudDepth: $("hudDepth"), hudScore: $("hudScore"), pips: $("pips"), hudPrompt: $("hudPrompt"),
    quit: $("quitBtn"),
    title: $("screenTitle"), play: $("screenPlay"), result: $("screenResult"), end: $("screenEnd"),
    tierTable: $("tierTable"), titleStats: $("titleStats"), diveNum: $("diveNum"), start: $("startBtn"),
    eyebrow: $("promptEyebrow"), promptText: $("promptText"), feedback: $("feedback"),
    resultIcon: $("resultIcon"), resultTier: $("resultTier"), resultAnswer: $("resultAnswer"), resultPoints: $("resultPoints"),
    resultFlavor: $("resultFlavor"), next: $("nextBtn"),
    endDepth: $("endDepth"), endZone: $("endZone"), endScore: $("endScore"), endLandmark: $("endLandmark"), endLog: $("endLog"),
    endStats: $("endStats"), again: $("againBtn"), home: $("homeBtn"),
    bar: $("answerBar"), input: $("answerInput"), diveBtn: $("diveBtn"), timer: $("timer"), timerRing: $("timerRing"), timerNum: $("timerNum"),
  };

  const tierColor = (t) => `var(--t-${t})`;

  const KRILL = [
    "..........w..",
    ".......w.w...",
    "..rrrrr.w....",
    ".rrrrrrrrr...",
    "rrrrrrrrrrre.",
    ".rrrrrrrrrrrr",
    "..r.rrrrrrr..",
    "...r.r.r.r...",
    "..r.r.r.r....",
  ];
  function sprite(rows) {
    const w = rows[0].length, h = rows.length;
    let rects = "";
    rows.forEach((row, y) => [...row].forEach((c, x) => {
      if (c === ".") return;
      const fill = c === "e" ? "#05080f" : c === "w" ? "currentColor\" opacity=\"0.6" : "currentColor";
      rects += `<rect x="${x}" y="${y}" width="1.02" height="1.02" fill="${fill}"/>`;
    }));
    return `<svg viewBox="0 0 ${w} ${h}" shape-rendering="crispEdges">${rects}</svg>`;
  }

  // ---------- Backdrop ----------
  function hexToRgb(h) { const n = parseInt(h.slice(1), 16); return [n >> 16, (n >> 8) & 255, n & 255]; }
  function depthColor(m) {
    for (let i = 1; i < DEPTH_COLORS.length; i++) {
      const [m1, c1] = DEPTH_COLORS[i];
      if (m <= m1) {
        const [m0, c0] = DEPTH_COLORS[i - 1];
        const t = (m - m0) / (m1 - m0);
        const a = hexToRgb(c0), b = hexToRgb(c1);
        return `rgb(${a.map((v, k) => Math.round(v + (b[k] - v) * t)).join(",")})`;
      }
    }
    return DEPTH_COLORS[DEPTH_COLORS.length - 1][1];
  }
  const zoneFor = (m) => (m >= MAX_DEPTH ? { name: "Trench Floor" } : ZONES.find((z) => m < z.to));

  function buildRuler() {
    const track = el.rulerTrack;
    track.style.setProperty("--len", MAX_DEPTH * RULER_PX_PER_M + "px");
    let html = "";
    for (let m = 0; m <= MAX_DEPTH; m += 20) {
      const labelled = m % 100 === 0;
      html += `<div class="tick${labelled ? " major" : ""}" style="top:${m * RULER_PX_PER_M}px">${labelled ? `<span>${m ? "-" : ""}${m.toLocaleString()}m</span>` : ""}</div>`;
    }
    for (const l of LANDMARKS) {
      html += `<div class="landmark" style="top:${l.m * RULER_PX_PER_M}px"><span>${l.name} · ${l.m.toLocaleString()}m</span></div>`;
    }
    track.innerHTML = html;
  }

  function spawnFauna() {
    let html = "";
    for (let i = 0; i < 9; i++) {
      const dir = Math.random() < 0.5 ? "" : " left";
      html += `<div class="fish${dir}" style="top:${55 + Math.random() * 40}vh;animation-duration:${18 + Math.random() * 22}s;animation-delay:-${Math.random() * 30}s;transform:scale(${0.6 + Math.random()})"></div>`;
    }
    el.fauna.innerHTML = html;
    let bub = "";
    for (let i = 0; i < 14; i++) {
      const s = 3 + Math.random() * 6;
      bub += `<div class="bubble" style="left:${Math.random() * 92}vw;width:${s}px;height:${s}px;animation-duration:${8 + Math.random() * 10}s;animation-delay:-${Math.random() * 18}s"></div>`;
    }
    el.bubbles.innerHTML = bub;
  }

  let currentDepth = 0;
  function setDepthVisual(m) {
    currentDepth = m;
    document.dispatchEvent(new CustomEvent("krill:depth", { detail: m }));
    el.ocean.style.backgroundColor = depthColor(m);
    el.ocean.classList.toggle("submerged", m > 0);
    el.rulerTrack.style.transform = `translateY(${-m * RULER_PX_PER_M}px)`;
    // Fish thin out as it gets darker.
    el.fauna.style.opacity = String(Math.max(0.15, 1 - m / 5000));
  }

  let counterAnim = 0;
  function animateCounters(fromScore, toScore, dur = 1300) {
    cancelAnimationFrame(counterAnim);
    const start = performance.now();
    const step = (now) => {
      const t = Math.min(1, (now - start) / dur);
      const e = 1 - Math.pow(1 - t, 3);
      const s = Math.round(fromScore + (toScore - fromScore) * e);
      el.hudScore.textContent = s;
      el.hudDepth.textContent = (s * METRES_PER_POINT).toLocaleString() + "m";
      if (t < 1) counterAnim = requestAnimationFrame(step);
    };
    counterAnim = requestAnimationFrame(step);
  }

  // ---------- Game state ----------
  let dive = null;
  let timerRaf = 0, deadline = 0, resultShownAt = 0, descentTimer = 0;

  const isMp = () => !!(window.KrillMP && window.KrillMP.active);

  function show(screen) {
    for (const s of document.querySelectorAll(".screen")) s.classList.toggle("hidden", s !== screen);
    el.bar.classList.toggle("hidden", screen !== el.play);
    el.hud.classList.toggle("idle", screen === el.title || screen.dataset.idle === "true");
    el.quit.classList.toggle("hidden", screen === el.title || screen === el.end || screen.dataset.noquit === "true");
    el.title.parentElement.scrollTop = 0;
  }

  function renderPips() {
    el.pips.innerHTML = Array.from({ length: dive.prompts.length }, (_, i) => {
      const r = dive.results[i];
      if (r) return `<div class="pip" style="background:${r.tier ? tierColor(r.tier) : "var(--t-miss)"}"></div>`;
      return `<div class="pip${i === dive.i ? " current" : ""}"></div>`;
    }).join("");
    el.hudPrompt.textContent = `PROMPT ${Math.min(dive.i + 1, dive.prompts.length)} OF ${dive.prompts.length}`;
  }

  function renderTitle() {
    el.tierTable.innerHTML = TIER_ORDER.map((t) =>
      `<tr><td style="color:${tierColor(t)}">${TIERS[t].name}</td><td>${TIERS[t].pts} pts</td><td>${(TIERS[t].pts * METRES_PER_POINT).toLocaleString()} m</td></tr>`
    ).join("");
    const st = store.get("stats", { dives: 0, best: 0, total: 0 });
    el.titleStats.textContent = st.dives
      ? `dives ${st.dives} · best ${(st.best * METRES_PER_POINT).toLocaleString()}m · avg ${Math.round((st.total / st.dives) * METRES_PER_POINT).toLocaleString()}m`
      : "";
    el.diveNum.textContent = `ENDLESS DIVE #${st.dives + 1}`;
  }

  function goHome() {
    stopTimer();
    endDescent();
    dive = null;
    el.ocean.classList.remove("mp");
    el.hudScore.textContent = "0";
    el.hudDepth.textContent = "0m";
    setDepthVisual(0);
    renderTitle();
    show(el.title);
    el.start.focus({ preventScroll: true });
  }

  function startDive() {
    const ids = drawPrompts(PROMPTS_PER_DIVE);
    dive = {
      prompts: ids.map((id) => {
        const p = window.KRILLION_PROMPTS[id];
        return { ...p, ...buildIndex(p) };
      }),
      i: 0,
      score: 0,
      results: [],
    };
    el.hudScore.textContent = "0";
    el.hudDepth.textContent = "0m";
    setDepthVisual(0);
    startPrompt();
  }

  function startPrompt() {
    const p = dive.prompts[dive.i];
    renderPips();
    el.eyebrow.textContent = `PROMPT ${dive.i + 1} OF ${dive.prompts.length}`;
    el.promptText.textContent = p.prompt;
    el.feedback.textContent = "";
    el.feedback.className = "feedback";
    el.input.value = "";
    el.input.disabled = false;
    el.diveBtn.disabled = false;
    setTimerDisplay(SECONDS_PER_PROMPT, 1);
    show(el.play);
    el.input.focus();
    startTimer();
  }

  function setTimerDisplay(secsLeft, frac) {
    el.timerNum.textContent = Math.ceil(secsLeft);
    el.timerRing.style.strokeDashoffset = String(119.4 * (1 - frac));
    el.timer.classList.toggle("low", secsLeft <= 5);
  }

  // deadline is a performance.now() timestamp; multiplayer passes one derived from the server clock.
  function startTimer(deadlineAt = performance.now() + SECONDS_PER_PROMPT * 1000, onExpire = () => finishPrompt(null)) {
    stopTimer();
    deadline = deadlineAt;
    const tick = (now) => {
      const left = Math.max(0, (deadline - now) / 1000);
      setTimerDisplay(left, Math.min(1, left / SECONDS_PER_PROMPT));
      if (left <= 0) return onExpire();
      timerRaf = requestAnimationFrame(tick);
    };
    timerRaf = requestAnimationFrame(tick);
  }
  function stopTimer() { cancelAnimationFrame(timerRaf); }

  function submitAnswer(e) {
    e.preventDefault();
    if (el.input.disabled) return;
    const raw = el.input.value.trim();
    if (!raw) return;
    if (isMp()) return window.KrillMP.onSubmit(raw);
    if (!dive) return;
    const hit = match(dive.prompts[dive.i], raw);
    if (hit) return finishPrompt(hit);
    rejectGuess(raw);
  }

  function rejectGuess(raw) {
    el.feedback.className = "feedback bad";
    el.feedback.textContent = `“${raw}” isn't on the list`;
    el.input.classList.remove("shake");
    void el.input.offsetWidth;
    el.input.classList.add("shake");
    el.input.select();
  }

  function finishPrompt(hit) {
    stopTimer();
    el.input.disabled = true;
    el.diveBtn.disabled = true;
    const p = dive.prompts[dive.i];
    const info = hit ? TIERS[hit.tier] : MISS;
    const before = dive.score;
    dive.score += info.pts;
    dive.results[dive.i] = { prompt: p.prompt, answer: hit ? hit.display : null, tier: hit ? hit.tier : null, pts: info.pts, gem: p.gem };
    showVerdict(hit, before, dive.score, dive.i + 1 < dive.prompts.length ? "DESCEND ▼" : "SEE YOUR DIVE ▼");
    renderPips();
  }

  // Shows your verdict for a prompt: sink from `before` to `after` points, then reveal the tier.
  // Returns how long the descent takes (ms).
  function showVerdict(hit, before, after, nextLabel) {
    stopTimer();
    el.input.disabled = true;
    el.diveBtn.disabled = true;
    const info = hit ? TIERS[hit.tier] : MISS;
    const color = hit ? tierColor(hit.tier) : "var(--t-miss)";
    el.result.style.setProperty("--tier", color);
    el.resultIcon.style.color = color;
    el.resultIcon.innerHTML = sprite(KRILL);
    el.resultTier.textContent = info.name.toUpperCase();
    el.resultTier.style.color = color;
    el.resultAnswer.textContent = hit ? `“${hit.display}”` : "—";
    el.resultPoints.innerHTML = hit
      ? `<b>+${info.pts} PTS</b> · sink ${(info.pts * METRES_PER_POINT).toLocaleString()}m`
      : `<b>+0 PTS</b> · no descent`;
    el.resultFlavor.textContent = info.flavor;
    el.next.textContent = nextLabel || "";
    el.next.classList.toggle("hidden", !nextLabel);
    show(el.result);

    // Sink to the new depth first; the verdict appears once you arrive.
    const dur = info.pts ? Math.min(3000, 1000 + info.pts * 20) : 0;
    document.documentElement.style.setProperty("--descent-dur", (dur || 600) + "ms");
    resultShownAt = performance.now() + dur;
    if (dur) {
      el.result.classList.add("sinking");
      el.ocean.classList.add("descending");
      el.resultIcon.classList.remove("pop");
      el.resultIcon.style.animationDuration = dur + "ms";
    }
    setDepthVisual(after * METRES_PER_POINT);
    animateCounters(before, after, dur || 600);
    clearTimeout(descentTimer);
    descentTimer = setTimeout(() => {
      endDescent();
      for (const n of [el.resultIcon, el.resultTier]) { n.classList.remove("pop"); void n.offsetWidth; n.classList.add("pop"); }
      if (nextLabel) el.next.focus({ preventScroll: true });
    }, dur);
    return dur;
  }

  function endDescent() {
    clearTimeout(descentTimer);
    el.result.classList.remove("sinking");
    el.ocean.classList.remove("descending");
    el.resultIcon.style.animationDuration = "";
  }

  function nextPrompt() {
    if (!dive) return;
    dive.i++;
    if (dive.i < dive.prompts.length) startPrompt();
    else endDive();
  }

  function endDive() {
    const depth = dive.score * METRES_PER_POINT;
    const st = store.get("stats", { dives: 0, best: 0, total: 0 });
    const newBest = dive.score > st.best;
    st.dives++; st.total += dive.score; st.best = Math.max(st.best, dive.score);
    store.set("stats", st);

    el.endDepth.textContent = depth.toLocaleString() + "m";
    el.endZone.textContent = zoneFor(depth).name.toUpperCase();
    el.endScore.textContent = `${dive.score} / ${dive.prompts.length * 100} pts${newBest && st.dives > 1 ? " · new personal best!" : ""}`;
    const passed = LANDMARKS.filter((l) => depth >= l.m).pop();
    const nextL = LANDMARKS.find((l) => depth < l.m);
    el.endLandmark.textContent = passed
      ? `You passed the ${passed.name.toLowerCase()} (${passed.m.toLocaleString()}m)` + (nextL ? ` · next: ${nextL.name.toLowerCase()} at ${nextL.m.toLocaleString()}m` : "")
      : `Next landmark: ${nextL.name.toLowerCase()} at ${nextL.m.toLocaleString()}m`;

    el.endLog.innerHTML = dive.results.map((r) => {
      const c = r.tier ? tierColor(r.tier) : "var(--t-miss)";
      const tname = r.tier ? TIERS[r.tier].name : MISS.name;
      return `<li style="--tier:${c}">
        <span class="q">${escapeHtml(r.prompt)}</span>
        <span class="a">${r.answer ? escapeHtml(r.answer) : "<i>no answer</i>"}</span>
        <span class="pts">+${r.pts}<small>${tname}</small></span>
        ${r.tier === "gem" ? "" : `<span class="g">one in a krillion: <b>${escapeHtml(r.gem)}</b></span>`}
      </li>`;
    }).join("");
    el.endStats.textContent = `dives ${st.dives} · best ${(st.best * METRES_PER_POINT).toLocaleString()}m · avg ${Math.round((st.total / st.dives) * METRES_PER_POINT).toLocaleString()}m`;
    show(el.end);
    el.again.focus({ preventScroll: true });
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // ---------- Wire up ----------
  el.start.addEventListener("click", startDive);
  el.again.addEventListener("click", startDive);
  el.home.addEventListener("click", goHome);
  el.next.addEventListener("click", () => { if (!isMp() && performance.now() - resultShownAt > 300) nextPrompt(); });
  el.bar.addEventListener("submit", submitAnswer);
  el.quit.addEventListener("click", () => {
    if (isMp()) return window.KrillMP.confirmLeave();
    if (confirm("Abandon this dive and return to the surface?")) goHome();
  });
  el.input.addEventListener("input", () => { if (el.feedback.classList.contains("bad")) { el.feedback.textContent = ""; el.feedback.className = "feedback"; } });

  // Shared with mp.js
  window.Krill = {
    TIERS, TIER_ORDER, MISS, METRES_PER_POINT, SECONDS_PER_PROMPT, PROMPTS_PER_DIVE, RULER_PX_PER_M,
    el, store, show, goHome, buildIndex, match, drawPrompts, tierColor, escapeHtml, zoneFor,
    setDepthVisual, animateCounters, setTimerDisplay, startTimer, stopTimer, rejectGuess, showVerdict, endDescent,
    get depth() { return currentDepth; },
  };

  buildRuler();
  spawnFauna();
  goHome();
})();

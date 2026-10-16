// The backdrop: sky, ocean and the inside of the Earth, drawn as pixel art on one canvas.
// Everything is placed in "points" (1 pt = 10 m in the ocean), the same unit as the score,
// so the camera, the ruler and the fun facts all move together.
(() => {
  "use strict";

  const P = 3;            // CSS px per art pixel
  const PX_PER_PT = 20;   // matches the ruler: 2 px per metre, 10 m per point
  const ANCHOR = 0.52;    // the YOU line sits at 52% of the viewport height

  // ---------- The route: down through the ocean, through the core, out the other side ----------
  const DOWN = [
    { key: "ocean", name: "Ocean",        pts: 700, km: 7 },
    { key: "crust", name: "Crust",        pts: 200, km: 35 },
    { key: "upper", name: "Upper Mantle", pts: 400, km: 625 },
    { key: "lower", name: "Lower Mantle", pts: 600, km: 2230 },
    { key: "outer", name: "Outer Core",   pts: 600, km: 2260 },
    { key: "inner", name: "Inner Core",   pts: 400, km: 1221 },
  ];
  const UP = [
    { key: "inner", name: "Inner Core",   pts: 400, km: 1221 },
    { key: "outer", name: "Outer Core",   pts: 600, km: 2260 },
    { key: "lower", name: "Lower Mantle", pts: 600, km: 2230 },
    { key: "upper", name: "Upper Mantle", pts: 400, km: 625 },
    { key: "crust", name: "Ocean Crust",  pts: 200, km: 7 },
    { key: "ocean", name: "Indian Ocean", pts: 400, km: 4 },
  ];
  const ROUTE = [];
  {
    let pts = 0, km = 0;
    for (const [list, up] of [[DOWN, false], [UP, true]]) {
      for (const l of list) {
        ROUTE.push({ ...l, up, from: pts, to: pts + l.pts, kmFrom: km, kmTo: km + l.km });
        pts += l.pts; km += l.km;
      }
    }
  }
  const SEABED = 700;
  const CENTRE = DOWN.reduce((s, l) => s + l.pts, 0);
  const FAR_SEABED = ROUTE[ROUTE.length - 1].from;
  const END = ROUTE[ROUTE.length - 1].to;

  const layerAt = (pts) => ROUTE.find((l) => pts < l.to) || ROUTE[ROUTE.length - 1];
  function kmAt(pts) {
    const l = layerAt(Math.max(0, Math.min(END, pts)));
    return l.kmFrom + ((Math.max(0, Math.min(END, pts)) - l.from) / l.pts) * l.km;
  }
  // 0..1 through a layer, measured from its outer edge (so both sides of the Earth match).
  function depthIn(l, pts) {
    const t = (pts - l.from) / l.pts;
    return l.up ? 1 - t : t;
  }

  // ---------- Colours ----------
  const hex = (h) => { const n = parseInt(h.slice(1), 16); return [n >> 16, (n >> 8) & 255, n & 255]; };
  const STOPS = {
    ocean: [[0, "#2b8cc0"], [0.03, "#1f6ea3"], [0.14, "#154a78"], [0.4, "#0b2340"], [0.7, "#081628"], [1, "#04080f"]],
    crust: [[0, "#3a3029"], [0.06, "#4b3a2c"], [0.5, "#3e2d22"], [1, "#2e1d15"]],
    upper: [[0, "#4a2214"], [1, "#7a2a10"]],
    lower: [[0, "#6a210e"], [1, "#8e3610"]],
    outer: [[0, "#b04a0c"], [0.5, "#d26a12"], [1, "#eb8f1e"]],
    inner: [[0, "#e8962a"], [1, "#ffc95e"]],
  };
  for (const k in STOPS) STOPS[k] = STOPS[k].map(([t, c]) => [t, hex(c)]);
  function ramp(stops, t) {
    for (let i = 1; i < stops.length; i++) {
      if (t <= stops[i][0]) {
        const [t0, a] = stops[i - 1], [t1, b] = stops[i];
        const f = (t - t0) / (t1 - t0 || 1);
        return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f];
      }
    }
    return stops[stops.length - 1][1];
  }
  function groundColor(pts) {
    const l = layerAt(pts);
    let t = depthIn(l, pts);
    // The far ocean is shallow: use the top part of the ocean ramp.
    if (l.key === "ocean" && l.up) t *= l.km / 7;
    return ramp(STOPS[l.key], Math.max(0, Math.min(1, t)));
  }
  const SKY = [[0, hex("#eef6f3")], [0.35, hex("#a6d4ec")], [1, hex("#4f9fd2")]];
  const rgb = (c, k = 1) => `rgb(${Math.round(c[0] * k)},${Math.round(c[1] * k)},${Math.round(c[2] * k)})`;

  // ---------- Deterministic noise ----------
  function hash(a, b = 0) {
    let h = (a * 374761393 + b * 668265263) | 0;
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
  }
  function rng(seed) {
    return () => {
      seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const smooth = (x) => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return hash(i) * (1 - u) + hash(i + 1) * u; };

  // ---------- Sprites ----------
  // Each row is a string; "." is transparent and other characters index into the palette.
  const SPRITES = {
    fish:   { rows: ["..aaa..a", ".aaaaaaa", "aeaaaab.", ".abbbbba", "..bbb..a"] },
    jelly:  { rows: ["..lll..", ".lppppl", "lppppppl", "pppppppp", "p.p..p.p", "p.p..p.p", ".p.p..p.", ".p....p."].map((r) => r.padEnd(8, ".")) },
    whale:  { rows: [
      "aaaaaaaaaa..................",
      "aaaaaaaaaaaaaa...........aa.",
      "aeaaaaaaaaaaaaaaaa......aaa.",
      "aaaaaaaaaaaaaaaaaaaaaaaaaa..",
      "baaaaaaaaaaaaaaaaaaaaaaaaaa.",
      ".bbbbbbbbbbbbbbbbbbbbb...aaa",
      "..b.bbbbbbbbbbbbb.........a.",
    ] },
    squid:  { rows: [
      "...rrrr..............",
      ".rrrrrrrrr.r..r..r...",
      "rrrrrrrrrrrrrrrrrrrrr",
      "rerrrrrrrrrrrrrrrrrr.",
      "rrrrrrrrrrrrrrrrrrrrr",
      ".rrrrrrrrr.r..r..r...",
      "...rrrr..............",
    ] },
    angler: { rows: [
      "..g........",
      "...g.......",
      "....g......",
      "..aaaaa....",
      ".aaeaaaaa.a",
      "awwaaaaaaaa",
      ".waaaaaaa.a",
      "..aaaaa....",
    ] },
    titanic: { rows: [
      "..........ss...ss...ss......",
      "..........ss...ss...ss......",
      ".........sss..sss..sss......",
      "hhhhhhhhhhhhhhhhhhhhhhhhh...",
      "hhwhhwhhwhhwhhwhhwhhwhhhhhh.",
      ".hhhhhhhhhhhhhhhhhhhhhhhhhhh",
      "..hhhhhhhhhhhhhhhhhhhhhhhhh.",
      "....hhhhhhhhhhhhhhhhhhhhh...",
    ] },
    boat:   { rows: [
      "........f.......",
      "........fff.....",
      "........fffff...",
      "........m.......",
      "........m.......",
      ".....cccmcc.....",
      ".....cwcwcc.....",
      "hhhhhhhhhhhhhhhh",
      ".hhhhhhhhhhhhhh.",
      "..hrrrrrrrrrrh..",
    ] },
    cuke:   { rows: ["..pppp..", ".pppppp.", "pp.pp.pp"] },
    worm:   { rows: ["rr", "rr", "ww", ".w", "w.", "w.", ".w"] },
    ammonite: { rows: ["..bbb..", ".b...b.", "b..b..b", "b.b.b.b", "b..bb.b", ".b....b", "..bbbb."] },
    bones:  { rows: ["...b.b.b..", "b.bbbbbbbb", "bbbbbbbbbe", "b.bbbbbbbb", "...b.b.b.."] },
    skull:  { rows: ["..bbbbbb..", ".bbbbbbbbb", "bbebbbbbbb", "bbbbbbbbbb", "b.b.b.bbb.", "..........", "b.b.b.b..."] },
    diamond: { rows: ["..w..", ".wcw.", "wcccw", ".wcw.", "..w.."] },
    crystal: { rows: [".w.", "wcw", "wcw", "wcw", "ccc", "ccc", ".c."] },
    drill:  { rows: [
      ".ggggggggg.",
      "gyyyyyyyyyg",
      "gyykkkkkyyg",
      "gyyyyyyyyyg",
      "ggggggggggg",
      ".sSsSsSsSs.",
      "..sSsSsSs..",
      "..SsSsSsS..",
      "...sSsSs...",
      "...SsSsS...",
      "....sSs....",
      ".....s.....",
    ] },
    bird:   { rows: ["b...b", ".b.b.", "..b.."] },
  };
  const spriteCache = new Map();
  function sprite(name, pal, flipX = false, flipY = false) {
    const key = name + JSON.stringify(pal) + flipX + flipY;
    let c = spriteCache.get(key);
    if (c) return c;
    const rows = SPRITES[name].rows;
    const w = Math.max(...rows.map((r) => r.length)), h = rows.length;
    c = document.createElement("canvas");
    c.width = w; c.height = h;
    const g = c.getContext("2d");
    rows.forEach((row, y) => [...row].forEach((ch, x) => {
      if (ch === "." || !pal[ch]) return;
      g.fillStyle = pal[ch];
      g.fillRect(flipX ? w - 1 - x : x, flipY ? h - 1 - y : y, 1, 1);
    }));
    spriteCache.set(key, c);
    return c;
  }

  // ---------- The things that live (and lie buried) along the route ----------
  const things = [];
  function populate() {
    const r = rng(7);
    const between = (a, b) => a + r() * (b - a);
    const add = (o) => things.push({ x: r(), vx: 0, bob: r() * 6.28, ...o });
    const fishCols = [["#ffcf5a", "#d9932c"], ["#7fe0e8", "#3a9fb4"], ["#ff8a6b", "#c4523e"], ["#b9f27a", "#6faa3d"], ["#f2f2f2", "#9fb5c4"]];

    // Sunlit shallows: schools of fish, near side and far side.
    for (const [a, b, n] of [[1, 18, 9], [18, 70, 7], [END - 60, END - 1, 9]]) {
      for (let i = 0; i < n; i++) {
        const [c1, c2] = fishCols[Math.floor(r() * fishCols.length)];
        const dir = r() < 0.5 ? -1 : 1, y = between(a, b), x = r(), speed = 6 + r() * 10, count = 3 + Math.floor(r() * 6);
        const dim = y > 18 && y < END - 60 ? 0.55 : 1;
        for (let k = 0; k < count; k++) {
          add({ kind: "fish", y: y + (r() - 0.5) * 1.6, x: x + (r() - 0.5) * 0.08, vx: dir * speed, pal: { a: c1, b: c2, e: "#08131f" }, dim, flip: dir > 0 });
        }
      }
    }
    for (let i = 0; i < 12; i++) {
      const hue = r() < 0.5 ? ["#ff7fc8", "#ffc2e6"] : ["#7fe8ff", "#d0f8ff"];
      add({ kind: "jelly", y: between(16, 150), vx: (r() - 0.5) * 3, pal: { p: hue[0], l: hue[1] }, glow: hue[0], float: true });
    }
    add({ kind: "whale", y: 62, x: 0.15, vx: 5, pal: { a: "#2d4a63", b: "#3f6684", e: "#0a1626" }, flip: true });
    add({ kind: "squid", y: 124, x: 0.7, vx: -4, pal: { r: "#a63a3a", e: "#ffe066" } });
    for (let i = 0; i < 110; i++) add({ kind: "lantern", y: between(60, 680), vx: (r() - 0.5) * 6, glow: r() < 0.5 ? "#7fe8ff" : "#b8ff9a" });
    for (let i = 0; i < 14; i++) {
      const dir = r() < 0.5 ? -1 : 1;
      add({ kind: "angler", y: between(150, 690), vx: dir * (2 + r() * 3), pal: { a: "#1b2a38", e: "#ffe066", w: "#d8e4ee", g: "#4a6274" }, glow: "#ffe066", flip: dir > 0 });
    }
    add({ kind: "titanic", y: 380, x: 0.6, pal: { h: "#5b3a2a", w: "#ffd98a", s: "#7a4a30" }, glow: "#ffcf7a" });
    for (let i = 0; i < 10; i++) add({ kind: "cuke", y: between(430, 690), vx: (r() - 0.5) * 1.5, pal: { p: "#c46b8f" } });
    // Seabed (both sides)
    for (const bed of [SEABED, FAR_SEABED]) {
      for (let i = 0; i < 9; i++) add({ kind: "worm", y: bed - 0.2, x: 0.05 + r() * 0.9, pal: { r: "#e0454f", w: "#e8e2d0" }, anchor: "bottom" });
    }
    // Inside the Earth (both sides use the same layer ranges, mirrored).
    const both = (a, b) => (r() < 0.5 ? between(a, b) : 2 * CENTRE - between(a, b));
    const bone = { b: "#c9b99a", e: "#2a1e16", w: "#c9b99a" };
    for (let i = 0; i < 22; i++) {
      const kinds = ["ammonite", "bones", "skull"];
      add({ kind: kinds[Math.floor(r() * 3)], y: both(SEABED + 15, SEABED + 190), pal: bone, flip: r() < 0.5 });
    }
    for (let i = 0; i < 26; i++) add({ kind: "diamond", y: both(920, 1050), pal: { w: "#ffffff", c: "#9fe8ff" }, glow: "#bff4ff", sparkle: true });
    for (let i = 0; i < 90; i++) add({ kind: "magma", y: both(910, 1890), size: 2 + r() * 5, vy: 0.4 + r() * 0.8 });
    for (let i = 0; i < 26; i++) add({ kind: "crystal", y: both(2520, 2890), pal: { w: "#ffffff", c: "#ffe7a3" }, glow: "#fff4c8", sparkle: true, flip: r() < 0.5 });
  }

  // ---------- Facts that drift past as you go ----------
  const FACTS = [
    [20, "sunlight fades out around here"],
    [33, "deepest scuba dive on record — 332 m"],
    [55, "emperor penguins can dive this deep"],
    [100, "THE MIDNIGHT ZONE — no sunlight below"],
    [124, "sperm whales hunt giant squid down here"],
    [186, "the Grand Canyon would fit above this line"],
    [300, "the water is about 2°C and pitch black"],
    [380, "the Titanic wreck lies at 3,800 m"],
    [400, "THE ABYSSAL ZONE"],
    [600, "THE HADAL ZONE — named after Hades"],
    [700, "THE TRENCH FLOOR — a perfect dive stops here"],
  ];
  const DIG_FACTS = [
    [705, "THE CRUST — you've broken through the seabed"],
    [729, "deepest hole humans ever dug: 12 km (Kola, Russia)"],
    [900, "THE UPPER MANTLE — rock that flows like very slow taffy"],
    [969, "diamonds form around 150 km down"],
    [1300, "THE LOWER MANTLE — 660 km down"],
    [1600, "the pressure here would crush a submarine like a can"],
    [1900, "THE OUTER CORE — liquid iron at about 4,500°C"],
    [2150, "this swirling iron is what makes Earth's magnetic field"],
    [2500, "THE INNER CORE — solid iron hotter than the Sun's surface"],
    [CENTRE, "THE CENTRE OF THE EARTH — 6,371 km. Halfway."],
    [CENTRE + 400, "THE OUTER CORE — now climbing up the other side"],
    [CENTRE + 1000, "THE LOWER MANTLE"],
    [CENTRE + 1600, "THE UPPER MANTLE"],
    [FAR_SEABED - 200, "THE OCEAN CRUST — almost there"],
    [FAR_SEABED, "THE SEABED — of the Indian Ocean. Not China. Sorry."],
    [END, "THE SURFACE — you dug through the whole planet"],
  ];

  // ---------- Canvas + camera ----------
  let canvas, ctx, factsTrack, W = 0, H = 0, w = 0, h = 0;
  let cam = 0, camFrom = 0, camTo = 0, camT0 = 0, camDur = 0, lastCam = 0;
  let dig = false, lastT = 0, moving = false;
  const particles = [];
  const listeners = [];

  function resize() {
    W = innerWidth; H = innerHeight;
    w = Math.ceil(W / P); h = Math.ceil(H / P);
    canvas.width = w; canvas.height = h;
    ctx.imageSmoothingEnabled = false;
    particles.length = 0;
    for (let i = 0; i < Math.round((w * h) / 900); i++) particles.push(newParticle(true));
  }
  function newParticle(anywhere) {
    return { x: Math.random() * w, y: anywhere ? Math.random() * h : Math.random() < 0.5 ? -2 : h + 2, s: Math.random(), ph: Math.random() * 6.28 };
  }

  const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const ptsAtRow = (y) => cam + (y * P - H * ANCHOR) / PX_PER_PT;
  const rowAtPts = (pts) => (H * ANCHOR + (pts - cam) * PX_PER_PT) / P;

  function goTo(pts, dur = 0) {
    if (Math.abs(pts - cam) > 1500) dur = 0; // e.g. back home after going all the way through
    camFrom = cam; camTo = pts; camT0 = performance.now(); camDur = dur;
    if (!dur) cam = pts;
  }

  function buildFacts() {
    const list = dig ? [...FACTS, ...DIG_FACTS] : FACTS;
    factsTrack.innerHTML = list.map(([pts, text]) => {
      const big = /^THE [A-Z]{3}/.test(text);
      return `<div class="fact${big ? " big" : ""}" style="top:${pts * PX_PER_PT}px">── ${text}</div>`;
    }).join("");
  }

  // ---------- Drawing ----------
  function drawBackground(t) {
    const sY = rowAtPts(0), fY = rowAtPts(END);
    for (let y = 0; y < h; y++) {
      const pts = ptsAtRow(y + 0.5);
      let c;
      if (pts < 0) {
        c = ramp(SKY, Math.min(1, (sY - y) / (h * ANCHOR)));
      } else if (pts > END) {
        c = ramp(SKY, Math.min(1, (y - fY) / (h * ANCHOR)));
      } else {
        c = groundColor(pts);
        const l = layerAt(pts);
        if (l.key !== "ocean") {
          const wr = Math.floor((pts * PX_PER_PT) / P);
          // Strata: slow bands of light and dark rock.
          const k = 0.86 + smooth(wr / 9) * 0.22 + (l.key === "crust" ? Math.sin(wr * 0.35) * 0.05 : 0);
          c = [c[0] * k, c[1] * k, c[2] * k];
        }
      }
      ctx.fillStyle = rgb(c);
      ctx.fillRect(0, y, w, 1);
    }
    // Rock grain: a few speckles per art row, fixed to the world.
    const top = Math.max(0, Math.floor(rowAtPts(SEABED))), bot = Math.min(h, Math.ceil(rowAtPts(FAR_SEABED)));
    for (let y = top; y < bot; y++) {
      const pts = ptsAtRow(y + 0.5);
      const wr = Math.floor((pts * PX_PER_PT) / P);
      const hot = pts > 1890 && pts < 2 * CENTRE - 1890;
      for (let k = 0; k < 7; k++) {
        const x = Math.floor(hash(wr, k) * w);
        const v = hash(wr, k + 50);
        ctx.fillStyle = hot ? (v < 0.5 ? "rgba(255,240,180,0.35)" : "rgba(120,30,0,0.25)") : v < 0.5 ? "rgba(0,0,0,0.22)" : "rgba(255,230,200,0.1)";
        ctx.fillRect(x, y, v < 0.2 ? 2 : 1, 1);
      }
    }
    // Liquid-iron currents in the outer core.
    for (const [a, b] of [[1900, 2500], [2 * CENTRE - 2500, 2 * CENTRE - 1900]]) {
      const y0 = Math.max(0, Math.floor(rowAtPts(a))), y1 = Math.min(h, Math.ceil(rowAtPts(b)));
      if (y1 <= y0) continue;
      ctx.fillStyle = "rgba(255,220,120,0.28)";
      for (let y = y0; y < y1; y += 1) {
        const wr = Math.floor((ptsAtRow(y) * PX_PER_PT) / P);
        if (wr % 11) continue;
        for (let x = 0; x < w; x++) {
          const yy = y + Math.round(Math.sin(x * 0.08 + t * 0.9 + wr) * 2);
          if (x % 3 !== 0) ctx.fillRect(x, yy, 1, 1);
        }
      }
    }
  }

  function drawSky(t, surfaceRow, flip) {
    // flip: the sky on the far side of the Earth, hanging below you.
    const dir = flip ? 1 : -1;
    const at = (frac) => surfaceRow + dir * frac * h * ANCHOR;
    if ((flip && surfaceRow > h) || (!flip && surfaceRow < 0)) return;
    // Sun
    const sx = w * 0.82, sy = at(0.6);
    const glow = ctx.createRadialGradient(sx, sy, 2, sx, sy, 26);
    glow.addColorStop(0, "rgba(255,230,140,0.9)"); glow.addColorStop(1, "rgba(255,230,140,0)");
    ctx.fillStyle = glow; ctx.fillRect(sx - 26, sy - 26, 52, 52);
    ctx.fillStyle = "#ffd76b";
    for (let dy = -7; dy <= 7; dy++) { const hw = Math.round(Math.sqrt(49 - dy * dy)); ctx.fillRect(Math.round(sx - hw), Math.round(sy + dy), hw * 2, 1); }
    // Clouds
    for (let i = 0; i < 5; i++) {
      const cw = 14 + hash(i, 3) * 22;
      const x = ((hash(i, 1) * (w + 80) + t * (1.5 + hash(i, 2) * 2)) % (w + 80)) - 40;
      const y = at(0.25 + hash(i, 4) * 0.55);
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(Math.round(x), Math.round(y), Math.round(cw), 4);
      ctx.fillRect(Math.round(x + cw * 0.2), Math.round(y - 3), Math.round(cw * 0.45), 4);
      ctx.fillRect(Math.round(x + cw * 0.5), Math.round(y - 5), Math.round(cw * 0.3), 4);
      ctx.fillStyle = "#dceef6";
      ctx.fillRect(Math.round(x + 1), Math.round(y + 3), Math.round(cw - 2), 1);
    }
    // Gulls
    for (let i = 0; i < 2; i++) {
      const x = ((hash(i, 9) * w + t * 6) % (w + 20)) - 10;
      const y = at(0.45 + i * 0.12) + Math.sin(t * 2 + i) * 2;
      ctx.drawImage(sprite("bird", { b: "#3b4b5a" }, false, flip), Math.round(x), Math.round(y));
    }
    // Waves, with the boat riding them
    for (let x = 0; x < w; x++) {
      const off = Math.round(Math.sin(x * 0.18 + t * 1.6) + Math.sin(x * 0.07 - t * 0.8));
      const y = Math.round(surfaceRow) + (flip ? -off : off);
      ctx.fillStyle = "#d6f1fb"; ctx.fillRect(x, y, 1, 1);
      ctx.fillStyle = "#5fb7df"; ctx.fillRect(x, y + (flip ? -1 : 1), 1, 1);
    }
    const bx = Math.round(w * 0.27), bob = Math.round(Math.sin(t * 1.6 + bx * 0.18));
    const boat = sprite("boat", { f: "#ff5f7e", m: "#2a3542", c: "#e9eef2", w: "#7ab8d6", h: "#13202e", r: "#ff5f7e" }, false, flip);
    ctx.drawImage(boat, bx, flip ? Math.round(surfaceRow) - 2 + bob : Math.round(surfaceRow) - boat.height + 3 + bob);
  }

  function drawLightRays(t) {
    const fade = Math.max(0, 1 - cam / 45);
    if (fade <= 0) return;
    const sY = rowAtPts(0);
    ctx.save();
    ctx.globalAlpha = 0.08 * fade;
    ctx.fillStyle = "#e6fbff";
    for (let i = 0; i < 6; i++) {
      const x = (i / 6) * w + Math.sin(t * 0.3 + i) * 6;
      const len = h * 0.9;
      ctx.beginPath();
      ctx.moveTo(x, sY); ctx.lineTo(x + 10, sY); ctx.lineTo(x + 10 + len * 0.35, sY + len); ctx.lineTo(x + len * 0.35 - 6, sY + len);
      ctx.fill();
    }
    ctx.restore();
  }

  function drawTrench() {
    const y0 = Math.max(0, Math.floor(rowAtPts(560))), y1 = Math.min(h, Math.ceil(rowAtPts(SEABED)));
    for (let y = y0; y < y1; y++) {
      const pts = ptsAtRow(y);
      const f = Math.max(0, (pts - 560) / 140);
      const wr = Math.floor((pts * PX_PER_PT) / P);
      const left = Math.round(w * (0.04 + 0.14 * f) + smooth(wr / 5) * 8);
      const right = Math.round(w * (0.04 + 0.14 * f) + smooth(wr / 5 + 40) * 8);
      ctx.fillStyle = "#03060b"; ctx.fillRect(0, y, left, 1); ctx.fillRect(w - right, y, right, 1);
      ctx.fillStyle = "#0c1824"; ctx.fillRect(left, y, 1, 1); ctx.fillRect(w - right - 1, y, 1, 1);
    }
  }

  function drawSeabed(bedPts, flip) {
    const y = rowAtPts(bedPts);
    if (y < -20 || y > h + 20) return;
    for (let x = 0; x < w; x++) {
      const bump = Math.round(smooth(x / 7 + bedPts) * 3);
      ctx.fillStyle = "#4e463c"; ctx.fillRect(x, Math.round(y) - (flip ? -bump : bump), 1, 2);
      ctx.fillStyle = "#6b6052"; ctx.fillRect(x, Math.round(y) - (flip ? -bump : bump), 1, 1);
    }
    // Rocks
    for (let i = 0; i < 9; i++) {
      const x = Math.round(hash(i, bedPts) * w), rw = 3 + Math.round(hash(i, bedPts + 1) * 6);
      ctx.fillStyle = "#2c2721";
      ctx.fillRect(x, Math.round(y) - (flip ? -1 : 3), rw, 3);
      ctx.fillRect(x + 1, Math.round(y) - (flip ? -3 : 4), rw - 2, 1);
    }
  }

  function drawThings(t, dt) {
    for (const o of things) {
      const y = rowAtPts(o.y);
      if (y < -40 || y > h + 40) continue;
      o.x += (o.vx * dt) / w;
      if (o.x > 1.15) o.x -= 1.3; else if (o.x < -0.15) o.x += 1.3;
      const x = Math.round(o.x * w);
      const by = Math.round(y + (o.float ? Math.sin(t * 1.2 + o.bob) * 3 : o.kind === "fish" ? Math.sin(t * 3 + o.bob) * 0.6 : 0));

      if (o.kind === "lantern") {
        const on = Math.sin(t * 2 + o.bob * 3) > -0.3;
        if (on) { ctx.fillStyle = o.glow; ctx.globalAlpha = 0.8; ctx.fillRect(x, by, 1, 1); ctx.globalAlpha = 1; }
        continue;
      }
      if (o.kind === "magma") {
        const yy = y - ((t * o.vy * 6 + o.bob * 20) % 30);
        const g = ctx.createRadialGradient(x, yy, 0, x, yy, o.size * 2);
        g.addColorStop(0, "rgba(255,200,90,0.85)"); g.addColorStop(0.5, "rgba(255,110,30,0.5)"); g.addColorStop(1, "rgba(255,80,20,0)");
        ctx.fillStyle = g; ctx.fillRect(x - o.size * 2, yy - o.size * 2, o.size * 4, o.size * 4);
        continue;
      }
      if (o.glow) {
        const pulse = o.sparkle ? 0.4 + 0.6 * Math.max(0, Math.sin(t * 3 + o.bob * 5)) : 0.7;
        const gx = o.kind === "angler" ? x + (o.flip ? 8 : 2) : x + 3, gy = o.kind === "angler" ? by : by + 3;
        const g = ctx.createRadialGradient(gx, gy, 0, gx, gy, 9);
        g.addColorStop(0, o.glow); g.addColorStop(1, "rgba(0,0,0,0)");
        ctx.globalAlpha = 0.45 * pulse; ctx.fillStyle = g; ctx.fillRect(gx - 9, gy - 9, 18, 18); ctx.globalAlpha = 1;
      }
      const s = sprite(o.kind, o.pal, !!o.flip);
      ctx.globalAlpha = o.dim || 1;
      ctx.drawImage(s, x, o.anchor === "bottom" ? by - s.height : by - Math.round(s.height / 2));
      ctx.globalAlpha = 1;
    }
  }

  // Other players' drills in a multiplayer dig race, each in its own tunnel beside yours.
  let mates = [];
  function drawMateTunnels(t, cx) {
    const top = Math.max(0, Math.round(rowAtPts(SEABED)));
    mates.forEach((m, i) => {
      const x = cx + (i % 2 ? 1 : -1) * 14 * (1 + (i >> 1));
      const at = Math.round(rowAtPts(Math.min(m.pts, END)));
      const end = Math.min(h, at, Math.round(rowAtPts(FAR_SEABED)));
      if (end > top) {
        ctx.fillStyle = "rgba(10,6,4,0.6)"; ctx.fillRect(x - 4, top, 9, end - top);
        ctx.fillStyle = m.color; ctx.globalAlpha = 0.35; ctx.fillRect(x - 5, top, 1, end - top); ctx.fillRect(x + 5, top, 1, end - top); ctx.globalAlpha = 1;
      }
      if (m.pts > SEABED - 2 && m.pts < FAR_SEABED && at > -20 && at < h + 20) {
        const spin = Math.floor(t * 4 + i) % 2;
        const d = sprite("drill", { g: "#3b4652", y: m.color, k: "#13202e", s: spin ? "#c9d3dc" : "#7d8a96", S: spin ? "#7d8a96" : "#c9d3dc" });
        ctx.drawImage(d, x - 5, at - d.height + 3);
      }
    });
  }

  function drawTunnel(t) {
    if (!dig) return;
    const cx = Math.round((W / 2 - 30) / P), you = Math.round(rowAtPts(cam));
    drawMateTunnels(t, cx);
    const top = Math.max(0, Math.round(rowAtPts(SEABED)));
    const end = Math.min(you, Math.round(rowAtPts(FAR_SEABED)));
    if (end <= top) return;
    ctx.fillStyle = "rgba(10,6,4,0.78)"; ctx.fillRect(cx - 5, top, 11, end - top);
    ctx.fillStyle = "rgba(255,255,255,0.08)"; ctx.fillRect(cx - 6, top, 1, end - top); ctx.fillRect(cx + 6, top, 1, end - top);
    if (cam > SEABED - 2 && cam < FAR_SEABED) {
      const shake = moving ? Math.round(Math.sin(t * 60)) : 0;
      const spin = Math.floor(t * (moving ? 24 : 4)) % 2;
      const pal = { g: "#3b4652", y: "#ffd23f", k: "#13202e", s: spin ? "#c9d3dc" : "#7d8a96", S: spin ? "#7d8a96" : "#c9d3dc" };
      const d = sprite("drill", pal);
      ctx.drawImage(d, cx - 5 + shake, you - d.height + 3);
    }
  }

  function drawParticles(dt, dCam) {
    const shift = (dCam * PX_PER_PT) / P;
    for (const p of particles) {
      const pts = ptsAtRow(p.y);
      const inWater = (pts > 0 && pts < SEABED) || (pts > FAR_SEABED && pts < END);
      const hot = pts > 900 && pts < 2 * CENTRE - 900;
      // Water: marine snow drifts down and bubbles drift up. Rock: dust, or embers when it's hot.
      p.y -= shift + (inWater ? (p.s < 0.3 ? 4 : -0.8) : hot ? 2.5 : 0) * dt;
      p.x += Math.sin(p.ph + p.y * 0.05) * 0.1;
      if (p.y < -3 || p.y > h + 3) Object.assign(p, newParticle(false), { y: p.y < -3 ? h + 2 : -2 });
      if (pts < 0 || pts > END) continue;
      const streak = Math.abs(shift) > h ? 0 : Math.min(4, Math.abs(shift) * 0.4) | 0;
      if (inWater) ctx.fillStyle = p.s < 0.3 ? "rgba(190,235,255,0.55)" : "rgba(220,235,245,0.35)";
      else if (hot) ctx.fillStyle = p.s < 0.5 ? "rgba(255,190,80,0.8)" : "rgba(255,120,40,0.6)";
      else ctx.fillStyle = "rgba(230,210,180,0.3)";
      ctx.fillRect(Math.round(p.x), Math.round(p.y), 1, 1 + streak);
    }
  }

  function drawDepthShade() {
    // Darken the edges more as the light goes, then warm them as the Earth heats up.
    const pts = cam;
    const g = ctx.createRadialGradient(w / 2, h * ANCHOR, h * 0.25, w / 2, h * ANCHOR, h * 0.9);
    const dark = pts < SEABED ? Math.min(0.55, pts / 700) : pts < 1900 ? 0.5 : 0.2;
    g.addColorStop(0, "rgba(0,0,0,0)"); g.addColorStop(1, `rgba(0,0,0,${dark})`);
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  }

  function frame(now) {
    const t = now / 1000;
    const dt = Math.min(0.05, lastT ? t - lastT : 0);
    lastT = t;
    if (camDur) {
      const f = Math.min(1, (now - camT0) / camDur);
      cam = camFrom + (camTo - camFrom) * ease(f);
      if (f >= 1) camDur = 0;
    }
    const dCam = cam - lastCam;
    moving = Math.abs(dCam) > 0.01;
    lastCam = cam;

    drawBackground(t);
    drawLightRays(t);
    drawTrench();
    drawThings(t, dt);
    drawSeabed(SEABED, false);
    if (dig) drawSeabed(FAR_SEABED, true);
    drawTunnel(t);
    drawParticles(dt, dCam);
    drawSky(t, rowAtPts(0), false);
    if (dig) drawSky(t, rowAtPts(END), true);
    drawDepthShade();

    factsTrack.style.transform = `translateY(${-cam * PX_PER_PT}px)`;
    for (const fn of listeners) fn(cam);
    requestAnimationFrame(frame);
  }

  function init() {
    canvas = document.getElementById("sea");
    ctx = canvas.getContext("2d");
    factsTrack = document.getElementById("factsTrack");
    populate();
    resize();
    buildFacts();
    addEventListener("resize", resize);
    requestAnimationFrame(frame);
  }

  window.Scene = {
    PX_PER_PT, ROUTE, SEABED, CENTRE, FAR_SEABED, END,
    init, goTo, layerAt, kmAt,
    onCamera(fn) { listeners.push(fn); },
    // [{ pts, color }] for other players' drills; [] to clear.
    setMates(list) { mates = list; },
    setDig(on) { if (dig !== !!on) { dig = !!on; if (factsTrack) buildFacts(); } },
    get cam() { return cam; },
  };
})();

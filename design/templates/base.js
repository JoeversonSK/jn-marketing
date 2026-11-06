/* =========================================================
   JN Higienização — componentes compartilhados dos templates
   - ícones de linha (grade 64x64, traço arredondado)
   - formas orgânicas de água (blobs, bolhas, gotas)
   - texto rico simples, ajuste automático de fonte, checagem de layout
   ========================================================= */
(function () {
  const JN = {};

  /* ---------- ícones de linha (todos desenhados para a marca) ---------- */
  const I = {
    sofa: '<path d="M13 31v-8a8 8 0 0 1 8-8h22a8 8 0 0 1 8 8v8"/><path d="M32 15.5V31"/><path d="M8 35a5 5 0 0 1 10 0v4h28v-4a5 5 0 0 1 10 0v11a3 3 0 0 1-3 3H11a3 3 0 0 1-3-3z"/><path d="M14 49v5M50 49v5"/>',
    colchao: '<rect x="7" y="25" width="50" height="22" rx="6"/><path d="M7 35h50"/><path d="M15 25v-5a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v5"/><path d="M12 47v5M52 47v5"/><circle cx="20" cy="41" r=".6"/><circle cx="32" cy="41" r=".6"/><circle cx="44" cy="41" r=".6"/>',
    cadeira: '<path d="M20 8h24a3 3 0 0 1 3 3v20H17V11a3 3 0 0 1 3-3z"/><path d="M13 31h38a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2H13a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2z"/><path d="M17 40v16M47 40v16"/><path d="M24 18h16"/>',
    poltrona: '<path d="M16 31V19a9 9 0 0 1 9-9h14a9 9 0 0 1 9 9v12"/><path d="M9 33a5 5 0 0 1 10 0v6h26v-6a5 5 0 0 1 10 0v11a3 3 0 0 1-3 3H12a3 3 0 0 1-3-3z"/><path d="M16 47l-2 7M48 47l2 7"/>',
    tapete: '<rect x="12" y="12" width="40" height="40" rx="3"/><path d="M32 22l10 10-10 10-10-10z"/><path d="M17 6v6M25 6v6M33 6v6M41 6v6M47 6v6M17 52v6M25 52v6M33 52v6M41 52v6M47 52v6"/>',
    gota: '<path d="M32 7S15 26 15 39a17 17 0 0 0 34 0C49 26 32 7 32 7z"/><path d="M24 41a8 8 0 0 0 7 8"/>',
    acaro: '<ellipse cx="32" cy="36" rx="11" ry="13"/><circle cx="32" cy="18" r="5"/><path d="M29 14l-4-6M35 14l4-6"/><path d="M21 30l-8-5-3-7M21 36H11l-4 4M21 42l-8 4-3 7M24 47l-5 8"/><path d="M43 30l8-5 3-7M43 36h10l4 4M43 42l8 4 3 7M40 47l5 8"/><path d="M32 26v20"/>',
    mancha: '<rect x="8" y="8" width="48" height="48" rx="6"/><path d="M14 14h36v36H14z" stroke-dasharray="3 4" stroke-width="2"/><path d="M27 18c6-4 13 0 14 6 6 1 9 8 5 13 3 6-3 12-9 10-4 5-12 4-14-2-6-1-9-8-5-12-3-6 2-14 9-15z"/>',
    odor: '<path d="M18 54c-7-6 7-10 0-17s7-11 0-18"/><path d="M32 54c-7-6 7-10 0-17s7-11 0-18"/><path d="M46 54c-7-6 7-10 0-17s7-11 0-18"/><path d="M15 10h6M29 8h6M43 10h6"/>',
    encardido: '<path d="M13 31v-8a8 8 0 0 1 8-8h22a8 8 0 0 1 8 8v8"/><path d="M8 35a5 5 0 0 1 10 0v4h28v-4a5 5 0 0 1 10 0v11a3 3 0 0 1-3 3H11a3 3 0 0 1-3-3z"/><path d="M14 49v5M50 49v5"/><circle cx="12" cy="34" r="1.2"/><circle cx="15" cy="38" r="1.2"/><circle cx="51" cy="35" r="1.2"/><circle cx="53" cy="39" r="1.2"/><circle cx="26" cy="24" r="1.2"/><circle cx="38" cy="22" r="1.2"/><circle cx="31" cy="27" r="1.2"/>',
    calendario: '<rect x="9" y="14" width="46" height="41" rx="7"/><path d="M9 26h46M21 8v11M43 8v11"/><path d="M23 41l6 6 12-12"/>',
    relogio: '<circle cx="32" cy="32" r="23"/><path d="M32 18v14l9 6"/>',
    check: '<path d="M15 33l11 11 23-24"/>',
    camera: '<path d="M9 23a4 4 0 0 1 4-4h8l4-6h14l4 6h8a4 4 0 0 1 4 4v24a4 4 0 0 1-4 4H13a4 4 0 0 1-4-4z"/><circle cx="32" cy="34" r="9"/>',
    chat: '<path d="M13 12h38a5 5 0 0 1 5 5v22a5 5 0 0 1-5 5H29l-11 9v-9h-5a5 5 0 0 1-5-5V17a5 5 0 0 1 5-5z"/><path d="M20 24h24M20 32h16"/>',
    seta: '<path d="M13 32h37M36 18l14 14-14 14"/>',
    local: '<path d="M32 57S15 40 15 27a17 17 0 0 1 34 0c0 13-17 30-17 30z"/><circle cx="32" cy="27" r="6"/>',
    brilho: '<path d="M30 8c2 12 7 17 19 19-12 2-17 7-19 19-2-12-7-17-19-19 12-2 17-7 19-19z"/><path d="M50 42c1 5 3 7 8 8-5 1-7 3-8 8-1-5-3-7-8-8 5-1 7-3 8-8z"/>',
    casa: '<path d="M8 30L32 11l24 19"/><path d="M15 25v28h34V25"/><path d="M27 53V40h10v13"/>',
    pergunta: '<circle cx="32" cy="32" r="23"/><path d="M25 25a7 7 0 1 1 10 6c-2 1-3 3-3 5v2"/><circle cx="32" cy="46" r=".8"/>',
  };

  JN.icone = function (nome, opts = {}) {
    const sw = opts.traco || 3.2;
    const corpo = I[nome];
    if (!corpo) throw new Error("ícone desconhecido: " + nome);
    return `<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${corpo}</svg>`;
  };
  JN.ico = (nome, px, extra = "", traco) =>
    `<span class="ico ${extra}" style="width:${px}px;height:${px}px">${JN.icone(nome, { traco })}</span>`;
  JN.ICONES = Object.keys(I);

  /* ---------- formas orgânicas ---------- */
  function prng(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  /* blob suave (Catmull-Rom fechado -> Bézier) num quadro 0..100 */
  JN.blob = function (seed = 1, n = 7, irregular = 0.16) {
    const r = prng(seed), pts = [];
    for (let i = 0; i < n; i++) {
      const ang = (i / n) * Math.PI * 2 + (r() - 0.5) * 0.35;
      const rad = 50 * (1 - irregular + r() * irregular * 2) * 0.96;
      pts.push([50 + Math.cos(ang) * rad, 50 + Math.sin(ang) * rad]);
    }
    let d = `M${pts[0][0].toFixed(2)} ${pts[0][1].toFixed(2)}`;
    for (let i = 0; i < n; i++) {
      const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
      const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += `C${c1[0].toFixed(2)} ${c1[1].toFixed(2)} ${c2[0].toFixed(2)} ${c2[1].toFixed(2)} ${p2[0].toFixed(2)} ${p2[1].toFixed(2)}`;
    }
    return d + "Z";
  };
  /* <svg> posicionado com um blob preenchido */
  JN.formaBlob = function ({ x, y, w, h, cor, seed = 1, n = 7, irregular = 0.16, opacidade = 1, rot = 0, cls = "" }) {
    return `<svg class="${cls}" viewBox="0 0 100 100" preserveAspectRatio="none" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;opacity:${opacidade};transform:rotate(${rot}deg)"><path d="${JN.blob(seed, n, irregular)}" fill="${cor}"/></svg>`;
  };
  /* bolha desenhada: contorno + reflexo em arco */
  JN.bolha = function ({ x, y, r, cor = "var(--agua)", traco = 3, opacidade = 1, cheia = false, cls = "" }) {
    const s = r * 2 + traco * 2, c = s / 2;
    const ar = r * 0.62;
    const a0 = (200 * Math.PI) / 180, a1 = (250 * Math.PI) / 180;
    const p0 = [c + Math.cos(a0) * ar, c + Math.sin(a0) * ar], p1 = [c + Math.cos(a1) * ar, c + Math.sin(a1) * ar];
    const reflexo = r > 14 ? `<path d="M${p0[0].toFixed(1)} ${p0[1].toFixed(1)} A${ar} ${ar} 0 0 1 ${p1[0].toFixed(1)} ${p1[1].toFixed(1)}" stroke="${cor}" stroke-width="${traco}" stroke-linecap="round" fill="none"/>` : "";
    const corpo = cheia
      ? `<circle cx="${c}" cy="${c}" r="${r}" fill="${cor}"/>`
      : `<circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="${cor}" stroke-width="${traco}"/>${reflexo}`;
    return `<svg class="${cls}" viewBox="0 0 ${s} ${s}" style="left:${x - c}px;top:${y - c}px;width:${s}px;height:${s}px;opacity:${opacidade}">${corpo}</svg>`;
  };
  /* gota preenchida (ponta para cima) */
  JN.gota = function ({ x, y, h, cor = "var(--agua)", opacidade = 1, cls = "" }) {
    const w = h * 0.72;
    return `<svg class="${cls}" viewBox="0 0 72 100" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;opacity:${opacidade}"><path d="M36 0C36 0 0 42 0 64a36 36 0 0 0 72 0C72 42 36 0 36 0z" fill="${cor}"/></svg>`;
  };
  /* onda horizontal (faixa inferior) */
  JN.onda = function ({ y, h, cor, amp = 0.35, cls = "" }) {
    return `<svg class="${cls}" viewBox="0 0 1080 100" preserveAspectRatio="none" style="left:0;top:${y}px;width:1080px;height:${h}px"><path d="M0 ${40 * amp + 30}C240 ${-10 * amp} 420 ${120 * amp} 640 ${50 * amp + 20}S960 ${-20 * amp + 10} 1080 ${30 * amp + 20}V100H0Z" fill="${cor}"/></svg>`;
  };

  /* ---------- texto ---------- */
  const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  /* *destaque* -> cor de acento | _oferta_ -> limão | \n -> quebra | ~ -> espaço inseparável */
  JN.rico = function (s) {
    return esc(s)
      .replace(/\*(.+?)\*/g, '<span class="acento">$1</span>')
      .replace(/_(.+?)_/g, '<span class="limao">$1</span>')
      .replace(/~/g, "&nbsp;")
      .replace(/\n/g, "<br>");
  };
  JN.esc = esc;

  /* ---------- assinatura ---------- */
  JN.marca = (comNome = true) =>
    `<div class="marca"><img src="../logo-simbolo.svg" alt="">${comNome ? "<span>JN Higienização</span>" : ""}</div>`;
  JN.rodape = (s = {}) =>
    `<div class="rodape"><span class="handle">${esc(s.instagram || "@jn_.higienizacao")}</span><span>${s.rodape_dir ? JN.rico(s.rodape_dir) : esc(s.cidades || "Juazeiro do Norte · Barbalha")}</span></div>`;
  JN.cta = (texto, sub, variante = "") =>
    `<div class="cta ${variante}"><div>${JN.rico(texto)}${sub ? `<small>${JN.rico(sub)}</small>` : ""}</div><span class="seta">${JN.ico("seta", 44, "", 4)}</span></div>`;
  /* bloco de oferta; fundo = {seed, ...} desenha um blob royal preso ao bloco */
  /* anim: { fundo|valor|quem: "tipo:atraso" } ex.: "escala:0.3" (usado nos reels) */
  const an = (v) => { if (!v) return ["", ""]; const [t, d] = v.split(":"); return [`a a-${t}`, `animation-delay:${d || 0}s;`]; };
  JN.oferta = (o = {}, tamanho = 260, fundo = null, anim = {}) => `
    <div class="oferta">
      ${fundo ? `<div class="fundo-oferta ${an(anim.fundo)[0]}" style="${an(anim.fundo)[1]}left:${fundo.x ?? -240}px;top:${fundo.y ?? -90}px;right:${fundo.r ?? -60}px;bottom:${fundo.b ?? -90}px"><svg viewBox="0 0 100 100" preserveAspectRatio="none" style="transform:rotate(${fundo.rot ?? -5}deg)"><path d="${JN.blob(fundo.seed ?? 11, 7, 0.14)}" fill="${fundo.cor || "var(--royal)"}"/></svg></div>` : ""}
      <div class="valor ${an(anim.valor)[0]}" style="${an(anim.valor)[1]}font-size:${tamanho}px">${esc(o.valor || "20")}<span class="pct">%</span><span class="off"><span>OFF</span></span></div>
      ${o.para ? `<div class="quem ${an(anim.quem)[0]}" style="${an(anim.quem)[1]}">${JN.rico(o.para)}</div>` : ""}
    </div>`;
  JN.itens = (lista) => `<ul class="itens">${lista.map((it) => `<li>${JN.ico(it.icone, 56)}${esc(it.nome)}</li>`).join("")}</ul>`;
  /* ícone dentro de um blob (selo orgânico) */
  JN.seloIcone = ({ icone, tam = 260, cor = "var(--royal)", corIcone = "var(--branco)", seed = 3, traco = 3 }) =>
    `<div class="selo-blob" style="width:${tam}px;height:${tam}px;color:${corIcone}"><svg viewBox="0 0 100 100" class="sb-fundo"><path d="${JN.blob(seed, 6, 0.1)}" fill="${cor}"/></svg>${JN.ico(icone, Math.round(tam * 0.5), "", traco)}</div>`;
  /* barra de progresso do carrossel */
  JN.progresso = (atual, total) =>
    `<div class="progresso">${Array.from({ length: total }, (_, i) => `<i class="${i + 1 === atual ? "on" : i + 1 < atual ? "ja" : ""}"></i>`).join("")}</div>`;
  JN.ITENS_PADRAO = [
    { icone: "sofa", nome: "Sofás" },
    { icone: "colchao", nome: "Colchões" },
    { icone: "cadeira", nome: "Cadeiras" },
    { icone: "poltrona", nome: "Poltronas" },
    { icone: "tapete", nome: "Tapetes" },
  ];

  /* ---------- ajuste automático de fonte ---------- */
  /* elementos com data-fit="min" encolhem até caber na largura e no data-max-h */
  JN.ajustar = function () {
    document.querySelectorAll("[data-fit]").forEach((el) => {
      const min = parseFloat(el.dataset.fit) || 40;
      const maxH = parseFloat(el.dataset.maxH || "0");
      let fs = parseFloat(getComputedStyle(el).fontSize);
      const estoura = () => el.scrollWidth > el.clientWidth + 1 || (maxH && el.getBoundingClientRect().height > maxH);
      while (estoura() && fs > min) { fs -= 2; el.style.fontSize = fs + "px"; }
    });
  };

  /* ---------- checagem de qualidade (lida pelo render.py) ---------- */
  JN.checar = function () {
    const avisos = [];
    const cv = document.querySelector(".canvas");
    if (!cv) return ["sem .canvas"];
    const R = cv.getBoundingClientRect();
    const story = cv.classList.contains("story");
    const nomeEl = (el) => el.className && typeof el.className === "string" ? "." + el.className.split(" ")[0] : el.tagName.toLowerCase();
    cv.querySelectorAll(".conteudo *").forEach((el) => {
      if (el.closest(".deco, .fundo-oferta, [data-deco], svg")) return;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) return;
      if (r.left < R.left - 1 || r.right > R.right + 1 || r.top < R.top - 1 || r.bottom > R.bottom + 1)
        avisos.push(`fora do canvas: ${nomeEl(el)} "${(el.textContent || "").trim().slice(0, 30)}"`);
      if (el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow !== "visible")
        avisos.push(`texto cortado na largura: ${nomeEl(el)}`);
      if (story && !el.closest("[data-livre]") && el.children.length === 0 && el.textContent.trim()) {
        if (r.top - R.top < 240 || R.bottom - r.bottom < 240)
          avisos.push(`texto na zona de interface do story: ${nomeEl(el)} "${el.textContent.trim().slice(0, 30)}"`);
      }
    });
    const c = cv.querySelector(".conteudo");
    if (c && c.scrollHeight > c.clientHeight + 2) avisos.push(`conteúdo excede a área útil em ${c.scrollHeight - c.clientHeight}px`);
    return [...new Set(avisos)];
  };

  /* ---------- montagem ---------- */
  JN.montar = async function (renderizar, demo) {
    const spec = Object.assign({}, demo, window.SPEC || {});
    if (window.ANIMAR) document.documentElement.classList.add("animar");
    document.body.innerHTML = renderizar(spec);
    await document.fonts.ready;
    await Promise.all([...document.images].map((im) => (im.complete ? 0 : new Promise((r) => (im.onload = im.onerror = r)))));
    JN.ajustar();
    window.JN_PRONTO = true;
  };

  window.JN = JN;
})();
JN.chips = (lista) => `<div class="chips">${lista.map((it) => `<span class="chip">${JN.ico(it.icone, 50)}${JN.esc(it.nome)}</span>`).join("")}</div>`;

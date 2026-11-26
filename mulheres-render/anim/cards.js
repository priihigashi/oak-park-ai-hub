/* Versão bonita da automação News: cenas desenhadas nos templates do Painel da Manhã
   (painel-da-manha.vercel.app/templates/, 35 cards reconstruídos dos posts dela). Palco 1080x1920.
   Contrato da cena no manifesto: {type:"card", card:"05", start, end, campos:{...}}; itens/pessoas podem ter
   "t" (segundo absoluto em que a palavra-gatilho é falada, calculado pelo producao.py a partir de "entra").
   CARDS.html(cena, t, palavras) é função PURA do tempo: player, quadros da auditoria e MP4 usam a mesma linha.
   Zona segura dela (1080x1920): conteúdo essencial (classe "zs" e a legenda) entre x 150-915 e y 268-1680;
   rodapé fixo: @handle em y 1626 e fonte em y 1668 (sem colidir; fonte longa quebra em 2-3 linhas pequenas, nunca "…").
   Legenda: 2 linhas cheias por página, paginada pela largura medida no navegador (nunca 3ª linha).
   23/11 (auditorias Dosimetria, PL 2374, Semana: mesmos defeitos em toda versão, consertado AQUI e não por peça):
   TODO texto passa por texto(): mede cada palavra (no DOM, depois das fontes carregadas, com folga de 2,5%; fonte real, letter-spacing e o
   recuo do destaque), escolhe o MAIOR corpo que cabe em x 150-915 e na altura reservada, e quebra as linhas
   equilibradas com a regra dela: destaque colorido nunca sozinho numa linha e nunca partido (se der pra evitar),
   número/ano/data/"PL 2374/2024" nunca separado, e-mail/URL só quebra em ponto seguro (depois de "." ou "/",
   antes de "@") sem trocar caractere. As linhas saem explícitas (span.ln, nowrap): o navegador não requebra.
   Cada card empilha os blocos com cursor (nada de topo fixo que encavala) e, se passar da legenda (y 1450),
   redesenha com corpo menor (k). Fundo do destaque (.hl) pinta ATRÁS de todas as linhas (z-index -1 num bloco
   isolado): antes o fundo da 2ª linha cobria a 1ª nos títulos condensados ("RELATOR RECOMENDA" cortado).
   Entrada animada usa a propriedade `translate` (não sobrescreve escala/rotação); CARDS.medir mede o texto REAL
   (Range.getClientRects, caixa de tinta, fundo do destaque) no fim da animação e aponta fora/sobreposto/cortado. */
(function (G) {
  const E = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const cl = (x, a, b) => Math.max(a, Math.min(b, x));
  const ease = x => 1 - Math.pow(1 - cl(x, 0, 1), 3);
  const p = (tl, t0, d = 0.45) => ease((tl - t0) / d);
  /* 23/11 (pedido dela: "não é pra usar igual", acervo = inspiração): a direção de entrada é escolhida por cena
     (campo "entrada": baixo|cima|esquerda|direita|escala). ENT é ligada por html() antes de desenhar a cena. */
  let ENT = 'baixo', CAPA = false; // CAPA (24/11 A1): 1ª cena do vídeo já nasce pronta no quadro 0 (miniatura do Instagram não sai vazia)
  const ent = (tl, t0, d = 0.45, dy = 40) => { const k = CAPA && t0 < 1 ? 1 : p(tl, t0, d), m = (1 - k) * dy, o = `opacity:${k.toFixed(3)};`;
    if (ENT === 'escala') return o + `scale:${(0.88 + 0.12 * k).toFixed(3)};`;
    if (ENT === 'esquerda' || ENT === 'direita') return o + `translate:${((ENT === 'esquerda' ? -1.6 : 1.6) * m).toFixed(1)}px 0;`;
    return o + `translate:0 ${((ENT === 'cima' ? -1 : 1) * m).toFixed(1)}px;`; };
  const X0 = 150, X1 = 915, LARG = X1 - X0, Y0 = 268, LIM = 1450; // LIM: conteúdo termina acima da legenda (2 linhas, topo 1470)
  /* 23/11: corpos mínimos legíveis no palco 1080 (skill reel-zona-segura: frase-guia 64, letra miúda 30, texto que
     precisa ser lido 23-24, fonte/crédito 20-22). Ela confere no iPhone grande; o público tem celular menor. */
  const MIN_TIT = 64, MIN_ETQ = 30, MIN_LER = 24, MIN_FONTE = 20;

  // ---------- medida e quebra de texto ----------
  const ESTIMA = { 'Patrick Hand SC': 0.5, 'Inter Tight': 0.52, Rubik: 0.62, Anton: 0.48, 'JetBrains Mono': 0.62, 'DM Serif Display': 0.56 }; // fora do navegador (node)
  const FAMCSS = { 'Patrick Hand SC': "'Patrick Hand SC',cursive", 'Inter Tight': "'Inter Tight',Arial,sans-serif", Rubik: 'Rubik,sans-serif', Anton: 'Anton,Impact,sans-serif', 'JetBrains Mono': "'JetBrains Mono',monospace", 'DM Serif Display': "'DM Serif Display',Georgia,serif" };
  /* 23/11 (Semana v3 no GitHub: "Fonte: Autógrafo do PLP 299/2026, 19/11/2026; Agência Senado" medido 756 px no canvas,
     desenhado 780 px no Chromium do runner, que arredonda o avanço de cada letra pro pixel inteiro: 12,6 -> 13 px).
     Agora: (1) a medida sai do PRÓPRIO DOM (span escondido, mesma pilha de fontes do CSS, mesma regra de desenho),
     não do canvas; (2) o palco e o medidor desenham com text-rendering:geometricPrecision (sem arredondar avanço,
     igual em qualquer máquina/escala); (3) nada é guardado em cache antes de document.fonts terminar de carregar, e
     o cache é zerado quando uma fonte termina de carregar (CARDS.pronto() espera tudo); (4) folga de 2,5% na largura. */
  const FOLGA = 0.025;
  let _cv = null, _mh = null, _w = new Map(), _lay = new Map(), _cache = new WeakMap(); // _cache: páginas da legenda
  const fonteOk = (peso, fam) => typeof document === 'undefined' || !document.fonts ||
    (document.fonts.status === 'loaded' && document.fonts.check(`${peso} 50px "${fam}"`));
  function medidor() { // span escondido no body: mede como o navegador desenha (pilha de fontes, peso, kerning)
    if (_mh && _mh.isConnected) return _mh;
    if (typeof document === 'undefined' || !document.createElement || !document.body) return null;
    const d = document.createElement('div'); d.setAttribute('aria-hidden', 'true'); d.setAttribute('data-deco', '');
    d.style.cssText = 'position:absolute;left:-100000px;top:0;visibility:hidden;pointer-events:none;white-space:pre;' +
      'text-rendering:geometricPrecision;font-kerning:normal;letter-spacing:0;text-transform:none;line-height:1';
    _mh = document.createElement('span'); d.appendChild(_mh); document.body.appendChild(d); return _mh;
  }
  function w100(txt, fam, peso) { // largura a 100px, sem letter-spacing
    const key = fam + '|' + peso + '|' + txt; if (_w.has(key)) return _w.get(key);
    let w = null; const sp = medidor();
    if (sp) { sp.style.font = `${peso} 100px ${FAMCSS[fam] || fam}`; sp.textContent = txt; w = sp.getBoundingClientRect().width; }
    if (w === null) {
      if (_cv === null) { _cv = false; if (typeof document !== 'undefined' && document.createElement) { const cv = document.createElement('canvas'); _cv = (cv.getContext && cv.getContext('2d')) || false; } }
      if (!_cv) return [...txt].length * 100 * (ESTIMA[fam] || 0.62); // fora do navegador (node): estimativa
      _cv.font = `${peso} 100px ${FAMCSS[fam] || fam}`; w = _cv.measureText(txt).width;
    }
    if (fonteOk(peso, fam)) _w.set(key, w);
    return w;
  }
  function limpar() { _w = new Map(); _lay = new Map(); _cache = new WeakMap(); }
  if (typeof document !== 'undefined' && document.fonts && document.fonts.addEventListener) document.fonts.addEventListener('loadingdone', limpar);
  // CARDS.pronto(): espera TODAS as fontes do renderizador (e as que a página declarou) e zera o cache de medidas
  async function pronto() {
    if (typeof document === 'undefined' || !document.fonts) return;
    const lista = [['Rubik', 400], ['Rubik', 600], ['Rubik', 700], ['Rubik', 800], ['Rubik', 900], ['Anton', 400], ['DM Serif Display', 400], ['JetBrains Mono', 400], ['JetBrains Mono', 700], ['Inter Tight', 700], ['Patrick Hand SC', 400]];
    await Promise.all(lista.map(([f, p]) => document.fonts.load(`${p} 50px "${f}"`).catch(() => null)));
    await document.fonts.ready; limpar();
  }
  // e-mail/URL: pode quebrar em ponto seguro; número nunca
  const QUEBRAVEL = t => !/^[\d(]/.test(t) && (/\S@\S/.test(t) || /^(https?:\/\/|www\.)/i.test(t) || (/^[\w-]+(\.[\w-]+)+(\/\S*)?$/.test(t) && /\.[a-z]{2,}/i.test(t) && t.length > 14));
  function pedacos(tok) { // depois de "." e "/", antes de "@"; pedaços de pelo menos 4 caracteres; sem trocar caractere
    const out = []; let ini = 0;
    for (let i = 1; i < tok.length; i++) { const a = tok[i - 1], b = tok[i];
      if ((a === '.' || a === '/' || b === '@') && i - ini >= 4 && tok.length - i >= 4) { out.push(tok.slice(ini, i)); ini = i; } }
    out.push(tok.slice(ini)); return out;
  }
  const COLA_ANTES = /^(R\$|US\$|§+|nº|n\.º|art\.|arts\.|lei|pl|plp|pec|adi|adis|mp)$/i;
  const COLA_DEPOIS = /^(%|bi|mi|mil|anos?|meses|dias|horas|tri)[.,;:!?)]*$/i;
  function tokens(txt) {
    const out = []; const re = /\S+/g; let m;
    while ((m = re.exec(txt))) {
      const ps = QUEBRAVEL(m[0]) ? pedacos(m[0]) : [m[0]]; let off = m.index;
      ps.forEach((x, i) => { out.push({ a: off, b: off + x.length, sp: i === 0 && out.length > 0 }); off += x.length; });
    }
    for (let i = 1; i < out.length; i++) { // "PL 2374/2024", "R$ 14", "11 anos", "72 %" ficam juntos
      const ant = txt.slice(out[i - 1].a, out[i - 1].b), cur = txt.slice(out[i].a, out[i].b);
      if (out[i].sp && ((COLA_ANTES.test(ant) && /^[\d§]/.test(cur)) || (/^[+=×x−-]$/.test(ant) && /^\d/.test(cur)) || (/\d$/.test(ant) && COLA_DEPOIS.test(cur)))) { out[i - 1].b = out[i].b; out.splice(i, 1); i--; }
    }
    return out;
  }
  function trecho(txt, a, b, ha, hb, cls) {
    if (ha < 0 || hb <= a || ha >= b) return E(txt.slice(a, b));
    const x = Math.max(a, ha), y = Math.min(b, hb);
    return E(txt.slice(a, x)) + `<span class="${cls}">` + E(txt.slice(x, y)) + '</span>' + E(txt.slice(y, b));
  }
  /* texto(txt, o) -> {fs, n, h, w, html, linhas, ok}
     o: f (família), p (peso), base, min (menor corpo legível), piso (só pra caber, abaixo do min), larg, maxLin,
        alt (altura máxima), lh, ls (em), up (caixa alta), sy (escala vertical), dest + cls (destaque),
        fim {txt, max, rel, p} (sufixo menor na última linha). */
  function WSP(o) { return o.wsp ?? (o.f === 'Inter Tight' ? 0.12 : 0); }
  function texto(txt, o) {
    txt = String(txt ?? '').replace(/\s+/g, ' ').trim();
    const key = JSON.stringify([txt, o.f, o.p, o.base, o.min, o.piso, o.larg, o.maxLin, o.alt, o.lh, o.ls, o.up, o.sy, o.dest, o.cls, o.fim]);
    if (_lay.has(key)) return _lay.get(key);
    const lh = o.lh || 1.1, sy = o.sy || 1, tk = tokens(txt), n = tk.length;
    const pedaco = x => { const t = txt.slice(x.a, x.b); return o.up ? t.toUpperCase() : t; };
    const ws = tk.map(x => w100(pedaco(x), o.f, o.p)), nch = tk.map(x => [...pedaco(x)].length), esp = w100(' ', o.f, o.p);
    let ha = -1, hb = -1;
    if (o.dest) { const i = txt.toLowerCase().indexOf(String(o.dest).toLowerCase().trim()); if (i >= 0) { ha = i; hb = i + String(o.dest).trim().length; } }
    const emD = tk.map(x => ha >= 0 && x.a < hb && x.b > ha), temFora = emD.some(x => !x);
    const pad = o.cls === 'hl' ? 22 : 0;
    const solta = (i, j) => { if (ha < 0 || n < 5) return false; let dn = 0, fo = 0; for (let q = i; q <= j; q++) emD[q] ? dn++ : fo++; return fo === 1 && dn >= 2; };
    const fimW = s => o.fim ? w100(o.fim.txt, o.f, o.fim.p || o.p) * Math.min(o.fim.max, Math.round(s * o.fim.rel)) / 100 : 0;
    function resolver(s, L) {
      const k = s / 100, lsx = (o.ls || 0) * s, wsx = WSP(o) * s;
      const lw = (i, j) => { let w = 0, d = false;
        for (let q = i; q <= j; q++) { w += ws[q] * k + lsx * nch[q] + (q > i && tk[q].sp ? esp * k + lsx + wsx : 0); d = d || emD[q]; }
        return w + (d ? pad : 0) + (j === n - 1 ? fimW(s) : 0) + 2; };
      const custo = (i, j) => {
        const w = lw(i, j); if (w > o.larg * (1 - FOLGA)) return Infinity;      // folga de 2,5% pra diferença de desenho
        let c = ((o.larg - w) / o.larg) ** 2;
        if (temFora && emD.slice(i, j + 1).every(Boolean)) c += 1e6;      // destaque colorido sozinho na linha: proibido
        if (j < n - 1 && emD[j] && emD[j + 1]) c += 1e4;                   // destaque partido entre linhas
        if (j < n - 1 && !tk[j + 1].sp) c += 0.3;                          // quebra dentro de e-mail/URL (ponto seguro)
        if (i === j && n >= 3) c += 1e4;                                   // palavra sozinha na linha (regra dela): corpo menor antes
        /* 23/11 (prints das variações: "luz" sozinho na linha do título). Linhas equilibradas, regra dela: nenhuma
           linha com 1 ou 2 palavras quando dá pra equilibrar (texto com 5+ palavras), e palavra comum solta ao lado do
           destaque (1 palavra sem cor + 2 ou mais com cor na mesma linha) evitada quando outra quebra resolve. */
        if (n >= 5 && j - i === 1) c += 1e3;
        if (solta(i, j)) c += 600;
        return c; };
      const best = Array.from({ length: n + 1 }, () => new Array(L + 1).fill(Infinity)), de = Array.from({ length: n + 1 }, () => new Array(L + 1).fill(-1));
      best[0][0] = 0;
      for (let l = 1; l <= L; l++) for (let j = 1; j <= n; j++) for (let i = j - 1; i >= 0; i--) {
        const c = custo(i, j - 1); if (c === Infinity) break;
        if (best[i][l - 1] === Infinity) continue;
        const v = best[i][l - 1] + c; if (v < best[j][l]) { best[j][l] = v; de[j][l] = i; }
      }
      let m = Infinity, lb = 0; for (let l = 1; l <= L; l++) if (best[n][l] < m) { m = best[n][l]; lb = l; }
      if (m === Infinity) return null;
      const linhas = []; let j = n; for (let l = lb; l > 0; l--) { const i = de[j][l]; linhas.unshift([i, j - 1]); j = i; }
      return { s, custo: m, linhas, w: Math.max(...linhas.map(([i, j]) => lw(i, j))), solta: linhas.some(([i, j]) => solta(i, j)) };
    }
    const maxL = s => Math.max(1, Math.min(o.maxLin || 9, o.alt ? Math.floor(o.alt / (s * lh * sy) + 1e-6) : 9));
    const piso = o.piso ?? Math.min(o.min, 14), nivel = r => (r.custo >= 1e6 ? 2 : r.custo >= 1e4 ? 1 : 0);
    let s = Math.round(o.base), res = null;
    if (!n) res = { s, custo: 0, linhas: [], w: 0 };
    while (n) {
      const r = resolver(s, maxL(s));
      if (r) { if (!res || nivel(r) < nivel(res)) res = r; if (nivel(r) === 0) break; }
      // abaixo do min só pra caber, ou pra não deixar destaque colorido sozinho numa linha (até 75% do min)
      if ((s <= o.min && res && (nivel(res) === 0 || s <= o.min * (nivel(res) === 2 ? 0.75 : 0.85))) || s <= piso) break;
      const nx = Math.max(piso, Math.floor(s * 0.97)); s = nx >= s ? s - 1 : nx;
    }
    let ok = true;
    if (!res) { ok = false; res = { s: piso, custo: Infinity, linhas: tk.map((x, i) => [i, i]), w: o.larg }; } // não cabe nem no piso: o verificador aponta
    const fimH = s => o.fim ? `<span style="font-size:${Math.min(o.fim.max, Math.round(s * o.fim.rel))}px;letter-spacing:0">${E(o.fim.txt)}</span>` : '';
    const html = res.linhas.map(([i, j]) => `<span class="ln">${trecho(txt, tk[i].a, tk[j].b, ha, hb, o.cls)}${j === n - 1 ? fimH(res.s) : ''}</span>`).join(' ') || (o.fim ? `<span class="ln">${fimH(res.s)}</span>` : '');
    /* 25/11 (A2 EL-NINO, q_001500 "UM EL NIÑO", q_004400 "DO PACÍFICO"): Anton em caixa alta com entrelinha < 1 joga o
       acento da maiúscula da 2ª linha pra dentro da linha de cima (til do Ñ virava gancho sob o "DE"). Bloco Anton com
       letra acentuada fora da 1ª linha ganha entrelinha 1.2 (o acento do Anton sobe ~1,07 em); o resto segue com a entrelinha justa do original. */
    const lhx = o.f === 'Anton' && lh < 1.2 && res.linhas.slice(1).some(([i, j]) => /[ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÑ]/.test(txt.slice(tk[i].a, tk[j].b).toUpperCase())) ? 1.2 : lh;
    const out = { fs: res.s, n: Math.max(1, res.linhas.length), h: Math.max(1, res.linhas.length) * res.s * lhx * sy, w: res.w, html, ok, lh: lhx !== lh ? lhx : undefined,
      linhas: res.linhas.map(([i, j]) => txt.slice(tk[i].a, tk[j].b)), regra: res.custo < 1e4, solta: !!res.solta };
    if (fonteOk(o.p, o.f)) _lay.set(key, out);
    return out;
  }
  const RUB = (p, lh = 1.1, ls = 0) => ({ f: 'Rubik', p, lh, ls });
  const TIT = { f: 'Rubik', p: 800, lh: 0.98, ls: -0.035 };
  const ANTON = { f: 'Anton', p: 400, lh: 0.92, ls: -0.005, up: 1 };
  const MONO = { f: 'JetBrains Mono', p: 700, lh: 1.2, ls: 0.06, up: 1 };
  const SERIF = { f: 'DM Serif Display', p: 400, lh: 1.08, ls: 0 };
  /* 25/11 (A2 BIG-TECHS, capa p116 "Poderabsoluto"): o espaço da Inter Tight 700 do subset é estreito e, com letter-spacing
     negativo, as palavras grudavam. Inter Tight ganha word-spacing (medido em texto() e aplicado no CSS). */
  const fonteCss = (o, r) => `font:${o.p} ${r.fs}px/${(r && r.lh) || o.lh} ${FAMCSS[o.f]};letter-spacing:${o.ls || 0}em;${WSP(o) ? `word-spacing:${WSP(o)}em;` : ''}${o.up ? 'text-transform:uppercase;' : ''}${o.sy && o.sy !== 1 ? `transform:scaleY(${o.sy});transform-origin:top left;` : ''}`;
  // bloco de texto posicionado: {r, html, bot}
  function bloco(txt, o, top, extra = '', cls = 'ab') {
    const r = texto(txt, o);
    return { r, bot: top + r.h, html: `<div class="${cls} tx zs" style="top:${top}px;${fonteCss(o, r)}${extra}">${r.html}</div>` };
  }
  const solto = (txt, o, extra = '', cls = '') => { const r = texto(txt, o); return { r, html: `<div class="tx ${cls}" style="${fonteCss(o, r)}${extra}">${r.html}</div>` }; };

  const ICONES = {
    doc: '<rect x="18" y="8" width="64" height="84" rx="6"/><path d="M30 30h40M30 46h40M30 62h28"/>',
    lei: '<path d="M50 10v80M22 26h56M22 26l-12 30h24zM78 26l-12 30h24zM34 90h32"/>',
    dinheiro: '<rect x="8" y="26" width="84" height="48" rx="6"/><circle cx="50" cy="50" r="12"/><path d="M20 38v24M80 38v24"/>',
    // 25/11 (A2 PLP299): barril de petróleo pedido por ela (NOTA-DELA 23/11), sem PNG nas pastas
    // 25/11 (A3 PLP299): cilindro reto lia como ícone de banco de dados; agora barril com bojo, aros e bujão
    barril: '<path d="M28 8h44c10 14 10 70 0 84H28c-10-14-10-70 0-84z"/><path d="M22 28h56M22 72h56"/><circle cx="50" cy="50" r="6"/>',
    pessoa: '<circle cx="50" cy="32" r="16"/><path d="M18 90c0-20 14-32 32-32s32 12 32 32"/>',
    pessoas: '<circle cx="34" cy="34" r="13"/><circle cx="68" cy="34" r="13"/><path d="M8 86c0-16 11-26 26-26s26 10 26 26M42 86c0-16 11-26 26-26s26 10 26 26"/>',
    celular: '<rect x="28" y="6" width="44" height="88" rx="8"/><path d="M44 82h12"/>',
    alerta: '<path d="M50 10L92 88H8z"/><path d="M50 38v24M50 72v4"/>',
    voto: '<rect x="14" y="50" width="72" height="40" rx="4"/><path d="M30 50V22h40v28M38 36l8 8 14-16"/>',
    relogio: '<circle cx="50" cy="50" r="40"/><path d="M50 26v26l16 10"/>',
    martelo: '<path d="M30 20l24 24M22 28l24-24 16 16-24 24zM46 40l36 36-8 8-36-36M14 92h44"/>',
    megafone: '<path d="M14 40v20h14l40 20V20L28 40zM28 60l6 26h12l-6-24"/>',
    check: '<circle cx="50" cy="50" r="40"/><path d="M30 52l14 14 26-30"/>',
    x: '<circle cx="50" cy="50" r="40"/><path d="M34 34l32 32M66 34L34 66"/>',
    grafico: '<path d="M12 88h80M22 88V60M42 88V40M62 88V52M82 88V22"/>',
    casa: '<path d="M10 48L50 12l40 36M20 40v48h60V40M42 88V64h16v24"/>',
    tela: '<rect x="6" y="14" width="88" height="58" rx="6"/><path d="M36 88h28M50 72v16"/>',
  };
  const ico = (n, cor = 'currentColor', w = 6) => `<svg viewBox="0 0 100 100" fill="none" stroke="${cor}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round">${ICONES[n] || ICONES.doc}</svg>`;
  const iniciais = n => String(n || '?').split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join('');
  const rosto = (ps, tam) => `<div class="rec" style="width:${tam}px;height:${tam}px">${ps.foto ? `<img src="${E(ps.foto)}">` : `<b style="font-size:${Math.round(tam / 2.6)}px">${E(iniciais(ps.nome))}</b>`}</div>`;
  // chip de partido/ideologia: cabe na coluna (quebra em 2 linhas pequenas se precisar, nunca vaza)
  const chipH = (ps, larg) => { if (!ps.chip) return { h: 0, html: '' }; const r = texto(ps.chip, { ...RUB(700, 1.2), base: 26, min: MIN_LER, piso: MIN_LER, larg: larg - 34, maxLin: 2 });
    return { h: r.h + 12, html: `<span class="chip tx ${ps.lado === 'esq' ? 'esq' : ps.lado === 'dir' ? 'dir' : 'neu'}" style="font-size:${r.fs}px;${r.n > 1 ? 'border-radius:18px;' : ''}">${r.html}</span>` }; };
  const tItem = (it, k, n, s) => (typeof it.t === 'number' ? it.t - s.start : (s.end - s.start) * (0.15 + 0.7 * k / Math.max(n, 1)));
  // item com destaque próprio (ex.: "75% da pena antes de mudar de regime"): grifa se estiver no texto, senão vai embaixo
  function itemBloco(x, o, cls, larg, extra = '') {
    const d = x.destaque, dentro = d && String(x.texto ?? '').toLowerCase().includes(String(d).toLowerCase());
    const r = texto(x.texto, { ...o, larg, dest: dentro ? d : null, cls });
    let h = r.h, html = `<div class="tx" style="${fonteCss(o, r)}${extra}">${r.html}</div>`;
    if (d && !dentro) { const q = texto(d, { ...o, base: Math.round(r.fs * 0.9), min: Math.min(o.min, 28), larg, maxLin: 3 });
      h += 6 + q.h; html += `<div class="tx sub-dest ${cls}" style="${fonteCss(o, q)}">${q.html}</div>`; }
    return { h, html };
  }
  const rot = (c, cor) => { if (!c.rotulo) return { html: '', bot: Y0 - 20 };
    const r = texto(c.rotulo, { ...MONO, base: 28, min: MIN_LER, piso: MIN_LER, larg: LARG, maxLin: 2, dest: c.rotulo_destaque, cls: 'tc' });
    return { html: `<div class="rotulo tx zs" style="${cor ? 'color:' + cor + ';' : ''}font-size:${r.fs}px">${r.html}</div>`, bot: Y0 + 24 + r.h }; };
  const etq = (txt, larg = LARG - 60) => { const r = texto(txt, { ...RUB(800, 1.2), base: 36, min: MIN_ETQ, piso: MIN_ETQ, larg, maxLin: 2 });
    return { h: r.h + 30, html: (st = '') => `<span class="etiqueta tx" style="font-size:${r.fs}px;${st}">${r.html}</span>` }; };

  const CSS = `
.cpalco{position:absolute;inset:0;width:1080px;height:1920px;overflow:hidden;font-family:Rubik,sans-serif;color:#0B0B0C;text-rendering:geometricPrecision;font-kerning:normal}
.cpalco *{box-sizing:border-box}
.cpalco .papel::before,.cpalco.papel::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.22;mix-blend-mode:multiply;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 .4 0 0 0 0 .35 0 0 0 0 .3 0 0 0 .55 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)'/%3E%3C/svg%3E")}
.cpalco.vinco::after{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(90deg,transparent 49.8%,rgba(0,0,0,.08) 50%,rgba(255,255,255,.35) 50.2%,transparent 50.5%),linear-gradient(0deg,transparent 61.8%,rgba(0,0,0,.06) 62%,rgba(255,255,255,.3) 62.2%,transparent 62.5%)}
.cpalco .rotulo{position:absolute;left:150px;right:165px;top:268px;border-top:4px solid currentColor;padding-top:20px;font:700 28px/1.2 'JetBrains Mono',monospace;letter-spacing:.06em;text-transform:uppercase}
.cpalco .tc{color:var(--tc,#B5482E)}
.cpalco .tcd{color:var(--tcd,var(--tc,#B5482E))}
.cpalco .ab{position:absolute;left:150px;right:165px}
.cpalco .tx{isolation:isolate}
.cpalco .ln{display:block;white-space:nowrap}
.cpalco .titulo{margin:0}
.cpalco .anton{font-family:Anton,Impact,sans-serif;font-weight:400;text-transform:uppercase;letter-spacing:-.005em;line-height:.92}
.cpalco .serif{font-family:'DM Serif Display',Georgia,serif;font-weight:400}
.cpalco .mono{font-family:'JetBrains Mono',monospace;font-weight:700;text-transform:uppercase;letter-spacing:.06em}
.cpalco .rec{flex:none;border-radius:50%;overflow:hidden;background:#d9d2c3;display:grid;place-items:center;color:#0B0B0C;font-weight:900;
  filter:drop-shadow(6px 0 0 #fff) drop-shadow(-6px 0 0 #fff) drop-shadow(0 6px 0 #fff) drop-shadow(0 -6px 0 #fff) drop-shadow(10px 14px 10px rgba(0,0,0,.35))}
.cpalco .rec img{width:100%;height:100%;object-fit:cover;filter:grayscale(1)}
.cpalco .rec img[src^="data:image/svg"]{filter:none} /* 24/11 A1: desenho (lula do governo atual) fica colorido */
.cpalco .chip{display:inline-block;padding:6px 16px;border-radius:999px;font:700 24px/1.2 Rubik;color:#fff}
.cpalco .chip.dir{background:#2F5BEA}.cpalco .chip.esq{background:#E3342B}.cpalco .chip.neu{background:#0B0B0C}
.cpalco .moldura{position:absolute;border:22px solid #FFF9EF;border-radius:46px;overflow:hidden;box-shadow:18px 22px 0 #0B0B0C;transform:rotate(-2deg);background:#2a2a2a;display:grid;place-items:center}
.cpalco .moldura img,.cpalco .moldura video{width:100%;height:100%;object-fit:cover}
.cpalco .estrela4{position:absolute;width:110px;height:110px;background:#FF4A3D;clip-path:polygon(50% 0,61% 39%,100% 50%,61% 61%,50% 100%,39% 61%,0 50%,39% 39%)}
.cpalco .etiqueta{display:inline-block;background:#FFF9EF;color:#0B0B0C;border:4px solid #0B0B0C;border-radius:10px;padding:8px 20px;font:800 30px/1.2 Rubik;box-shadow:6px 6px 0 #0B0B0C}
.cpalco .fonte{position:absolute;left:150px;right:165px;top:1668px;bottom:auto;height:auto;white-space:normal;overflow:visible;text-overflow:clip;font:400 22px/28px 'JetBrains Mono',monospace;opacity:.72;text-align:center}
.cpalco .arroba{position:absolute;left:150px;right:165px;top:1626px;bottom:auto;height:34px;font:800 26px/34px Rubik;text-align:center;opacity:.9;white-space:nowrap}
/* 24/11 (regra 1 dela): legenda mais fina (Rubik 600, nunca 800), sem fundo preto. Estilo padrão "sem fundo": branca com
   sombra suave e a palavra falada MAIOR na cor principal da peça (--cor-tema). Estilo "faixa": faixa branca translúcida de
   cantos arredondados, tudo branco, palavra falada só maior. Escolha por peça em manifest/cenas: legenda_estilo. */
.cpalco .leg{position:absolute;left:150px;right:165px;bottom:330px;text-align:center;font:600 50px/1.25 Rubik;color:#fff;
  text-shadow:0 2px 10px rgba(0,0,0,.75),0 0 2px rgba(0,0,0,.6)}
.cpalco .leg.faixa{background:rgba(255,255,255,.22);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);border-radius:26px;padding:10px 18px;text-shadow:0 1px 6px rgba(0,0,0,.55)}
.cpalco .leg div{white-space:nowrap}
.cpalco .sub-dest{margin-top:6px}
.cpalco .leg .agora{display:inline-block;color:var(--cor-tema,#FFD34D);transform:scale(1.16);transform-origin:50% 60%;margin:0 8px} /* 24/11 A1: margem real vem da largura da palavra (scale 1.16 cresce 8% de cada lado), senão encosta ("do8 de janeirovai") */
.cpalco .leg.faixa .agora{color:#fff}
.cpalco .leg.claro{color:#0B0B0C!important;text-shadow:0 1px 8px rgba(255,255,255,.8)}
.cpalco .leg.claro .agora{color:color-mix(in srgb,var(--cor-tema,#FFD34D) 55%,#000)}
.cpalco .leg.claro.faixa{background:rgba(11,11,12,.10)}
.cpalco .leg.claro.faixa .agora{color:#0B0B0C}
.cpalco .hl{position:relative;color:#0B0B0C;padding:0 10px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.cpalco .hl::before{content:"";position:absolute;left:0;right:0;top:.06em;bottom:.02em;background:var(--ac,#FFD34D);z-index:-1}
.cpalco .anton .hl::before,.cpalco [style*="Anton"] .hl::before{top:.2em;bottom:.2em}
.cpalco .am{color:var(--ac,#FFD34D)}.cpalco .vm{color:#FF4A3D}
.cpalco .seta{height:8px;background:var(--ac,#FFD34D);position:relative}.cpalco .seta::after{content:"";position:absolute;right:-6px;top:-14px;border:18px solid transparent;border-left:26px solid var(--ac,#FFD34D);border-right:0}
.cpalco .linha-item{border-bottom:4px solid #0B0B0C;padding:22px 0}
.cpalco .icone{width:110px;height:110px;flex:none}
.cpalco .cel{position:absolute;border:14px solid #111;border-radius:64px;background:#fff;overflow:hidden;box-shadow:0 30px 60px rgba(0,0,0,.45)}
.cpalco .brilho{position:absolute;color:#F7EFA0;font-size:44px}
.cpalco.medir [style*="translate:"]{translate:none!important}
.cpalco.medir [style*="scale:"]{scale:none!important}
`;

  // cada card devolve {bg, fg, papel, escuro, html, fim}; fim = base do último bloco (cabe acima da legenda: LIM)
  // k = fator de corpo (1 = desenho original); html() tenta k menor se passar do LIM.
  const C = {};
  function cardMoldura(c, tl, k, d) { // 01 e 03: título, apoio, moldura com mídia, etiqueta
    const R = rot(c, d.corRot); let h = R.html, y = Math.max(R.bot + 44, d.yTit);
    if (c.pessoa) { const n = solto(c.pessoa, { ...RUB(800, 1.15), base: 40, min: 30, larg: LARG - 146, maxLin: 2 });
      h += `<div class="ab zs" style="top:${y}px;display:flex;align-items:center;gap:26px;${ent(tl, 0.1)}">${rosto({ nome: c.pessoa, foto: c.foto_pessoa }, 120)}${n.html}</div>`; y += Math.max(120, n.r.h) + 30; }
    const T = bloco(c.titulo, { ...TIT, base: d.tam * k, min: 56, larg: LARG, maxLin: 3, dest: c.destaque, cls: d.cls }, y, `${d.corTit || ''}${ent(tl, d.tTit)}`, 'ab titulo');
    h += T.html; y = T.bot + 34;
    if (c.apoio) { const A = bloco(c.apoio, { ...RUB(600, 1.25), base: d.tamApoio * k, min: 30, larg: LARG, maxLin: 3 }, y, `${d.corTit || ''}${ent(tl, 0.45)}`); h += A.html; y = A.bot + 40; }
    const et = c.etiqueta ? etq(c.etiqueta) : null;
    const mt = Math.max(y, d.yMol), H = Math.min(d.hMol, LIM - mt - (et ? et.h - 20 : 0));
    h += `<div class="moldura" style="left:150px;right:165px;top:${mt}px;height:${Math.max(H, 300)}px;transform:none;${ent(tl, d.tMol, 0.5, 80)}">${c.midia ? `<img src="${E(c.midia)}">` : `<div style="width:${Math.round(Math.min(H, d.ico) * 0.95)}px;height:${Math.round(Math.min(H, d.ico) * 0.95)}px;color:#FFD34D">${ico(c.icone || d.icone)}</div>`}</div>`;
    h += `<div class="estrela4" style="right:60px;top:${mt - 50}px;${d.estrela}"></div>`;
    let fim = mt + Math.max(H, 300);
    if (et) { const ty = mt + Math.max(H, 300) - 20; h += `<div class="ab zs" style="top:${ty}px;${ent(tl, 0.9)}">${et.html('transform:rotate(-2deg)')}</div>`; fim = ty + et.h; }
    return { h, fim };
  }
  C['01'] = (c, tl, s, k) => { const r = cardMoldura(c, tl, k, { yTit: 396, tam: 104, cls: 'hl', tTit: 0.2, tamApoio: 34, yMol: 916, hMol: 520, ico: 220, icone: 'doc', tMol: 0.6, estrela: `transform:rotate(${(tl * 20) % 360}deg)` });
    return { bg: '#FFD34D', papel: 1, html: r.h, fim: r.fim }; };
  C['02'] = (c, tl, s, k) => { const ps = (c.pessoas || []).slice(0, 2); const R = rot(c); let y = Math.max(R.bot + 30, 356);
    // título condensado com escala vertical 1,2 (desenho do template); altura reservada já conta a escala
    const T = bloco(c.titulo, { ...ANTON, base: 150 * k, min: 72, larg: LARG, maxLin: 3, sy: 1.2, dest: c.destaque, cls: 'tc' }, y, '', 'ab anton');
    y = Math.max(T.bot + 50, Math.min(856, LIM - 560 * k));
    const col = (LARG - 60) / 2, tr = Math.round(280 * k);
    let alt = 0; const cols = ps.map((x, q) => { const n = texto(x.nome, { ...RUB(800, 1.1), base: 44 * k, min: 32, larg: col, maxLin: 2 }); const cg = x.cargo ? texto(x.cargo, { ...RUB(600, 1.3), base: 30 * k, min: 26, larg: col, maxLin: 3 }) : null; const ch = chipH(x, col);
      alt = Math.max(alt, tr + 26 + n.h + (cg ? cg.h : 0) + (ch.h ? ch.h + 12 : 0));
      return `<div style="${ent(tl, tItem(x, q, ps.length, s))}">${rosto(x, tr)}<div class="tx" style="font:800 ${n.fs}px/1.1 Rubik;margin-top:26px">${n.html}</div>${cg ? `<div class="tx" style="font:600 ${cg.fs}px/1.3 Rubik">${cg.html}</div>` : ''}${ch.html ? '<div style="margin-top:12px">' + ch.html + '</div>' : ''}</div>`; });
    return { bg: '#F2E6D0', papel: 1, vinco: 1, fim: y + alt, html: R.html + T.html + `<div class="ab zs" style="top:${y}px;display:grid;grid-template-columns:1fr 1fr;gap:60px">${cols.join('')}</div>` }; };
  C['03'] = (c, tl, s, k) => { const r = cardMoldura(c, tl, k, { corRot: '#fff', yTit: 366, tam: 110, cls: 'am', corTit: 'color:#fff;', tTit: 0.1, tamApoio: 36, yMol: 796, hMol: 620, ico: 240, icone: 'alerta', tMol: 0.7, estrela: 'background:#F2C94C' });
    return { bg: '#C0262D', fg: '#fff', escuro: 1, html: r.h, fim: r.fim }; };
  C['04'] = (c, tl, s, k) => { const alvo = parseFloat(String(c.numero).replace(/\./g, '').replace(',', '.')); const kk = p(tl, 0.3, 0.9);
    const numerico = isFinite(alvo) && /^[\d.,]+$/.test(String(c.numero));
    const R = rot(c); let y = Math.max(R.bot + 50, 386), h = '<svg style="position:absolute;inset:0" width="1080" height="1920"><circle cx="980" cy="1000" r="620" fill="none" stroke="#0B0B0C" stroke-opacity=".12" stroke-width="2"/><circle cx="-60" cy="1500" r="520" fill="none" stroke="#0B0B0C" stroke-opacity=".12" stroke-width="2"/></svg>' + R.html;
    const T = bloco(c.titulo, { ...RUB(800, 1.02, -0.02), base: 76 * k, min: 44, larg: LARG, maxLin: 3, dest: c.destaque, cls: 'hl' }, y, ent(tl, 0.05)); h += T.html; y = Math.max(T.bot + 50, 676);
    // número: nunca separado; reduz o corpo até caber (texto com espaço, ex. "6 meses a 2 anos", pode ir a 2 linhas)
    const sp = /\s/.test(String(c.numero).trim());
    const No = { ...RUB(900, 0.9, -0.05), base: 300 * k, min: sp ? 90 : 120, piso: 40, larg: LARG - 48, maxLin: sp ? 2 : 1, fim: c.sufixo ? { txt: c.sufixo, max: 72, rel: 0.36, p: 900 } : null };
    // mede o número como ele APARECE no fim da contagem ("2374" vira "2.374"; antes media sem o ponto e passava de 915)
    const fmt = v => (Number.isInteger(alvo) ? Math.round(v).toLocaleString('pt-BR') : v.toFixed(1).replace('.', ','));
    const N = texto(numerico ? fmt(alvo) : c.numero, No);
    const num = numerico ? fmt(alvo * kk) : null;
    const nHtml = num !== null ? `<span class="ln">${num}<span style="font-size:${Math.min(72, Math.round(N.fs * 0.36))}px;letter-spacing:0">${E(c.sufixo || '')}</span></span>` : N.html;
    h += `<div class="ab tx zs" style="top:${y}px;${fonteCss(No, N)}${ent(tl, 0.25)}">${nHtml}</div>`; const nb = y + N.h; y = Math.max(nb + 60, 1056);
    if (c.apoio) { const A = bloco(c.apoio, { ...RUB(600, 1.25), base: 40 * k, min: 30, larg: LARG, maxLin: 4 }, y, ent(tl, 0.9)); h += A.html; y = A.bot; } else y = nb;
    return { bg: '#F7F8FA', html: h, fim: y }; };
  C['05'] = (c, tl, s, k) => { const tD = typeof c.t_depois === 'number' ? c.t_depois - s.start : (s.end - s.start) * 0.45; const kk = p(tl, tD, 0.6);
    const R = rot(c, '#fff'); let y = Math.max(R.bot + 44, 366), h = R.html;
    const T = bloco(c.titulo, { ...TIT, base: 92 * k, min: 52, larg: LARG, maxLin: 3, dest: c.destaque, cls: 'am' }, y, `color:#fff;${ent(tl, 0.05)}`, 'ab titulo'); h += T.html; y = Math.max(T.bot + 60, 756);
    const ic = Math.round(200 * Math.min(1, k + 0.1)), O = { ...RUB(800, 1.15), base: 42 * k, min: 30, larg: 250, maxLin: 4 };
    const A = texto(c.antes, O), D = texto(c.depois, O);
    h += `<div class="ab zs" style="top:${y}px;display:flex;align-items:flex-start;justify-content:space-between">` +
      `<div style="width:250px;text-align:center;${ent(tl, 0.3)}"><div style="width:${ic}px;height:${ic}px;margin:0 auto;color:#fff">${ico(c.icone_antes || 'doc', '#fff', 4)}</div><div class="tx" style="font:800 ${A.fs}px/1.15 Rubik;color:#fff;margin-top:18px">${A.html}</div></div>` +
      `<div class="seta" style="margin-top:${Math.round(ic / 2)}px;width:${Math.round(220 * kk)}px;opacity:${kk.toFixed(2)}"></div>` +
      `<div style="width:250px;text-align:center;opacity:${kk.toFixed(2)}"><div style="width:${ic}px;height:${ic}px;margin:0 auto">${ico(c.icone_depois || 'doc', '#FFD34D', 4)}</div><div class="tx" style="font:800 ${D.fs}px/1.15 Rubik;color:#FFD34D;margin-top:18px">${D.html}</div></div></div>`;
    y += ic + 18 + Math.max(A.h, D.h);
    if (c.etiqueta) { const et = etq(c.etiqueta); const ty = Math.max(y + 50, Math.min(1236, LIM - et.h)); h += `<div class="ab zs" style="top:${ty}px;${ent(tl, tD + 0.4)}">${et.html('transform:rotate(-4deg)')}</div>`; y = ty + et.h; }
    return { bg: '#161B2A', fg: '#fff', escuro: 1, html: h, fim: y }; };
  C['06'] = (c, tl, s, k) => { const it = (c.itens || []).slice(0, 4); const ts = it.map((x, q) => tItem(x, q, it.length, s)); let at = -1; ts.forEach((x, q) => { if (tl >= x) at = q; });
    const R = rot(c); let y = Math.max(R.bot + 44, 366), h = R.html;
    const T = bloco(c.titulo, { ...TIT, base: 96 * k, min: 52, larg: LARG, maxLin: 3, dest: c.destaque, cls: 'hl' }, y, ent(tl, 0.05), 'ab titulo'); h += T.html; y = Math.max(T.bot + 50, 656);
    const y0 = y; const linhas = it.map((x, q) => { const b = itemBloco(x, { ...RUB(800, 1.1), base: 54 * k, min: 34, maxLin: 2 }, 'tc', LARG); y += b.h + 48;
      return `<div class="linha-item" style="opacity:${q === at ? 1 : q < at ? 0.55 : 0.18}">${b.html}</div>`; });
    return { bg: '#FFD34D', fim: y, html: h + `<div class="ab zs" style="top:${y0}px">${linhas.join('')}</div>` }; };
  C['07'] = (c, tl, s, k) => { const R = rot(c); let y = Math.max(R.bot + 44, 366), h = R.html;
    const T = bloco(c.titulo, { ...TIT, base: 110 * k, min: 60, larg: LARG, maxLin: 2 }, y, ent(tl, 0.05), 'ab titulo'); h += T.html; y = Math.max(T.bot + 40, 596);
    const tam = Math.round(400 * k); h += `<div class="zs" style="position:absolute;left:${540 - tam / 2}px;top:${y}px;width:${tam}px;height:${tam}px;${ent(tl, 0.3)}">${ico(c.icone || 'pessoa', '#0B0B0C', 3)}</div>`; y = Math.max(y + tam + 50, 1076);
    if (c.apoio) { const A = bloco(c.apoio, { ...RUB(600, 1.2), base: 46 * k, min: 32, larg: LARG, maxLin: 3 }, y, ent(tl, 0.6)); h += A.html; y = A.bot + 40; }
    if (c.link) { const L = texto(c.link, { ...RUB(700, 1.2), base: 40 * k, min: 30, larg: LARG, maxLin: 2 }); y = Math.max(y, 1256); h += `<div class="ab tx zs" style="top:${y}px;border-top:4px solid #0B0B0C;border-bottom:4px solid #0B0B0C;padding:18px 0;font:700 ${L.fs}px/1.2 Rubik;${ent(tl, 0.9)}">${L.html}</div>`; y += L.h + 44; }
    return { bg: '#FF4A3D', html: h, fim: y }; };
  C['10'] = (c, tl, s, k) => { const it = (c.itens || []).slice(0, 3);
    const Rr = bloco(c.rotulo || 'FUNCIONA ASSIM', { ...MONO, base: 30, min: 20, larg: LARG, maxLin: 2 }, Y0, '', 'ab mono');
    let y = Math.max(Rr.bot + 32, 336), h = Rr.html;
    const T = bloco(c.titulo, { ...ANTON, base: 120 * k, min: 64, larg: LARG, maxLin: 3, dest: c.destaque, cls: 'hl' }, y, ent(tl, 0.05), 'ab anton'); h += T.html; y = Math.max(T.bot + 60, 756);
    const y0 = y, larg = LARG - 110 - 34;
    const its = it.map((x, q) => { const b = itemBloco(x, { ...RUB(800, 1.12), base: 50 * k, min: 32, maxLin: 3 }, 'vm', larg); const a = Math.max(110, b.h); y += a + (q < it.length - 1 ? 56 : 0);
      return `<div style="display:flex;gap:34px;align-items:center;margin-bottom:${q < it.length - 1 ? 56 : 0}px;${ent(tl, tItem(x, q, it.length, s))}"><div class="icone" style="background:#0B0B0C;border-radius:22px;padding:18px">${ico(x.icone || 'doc', '#FFD34D', 7)}</div><div style="width:${larg}px">${b.html}</div></div>`; });
    return { bg: '#FFD34D', fim: y, html: h + `<div class="ab zs" style="top:${y0}px">${its.join('')}</div>` }; };
  C['11'] = (c, tl, s, k) => { const Rr = bloco(c.rotulo || 'FAZ A CONTA', { ...MONO, base: 30, min: 20, larg: LARG, maxLin: 2 }, Y0, 'color:#FFD34D;', 'ab mono');
    let y = Math.max(Rr.bot + 40, 356), h = Rr.html;
    if (c.apoio_topo) { const A = texto(c.apoio_topo, { ...RUB(600, 1.25), base: 36 * k, min: 30, larg: LARG - 140, maxLin: 3 });
      h += `<div class="ab zs" style="top:${y}px;display:flex;gap:30px;align-items:center;color:#fff;${ent(tl, 0.05)}"><div class="icone">${ico(c.icone || 'dinheiro', '#fff', 5)}</div><div class="tx" style="font:600 ${A.fs}px/1.25 Rubik">${A.html}</div></div>`; y = Math.max(y + Math.max(110, A.h) + 60, 556); }
    // número/data: nunca separado ("22/12/2026" inteiro); corpo reduz até caber
    const sp = /\s/.test(String(c.numero).trim()) && !/^R\$\s*\d/.test(String(c.numero).trim());
    const No = { ...RUB(900, 1, -0.04), base: 210 * k, min: sp ? 80 : 100, piso: 40, larg: LARG, maxLin: sp ? 2 : 1, fim: c.sufixo ? { txt: ' ' + c.sufixo, max: 64, rel: 0.4, p: 900 } : null };
    const N = bloco(c.numero, No, y, `color:#FF4A3D;${ent(tl, 0.3)}`); h += N.html; y = Math.max(N.bot + 50, 836);
    const T = bloco(c.titulo, { ...RUB(800, 1.15), base: 52 * k, min: 36, larg: LARG, maxLin: 3, dest: c.destaque, cls: 'am' }, y, `color:#fff;${ent(tl, 0.7)}`); h += T.html; y = Math.max(T.bot + 40, 1056);
    if (c.apoio) { const A = bloco(c.apoio, { ...RUB(400, 1.35), base: 30 * k, min: 26, larg: LARG, maxLin: 4 }, y, `color:#cfcac0;${ent(tl, 1)}`); h += A.html; y = A.bot; } else y = T.bot;
    return { bg: '#0B0B0C', fg: '#fff', escuro: 1, html: h, fim: y }; };
  C['12'] = (c, tl, s, k) => { const ps = (c.pessoas || []).slice(0, 4); const R = rot(c);
    // linhas de rostos empilhadas pela altura real (antes: posições fixas, o 4º rosto e as aspas caíam em cima do título)
    const tr = Math.round((ps.length > 2 ? 150 : 170) * Math.min(1, k + 0.1)), larg = 320;
    const alt = ps.map(x => { const ch = chipH({ ...x, chip: x.chip || x.nome }, larg); const a = x.aspas ? texto('“' + x.aspas + '”', { ...RUB(800, 1.15), base: 30 * k, min: 26, larg, maxLin: 3 }) : null; return { ch, a, h: tr + 14 + ch.h + (a ? 12 + a.h : 0) }; });
    const lin = ps.length > 2 ? [[0, 1], [2], [3]] : [[0, 1]]; const pos = []; let y = Math.max(R.bot + 40, ps.length > 2 ? 356 : 416);
    lin.forEach(l => { const q = l.filter(i => i < ps.length); if (!q.length) return; const x = q.length === 2 ? [150, 595] : [ps.length === 4 && q[0] === 3 ? 150 : 380];
      q.forEach((i, j) => { pos[i] = [x[j], y]; }); y += Math.max(...q.map(i => alt[i].h)) + 40; });
    const ts = ps.map((x, q) => tItem(x, q, ps.length, s)); const cx = 540, cy = pos.length > 2 ? pos[2][1] + tr / 2 : (pos[0] ? pos[0][1] + tr + 60 : 896);
    let linhas = ''; ps.forEach((x, q) => { const g = p(tl, ts[q] + 0.2, 0.5); const [px, py] = pos[q]; linhas += `<line x1="${cx}" y1="${cy}" x2="${cx + (px + 160 - cx) * g}" y2="${cy + (py + tr / 2 - cy) * g}" stroke="#0B0B0C" stroke-width="6"/>`; });
    const T = bloco(c.titulo || 'Pegou a conexão?', { ...RUB(900, 1), base: 78 * k, min: 40, larg: LARG, maxLin: 2, up: 1, dest: c.destaque, cls: 'hl' }, Math.max(y, Math.min(1366, LIM - 160)), ent(tl, (s.end - s.start) * 0.75));
    return { bg: '#FFD34D', papel: 1, fim: T.bot, html: `<svg style="position:absolute;inset:0" width="1080" height="1920">${linhas}</svg>` + R.html + ps.map((x, q) => { const [px, py] = pos[q];
      return `<div class="zs" style="position:absolute;left:${px}px;top:${py}px;width:${larg}px;text-align:center;${ent(tl, ts[q])}"><div style="display:flex;justify-content:center">${rosto(x, tr)}</div><div style="margin-top:14px">${alt[q].ch.html}</div>${alt[q].a ? `<div class="tx" style="font:800 ${alt[q].a.fs}px/1.15 Rubik;margin-top:12px">${alt[q].a.html}</div>` : ''}</div>`; }).join('') + T.html }; };
  C['16'] = (c, tl, s, k) => { const ps = (c.pessoas || []).slice(0, 2); const bs = (c.barras || []).slice(0, 2);
    let y = 276, h = ''; const T = bloco(c.titulo, { ...RUB(800, 1.12), base: 52 * k, min: 36, larg: LARG, maxLin: 3, dest: c.destaque, cls: 'hl' }, y, ent(tl, 0.05)); h += T.html; y = Math.max(T.bot + 44, 476);
    const tr = Math.round(230 * k); let alt = 0;
    h += `<div class="ab zs" style="top:${y}px;display:flex;justify-content:space-between">` + ps.map((x, q) => { const ch = chipH({ ...x, chip: x.chip || x.nome }, 330); alt = Math.max(alt, tr + 16 + ch.h);
      return `<div style="text-align:center;width:330px;${ent(tl, 0.3 + q * 0.25)}"><div style="display:flex;justify-content:center">${rosto(x, tr)}</div><div style="margin-top:16px">${ch.html}</div></div>`; }).join('') + '</div>';
    y = Math.max(y + alt + 40, 896); const yb = y;
    const bh = bs.map((b, q) => { const a = +b.a || 0, z = +b.b || 0, tot = a + z || 1; const g = p(tl, tItem(b, q, bs.length, s), 0.7); const L = texto(b.rotulo || '', { ...RUB(800, 1.15), base: 30, min: 26, larg: LARG, maxLin: 2 }); y += 36 + L.h + 70 + 8;
      return `<div class="tx" style="font:800 ${L.fs}px/1.15 Rubik;margin:26px 0 10px">${L.html}</div><div style="display:flex;height:70px;border:4px solid #0B0B0C;border-radius:10px;overflow:hidden;font:800 28px Rubik;color:#fff"><div style="width:${(100 * a / tot * g).toFixed(1)}%;background:#E3342B;display:flex;align-items:center;padding-left:14px;white-space:nowrap">${E(b.a_txt || a + '%')}</div><div style="flex:1;background:#2F5BEA;display:flex;align-items:center;justify-content:flex-end;padding-right:14px;white-space:nowrap">${E(b.b_txt || z + '%')}</div></div>`; }).join('');
    let et = ''; if (c.etiqueta) { const e = etq(c.etiqueta); et = `<div style="margin-top:34px;${ent(tl, (s.end - s.start) * 0.7)}">${e.html('background:#FFD34D')}</div>`; y += 34 + e.h; }
    return { bg: '#F7F4EE', papel: 1, fim: y, html: h + `<div class="ab zs" style="top:${yb}px">${bh}${et}</div>` }; };
  C['17'] = (c, tl, s, k) => { const it = (c.itens || []).slice(0, 3);
    const Ch = texto(c.rotulo || 'NOVO', { ...RUB(700, 1.2), base: 24, min: 19, larg: LARG - 34, maxLin: 2 });
    let h = `<div class="ab zs" style="top:268px"><span class="chip tx" style="background:#4ADE80;color:#0B0B0C;font-size:${Ch.fs}px">${Ch.html}</span></div>`, y = Math.max(268 + Ch.h + 12 + 40, 346);
    const T = bloco(c.titulo, { ...RUB(800, 1.08), base: 64 * k, min: 40, larg: LARG, maxLin: 3, dest: c.destaque, cls: 'am' }, y, `color:#fff;${ent(tl, 0.05)}`); h += T.html; y = Math.max(T.bot + 44, 596);
    // celular: tudo que vai dentro tem que caber na tela (overflow hidden cortava letra)
    const H = Math.min(860, LIM + 6 - y), dentro = 580 - 28 - 68;
    const S = c.site ? texto(c.site, { ...RUB(800, 1.15), base: 30 * k, min: 24, larg: dentro, maxLin: 2 }) : null;
    const TT = c.tela_titulo ? texto(c.tela_titulo, { ...RUB(800, 1.1), base: 46 * k, min: 32, larg: dentro, maxLin: 2 }) : null;
    let ch = 46 + (S ? S.h + 8 : 0) + (TT ? TT.h + 30 : 0);
    const its = it.map((x, q) => { const b = itemBloco(x, { ...RUB(700, 1.25), base: 30 * k, min: 24, maxLin: 3 }, 'tc', dentro - 70); ch += Math.max(52, b.h) + 28;
      return `<div style="display:flex;gap:18px;align-items:flex-start;margin-bottom:28px;${ent(tl, tItem(x, q, it.length, s))}"><b style="flex:none;width:52px;height:52px;border-radius:50%;background:#FFD34D;display:grid;place-items:center;font:800 28px Rubik">${q + 1}</b><div style="width:${dentro - 70}px">${b.html}</div></div>`; });
    h += `<div class="cel zs" style="left:250px;top:${y}px;width:580px;height:${H}px;${ent(tl, 0.35, 0.6, 120)}"><div style="padding:46px 34px;color:#0B0B0C">${S ? `<div class="tx" style="font:800 ${S.fs}px/1.15 Rubik;margin-bottom:8px">${S.html}</div>` : ''}${TT ? `<div class="tx" style="font:800 ${TT.fs}px/1.1 Rubik;margin-bottom:30px">${TT.html}</div>` : ''}` + its.join('') + '</div></div>';
    return { bg: '#1F2A22', fg: '#fff', escuro: 1, papel: 1, html: h, fim: ch > H - 28 ? LIM + 1 : y + H - 6 }; };
  C['20'] = (c, tl, s, k) => { let h = `<div style="position:absolute;left:${560 - 40 * p(tl, 0, 1.6)}px;top:676px;width:760px;height:760px;border-radius:50%;background:#F2C94C"></div>`;
    const T = bloco(c.titulo, { ...ANTON, base: 128 * k, min: 64, larg: LARG, maxLin: 3, dest: c.destaque, cls: 'tc' }, 336, ent(tl, 0.05), 'ab anton'); h += T.html; let y = T.bot;
    if (c.apoio) { const A = bloco(c.apoio, { ...SERIF, lh: 1.15, base: 46 * k, min: 34, larg: LARG, maxLin: 3 }, Math.max(T.bot + 50, Math.min(1276, LIM - 3 * 53)), `text-align:center;${ent(tl, 0.6)}`, 'ab serif'); h += A.html; y = A.bot; }
    return { bg: '#F2E6D0', papel: 1, vinco: 1, html: h, fim: y }; };
  C['22'] = (c, tl, s, k) => { let h = '', yr = 268;
    if (c.rotulo) { const r = texto(c.rotulo, { ...MONO, base: 26, min: 19, larg: LARG - 32, maxLin: 2 }); h += `<div class="ab zs" style="top:268px"><span class="mono tx" style="display:inline-block;background:#0B0B0C;color:#fff;padding:8px 16px;font-size:${r.fs}px;line-height:1.2">${r.html}</span></div>`; yr = 268 + r.h + 16; }
    let yn = Math.max(yr + 30, 336), fimN = yn;
    if (c.nota) { const N = texto(c.nota, { ...RUB(700, 1.3), base: 30 * k, min: 24, larg: 330 - 40, maxLin: 7 }); h += `<div class="tx zs" style="position:absolute;right:165px;top:${yn}px;width:330px;background:#E3342B;color:#fff;padding:16px 20px;font:700 ${N.fs}px/1.3 Rubik;${ent(tl, 1)}">${N.html}</div>`; fimN = yn + N.h + 32; }
    const yi = Math.max(yr + 40, 416); h += `<div class="zs" style="position:absolute;left:150px;top:${yi}px;width:200px;height:200px;${ent(tl, 0.1)}">${ico(c.icone || 'voto', '#0B0B0C', 5)}</div>`;
    let y = Math.max(yi + 200 + 50, fimN + 40, 896);
    if (c.foto) { const yf = Math.max(556, fimN + 30); h += `<div style="position:absolute;right:165px;top:${yf}px;width:380px;height:440px;overflow:hidden;filter:grayscale(1) contrast(1.1)"><img style="width:100%;height:100%;object-fit:cover" src="${E(c.foto)}"></div>`; y = Math.max(y, yf + 440 + 40); }
    const T = bloco(c.titulo, { ...ANTON, base: 150 * k, min: 64, larg: LARG, maxLin: 3, dest: c.destaque, cls: 'am' }, y, `color:#fff;${ent(tl, 0.3)}`, 'ab anton'); h += T.html;
    return { bg: '#B5482E', fg: '#fff', escuro: 1, html: h, fim: T.bot }; };
  C['24'] = (c, tl, s, k) => { const b = [[150, 300, 0], [880, 360, 0.7], [820, 1180, 1.3], [200, 1300, 2.1]];
    const T = bloco(c.titulo, { ...SERIF, lh: 1.05, base: 104 * k, min: 56, larg: LARG, maxLin: 6, alt: LIM - 456 }, 456, `color:#F7EFA0;text-align:center;${ent(tl, 0.1, 0.8)}`, 'ab serif');
    return { bg: '#0B0B0C', fg: '#fff', escuro: 1, fim: T.bot, html: b.map(([x, y, f]) => `<div class="brilho" style="left:${x}px;top:${y}px;opacity:${(0.25 + 0.75 * Math.abs(Math.sin((tl + f) * 2))).toFixed(2)}">✦</div>`).join('') + T.html }; };
  C['26'] = (c, tl, s, k) => { const it = (c.itens || []).slice(0, 3);
    let h = `<div style="position:absolute;left:-160px;top:1136px;width:520px;height:520px;background:#F7F4EE;clip-path:polygon(50% 0,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%);transform:rotate(${(tl * 6).toFixed(1)}deg)"></div>`;
    const T = bloco(c.titulo, { ...ANTON, base: 120 * k, min: 64, larg: LARG, maxLin: 2 }, 286, `color:#fff;${ent(tl, 0.05)}`, 'ab anton'); h += T.html; let y = Math.max(T.bot + 30, 466);
    if (c.destaque) { const D = bloco(c.destaque, { ...ANTON, base: 190 * k, min: 80, larg: LARG, maxLin: 2 }, y, `color:#FFD34D;${ent(tl, 0.3)}`, 'ab anton'); h += D.html; y = D.bot; }
    y = Math.max(y + 50, 796); const y0 = y, larg = LARG - 350;
    const its = it.map((x, q) => { const A = texto(x.texto, { ...ANTON, base: 80 * k, min: 50, larg, maxLin: 2 }); const S = x.sub ? texto(x.sub, { ...RUB(700, 1.2), base: 30 * k, min: 24, larg, maxLin: 3 }) : null; y += A.h + (S ? S.h : 0) + (q < it.length - 1 ? 34 : 0);
      return `<div style="margin-bottom:${q < it.length - 1 ? 34 : 0}px;${ent(tl, tItem(x, q, it.length, s))}"><div class="tx" style="${fonteCss(ANTON, A)}color:#FFD34D">${A.html}</div>${S ? `<div class="tx" style="font:700 ${S.fs}px/1.2 Rubik;color:#fff">${S.html}</div>` : ''}</div>`; });
    return { bg: '#E4382E', fg: '#fff', escuro: 1, vinco: 1, fim: y, html: h + `<div class="zs" style="position:absolute;left:500px;right:165px;top:${y0}px">${its.join('')}</div>` }; };

  /* ---------- variação e card livre (23/11, palavras dela: "o template é só inspiration, não é pra usar igual";
     "eu já postei quase tds esses cards e sem contar que estão usando os mesmos toda hora") ----------
     Campos da CENA (não de campos{}): composicao, variante (moldura), fundo, paleta, entrada. Valem pra todo card:
       - cards do acervo: composicao = alinhamento (esq|centro|dir); paleta troca fundo e cor de destaque se tiver o
         mesmo claro/escuro do card (senão só o destaque); fundo = textura; variante = moldura; entrada = direção.
       - card "livre": o modelo monta a cena por blocos (campos.blocos) e escolhe o layout em composicao.
     O encaixe medido continua igual: todo texto passa por texto() na largura da coluna, e html() reduz o corpo (k)
     até o último bloco ficar acima da legenda. Mesmas listas em runner/cards.py (teste confere que batem). */
  const PALETAS = {
    'creme-amarelo': { bg: '#F2E6D0', fg: '#0B0B0C', ac: '#FFD34D', tc: '#B5482E' },
    'creme-rosa': { bg: '#F7EFE3', fg: '#0B0B0C', ac: '#FF5FA8', tc: '#B8336A' },
    'branco-verde': { bg: '#F7F8FA', fg: '#0B0B0C', ac: '#4ADE80', tc: '#15803D' },
    'branco-laranja': { bg: '#FAF7F2', fg: '#0B0B0C', ac: '#FF8A3D', tc: '#B4471A' },
    'amarelo': { bg: '#FFD34D', fg: '#0B0B0C', ac: '#FFF9EF', tc: '#B5482E' },
    'rosa': { bg: '#FF8FC3', fg: '#0B0B0C', ac: '#FFF9EF', tc: '#7A1F45' },
    'verde': { bg: '#7BE3A0', fg: '#0B0B0C', ac: '#FFF9EF', tc: '#14532D' },
    'laranja': { bg: '#FF9F5A', fg: '#0B0B0C', ac: '#FFF9EF', tc: '#7C2D12' },
    'lilas': { bg: '#C9AEFF', fg: '#0B0B0C', ac: '#FFD34D', tc: '#4C1D95' },
    'grafite-amarelo': { bg: '#17171A', fg: '#FFFFFF', ac: '#FFD34D', tc: '#FFD34D', escuro: 1 },
    'grafite-verde': { bg: '#141A16', fg: '#FFFFFF', ac: '#4ADE80', tc: '#4ADE80', escuro: 1 },
    'grafite-rosa': { bg: '#1A1418', fg: '#FFFFFF', ac: '#FF5FA8', tc: '#FF5FA8', escuro: 1 },
    'terracota': { bg: '#B5482E', fg: '#FFFFFF', ac: '#FFD34D', tc: '#FFD34D', escuro: 1 },
    'vinho': { bg: '#6E1E2B', fg: '#FFFFFF', ac: '#FFB4C8', tc: '#FFB4C8', escuro: 1 },
    'vermelho': { bg: '#D9362B', fg: '#FFFFFF', ac: '#FFD34D', tc: '#FFD34D', escuro: 1 },
    'mata': { bg: '#1F3A2B', fg: '#FFFFFF', ac: '#FFD34D', tc: '#FFD34D', escuro: 1 },
  };
  // 24/11 (ela: "nada combina"): com cor_tema, a peça inteira usa UM esquema: a cor principal + neutros (creme, branco,
  // grafite) + preto. As paletas nomeadas só dizem o "tipo" da cena (clara, escura ou cheia na cor); a cor vem da peça.
  const _CHEIAS = ['amarelo', 'rosa', 'verde', 'laranja', 'lilas', 'terracota', 'vinho', 'vermelho', 'mata'];
  function _lum(h) { const m = /^#?([0-9a-f]{6})$/i.exec(String(h || '')); if (!m) return 1; const n = parseInt(m[1], 16);
    const c = [n >> 16, (n >> 8) & 255, n & 255].map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; });
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]; }
  function _esc(h, f) { const m = /^#?([0-9a-f]{6})$/i.exec(String(h || '')); if (!m) return h; const n = parseInt(m[1], 16);
    return '#' + [n >> 16, (n >> 8) & 255, n & 255].map(v => Math.round(v * f).toString(16).padStart(2, '0')).join(''); }
  /* 25/11 (A3 PLP299, #547D91): cor da peça escura demais some em fundo escuro (palavra falada e destaque). Clareia
     abaixo de 4,5 contra o fundo, mistura com branco até 7; cor já legível passa igual (outras peças não mudam). */
  function _contr(a, b) { const x = _lum(a), y = _lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); }
  function _legivel(c, bg) { const m = /^#?([0-9a-f]{6})$/i.exec(String(c || '')); if (!m || !/^#?[0-9a-f]{6}$/i.test(String(bg || ''))) return c;
    if (_contr(c, bg) >= 4.5) return c; const n = parseInt(m[1], 16), v = [n >> 16, (n >> 8) & 255, n & 255];
    for (let f = .1; f <= 1.001; f += .1) { const h = '#' + v.map(x => Math.round(x + (255 - x) * f).toString(16).padStart(2, '0')).join('');
      if (_contr(h, bg) >= 7) return h; } // só clareia quem ficou abaixo de 4,5; aí vai até 7 pra ler no celular
    return '#FFFFFF'; }
  function paletaDaPeca(s) {
    const base = PALETAS[s.paleta];
    if (!s.cor_tema || !/^#[0-9a-f]{6}$/i.test(s.cor_tema)) return base;
    const c = s.cor_tema, tinta = _esc(c, .55);
    if (_CHEIAS.includes(s.paleta)) { const claro = _lum(c) > .35;
      // 25/11 (A1 COP31, lima): ac preto em fundo claro fazia destaque (.hl) e chip (.pill) virarem texto preto em caixa
      // preta. Caixa/chip agora em creme com letra preta; texto colorido (tc) segue preto pra dar leitura na cor clara.
      return { bg: c, fg: claro ? '#0B0B0C' : '#FFFFFF', ac: '#FFF9EF', tc: claro ? '#0B0B0C' : '#FFF9EF', escuro: claro ? 0 : 1 }; }
    if (base && base.escuro) { const cl = _legivel(c, '#141416'); return { bg: '#141416', fg: '#FFFFFF', ac: cl, tc: cl, escuro: 1 }; }
    const fundo = (s.paleta || '').startsWith('branco') ? '#FAF8F4' : '#F4EEE4';
    return { bg: fundo, fg: '#0B0B0C', ac: c, tc: tinta };
  }
  const FUNDOS = ['chapado', 'papel', 'quadriculado', 'pontilhado', 'listras', 'gradiente', 'foto'];
  const MOLDURAS = ['limpa', 'filete', 'cantos', 'fita', 'carimbo'];
  const ENTRADAS = ['baixo', 'cima', 'esquerda', 'direita', 'escala'];
  const ALINHA = ['esq', 'centro', 'dir'];
  const LAYOUTS = ['pilha', 'centro', 'base', 'faixa', 'colunas', 'diagonal', 'cartao', 'manchete'];
  const DISPOSICAO = { itens: ['lista', 'numerada', 'grade', 'linha-tempo', 'chips'], pessoas: ['linha', 'grade', 'lista'], antes_depois: ['lado', 'empilhado'] };
  const BLOCOS = ['titulo', 'numero', 'texto', 'itens', 'pessoas', 'antes_depois', 'citacao', 'conexao', 'icone', 'etiqueta'];
  // fundo e cor originais dos cards do acervo (o "molde" que ela já postou)
  const ORIGINAL = { '01': '#FFD34D', '02': '#F2E6D0', '03': '#C0262D', '04': '#F7F8FA', '05': '#161B2A', '06': '#FFD34D', '07': '#FF4A3D',
    '10': '#FFD34D', '11': '#0B0B0C', '12': '#FFD34D', '16': '#F7F4EE', '17': '#1F2A22', '20': '#F2E6D0', '22': '#B5482E', '24': '#0B0B0C', '26': '#E4382E' };

  const CSS_VAR = `
.cpalco .fundo{position:absolute;inset:0;pointer-events:none}
.cpalco .f-quadriculado{background-image:linear-gradient(currentColor 2px,transparent 2px),linear-gradient(90deg,currentColor 2px,transparent 2px);background-size:64px 64px;opacity:.09}
.cpalco .f-pontilhado{background-image:radial-gradient(currentColor 3px,transparent 3.6px);background-size:38px 38px;opacity:.15}
.cpalco .f-listras{background-image:repeating-linear-gradient(135deg,currentColor 0 16px,transparent 16px 52px);opacity:.06}
.cpalco .f-gradiente{background:linear-gradient(170deg,rgba(255,255,255,.22),rgba(0,0,0,.24))}
.cpalco .f-foto img{width:100%;height:100%;object-fit:cover;filter:grayscale(1) contrast(1.05)}
.cpalco .f-foto::after{content:"";position:absolute;inset:0;background:var(--bg);opacity:.8}
.cpalco .mol{position:absolute;pointer-events:none;color:currentColor}
.cpalco .mol-filete{left:46px;right:46px;top:96px;bottom:96px;border:3px solid currentColor;border-radius:30px;opacity:.45}
.cpalco .mol-canto{width:96px;height:96px;border:0 solid currentColor;opacity:.7}
.cpalco .mol-fita{width:200px;height:56px;background:rgba(255,249,239,.78);box-shadow:0 2px 6px rgba(0,0,0,.15)}
.cpalco .mol-carimbo{right:40px;top:92px;width:150px;height:150px;border:5px dashed currentColor;border-radius:50%;opacity:.55;display:grid;place-items:center;font-size:58px}
.cpalco.al-centro .ab,.cpalco.al-centro .rotulo{text-align:center}
.cpalco.al-dir .ab,.cpalco.al-dir .rotulo{text-align:right}
.cpalco.al-centro .ab[style*="display:flex"]{justify-content:center}
.cpalco.al-dir .ab[style*="display:flex"]{justify-content:flex-end}
.cpalco .ul{text-decoration:underline;text-decoration-thickness:.1em;text-underline-offset:.12em;text-decoration-color:var(--ac,#FFD34D)}
.cpalco .lv{position:absolute}
.cpalco .pill{display:inline-block;background:var(--ac,#FFD34D);color:#0B0B0C;border-radius:999px;padding:10px 26px;white-space:nowrap}
.cpalco .tile{border:4px solid currentColor;border-radius:22px;padding:22px}
.cpalco .regra{border-top:6px solid currentColor}
`;
  function fundoHtml(f, s, c) {
    if (!f || f === 'chapado') return '';
    if (f === 'papel') return '<div class="fundo papel" data-deco></div>';
    if (f === 'foto') { const m = s.foto_fundo || c.midia; return m ? `<div class="fundo f-foto" data-deco><img src="${E(m)}"></div>` : '<div class="fundo papel" data-deco></div>'; }
    return `<div class="fundo f-${f}" data-deco></div>`;
  }
  function molduraHtml(v) {
    if (v === 'filete') return '<div class="mol mol-filete" data-deco></div>';
    if (v === 'cantos') return [['left:52px;top:100px', 'border-top-width:6px;border-left-width:6px'], ['right:52px;top:100px', 'border-top-width:6px;border-right-width:6px'],
      ['left:52px;bottom:100px', 'border-bottom-width:6px;border-left-width:6px'], ['right:52px;bottom:100px', 'border-bottom-width:6px;border-right-width:6px']]
      .map(([a, b]) => `<div class="mol mol-canto" data-deco style="${a};${b}"></div>`).join('');
    if (v === 'fita') return '<div class="mol mol-fita" data-deco style="left:34px;top:120px;transform:rotate(-14deg)"></div><div class="mol mol-fita" data-deco style="right:34px;top:120px;transform:rotate(12deg)"></div>';
    if (v === 'carimbo') return '<div class="mol mol-carimbo" data-deco style="transform:rotate(-12deg)">✦</div>';
    return '';
  }

  // ---- card livre: blocos medidos na largura da coluna e empilhados pelo layout escolhido ----
  const TAM = { g: 1, m: 0.78, p: 0.58 };
  function blocoLivre(b, W, al, k, tl, s, q, cx) {
    const tEnt = typeof b.t === 'number' ? b.t - s.start : 0.05 + 0.22 * q, st = `text-align:${al};`, dest = cx.dest;
    const caixa = (h, inner, extra = '') => ({ h, html: (x, y) => `<div class="lv zs" style="left:${x}px;top:${y}px;width:${W}px;${st}${extra}${ent(tl, tEnt)}">${inner}</div>` });
    const tx = (r, o, extra = '') => `<div class="tx" style="${fonteCss(o, r)}${extra}">${r.html}</div>`;
    const t = b.tipo;
    if (t === 'titulo') {
      // 23/11: sem serifa no livre (regra dela: fontes modernas, limpas, bold, levemente arredondadas); "serif" ou
      // letra desconhecida = Rubik. Título nunca abaixo de MIN_TIT (legível em celular menor), em qualquer tamanho.
      const fam = b.letra === 'anton' ? { ...ANTON, base: 150 } : { ...TIT, base: 118 };
      const f = cx.manchete ? { ...ANTON, base: 168, min: 72 } : { ...fam, min: MIN_TIT };
      let o = { ...f, base: Math.max(f.min, f.base * (TAM[b.tamanho] || TAM.m) * k), piso: f.min, larg: W, maxLin: 4, dest: b.destaque, cls: cx.destTit || dest };
      let r = texto(b.texto, o);
      // palavra comum solta ao lado do destaque em caixa (ex.: "luz" + [sobe em 2027]) que nenhuma quebra evita: o
      // destaque vira cor no texto (sem caixa), então a linha se lê inteira e as cores continuam misturadas na linha
      if (r.solta && o.cls === 'hl') { o = { ...o, cls: 'tcd' }; r = texto(b.texto, o); }
      const cx2 = caixa(r.h, tx(r, o, cx.corTit || '')); cx2.tit = { fs: r.fs, ok: r.ok, regra: r.regra }; return cx2;
    }
    if (t === 'texto') { const o = { ...RUB(600, 1.25), base: 42 * k, min: 30, larg: W, maxLin: 4, dest: b.destaque, cls: dest }; const r = texto(b.texto, o); return caixa(r.h, tx(r, o, 'opacity:.92;')); }
    if (t === 'numero') {
      const v = String(b.valor ?? ''), alvo = parseFloat(v.replace(/\./g, '').replace(',', '.')), numerico = isFinite(alvo) && /^[\d.,]+$/.test(v);
      const fmt = z => (Number.isInteger(alvo) ? Math.round(z).toLocaleString('pt-BR') : z.toFixed(1).replace('.', ','));
      const base = { gigante: 300, grande: 220, medio: 150 }[b.tamanho] || 220, sp = /\s/.test(v.trim());
      const o = { ...RUB(900, 0.92, -0.05), base: base * k, min: sp ? 70 : 96, piso: 40, larg: W - 24, maxLin: sp ? 2 : 1, fim: b.sufixo ? { txt: ' ' + b.sufixo, max: 72, rel: 0.36, p: 900 } : null };
      const N = texto(numerico ? fmt(alvo) : v, o), kk = p(tl, tEnt + 0.1, 0.9);
      const nh = numerico ? `<span class="ln">${fmt(alvo * kk)}<span style="font-size:${Math.min(72, Math.round(N.fs * 0.36))}px;letter-spacing:0">${E(b.sufixo ? ' ' + b.sufixo : '')}</span></span>` : N.html;
      let h = N.h, inner = `<div class="tx ${cx.claro ? 'tc' : 'am'}" style="${fonteCss(o, N)}">${nh}</div>`;
      if (b.legenda) { const L = texto(b.legenda, { ...RUB(700, 1.2), base: 38 * k, min: 28, larg: W, maxLin: 3 }); h += 14 + L.h; inner += `<div class="tx" style="font:700 ${L.fs}px/1.2 Rubik;margin-top:14px">${L.html}</div>`; }
      return caixa(h, inner);
    }
    if (t === 'citacao') {
      const o = { ...RUB(700, 1.15, -0.01), base: 60 * k, min: 36, larg: W, maxLin: 5 }, r = texto('“' + b.texto + '”', o); // sem serifa (23/11)
      let h = r.h, inner = tx(r, o);
      if (b.autor) { const A = texto(b.autor, { ...MONO, base: 26, min: MIN_LER, piso: MIN_LER, larg: W, maxLin: 2 }); h += 22 + A.h; inner += `<div class="tx mono ${cx.claro ? 'tc' : 'am'}" style="font-size:${A.fs}px;line-height:1.2;margin-top:22px">${A.html}</div>`; }
      return caixa(h, inner);
    }
    if (t === 'icone') { const z = Math.round(({ g: 340, m: 240, p: 160 }[b.tamanho] || 240) * k);
      const ml = al === 'center' ? (W - z) / 2 : al === 'right' ? W - z : 0;
      return caixa(z, `<div style="width:${z}px;height:${z}px;margin-left:${ml}px">${ico(b.icone || 'doc', 'currentColor', 4)}</div>`); }
    if (t === 'etiqueta') { const e = etq(b.texto, W - 60); return caixa(e.h, e.html('transform:rotate(-2deg)')); }
    if (t === 'itens') {
      let it = (b.itens || []).slice(0, 4), disp = b.disposicao || 'lista'; if (disp === 'grade' && W < 520) disp = 'lista';
      const tsI = it.map((x, i) => tItem(x, i, it.length, s));
      const ei = i => { const z = typeof it[i].t === 'number' ? it[i].t - s.start : tsI[i]; return ent(tl, z); };
      if (disp === 'chips') { const rows = []; let row = [], lw = 0;
        const ps = it.map(x => { const r = texto(x.texto, { ...RUB(800, 1.15), base: 40 * k, min: 30, larg: W - 56, maxLin: 2 }); return { r, w: r.w + 56 }; });
        ps.forEach((c, i) => { if (row.length && lw + 18 + c.w > W) { rows.push(row); row = [], lw = 0; } lw += (row.length ? 18 : 0) + c.w; row.push(i); }); if (row.length) rows.push(row);
        const h = rows.reduce((a, r) => a + Math.max(...r.map(i => ps[i].r.h)) + 20, 0) + (rows.length - 1) * 18;
        const inner = rows.map(r => `<div style="display:flex;gap:18px;margin-bottom:18px;justify-content:${al === 'center' ? 'center' : al === 'right' ? 'flex-end' : 'flex-start'}">` + r.map(i => `<span class="pill tx" style="font:800 ${ps[i].r.fs}px/1.15 Rubik;${ps[i].r.n > 1 ? 'border-radius:28px;' : ''}${ei(i)}">${ps[i].r.html}</span>`).join('') + '</div>').join('');
        return caixa(h, inner); }
      if (disp === 'grade') { const cw = (W - 30) / 2, o = { ...RUB(800, 1.12), base: 44 * k, min: 32, maxLin: 4 };
        const cel = it.map(x => { const bb = itemBloco(x, o, dest, cw - 52); const ic = x.icone ? Math.round(80 * k) : 0; return { bb, ic, h: bb.h + 52 + (ic ? ic + 16 : 0) }; });
        let h = 0; const rowsH = []; for (let i = 0; i < cel.length; i += 2) { const hh = Math.max(cel[i].h, cel[i + 1] ? cel[i + 1].h : 0); rowsH.push(hh); h += hh + (i + 2 < cel.length ? 30 : 0); }
        const inner = `<div style="display:grid;grid-template-columns:${cw}px ${cw}px;gap:30px;text-align:left">` + cel.map((c, i) => `<div class="tile" style="height:${rowsH[Math.floor(i / 2)]}px;${ei(i)}">${c.ic ? `<div style="width:${c.ic}px;height:${c.ic}px;margin-bottom:16px">${ico(it[i].icone, 'currentColor', 6)}</div>` : ''}${c.bb.html}</div>`).join('') + '</div>';
        return caixa(h, inner); }
      if (disp === 'linha-tempo') { const o = { ...RUB(800, 1.12), base: 46 * k, min: 30, maxLin: 3 }, lw = W - 84; let h = 0;
        const cel = it.map((x, i) => { const bb = itemBloco(x, o, dest, lw); const hh = Math.max(44, bb.h); h += hh + (i < it.length - 1 ? 46 : 0); return { bb, hh }; });
        const inner = `<div style="position:relative;text-align:left"><div style="position:absolute;left:20px;top:22px;bottom:22px;width:6px;background:currentColor;opacity:.35"></div>` + cel.map((c, i) => `<div style="display:flex;gap:40px;align-items:flex-start;margin-bottom:${i < it.length - 1 ? 46 : 0}px;${ei(i)}"><b style="flex:none;width:46px;height:46px;border-radius:50%;background:var(--ac,#FFD34D);border:5px solid currentColor;position:relative"></b><div style="width:${lw}px">${c.bb.html}</div></div>`).join('') + '</div>';
        return caixa(h, inner); }
      const num = disp === 'numerada', ic = !num && it.some(x => x.icone), gut = num ? 140 : ic ? 124 : 0, lw = W - gut;
      const o = { ...RUB(800, 1.12), base: 50 * k, min: 32, maxLin: 3 }; let h = 0;
      const cel = it.map((x, i) => { const bb = itemBloco(x, o, dest, lw); const hh = Math.max(num ? 100 * k : ic ? 96 : 0, bb.h) + 44; h += hh + (i < it.length - 1 ? 4 : 0); return { bb, hh }; });
      const inner = cel.map((c, i) => `<div style="display:flex;align-items:center;gap:${gut ? 28 : 0}px;padding:22px 0;border-bottom:4px solid currentColor;text-align:left;${ei(i)}">` +
        (num ? `<b class="${cx.claro ? 'tc' : 'am'}" style="flex:none;width:112px;font:400 ${Math.round(100 * k)}px/1 Anton,Impact,sans-serif">${String(i + 1).padStart(2, '0')}</b>` : ic ? `<div style="flex:none;width:96px;height:96px">${ico(it[i].icone || 'doc', 'currentColor', 6)}</div>` : '') +
        `<div style="width:${lw}px">${c.bb.html}</div></div>`).join('');
      return caixa(h + 4 * it.length, inner);
    }
    if (t === 'pessoas') {
      const ps = (b.pessoas || []).slice(0, 4), disp = b.disposicao || (ps.length > 2 ? 'grade' : 'linha');
      if (disp === 'lista') { const tr = Math.round(130 * Math.min(1, k + 0.1)), lw = W - tr - 30; let h = 0;
        const cel = ps.map((x, i) => { const n = texto(x.nome, { ...RUB(800, 1.1), base: 44 * k, min: 30, larg: lw, maxLin: 2 }); const cg = x.cargo ? texto(x.cargo, { ...RUB(600, 1.25), base: 30 * k, min: 24, larg: lw, maxLin: 2 }) : null; const ch = chipH(x, lw);
          const hh = Math.max(tr, n.h + (cg ? cg.h + 6 : 0) + (ch.h ? ch.h + 10 : 0)); h += hh + (i < ps.length - 1 ? 34 : 0); return { n, cg, ch, hh }; });
        const inner = cel.map((c, i) => `<div style="display:flex;gap:30px;align-items:center;margin-bottom:${i < ps.length - 1 ? 34 : 0}px;text-align:left;${ent(tl, tItem(ps[i], i, ps.length, s))}">${rosto(ps[i], tr)}<div style="width:${lw}px"><div class="tx" style="font:800 ${c.n.fs}px/1.1 Rubik">${c.n.html}</div>${c.cg ? `<div class="tx" style="font:600 ${c.cg.fs}px/1.25 Rubik;margin-top:6px">${c.cg.html}</div>` : ''}${c.ch.html ? `<div style="margin-top:10px">${c.ch.html}</div>` : ''}</div></div>`).join('');
        return caixa(h, inner); }
      const porLinha = disp === 'grade' ? 2 : Math.max(1, ps.length), gap = 40, col = (W - gap * (porLinha - 1)) / porLinha;
      const tr = Math.round(Math.min(col - 10, (porLinha >= 3 ? 170 : 250) * k));
      const cel = ps.map(x => { const n = texto(x.nome, { ...RUB(800, 1.1), base: 40 * k, min: 26, larg: col, maxLin: 2 }); const cg = x.cargo ? texto(x.cargo, { ...RUB(600, 1.25), base: 28 * k, min: MIN_LER, larg: col, maxLin: 2 }) : null; const ch = chipH(x, col);
        return { n, cg, ch, h: tr + 18 + n.h + (cg ? cg.h + 4 : 0) + (ch.h ? ch.h + 10 : 0) }; });
      let h = 0; const rows = []; for (let i = 0; i < cel.length; i += porLinha) { const hh = Math.max(...cel.slice(i, i + porLinha).map(c => c.h)); rows.push(hh); h += hh + (i + porLinha < cel.length ? 40 : 0); }
      const inner = `<div style="display:grid;grid-template-columns:repeat(${porLinha},${col}px);column-gap:${gap}px;row-gap:40px;text-align:center">` + cel.map((c, i) => `<div style="${ent(tl, tItem(ps[i], i, ps.length, s))}"><div style="display:flex;justify-content:center">${rosto(ps[i], tr)}</div><div class="tx" style="font:800 ${c.n.fs}px/1.1 Rubik;margin-top:18px">${c.n.html}</div>${c.cg ? `<div class="tx" style="font:600 ${c.cg.fs}px/1.25 Rubik;margin-top:4px">${c.cg.html}</div>` : ''}${c.ch.html ? `<div style="margin-top:10px">${c.ch.html}</div>` : ''}</div>`).join('') + '</div>';
      return caixa(h, inner);
    }
    if (t === 'antes_depois') {
      const tD = typeof b.t_depois === 'number' ? b.t_depois - s.start : tEnt + (s.end - s.start) * 0.35, kk = p(tl, tD, 0.6);
      if ((b.disposicao || 'lado') === 'lado' && W >= 600) { const cw = (W - 160) / 2, ic = Math.round(150 * Math.min(1, k + 0.1)), O = { ...RUB(800, 1.15), base: 42 * k, min: 28, larg: cw, maxLin: 4 };
        const A = texto(b.antes, O), D = texto(b.depois, O), h = ic + 18 + Math.max(A.h, D.h);
        const inner = `<div style="display:flex;align-items:flex-start;justify-content:space-between;text-align:center"><div style="width:${cw}px;opacity:.75"><div style="width:${ic}px;height:${ic}px;margin:0 auto">${ico(b.icone_antes || 'doc', 'currentColor', 4)}</div><div class="tx" style="font:800 ${A.fs}px/1.15 Rubik;margin-top:18px">${A.html}</div></div>` +
          `<div class="seta" style="margin-top:${Math.round(ic / 2)}px;width:${Math.round(110 * kk)}px;opacity:${kk.toFixed(2)}"></div>` +
          `<div style="width:${cw}px;opacity:${kk.toFixed(2)}"><div style="width:${ic}px;height:${ic}px;margin:0 auto">${ico(b.icone_depois || 'check', 'currentColor', 4)}</div><div class="tx ${cx.claro ? '' : 'am'}" style="font:800 ${D.fs}px/1.15 Rubik;margin-top:18px">${D.html}</div></div></div>`;
        return caixa(h, inner); }
      const O = { ...RUB(800, 1.15), base: 48 * k, min: 30, larg: W - 40, maxLin: 3 }, A = texto(b.antes, O), D = texto(b.depois, O);
      const h = A.h + 40 + 70 + D.h + 40;
      const inner = `<div style="text-align:left"><div style="padding:20px;opacity:.6"><div class="tx" style="font:800 ${A.fs}px/1.15 Rubik;text-decoration:line-through;text-decoration-thickness:.08em">${A.html}</div></div>` +
        `<div style="height:70px;display:flex;align-items:center;padding-left:20px;opacity:${kk.toFixed(2)}"><div class="seta" style="width:120px"></div></div>` +
        `<div style="padding:20px;background:var(--ac,#FFD34D);color:#0B0B0C;opacity:${kk.toFixed(2)}"><div class="tx" style="font:800 ${D.fs}px/1.15 Rubik">${D.html}</div></div></div>`;
      return caixa(h, inner);
    }
    if (t === 'conexao') {
      const de = b.de || {}, pa = b.para || {}, tr = Math.round(Math.min(220, (W - 200) / 2) * Math.min(1, k + 0.1)), col = Math.min(330, W / 2 - 20);
      const nm = x => { const n = texto(x.nome || '', { ...RUB(800, 1.1), base: 36 * k, min: 24, larg: col, maxLin: 2 }); const ch = chipH(x, col); return { n, ch, h: n.h + (ch.h ? ch.h + 10 : 0) }; };
      const A = nm(de), B = nm(pa), g = p(tl, typeof b.t === 'number' ? b.t - s.start : tEnt + 0.4, 0.6);
      const R = b.rotulo ? texto(b.rotulo, { ...RUB(800, 1.15), base: 40 * k, min: 26, larg: W, maxLin: 2, dest: b.destaque, cls: dest }) : null;
      const h = tr + 16 + Math.max(A.h, B.h) + (R ? 26 + R.h : 0), lx = tr + 20, lw = W - 2 * tr - 40;
      const pes = (x, c, lado) => `<div style="position:absolute;${lado}:0;top:0;width:${col}px;text-align:${lado === 'left' ? 'left' : 'right'}"><div style="display:flex;justify-content:${lado === 'left' ? 'flex-start' : 'flex-end'}">${rosto(x, tr)}</div><div class="tx" style="font:800 ${c.n.fs}px/1.1 Rubik;margin-top:16px">${c.n.html}</div>${c.ch.html ? `<div style="margin-top:10px">${c.ch.html}</div>` : ''}</div>`;
      const inner = `<div style="position:relative;height:${h}px">${pes(de, A, 'left')}${pes(pa, B, 'right')}<div style="position:absolute;left:${lx}px;top:${Math.round(tr / 2) - 4}px;width:${Math.round(lw * g)}px;height:8px;background:currentColor"></div><div style="position:absolute;left:${lx + lw * g - 14}px;top:${Math.round(tr / 2) - 14}px;width:28px;height:28px;border-radius:50%;background:var(--ac,#FFD34D);opacity:${g.toFixed(2)}"></div>` +
        (R ? `<div class="tx" style="position:absolute;left:0;right:0;top:${h - R.h}px;text-align:center;font:800 ${R.fs}px/1.15 Rubik">${R.html}</div>` : '') + '</div>';
      return caixa(h, inner);
    }
    const r = texto(String(b.texto || ''), { ...RUB(600, 1.25), base: 40 * k, min: 30, larg: W, maxLin: 3 }); return caixa(r.h, `<div class="tx" style="font:600 ${r.fs}px/1.25 Rubik">${r.html}</div>`);
  }
  C.livre = (c, tl, s, k) => {
    const P = paletaDaPeca(s) || PALETAS['creme-amarelo'];
    let lay = LAYOUTS.includes(s.composicao) ? s.composicao : 'pilha';
    const bl = (c.blocos || []).filter(b => b && BLOCOS.includes(b.tipo)).slice(0, 5);
    const R = rot(c); let h = R.html; const y0 = c.rotulo ? R.bot + 40 : Y0 + 10, G = Math.round(46 * k);
    const cartao = lay === 'cartao', claro = cartao || !P.escuro;
    const cx = { claro, dest: claro ? 'hl' : 'am', manchete: false };
    // largura e alinhamento de cada bloco pelo layout
    const geo = (b, i) => {
      if (lay === 'centro' || cartao) return [X0, LARG, 'center'];
      if (lay === 'colunas') return i === 0 ? [X0, 300, 'left'] : i === 1 ? [X0 + 340, LARG - 340, 'left'] : [X0, LARG, 'left']; // 3º bloco em diante: largura toda embaixo das colunas
      if (lay === 'diagonal') return i % 2 ? [X0, 640, 'left'] : [X1 - 640, 640, 'right']; // começa pela direita (pilha começa pela esquerda)
      return [X0, LARG, 'left'];
    };
    const montar = () => bl.map((b, i) => { const [x, W, al] = geo(b, i);
      const ex = lay === 'faixa' && i === 0 && b.tipo === 'titulo' ? { ...cx, destTit: 'ul', corTit: `color:${P.escuro ? '#0B0B0C' : '#FFFFFF'};` }
        : lay === 'manchete' && b.tipo === 'titulo' ? { ...cx, manchete: true } : cx;
      return { x, W, al, m: blocoLivre(b, W, al, k, tl, s, i, ex) }; });
    let med = montar();
    /* 23/11 (print da variante colunas: título pequeno demais). Na coluna estreita o título precisa caber em
       MIN_TIT ou mais, sem quebra proibida; se não couber, a composição colunas é descartada pra esse texto e a cena
       sai em pilha (o mesmo conteúdo, largura toda). CARDS.composicao(cena) devolve a composição desenhada. */
    if (lay === 'colunas' && med.slice(0, 2).some(m => m.m.tit && (!m.m.tit.ok || !m.m.tit.regra || m.m.tit.fs < MIN_TIT))) { lay = 'pilha'; med = montar(); }
    let y, fim, pos = [];
    if (lay === 'colunas' && med.length > 1) {
      pos[0] = y0; pos[1] = y0; const fimCol = Math.max(y0 + med[0].m.h, y0 + med[1].m.h);
      h += `<div data-deco style="position:absolute;left:${X0 + 318}px;top:${y0}px;width:4px;height:${Math.max(0, fimCol - y0)}px;background:currentColor;opacity:.3"></div>`;
      let yy = fimCol + G + 20; med.slice(2).forEach((m, i) => { pos[i + 2] = yy; yy += m.m.h + G; });
      fim = med.length > 2 ? yy - G : fimCol;
    } else {
      const sep = lay === 'manchete' ? G + 30 : lay === 'faixa' ? G + 24 : G;
      const tot = med.reduce((a, m, i) => a + m.m.h + (i ? sep : 0), 0) + (lay === 'faixa' ? 40 : 0);
      y = lay === 'centro' || cartao ? Math.max(y0 + (cartao ? 40 : 0), y0 + (LIM - 40 - y0 - tot) / 2) : lay === 'base' ? Math.max(y0, LIM - 20 - tot) : y0 + (lay === 'faixa' ? 30 : 0);
      /* 23/11: o "sol de cor" vazio parecia espaço de foto faltando (proibido forma vazia sem função). O espaço em
         cima só ganha forma quando a cena tem imagem (campos.imagem/midia): foto em círculo, P&B. Sem imagem, nada. */
      const img = c.imagem || c.midia;
      if (lay === 'base' && img && y - y0 >= 260) { const z = Math.min(460, y - y0 - 40); h += `<div class="foto-base" style="position:absolute;left:${X1 - z + 60}px;top:${y0}px;width:${z}px;height:${z}px;border-radius:50%;overflow:hidden;background:var(--ac,#FFD34D);${ent(tl, 0, 0.8)}"><img style="width:100%;height:100%;object-fit:cover;filter:grayscale(1) contrast(1.05)" src="${E(img)}"></div>`; }
      const ini = y;
      med.forEach((m, i) => { if (i) y += sep; pos[i] = y;
        if (lay === 'manchete' && i) h += `<div data-deco class="regra" style="position:absolute;left:${X0}px;width:${LARG}px;top:${y - sep / 2 - 3}px"></div>`;
        if (lay === 'faixa' && i === 0 && bl[0].tipo === 'titulo') h += `<div data-deco style="position:absolute;left:-20px;right:-20px;top:${y - 30}px;height:${m.m.h + 60}px;background:${P.escuro ? 'var(--ac,#FFD34D)' : '#0B0B0C'};transform:rotate(-1.5deg);${ent(tl, 0, 0.5)}"></div>`;
        y += m.m.h; });
      fim = y;
      if (cartao) h += `<div data-deco style="position:absolute;left:112px;right:127px;top:${ini - 40}px;height:${fim - ini + 80}px;background:#FFF9EF;border:5px solid #0B0B0C;border-radius:26px;box-shadow:16px 18px 0 #0B0B0C;transform:rotate(-1deg)"></div>`;
    }
    // 25/11 (A3 Roubo): o cartão fixava o destaque em terracota (#B5482E) mesmo com cor_tema; agora usa a cor da peça escurecida
    med.forEach((m, i) => { h += m.m.html(m.x, pos[i]).replace('class="lv zs"', `class="lv zs"${cartao ? ' data-cartao' : ''}`).replace(/^<div ([^>]*)style="/, (a, b) => `<div ${b}style="${cartao ? `color:#0B0B0C;--tcd:${/^#[0-9a-f]{6}$/i.test(s.cor_tema || '') ? _esc(s.cor_tema, .8) : '#B5482E'};--tc:${/^#[0-9a-f]{6}$/i.test(s.cor_tema || '') ? _esc(s.cor_tema, .8) : '#B5482E'};` : ''}`); });
    return { bg: P.bg, fg: P.fg, escuro: P.escuro ? 1 : 0, html: h, fim: fim + (cartao ? 40 : 0), composicao: lay };
  };

  const SCHEMA = {
    '01': ['titulo'], '02': ['titulo', 'pessoas'], '03': ['titulo'], '04': ['titulo', 'numero'], '05': ['titulo', 'antes', 'depois'],
    '06': ['titulo', 'itens'], '07': ['titulo'], '10': ['titulo', 'itens'], '11': ['numero', 'titulo'], '12': ['pessoas'],
    '16': ['titulo', 'pessoas', 'barras'], '17': ['titulo', 'itens'], '20': ['titulo'], '22': ['titulo'], '24': ['titulo'], '26': ['titulo', 'itens'],
  };

  // Legenda: as palavras da cena são quebradas em linhas pela largura REAL (medida no DOM com a fonte da
  // legenda, folga de 2,5%) e agrupadas 2 linhas por página. Nunca há 3ª linha: cada linha é nowrap e cabe na largura medida.
  // 23/11: o contorno e a sombra da legenda vinham do CSS da página (quadros.html/previa.html) e agora estão fixos aqui
  // (mesmo desenho em qualquer página); a faixa desconta realce .agora (8+8), sombra (10 de cada lado) e contorno.
  const LEG_LARG = 1080 - 150 - 165 - 16 - 20 - 4 - 70; // 24/11 A1: +14 = margem .26em da palavra falada // 24/11: -56 = palavra falada 16% maior + faixa
  const LEG_UTIL = LEG_LARG * (1 - FOLGA); // mesma folga do texto()
  function largura(txt) { // medida no DOM (mesmo medidor do texto()); em node, estimativa conservadora (~0,6 em)
    if (typeof document !== 'undefined' && document.createElement) return w100(String(txt), 'Rubik', 600) / 2;
    return String(txt).length * 30;
  }
  const fontesProntas = () => fonteOk(600, 'Rubik');
  function paginar(palavras, s) {
    const chave = `${s.start}|${s.end}`;
    let m = _cache.get(palavras); if (m && m.has(chave)) return m.get(chave);
    const ws = palavras.filter(w => w.start >= s.start - 1e-3 && w.start < s.end);
    const esp = largura(' '), linhas = []; let cur = [], lw = 0;
    for (const w of ws) {
      const ww = largura(String(w.text));
      if (cur.length && lw + esp + ww > LEG_UTIL) { linhas.push(cur); cur = [], lw = 0; }
      lw += (cur.length ? esp : 0) + ww; cur.push(w);
    }
    if (cur.length) linhas.push(cur);
    const pags = []; for (let i = 0; i < linhas.length; i += 2) pags.push(linhas.slice(i, i + 2));
    // fim de cena: equilibra as 2 linhas da página (sem palavra sozinha na 2ª linha)
    const lw2 = l => l.reduce((a, w, k) => a + largura(String(w.text)) + (k ? esp : 0), 0);
    for (const pg of pags) if (pg.length === 2) {
      const [a, b] = pg;
      while (a.length > 1 && lw2([a[a.length - 1], ...b]) <= lw2(a.slice(0, -1))) b.unshift(a.pop());
    }
    if (fontesProntas()) { if (!m) { m = new Map(); _cache.set(palavras, m); } m.set(chave, pags); }
    return pags;
  }
  function _rgb(h) { const m = /^#?([0-9a-f]{6})$/i.exec(String(h || '')); if (!m) return null; const n = parseInt(m[1], 16); return [n >> 16, (n >> 8) & 255, n & 255]; }
  /* 25/11 (A2 EL-NINO): com 140, menta #7CF5C8 contava como "perto" do creme #F4EEE4 (distância ~123) e a palavra falada
     saía preta em todo fundo claro, contra a REGRA Nº 1 §5 (fundo claro = cor da peça escurecida). 70 só pega fundo que
     é mesmo a cor da peça (cena cheia na cor). */
  function _perto(a, b) { const x = _rgb(a), y = _rgb(b); if (!x || !y) return false; return Math.hypot(x[0] - y[0], x[1] - y[1], x[2] - y[2]) < 70; }
  function legenda(t, palavras, escuro, s, bg) {
    if (!palavras || !palavras.length) return '';
    const at = palavras.find(w => t >= w.start && t <= w.end) || palavras.filter(w => w.start <= t).pop();
    if (!at) return '';
    let pg = null;
    if (s && at.start >= s.start - 1e-3 && at.start < s.end) pg = paginar(palavras, s).find(p => p.some(l => l.includes(at)));
    if (!pg) { // palavra fora da cena (borda de cena): pagina a página do manifesto pela largura medida também
      const ws = palavras.filter(w => w.page === at.page);
      if (ws.length) pg = paginar(palavras, { start: ws[0].start, end: ws[ws.length - 1].start + 1e-3 }).find(p => p.some(l => l.includes(at)));
      if (!pg) pg = [[at]];
    }
    const esp = largura(' ');
    const ls = pg.slice(0, 2).map(l => { const w = l.reduce((a, x, q) => a + largura(String(x.text)) + (q ? esp : 0), 0);
      // palavra única mais larga que a faixa (raro): reduz o corpo dessa linha em vez de passar de x 915
      const fs = w > LEG_UTIL ? Math.floor(50 * LEG_UTIL / w) : 0;
      return `<div${fs ? ` style="font-size:${fs}px"` : ''}>` + l.map(w => w === at ? `<span class="agora" style="margin:0 ${Math.round(largura(String(w.text)) * 0.08 + 8)}px">${E(w.text)}</span>` : E(w.text)).join(' ') + '</div>'; });
    const est = (s && (s.legenda_estilo || (typeof window !== 'undefined' && window.LEGENDA_ESTILO))) === 'faixa' ? ' faixa' : '';
    // 24/11: palavra falada na cor da peça; se o fundo da cena já é dessa cor, ela some: aí vai na tinta do fundo oposto
    // 25/11 (A3 PLP299): em fundo escuro, cor da peça escura clareia até ler (#547D91 virava #A5BECB-ish), nunca some
    const cor = s && s.cor_tema ? `;--cor-tema:${_perto(s.cor_tema, bg) ? (escuro ? '#FFFFFF' : '#0B0B0C') : escuro ? _legivel(s.cor_tema, bg) : s.cor_tema}` : '';
    return `<div class="leg zs${escuro ? ' escuro' : ' claro'}${est}" style="${cor.slice(1)}">${ls.join('')}</div>`;
  }
  // rodapé: fonte em 1 linha; se não couber, 2 (ou 3) linhas pequenas, nunca cortada com "…"
  function rodape(fonte) {
    let h = '<div class="arroba">@tentandochegaratevoce</div>';
    if (!fonte) return h;
    // Dá folga à linha do crédito para diferenças entre a medida do canvas e o texto do rodapé no player.
    const base = { f: 'JetBrains Mono', p: 400, ls: 0, larg: LARG - 36 };
    // 23/11: nunca abaixo de MIN_FONTE (20 px); 3 linhas sobem um pouco pra caber até 1730
    let r = texto('Fonte: ' + fonte, { ...base, lh: 28 / 22, base: 22, min: 22, piso: 22, maxLin: 1 }), lh = 28 / 22, top = 1668;
    if (!r.ok) { lh = 1.18; top = 1666; r = texto('Fonte: ' + fonte, { ...base, lh, base: 22, min: MIN_FONTE, piso: MIN_FONTE, maxLin: 2 }); }
    if (!r.ok) { lh = 1.1; top = 1662; r = texto('Fonte: ' + fonte, { ...base, lh, base: MIN_FONTE, min: MIN_FONTE, piso: MIN_FONTE, maxLin: 3 }); }
    return h + `<div class="fonte tx" style="top:${top}px;font-size:${r.fs}px;line-height:${lh}" title="${E(fonte)}">${r.html}</div>`;
  }

  /* ---------- 24/11: TEMPLATES DO PAINEL DE VERDADE (ela viu o flow e disse que "não está igual aos favoritos") ----------
     Antes o flow só anotava template_painel "Card N" e desenhava um card antigo com outra cor. Agora C['pN'] É o card N
     do Painel da Manhã (painel-da-manha.vercel.app/templates/, catálogo templates/catalogo.json do repo painel-da-manha),
     reconstruído do HTML original: mesmo layout, tipografia (Inter Tight 700, JetBrains Mono 400, DM Serif Display,
     Rubik), fundo, filetes, molduras, grão e movimento. Muda só (1) a cor: a cor do template vira a cor principal da
     peça (cor_tema) e os neutros ficam; sem cor_tema sai a cor original; (2) o texto: campos da cena. Zona segura e
     medida iguais aos outros cards (texto() medido, x 150-915, conteúdo até LIM 1450, rodapé e legenda padrão).
     Campos de cada card: anim/TEMPLATES-PAINEL.md. O flow usa pN quando a cena traz card "pN" ou template_painel
     "Card N" (e o card tem os campos mínimos de PSCHEMA). Prova visual lado a lado: anim/prova_templates_painel.py. */
  const IT = { f: 'Inter Tight', p: 700, lh: 0.91, ls: -0.057 };
  const PMONO = { f: 'JetBrains Mono', p: 400, lh: 1.22, ls: 0.025, up: 1 };
  const PSERIF = { f: 'DM Serif Display', p: 400, lh: 0.9, ls: -0.036 };
  const PRUB = (p, lh = 1.3, ls = 0) => ({ f: 'Rubik', p, lh, ls });
  function _hsl(h) { const m = /^#?([0-9a-f]{6})$/i.exec(String(h || '')); if (!m) return null; const n = parseInt(m[1], 16);
    const r = (n >> 16) / 255, g = ((n >> 8) & 255) / 255, b = (n & 255) / 255, mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2;
    let hh = 0, ss = 0; if (mx !== mn) { const d = mx - mn; ss = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn);
      hh = (mx === r ? (g - b) / d + (g < b ? 6 : 0) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4) / 6; }
    return [hh, ss, l]; }
  function _hex(h, s, l) { const f = n => { const k = (n + h * 12) % 12, a = s * Math.min(l, 1 - l);
    return Math.round(255 * (l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1)))).toString(16).padStart(2, '0'); }; return '#' + f(0) + f(8) + f(4); }
  const tom = (c, s, l) => { const q = _hsl(c); return q ? _hex(q[0], Math.min(q[1], s), l) : c; };
  /* cor do template -> cor da peça. tipo diz o PAPEL da cor no original:
     escuro = fundo saturado escuro + destaque claro (refeitos do ChatGPT: vermelho, tijolo, azul-marinho);
     claro = fundo tinta clara + tinta escura (card 92, verde-limão); carvao = grafite neutro + destaque na cor;
     papel = papel neutro + destaque escurecido (leitura); matte = fundo quase preto tingido + destaque pálido (elenco);
     foto = foto escurecida + destaque na cor. */
  function pTema(s, orig, tipo) {
    const c = s && s.cor_tema && /^#[0-9a-f]{6}$/i.test(s.cor_tema) ? s.cor_tema : null;
    if (!c) return { ...orig };
    const clara = _lum(c) > 0.3, ac = clara ? c : tom(c, 0.85, 0.72);
    if (tipo === 'escuro') return { ...orig, bg: tom(c, 0.62, 0.27), ac };
    if (tipo === 'claro') return { ...orig, bg: tom(c, 0.64, 0.72), ink: tom(c, 0.3, 0.14), ac: tom(c, 0.6, 0.22) };
    if (tipo === 'papel') return { ...orig, ac: tom(c, 0.6, 0.33), ac2: tom(c, 0.6, 0.27) };
    if (tipo === 'matte') return { ...orig, bg: tom(c, 0.24, 0.18), ac: tom(c, 0.5, 0.74) };
    return { ...orig, ac }; // carvao, foto
  }
  const pVars = T => `--p-ac:${T.ac};--p-ac2:${T.ac2 || T.ac};--p-bg:${T.bg};--p-ink:${T.ink};`;
  const GRAO = `<div class="p-grao" data-deco></div>`;
  const RAIL = `<div class="p-rail" data-deco></div>`;
  const REGUA = `<div class="p-regua" data-deco></div>`;
  // pessoa sem foto: silhueta neutra (nunca rosto inventado)
  const SILHUETA = 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600"><g fill="#8d8a82"><circle cx="200" cy="170" r="92"/><path d="M40 600c0-170 70-300 160-300s160 130 160 300z"/></g></svg>');
  const pImg = (u, st = '') => u ? `<img src="${E(u)}" style="${st}">` : `<div class="p-semfoto"></div>`;
  function pChip(ps) { if (!ps) return null; const chip = ps.chip || [ps.partido, ps.ideologia].filter(Boolean).join(' · '); if (!chip) return null;
    const id = String(ps.ideologia || '').toLowerCase(); return { chip, lado: ps.lado || (/esquerda/.test(id) ? 'esq' : /direita/.test(id) ? 'dir' : 'neu') }; }
  const pcss = (o, r, extra = '') => `${fonteCss(o, r)}${extra}`;
  // cabeçalho: filete + etiqueta mono (esq.) + série na cor (dir.)
  function pMast(c, tl, o = {}) {
    const ls = o.ls ?? 0.025, fs = o.fs || 25, M = { ...PMONO, ls };
    const D = c.serie ? texto(String(c.serie), { ...M, base: fs, min: 22, piso: 20, larg: 300, maxLin: 1 }) : null;
    const L = texto(c.rotulo || '', { ...M, base: fs, min: 22, piso: 20, larg: LARG - (D ? D.w + 24 : 0), maxLin: 2 });
    const pt = o.pt ?? 19;
    return { bot: Y0 + pt + Math.max(L.h, D ? D.h : 0), html: `<div class="ab zs p-mast" style="top:${Y0}px;padding-top:${pt}px;${o.borda || ''}${ent(tl, 0)}">` +
      `<div class="tx" style="${pcss(M, L)}">${L.html}</div>${D ? `<div class="tx pa" style="${pcss(M, D)};flex:none">${D.html}</div>` : ''}</div>` };
  }
  /* título do template: grande, em 2 linhas como no original. Primeiro tenta perto do corpo original (até 80%) aceitando
     a quebra que a regra dela permite (destaque colorido nunca sozinho na linha: "Quanto / custa um voto?"); só se não
     couber desce até o mínimo legível (64) como os outros cards. Antes o texto() ia pra 1 linha pequena. */
  const pTit = (c, y, k, tl, o = {}) => {
    const fo = o.fonte || IT, b = (o.base || 111) * k, base = { ...fo, base: b, larg: LARG, maxLin: o.maxLin || 3, dest: c.destaque, cls: 'pa' };
    let r = texto(c.titulo, { ...base, min: Math.round(b * 0.8), piso: Math.round(b * 0.8), maxLin: Math.min(base.maxLin, 2) });
    if (!r.ok) r = texto(c.titulo, { ...base, min: o.min || 64 });
    // o original quebra o título em 2 linhas: se coube numa linha só e tem 3+ palavras, tenta 2 linhas no mesmo corpo
    if (r.ok && r.n === 1 && String(c.titulo || '').trim().split(/\s+/).length >= 3) {
      const r2 = texto(c.titulo, { ...base, larg: Math.round(r.w * 0.72), min: Math.round(b * 0.8), piso: Math.round(b * 0.8), maxLin: 2 });
      if (r2.ok && r2.n === 2 && r2.fs >= r.fs * 0.85) r = r2;
    }
    return { r, bot: y + r.h, html: `<div class="ab tx zs" style="top:${y}px;${fonteCss(fo, r)}${o.extra || ''}${ent(tl, o.t ?? 0.1)}">${r.html}</div>` };
  };
  // frase de apoio: no original mora no rodapé (y 1470); aqui fica logo acima da legenda (LIM) ou depois do conteúdo
  function pApoio(txt, y, k, tl, o = {}) {
    if (!txt) return { html: '', bot: y, h: 0 };
    const fo = o.fonte || PRUB(400, 1.32), A = texto(txt, { ...fo, base: (o.fs || 33) * k, min: o.min || 28, piso: 24, larg: o.larg || LARG, maxLin: o.maxLin || 3 });
    const top = o.top ?? Math.max(y, LIM - 8 - A.h);
    return { h: A.h, bot: top + A.h, html: `<div class="ab tx zs" style="top:${top}px;${pcss(fo, A)}${o.cor || ''}${ent(tl, o.t ?? 0.8)}">${A.html}</div>` };
  }
  const _ap = (txt, k, o = {}) => txt ? texto(txt, { ...(o.fonte || PRUB(400, 1.32)), base: (o.fs || 33) * k, min: o.min || 28, piso: 24, larg: LARG, maxLin: o.maxLin || 3 }).h : 0;
  // keyframes puros (t em segundos desde t0): [[fração, {props}]...]
  function kf(tl, t0, dur, pts) { const x = cl((tl - t0) / dur, 0, 1); let a = pts[0], b = pts[pts.length - 1];
    for (let i = 1; i < pts.length; i++) if (x <= pts[i][0]) { a = pts[i - 1]; b = pts[i]; break; }
    const u = b[0] === a[0] ? 1 : (x - a[0]) / (b[0] - a[0]), e = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2, o = {};
    for (const k in b[1]) o[k] = a[1][k] + (b[1][k] - a[1][k]) * e; return o; }
  const PN = {}; // cards do Painel (entram em C no fim)

  // Card 89 · Versão ChatGPT do card 03 (capa: pergunta + foto em moldura de filete + legenda da foto)
  PN.p89 = (c, tl, s, k) => pFig(c, tl, s, k, { orig: { bg: '#a32424', ink: '#fff4ec', ac: '#ffdb79' }, H: 550 });

  // Card 134 · Vibe cool VC02 "Aprovado sem faixa" (capa escura: foto P&B a 15% + meio-tom + janela com foto; c.faixa = VC01 com faixa)
  PN.p134 = (c, tl, s, k) => { const T = pTema(s, { bg: '#151716', ink: '#eeece3', ac: '#ff994e' }, 'carvao');
    const fundo = c.foto_fundo || s.foto_fundo || c.midia || c.foto;
    let h = fundo ? `<div class="p-back" data-deco><img src="${E(fundo)}" style="object-position:center 43%"></div><div class="p-meiotom" data-deco><img src="${E(fundo)}" style="object-position:center 43%"></div>` : '';
    h += '<div class="p-sombra134" data-deco></div>';
    const M = pMast(c, tl, { ls: 0.045, pt: 17 }); h += M.html; let y = Math.max(M.bot + 38, 356);
    const Ti = pTit(c, y, k, tl, { fonte: { f: 'Rubik', p: 800, lh: 0.89, ls: -0.054 }, base: 112 }); h += Ti.html;
    const top = Math.max(Ti.bot + 60, 1016), H = Math.min(Math.round(424 * Math.max(k, 0.85)), LIM - 10 - top);
    const fx = c.faixa ? texto(c.faixa, { ...PMONO, ls: 0.045, base: 25, min: 22, piso: 20, larg: LARG - 44, maxLin: 1 }) : null;
    h += `<div class="p-janela${fx ? ' com-faixa' : ''}" style="left:150px;width:765px;top:${top}px;height:${Math.max(H, 280)}px;${ent(tl, 0.35, 0.6, 70)}">${pImg(c.midia || c.foto || fundo, 'object-position:50% 34%')}` +
      (fx ? `<div class="faixa tx" style="${pcss({ ...PMONO, ls: 0.045 }, fx)}">${fx.html}</div>` : '') + '</div>';
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim: top + Math.max(H, 280) }; };

  // Card 79 · Brasileirada B04 "Quanto pesa a passagem?" (foto de fundo + véu + gráfico de barras que cresce)
  PN.p79 = (c, tl, s, k) => { const T = pTema(s, { bg: '#262c24', ink: '#fff1d9', ac: '#ffcc77' }, 'foto');
    const fundo = c.foto_fundo || s.foto_fundo || c.midia || c.foto;
    let h = (fundo ? `<div class="p-back79" data-deco><img src="${E(fundo)}"></div>` : '') + '<div class="p-veu79" data-deco></div>';
    const M = pMast(c, tl, { fs: 26, ls: 0.04, pt: 16, borda: 'border-top-color:#fff0d6;' }); h += M.html; let y = M.bot + 25;
    const Ti = pTit(c, y, k, tl, { fonte: { ...IT, lh: 0.89, ls: -0.063 }, base: 121 }); h += Ti.html;
    const bs = (c.barras || []).slice(0, 5).map(b => ({ ...b, v: Number(b.valor ?? b.a ?? 0) || 0 }));
    const ilustracao = typeof c.ilustracao === 'string' && c.ilustracao.trim();
    const dt0 = Ti.bot + (ilustracao ? 210 : 50); // dt final depende da nota e do título do gráfico (abaixo)
    const Lb = texto(c.grafico_titulo || '', { ...PMONO, ls: 0.04, base: 28, min: 22, piso: 20, larg: LARG, maxLin: 2 });
    const nota = c.nota ? texto(c.nota, { ...PMONO, ls: 0.04, base: 22, min: 20, piso: 20, larg: LARG, maxLin: 2 }) : null;
    // 25/11 (A1 BC-ESCUTA): faixa de referência {de, ate, rotulo, sub, depois} desenhada atrás das barras; cada parte entra na fala
    const fx = c.faixa && typeof c.faixa === 'object' && isFinite(+c.faixa.de) && isFinite(+c.faixa.ate) ? c.faixa : null;
    const fxT = (t, d) => CAPA ? 1 : typeof t === 'number' ? cl((tl - (t - s.start)) / (d || 0.6), 0, 1) : 1;
    const fxL = fx ? [['rotulo', 't'], ['sub', 't_sub'], ['depois', 't_depois']].filter(([q]) => fx[q])
      .map(([q, tq]) => ({ q, a: fxT(fx[tq] ?? fx.t), r: texto(String(fx[q]), { ...PRUB(600, 1.2), base: 36 * k, min: 28, piso: 26, larg: LARG, maxLin: 2 }) })) : [];
    const fxH = fxL.reduce((a, l) => a + l.r.h + 8, 0) + (fxL.length ? 6 : 0);
    const resto = 19 + Lb.h + 9 + fxH + (nota ? nota.h + 14 : 0) + 6, dt = Math.max(dt0, Math.min(1020, LIM - resto - Math.round(445 * k)));
    const W = LARG, Hc = Math.max(250, Math.min(Math.round(445 * k), LIM - resto - dt));
    const un = String(c.unidade ?? '').trim();
    const moedaComCentavos = un === 'R$' && bs.some(b => !Number.isInteger(b.v));
    const fmt = (v, barra = false) => {
      const n = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2, minimumFractionDigits: barra && moedaComCentavos ? 2 : 0 }).format(v);
      return un === 'R$' ? 'R$ ' + n : n + (un === '%' ? '%' : un ? ' ' + un : '');
    };
    const mx0 = Math.max(1, ...bs.map(b => b.v)), base10 = 10 ** Math.floor(Math.log10(mx0)), mx = Math.ceil(mx0 / base10) * base10;
    const sy = Hc / 445, top = 75 * sy, bot = 355 * sy, Y = v => bot - (v / mx) * (bot - top) * 0.86, sx = W / 864;
    const x0 = Math.round(Math.max(95, (fmt(mx).length * 0.62 * 24) + 15) * sx), x1 = Math.round(826 * sx), n = Math.max(1, bs.length);
    const pl = n > 3 ? 26 : 31, vl = n > 3 ? 40 : 46, bw = Math.min(117 * sx, (x1 - x0) / n * 0.7);
    let sv = '';
    const nt = Number.isInteger(mx) && mx >= 2 && mx <= 5 ? mx : 4; // 25/11 (A3 PLP299): eixo 0/1/2/3 em vez de 0,75/1,5/2,25
    for (let i = 0; i <= nt; i++) { const a = bot - (i / nt) * (bot - top) * 0.86;
      sv += `<line x1="${x0}" y1="${a}" x2="${x1}" y2="${a}" stroke="${i ? 'rgba(255,241,217,.26)' : 'rgba(255,241,217,.67)'}" stroke-width="${i ? 1 : 2}"/><text x="${x0 - 13}" y="${a + 7}" text-anchor="end" font-family="JetBrains Mono" font-size="24" fill="#fff1d9">${E(fmt(mx * i / nt))}</text>`; }
    if (fx) { const a0 = fxT(fx.t), a1 = fx.t_teto != null ? fxT(fx.t_teto, 1.0) : a0, ad = fx.t_depois != null ? fxT(fx.t_depois, 0.8) : 0;
      const de = +fx.de, ate = de + (+fx.ate - de) * a1, ya = Y(ate), yb = Y(de);
      sv += `<rect x="${x0}" y="${ya}" width="${x1 - x0}" height="${Math.max(3, yb - ya)}" fill="${T.ac}" fill-opacity="${(0.3 + 0.25 * ad) * a0}" stroke="${T.ac}" stroke-width="3" stroke-dasharray="10 7" stroke-opacity="${a0}"/>`; }
    bs.forEach((b, i) => { const g = CAPA ? 1 : 1 - Math.pow(1 - cl((tl - (typeof b.t === 'number' ? b.t - s.start : 0.4)) / 1.45, 0, 1), 3);
      const x = x0 + (x1 - x0) * (i + 0.5) / n, at = Y(b.v * g), ult = i === bs.length - 1, cor = ult ? T.ac : 'rgba(255,241,217,.67)';
      sv += `<rect x="${x - bw / 2}" y="${at}" width="${bw}" height="${Math.max(0, bot - at)}" fill="${cor}"/>` +
        `<text x="${x}" y="${at - 18}" text-anchor="middle" font-family="Inter Tight" font-weight="700" font-size="${vl}" fill="${ult ? T.ac : '#fff1d9'}" opacity="${g > 0.02 ? 1 : 0}">${E(fmt(b.v, true))}</text>` +
        `<text x="${x}" y="${bot + 43 * sy + 6}" text-anchor="middle" font-family="JetBrains Mono" font-size="${pl}" fill="#fff1d9">${E(b.rotulo || '')}</text>`; });
    if (fx && fx.t_depois != null) { const ad = fxT(fx.t_depois, 0.8), yc = (Y(+fx.de) + Y(+fx.ate)) / 2;
      sv += `<circle cx="${x1 - 22}" cy="${yc}" r="${14 * ad}" fill="${T.ac}" stroke="#fff1d9" stroke-width="3" opacity="${ad}"/>`; }
    const fxHtml = fxL.map((l, i) => `<div class="tx" style="${pcss(PRUB(600, 1.2), l.r)};margin-top:${i ? 8 : 14}px;opacity:${l.a};${l.q === 'rotulo' || l.q === 'depois' ? `color:${T.ac}` : ''}">${l.r.html}</div>`).join('');
    // 25/11 (A2 EL-NINO, q_008500: eixo vazio 6,5 s): com barras ligadas à voz, o gráfico entra 0,5 s antes da 1ª barra
    const tbs = bs.filter(b => typeof b.t === 'number').map(b => b.t - s.start), tg = tbs.length ? Math.max(0.3, Math.min(...tbs) - 0.5) : 0.3;
    if (ilustracao) {
      const altura = Math.min(170, dt - Ti.bot - 30);
      h += `<img class="ab p-ilustracao79" data-deco alt="" src="${E(ilustracao)}" style="top:${Ti.bot + 12}px;height:${altura}px;width:${LARG}px;object-fit:contain;${ent(tl, tg, 0.45, 0)}">`;
    }
    h += `<div class="ab zs" style="top:${dt}px;border-top:1px solid rgba(255,240,214,.63);padding-top:19px;${ent(tl, tg)}"><div class="tx" style="${pcss({ ...PMONO, ls: 0.04 }, Lb)}">${Lb.html}</div>` +
      `<svg width="${W}" height="${Math.round(Hc)}" style="display:block;margin-top:9px;overflow:visible">${sv}</svg>` + fxHtml +
      (nota ? `<div class="tx" style="${pcss({ ...PMONO, ls: 0.04 }, nota)};margin-top:14px;opacity:${(0.85 * (typeof c.t_nota === 'number' ? fxT(c.t_nota) : 1)).toFixed(3)}">${nota.html}</div>` : '') + '</div>';
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA, fim: dt + 19 + Lb.h + 9 + Hc + fxH + (nota ? nota.h + 14 : 0) }; };

  // linhas numeradas (cards 92 e 112): número mono na cor | verbo Inter Tight | explicação Rubik
  function pLinhas(it, tl, s, k, o) {
    const ga = 20, ca = Math.round((LARG - 60 - 2 * ga) / 1.85), cb = LARG - 60 - 2 * ga - ca; let html = '', h = 0;
    it.forEach((x, q) => { const S = texto(x.texto || '', { f: 'Inter Tight', p: 700, lh: 1.03, ls: -0.025, base: 44 * k, min: 32, piso: 26, larg: ca, maxLin: 3 });
      const sb = x.sub || x.destaque || '', B = sb ? texto(sb, { ...PRUB(400, 1.2), base: 29 * k, min: 24, piso: 22, larg: cb, maxLin: 3 }) : null;
      const N = texto(String(q + 1).padStart(2, '0'), { ...PMONO, base: 25, min: 22, larg: 60, maxLin: 1 });
      const pad = Math.round(34 * k), lh = Math.max(Math.round(140 * k), S.h + 2 * pad, B ? B.h + 2 * pad : 0); h += lh;
      const st = o.estilo ? o.estilo(x, q) : '';
      html += `<div class="p-linha" style="height:${lh}px;padding:${pad}px 0;grid-template-columns:60px ${ca}px ${cb}px;gap:${ga}px;${st}"><div class="tx pa" style="${pcss(PMONO, N)}">${N.html}</div>` +
        `<div class="tx" style="${pcss({ f: 'Inter Tight', p: 700, lh: 1.03, ls: -0.025 }, S)}">${S.html}</div>${B ? `<div class="tx" style="${pcss(PRUB(400, 1.2), B)}">${B.html}</div>` : '<div></div>'}</div>`; });
    return { h: h + 1, html };
  }
  // Card 92 · Versão ChatGPT do card 06 (guia prático: passos numerados; a linha da vez acende quando a voz fala)
  PN.p92 = (c, tl, s, k) => { const T = pTema(s, { bg: '#d6e483', ink: '#263022', ac: '#3f5519' }, 'claro');
    const it = (c.itens || []).slice(0, 4), ts = it.map((x, q) => tItem(x, q, it.length, s)); let at = -1; ts.forEach((x, q) => { if (tl >= x) at = q; });
    const M = pMast(c, tl); let h = RAIL + M.html, y = Math.max(M.bot + 38, 356);
    const Ti = pTit(c, y, k, tl); h += Ti.html; y = Ti.bot + Math.round(57 * k);
    const L = pLinhas(it, tl, s, k, { estilo: (x, q) => `${q === at ? 'background:color-mix(in srgb,var(--p-ac) 15%,transparent);' : ''}${ent(tl, 0.3 + 0.12 * q)}` });
    h += `<div class="ab zs p-passos" style="top:${y}px">${L.html}</div>`; y += L.h;
    const A = pApoio(c.apoio, y + 40, k, tl); h += A.html;
    return { bg: T.bg, fg: T.ink, escuro: 0, vars: pVars(T), html: h + REGUA + GRAO, fim: Math.max(y, A.bot) }; };

  // Card 112 · Versão ChatGPT do card 26 (CTA: cartaz com estrela vazada girando devagar + verbos que entram com a voz)
  PN.p112 = (c, tl, s, k) => { const T = pTema(s, { bg: '#972e2b', ink: '#fff3e5', ac: '#ffc6a1' }, 'escuro');
    const it = (c.itens || []).slice(0, 4), ph = ((tl % 3) + 3) % 3 / 3, w = 0.5 - 0.5 * Math.cos(2 * Math.PI * ph);
    // estrela:false (peça política, A2 do dólar 25/11): sem a estrela de cinco pontas, que pode ser lida como símbolo de partido
    let h = (c.estrela === false ? '' : `<div class="p-estrela" data-deco style="right:-265px;top:720px;width:690px;height:690px;opacity:.21;transform:rotate(${(-15 + 7 * w).toFixed(2)}deg) scale(${(1 + 0.06 * w).toFixed(3)})"></div>`) + RAIL;
    const M = pMast(c, tl); h += M.html; let y = Math.max(M.bot + 38, 356);
    const Ti = pTit(c, y, k, tl); h += Ti.html; y = Ti.bot + Math.round(57 * k);
    const L = pLinhas(it, tl, s, k, { estilo: (x, q) => ent(tl, tItem(x, q, it.length, s)) });
    h += `<div class="ab zs p-passos" style="top:${y}px;background:color-mix(in srgb,var(--p-bg) 86%,transparent)">${L.html}</div>`; y += L.h;
    const A = pApoio(c.apoio, y + 40, k, tl); h += A.html;
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim: Math.max(y, A.bot) }; };

  // Card 118 · Versão ChatGPT do card 32 (citação: colagem de 2 fotos + papel rasgado com megafone e aspas em serifa)
  PN.p118 = (c, tl, s, k) => { const T = pTema(s, { bg: '#853e2a', ink: '#fff2ea', ac: '#ffcf96' }, 'escuro');
    const meg = s && s.cor_tema ? tom(s.cor_tema, 0.6, 0.38) : '#9e362b';
    const M = pMast(c, tl); let h = RAIL + M.html, y = Math.max(M.bot + 38, 356);
    const Ti = pTit(c, y, k, tl); h += Ti.html; y = Ti.bot + Math.round(57 * k);
    const ps = c.pessoa || {}, autor = c.autor || ps.nome || '', ctx = c.contexto || ps.cargo || '';
    const Q = texto('“' + String(c.citacao || '').replace(/^[“"]|[”"]$/g, '') + '”', { ...PSERIF, lh: 1.04, ls: 0, base: 51 * k, min: 34, piso: 30, larg: LARG - 54 - 64 - 97 - 24, maxLin: 4 });
    const rally = Math.max(75, Q.h) + 52, Hc = Math.max(Math.round(516 * k), rally + 260);
    const fx = c.foto2 ? pImg(c.foto2) : `<div class="p-tecido"></div>`;
    h += `<div class="ab zs" style="top:${y}px;height:${Hc}px">` +
      `<div class="p-media" style="position:absolute;left:0;top:0;width:72%;height:88%;${ent(tl, 0.3, 0.6, 50)}">${pImg(c.foto || c.midia || ps.foto, 'filter:grayscale(1) contrast(1.13);object-position:50% 40%')}</div>` +
      `<div class="p-media" style="position:absolute;right:0;top:24px;width:28%;height:75%;transform:rotate(6deg);${ent(tl, 0.45, 0.6, 50)}">${fx}</div>` +
      `<div class="p-rally" style="left:27px;right:27px;bottom:12px;${ent(tl, 0.7, 0.5, 40)}"><div class="p-megafone" style="background:${meg}"></div>` +
      `<div class="tx" style="${pcss({ ...PSERIF, lh: 1.04, ls: 0 }, Q)}">${Q.html}</div></div></div>`;
    y += Hc;
    if (autor || ctx) { const ga = 24, ca = Math.round((LARG - ga) * 0.9 / 1.9), cb = LARG - ga - ca;
      const S = texto(autor, { f: 'Inter Tight', p: 700, lh: 1.03, ls: -0.025, base: 40 * k, min: 30, piso: 26, larg: ca, maxLin: 2 });
      const ch = chipH(pChip(ps.nome ? ps : { ...ps, partido: c.partido, ideologia: c.ideologia }) || {}, ca);
      const B = ctx ? texto(ctx, { ...PRUB(400, 1.2), base: 30 * k, min: 24, piso: 22, larg: cb, maxLin: 3 }) : null;
      const lh = Math.max(Math.round(104 * k), S.h + (ch.h ? ch.h + 10 : 0) + 48, B ? B.h + 48 : 0);
      h += `<div class="ab zs p-linha" style="top:${y + 26}px;height:${lh}px;padding:24px 0;grid-template-columns:${ca}px ${cb}px;gap:${ga}px;${ent(tl, 0.9)}"><div><div class="tx" style="${pcss({ f: 'Inter Tight', p: 700, lh: 1.03, ls: -0.025 }, S)}">${S.html}</div>${ch.html ? `<div style="margin-top:10px">${ch.html}</div>` : ''}</div>` +
        `${B ? `<div class="tx" style="${pcss(PRUB(400, 1.2), B)}">${B.html}</div>` : '<div></div>'}</div>`; y += 26 + lh; }
    const A = pApoio(c.apoio, y + 40, k, tl); h += A.html;
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim: Math.max(y, A.bot) }; };

  // Card 98 · Versão ChatGPT do card 12 (etapas / quem está ligado a quem: 3 retratos P&B em degrau + colchete que liga)
  PN.p98 = (c, tl, s, k) => { const T = pTema(s, { bg: '#1f3561', ink: '#f9f2e8', ac: '#a9d3ff' }, 'escuro');
    const it = (c.itens || c.pessoas || []).slice(0, 3), n = Math.max(1, it.length), ga = 37, cw = Math.floor((LARG - ga * (n - 1)) / n);
    const M = pMast(c, tl); let h = RAIL + M.html, y = Math.max(M.bot + 38, 356);
    const Ti = pTit(c, y, k, tl); h += Ti.html; y = Ti.bot + Math.round(57 * k);
    const mh = Math.round((n === 2 ? 425 : 290) * k), deg = n === 3 ? Math.round(67 * k) : 0, ts = it.map((x, q) => tItem(x, q, it.length, s));
    let alt = 0; const cols = it.map((x, q) => {
      const R = texto(x.rotulo || `Etapa ${String(q + 1).padStart(2, '0')}`, { ...PMONO, base: 20, min: 20, piso: 18, larg: cw, maxLin: 2 });
      const S = texto(x.texto || x.nome || '', { f: 'Inter Tight', p: 700, lh: 1.04, ls: -0.02, base: 36 * k, min: 28, piso: 24, larg: cw, maxLin: 3 });
      const sub = x.texto && x.nome ? texto(x.nome, { ...PRUB(600, 1.15), base: 26, min: 24, piso: 22, larg: cw, maxLin: 2 }) : null;
      const ch = chipH(pChip(x) || {}, cw);
      const hh = (q === 1 ? deg : 0) + mh + 30 + R.h + 10 + S.h + (sub ? sub.h + 8 : 0) + (ch.h ? ch.h + 10 : 0) + 16; alt = Math.max(alt, hh);
      return `<div style="margin-top:${q === 1 ? deg : 0}px;padding-bottom:16px;border-bottom:2px solid currentColor;${ent(tl, ts[q])}"><div class="p-media" style="height:${mh}px;border:1px solid currentColor">${pImg(x.foto, 'filter:grayscale(1) contrast(1.05);object-position:center 40%')}</div>` +
        `<div class="tx pa" style="${pcss(PMONO, R)};margin:20px 0 10px">${R.html}</div><div class="tx" style="${pcss({ f: 'Inter Tight', p: 700, lh: 1.04, ls: -0.02 }, S)}">${S.html}</div>` +
        (sub ? `<div class="tx" style="${pcss(PRUB(600, 1.15), sub)};margin-top:8px">${sub.html}</div>` : '') + (ch.html ? `<div style="margin-top:10px">${ch.html}</div>` : '') + '</div>'; });
    const liga = ease((tl - (ts[n - 1] || 0)) / 0.9), bx = 0.48 + 0.52 * (CAPA ? 1 : liga);
    h += `<div class="ab zs" style="top:${y}px;display:grid;grid-template-columns:repeat(${n},${cw}px);gap:${ga}px;align-items:start">${cols.join('')}</div>`;
    y += alt + 20; h += `<div class="p-colchete" data-deco style="top:${y}px;transform:scaleX(${bx.toFixed(3)});opacity:${(0.42 + 0.58 * (CAPA ? 1 : liga)).toFixed(2)}"></div>`; y += 16;
    if (c.nota) { const N = texto(c.nota, { ...PMONO, base: 20, min: 20, piso: 18, larg: LARG, maxLin: 2 }); h += `<div class="ab tx zs" style="top:${y + 25}px;${pcss(PMONO, N)};${ent(tl, 0.9)}">${N.html}</div>`; y += 25 + N.h; }
    const A = pApoio(c.apoio, y + 40, k, tl); h += A.html;
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim: Math.max(y, A.bot) }; };

  // bloco de nome do elenco (cards 143, 160 e 162): nome Rubik 600 + cargo mono na cor + chip partido · ideologia
  function pNome(ps, larg, k, o = {}) {
    const W = texto(ps.nome || '', { ...PRUB(600, 1.07, -0.028), base: 37 * k, min: 30, piso: 26, larg, maxLin: 2 });
    const R = ps.cargo ? texto(ps.cargo, { ...PMONO, ls: 0.014, lh: 1.13, base: 23, min: 22, piso: 20, larg, maxLin: 2 }) : null;
    const ch = chipH(pChip(ps) || {}, larg);
    return { h: (o.borda === false ? 0 : 13) + W.h + (R ? R.h + 13 : 0) + (ch.h ? ch.h + 12 : 0), html: `<div style="${o.borda === false ? '' : 'padding-top:13px;border-top:1px solid currentColor;'}">` +
      `<div class="tx" style="${pcss(PRUB(600, 1.07, -0.028), W)}">${W.html}</div>${R ? `<div class="tx" style="${pcss({ ...PMONO, ls: 0.014, lh: 1.13 }, R)};margin-top:13px;color:${o.corCargo || 'var(--p-ac)'}">${R.html}</div>` : ''}` +
      `${ch.html ? `<div style="margin-top:12px">${ch.html}</div>` : ''}</div>` };
  }
  // Card 143 · Vibe cool VC08 "Sticker com pop de papel" (retrato recortado que cai, quica e assenta sobre papel pontilhado)
  PN.p143 = (c, tl, s, k) => { const T = pTema(s, { bg: '#e9e4d8', ink: '#1c201e', ac: '#91452f', ac2: '#71351f' }, 'papel');
    const ps = c.pessoa || (c.pessoas || [])[0] || {};
    const M = pMast(c, tl, { ls: 0.045, pt: 17 }); let h = M.html, y = Math.max(M.bot + 38, 356);
    const Ti = pTit(c, y, k, tl, { fonte: { ...PSERIF, lh: 0.89, ls: -0.043 }, base: 132 }); h += Ti.html;
    const Nm = pNome(ps, LARG, k), ap = c.apoio ? texto(c.apoio, { ...PMONO, ls: 0.045, lh: 1.2, base: 24, min: 22, piso: 20, larg: LARG, maxLin: 3 }) : null;
    const baixo = Nm.h + (ap ? ap.h + 22 : 0), ty = LIM - 8 - baixo;
    const cy = Math.max(Ti.bot + 30, 560), ch = Math.min(728, ty - 24 - cy);
    const pk = CAPA ? { y: 0, r: -5, o: 1 } : kf(tl, 0.3, 1.5, [[0, { y: -239, r: 9, o: 0 }], [0.3, { y: -40, r: -2, o: 1 }], [0.57, { y: 17, r: -8, o: 1 }], [0.8, { y: -22, r: -1, o: 1 }], [1, { y: 0, r: -5, o: 1 }]]);
    h += `<div class="p-pontos" data-deco style="left:165px;top:${cy + 67}px;width:714px;height:${Math.max(200, Math.min(575, ch - 60))}px"></div>`;
    h += `<div class="p-recorte" style="left:170px;top:${cy}px;width:715px;height:${Math.max(ch, 240)}px;opacity:${pk.o.toFixed(3)};transform:translateY(${pk.y.toFixed(1)}px) rotate(${pk.r.toFixed(2)}deg)"><img src="${E(ps.foto || SILHUETA)}"></div>`;
    h += `<div class="ab zs" style="top:${ty}px;${ent(tl, 0.9)}">${Nm.html}${ap ? `<div class="tx" style="${pcss({ ...PMONO, ls: 0.045, lh: 1.2 }, ap)};margin-top:22px;color:var(--p-ac2)">${ap.html}</div>` : ''}</div>`;
    return { bg: T.bg, fg: T.ink, escuro: 0, vars: pVars(T), html: h + REGUA + GRAO, fim: ty + baixo, falta: ch < 240 }; };

  // Card 160 · Vibe cool VC13 "News Brasil · Uma pessoa em foco" (pessoa nítida na frente, 2 desfocadas atrás, cidade P&B)
  PN.p160 = (c, tl, s, k) => { const T = pTema(s, { bg: '#24382F', ink: '#F8EEDF', ac: '#E3CB8D' }, 'matte');
    const ps = c.pessoa || (c.pessoas || [])[0] || {}, fp = (c.fundo_pessoas || []).slice(0, 2), cid = c.foto_fundo || s.foto_fundo;
    let h = cid ? `<div class="p-cidade" data-deco><img src="${E(cid)}"></div>` : '';
    const M = pMast(c, tl, { ls: 0.045, pt: 17 }); h += M.html; let y = Math.max(M.bot + 38, 355);
    const Ti = pTit(c, y, k, tl, { fonte: PSERIF, base: 114 }); h += Ti.html;
    const Nm = pNome(ps, 520, k), nt = LIM - 8 - Nm.h, ly = Math.max(Ti.bot + 20, 560), lb = nt + 100;
    const far = (u, x, yy, w, hh, a) => u ? `<div class="p-pessoa far" style="left:${x}px;top:${yy}px;width:${w}px;height:${hh}px;opacity:${(a * (CAPA ? 1 : ease((tl - 0.2) / 0.8))).toFixed(3)}"><img src="${E(u)}"></div>` : '';
    h += far(fp[0] && fp[0].foto, 28, ly + 27, 256, 625, 0.74) + far(fp[1] && fp[1].foto, 775, ly + 87, 266, 599, 0.7);
    h += `<div class="p-aro" data-deco style="left:229px;top:${ly - 29}px;opacity:${(CAPA ? 1 : ease((tl - 0.1) / 0.8)).toFixed(3)}"></div>`;
    h += `<div class="p-chao" data-deco style="top:${lb - 130}px"></div>`;
    h += `<div class="p-pessoa nitida fade" style="left:233px;top:${ly}px;width:617px;height:${Math.max(300, lb - ly)}px;${ent(tl, 0.3, 0.7, 40)}"><img src="${E(ps.foto || SILHUETA)}"></div>`;
    h += `<div class="p-sombra-txt" data-deco></div><div class="ab zs" style="top:${nt}px;right:auto;width:520px;z-index:8;${ent(tl, 0.8)}">${Nm.html}</div>`;
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim: nt + Nm.h, falta: lb - ly < 300 }; };

  // Card 162 · Vibe cool VC15 "News Brasil · Troca de foco" (dois lados de corpo inteiro; o foco passa de um pro outro com a voz)
  PN.p162 = (c, tl, s, k) => { const T = pTema(s, { bg: '#273642', ink: '#EFF2EA', ac: '#B4D0D7' }, 'matte');
    const ps = (c.pessoas || []).slice(0, 2); while (ps.length < 2) ps.push({});
    const M = pMast(c, tl, { ls: 0.045, pt: 17 }); let h = '<div class="p-palco162" data-deco></div>' + M.html, y = Math.max(M.bot + 38, 355);
    const Ti = pTit(c, y, k, tl, { fonte: PSERIF, base: 114 }); h += Ti.html;
    const cw = (LARG - 30) / 2, Ns = ps.map(p => pNome(p, cw, k)), nh = Math.max(...Ns.map(n => n.h)), nt = LIM - 8 - nh, base = nt - 56;
    const top = Math.max(Ti.bot + 30, 600), alto = base - 16 - top;
    const tS = typeof ps[1].t === 'number' ? ps[1].t - s.start : (s.end - s.start) * 0.45, f = CAPA && tS < 1 ? 0 : ease((tl - tS) / 0.7);
    const foco = (a) => `filter:grayscale(1) contrast(${(1.02 - 0.21 * a).toFixed(3)}) blur(${(7 * a).toFixed(2)}px)`;
    const fundo = c.fundo_pessoa && c.fundo_pessoa.foto;
    if (fundo) h += `<div class="p-pessoa far fade" style="left:414px;top:${top + 171}px;width:229px;height:${Math.max(200, alto - 171)}px;opacity:.37"><img src="${E(fundo)}"></div>`;
    h += `<div class="p-linhabase" data-deco style="top:${base}px"></div>`;
    h += `<div class="p-pessoa nitida" style="left:114px;top:${top}px;width:408px;height:${Math.max(300, alto)}px;opacity:${(1 - 0.44 * f).toFixed(3)};${ent(tl, 0.2, 0.6, 30)}"><img src="${E(ps[0].foto || SILHUETA)}" style="${foco(f)}"></div>`;
    h += `<div class="p-pessoa nitida" style="left:537px;top:${top + 29}px;width:408px;height:${Math.max(300, alto - 29)}px;opacity:${(0.56 + 0.44 * f).toFixed(3)};${ent(tl, 0.35, 0.6, 30)}"><img src="${E(ps[1].foto || SILHUETA)}" style="${foco(1 - f)}"></div>`;
    h += `<div class="p-sombra-txt" data-deco></div><div class="ab zs" style="top:${nt}px;display:grid;grid-template-columns:${cw}px ${cw}px;gap:30px;z-index:8;${ent(tl, 0.8)}">${Ns.map(n => `<div>${n.html}</div>`).join('')}</div>`;
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim: nt + nh, falta: alto < 300 }; };

  // capa com foto em moldura (cards 89, 117 e 119 são o mesmo esqueleto: muda o acabamento da moldura)
  function pFig(c, tl, s, k, cfg) {
    const T = pTema(s, cfg.orig, 'escuro');
    let h = RAIL;
    if (cfg.halo) h += `<div class="p-halo" data-deco style="right:-95px;top:565px;width:755px;height:755px;opacity:${(0.53 * (CAPA ? 1 : ease((tl - 0.1) / 0.9))).toFixed(3)}"></div>`;
    const M = pMast(c, tl); h += M.html; let y = Math.max(M.bot + 38, 356);
    const Ti = pTit(c, y, k, tl); h += Ti.html; y = Ti.bot + Math.round(57 * k);
    const cap = c.legenda_foto ? texto(c.legenda_foto, { ...PMONO, base: 20, min: 20, piso: 20, larg: LARG - 12 - (cfg.pad ? 26 : 0), maxLin: 2 }) : null;
    const pad = cfg.pad || 0, apH = _ap(c.apoio, k), livre = LIM - 8 - (apH ? apH + 40 : 0) - (cap ? cap.h + 22 : 0) - y - 14 - 2 * pad;
    const H = Math.max(300, Math.min(Math.round(cfg.H * k), livre)), zoom = 1.01 + 0.05 * ease((tl - 0.3) / Math.max(2, s.end - s.start));
    const atras = cfg.bloco ? `<div class="p-blococor" data-deco style="top:32px;right:-18px;bottom:${22 + (cap ? cap.h + 22 : 0)}px;left:20px"></div>` : '';
    h += `<div class="ab zs" style="z-index:2;top:${y + 7}px;left:156px;right:171px;${pad ? `padding:${pad}px;outline:1px solid currentColor;` : ''}${ent(tl, 0.35, 0.6, 60)}">${atras}<div class="p-media${pad ? '' : ' p-filete'}" style="position:relative;height:${H}px">${pImg(c.midia || c.foto, `object-position:${cfg.pos || '50% 51%'};scale:${zoom.toFixed(4)}`)}</div>` +
      (cap ? `<div class="tx" style="${pcss(PMONO, cap)};padding-top:22px;position:relative">${cap.html}</div>` : '') + '</div>';
    y += 7 + H + 2 * pad + (cap ? cap.h + 22 : 0);
    const A = pApoio(c.apoio, y + 40, k, tl); h += A.html;
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim: Math.max(y, A.bot) };
  }
  // Card 117 · Versão ChatGPT do card 31 "Brasil escrito com S" (foto com bloco de cor girado atrás)
  PN.p117 = (c, tl, s, k) => pFig(c, tl, s, k, { orig: { bg: '#334326', ink: '#fff5e5', ac: '#dfed97' }, H: 530, bloco: 1 });
  // Card 119 · Versão ChatGPT do card 33 "O território tem voz" (sol grande atrás + foto com passe-partout de filete)
  PN.p119 = (c, tl, s, k) => pFig(c, tl, s, k, { orig: { bg: '#552026', ink: '#fff4ec', ac: '#ffaf94' }, H: 570, halo: 1, pad: 13, pos: '50% 40%' });

  // foto inteira + título em serifa (cards 81, 84, 114 e 115)
  function pSerifa(c, tl, s, k, cfg) {
    const T = pTema(s, cfg.orig, 'foto'), fundo = c.foto_fundo || s.foto_fundo || c.midia || c.foto;
    const tc = s && s.cor_tema ? tom(s.cor_tema, 0.9, 0.87) : cfg.corTit; // título claro na tinta da cor da peça (84, 114, 115)
    let h = `<div class="p-back79" data-deco style="${cfg.serie ? 'background:var(--p-bg)' : ''}">${fundo ? `<img src="${E(fundo)}" style="object-position:50% ${cfg.pos || '50%'};${cfg.serie ? 'opacity:.86;' : ''}scale:${(1.0 + 0.04 * ease(tl / Math.max(2, s.end - s.start))).toFixed(4)}">` : ''}</div><div class="p-veu" data-deco style="background:${cfg.veu}"></div>`;
    if (cfg.serie) h += RAIL;
    const M = pMast(c, tl, cfg.serie ? {} : { fs: 26, ls: 0.065, pt: 18 }); h += M.html;
    const al = cfg.centro ? 'text-align:center;' : '';
    const fo = { ...PSERIF, lh: cfg.lh, ls: cfg.ls };
    const r0 = texto(c.titulo, { ...fo, base: cfg.base * k, min: Math.round(cfg.base * k * 0.8), piso: Math.round(cfg.base * k * 0.8), larg: LARG, maxLin: 2, dest: c.destaque, cls: 'pa' });
    const r = r0.ok ? r0 : texto(c.titulo, { ...fo, base: cfg.base * k, min: 64, larg: LARG, maxLin: 3, dest: c.destaque, cls: 'pa' });
    const ap = c.apoio ? texto(c.apoio, { ...PRUB(400, 1.32), base: 33 * k, min: 28, piso: 24, larg: LARG, maxLin: 3 }) : null;
    const estr = cfg.estrela ? Math.round(57 * 0.75) + 24 : 0;
    const top = Math.min(cfg.top, LIM - 8 - (ap ? ap.h + 40 : 0) - r.h), y0 = Math.max(M.bot + 60 + estr, top);
    if (cfg.estrela) h += `<div class="p-brilho" data-deco style="left:${cfg.centro ? 527 : 150}px;top:${y0 - estr}px;font-size:57px;color:var(--p-ac);${ent(tl, 0.2)}">✦</div>`;
    if (cfg.brilhos) h += `<div class="p-brilho" data-deco style="left:${cfg.brilhos[0]}px;top:${y0 - 40}px;font-size:${cfg.brilhos[2] || 55}px;color:${cfg.corBrilho || 'var(--p-ac)'};${ent(tl, 0.3)}">✦</div>` +
      `<div class="p-brilho" data-deco style="right:${cfg.brilhos[1]}px;top:${y0 + r.h - 50}px;font-size:${cfg.brilhos[3] || 38}px;color:${cfg.corBrilho || 'var(--p-ac)'};${ent(tl, 0.5)}">✧</div>`;
    h += `<div class="ab tx zs" style="top:${y0}px;${fonteCss(fo, r)}color:${tc};z-index:4;${al}${ent(tl, 0.15)}">${r.html}</div>`;
    let y = y0 + r.h;
    if (ap) { const t2 = Math.max(y + 40, LIM - 8 - ap.h); h += `<div class="ab tx zs" style="top:${t2}px;${pcss(PRUB(400, 1.32), ap)}${al}z-index:4;${ent(tl, 0.8)}">${ap.html}</div>`; y = t2 + ap.h; }
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim: y };
  }
  // Card 81 · Brasileirada B01 "Foto inteira" (paisagem real + título em serifa embaixo, estrelinha na cor)
  PN.p81 = (c, tl, s, k) => pSerifa(c, tl, s, k, { orig: { bg: '#25476a', ink: '#fff6dd', ac: '#ffe09c' }, corTit: '#fff6dd', base: 123, lh: 0.89, ls: -0.038, top: 1060, estrela: 1,
    veu: 'linear-gradient(180deg,#151913bf 7%,#15191338 28%,transparent 41%,#19180f74 52%,#18160df2 84%)' });
  // Card 84 · Brasileirada B06 "Foto caiçara com serifa" (título centralizado em creme, dois brilhos)
  PN.p84 = (c, tl, s, k) => pSerifa(c, tl, s, k, { orig: { bg: '#ae3c30', ink: '#fff1db', ac: '#fff0b3' }, corTit: '#fff0b3', corBrilho: 'var(--p-ac)', base: 108, lh: 0.95, ls: -0.04, top: 1005, centro: 1,
    brilhos: [160, 142, 55, 39], veu: 'linear-gradient(180deg,#241914c4 4%,#21160f0e 38%,#23181132 47%,#241811a3 70%,#241811ee 100%)' });
  const VEU_SERIE = 'linear-gradient(180deg,#19130ed9 0%,#19130e24 29%,#19130e10 39%,#19130ec7 66%,#19130eed 90%)';
  // Card 114 · Versão ChatGPT do card 28 (foto de cima + serifa creme + brilhos; pastel e caldo de cana)
  PN.p114 = (c, tl, s, k) => pSerifa(c, tl, s, k, { orig: { bg: '#853e2a', ink: '#fff4e7', ac: '#ffcf96' }, corTit: '#fff0bd', base: 116, lh: 0.93, ls: -0.035, top: 944, serie: 1, brilhos: [150, 171, 64, 38], veu: VEU_SERIE });
  // Card 115 · Versão ChatGPT do card 29 (mesmo desenho do 114, azul; papagaio)
  PN.p115 = (c, tl, s, k) => pSerifa(c, tl, s, k, { orig: { bg: '#1f3561', ink: '#fff4e7', ac: '#a9d3ff' }, corTit: '#fff0bd', base: 116, lh: 0.93, ls: -0.035, top: 944, serie: 1, brilhos: [150, 171, 64, 38], veu: VEU_SERIE });

  // cabeçalho da Brasileirada (filete + etiqueta mono 26, sem série)
  const pMastB = (c, tl) => pMast(c, tl, { fs: 26, ls: 0.065, pt: 18 });
  const ITB = { ...IT, lh: 0.91, ls: -0.06 };
  // Card 82 · Brasileirada B02 "Colagem editorial" (foto girada com borda de papel + recorte por cima + sol)
  PN.p82 = (c, tl, s, k) => { const T = pTema(s, { bg: '#853c2d', ink: '#fff2da', ac: '#f4c982' }, 'escuro');
    const ps = c.pessoa || {}, rec = c.recorte || ps.foto;
    const M = pMastB(c, tl); let h = M.html, y = Math.max(M.bot + 50, 371);
    const Ti = pTit(c, y, k, tl, { fonte: ITB, base: 120 }); h += Ti.html;
    const Nm = ps.nome ? pNome(ps, LARG, k) : null, nb = Nm ? Nm.h : 0;
    const top = Math.max(Ti.bot + 70, 715), alt = Math.max(320, Math.min(621, LIM - 8 - nb - (nb ? 30 : 0) - 40 - top));
    h += `<div class="p-sol" data-deco style="width:465px;height:465px;right:-84px;top:${top + 59}px;opacity:${(0.84 * (CAPA ? 1 : ease((tl - 0.2) / 0.8))).toFixed(3)}"></div>`;
    h += `<div class="p-cena" style="top:${top}px;left:108px;width:782px;height:${alt}px;transform:rotate(-4deg);${ent(tl, 0.3, 0.6, 60)}">${pImg(c.foto || c.midia)}</div>`;
    if (rec) h += `<div class="p-cutout" style="top:${top + Math.round(alt * 0.22)}px;right:66px;width:534px;height:${Math.round(alt * 0.87)}px;transform:rotate(5deg);${ent(tl, 0.6, 0.6, 60)}"><img src="${E(rec)}"></div>`;
    let fim = top + alt;
    if (Nm) { const ny = LIM - 8 - nb; h += `<div class="ab zs" style="top:${ny}px;z-index:6;${ent(tl, 0.9)}">${Nm.html}</div>`; fim = ny + nb; }
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim, falta: alt < 320 }; };
  // Card 83 · Brasileirada B03 "Cartaz com sticker" (objeto recortado girado sobre sol + faixa escura)
  PN.p83 = (c, tl, s, k) => { const T = pTema(s, { bg: '#214841', ink: '#fff2da', ac: '#ffc572' }, 'escuro');
    const M = pMastB(c, tl); let h = M.html, y = Math.max(M.bot + 50, 371);
    const Ti = pTit(c, y, k, tl, { fonte: ITB, base: 120 }); h += Ti.html;
    const ap = c.apoio ? texto(c.apoio, { ...PRUB(400, 1.32), base: 33 * k, min: 28, piso: 24, larg: LARG, maxLin: 3 }) : null;
    const top = Math.max(Ti.bot + 60, 684), alt = Math.max(320, Math.min(692, LIM - 8 - (ap ? ap.h + 30 : 0) - top));
    h += `<div class="p-sol" data-deco style="width:${Math.min(660, alt)}px;height:${Math.min(660, alt)}px;right:114px;top:${top}px;opacity:${(0.84 * (CAPA ? 1 : ease((tl - 0.2) / 0.8))).toFixed(3)}"></div>`;
    const pk = CAPA ? { y: 0, r: -7, o: 1 } : kf(tl, 0.35, 1.2, [[0, { y: -160, r: 6, o: 0 }], [0.55, { y: 14, r: -10, o: 1 }], [0.8, { y: -8, r: -6, o: 1 }], [1, { y: 0, r: -7, o: 1 }]]);
    /* 25/11 (A2 EL-NINO, q_000000 a q_000500 idênticos): na capa (1ª cena) tudo nasce pronto e a tela ficava 5 s parada.
       Depois de 1 s o objeto balança devagar (±2°, ±7 px, ciclo de 3 s); o quadro 0 continua igual à capa. */
    if (tl > 1) { const w = Math.sin(2 * Math.PI * (tl - 1) / 3), am = Math.min(1, (tl - 1) / 0.6); pk.r += 2 * w * am; pk.y += 7 * Math.sin(2 * Math.PI * (tl - 1) / 3 + 1.2) * am; }
    const obj = c.recorte || (c.pessoa && c.pessoa.foto);
    h += `<div class="p-cutout" style="left:149px;top:${top - 1}px;width:798px;height:${alt}px;z-index:2;opacity:${pk.o.toFixed(3)};transform:translateY(${pk.y.toFixed(1)}px) rotate(${pk.r.toFixed(2)}deg)">${obj ? `<img src="${E(obj)}">` : `<div style="width:${Math.round(alt * 0.55)}px;height:${Math.round(alt * 0.55)}px;margin:${Math.round(alt * 0.2)}px auto 0;color:var(--p-ink)">${ico(c.icone || 'casa', 'currentColor', 4)}</div>`}</div>`;
    h += `<div class="p-talho" data-deco style="top:${top + alt - 105}px"></div>`;
    let fim = top + alt;
    // 25/11 (A2 EL-NINO): apoio pode entrar na voz (campos.entra_apoio -> t_apoio); sem isso, 0,8 s como antes
    if (ap) { const t2 = LIM - 8 - ap.h, ta = typeof c.t_apoio === 'number' ? c.t_apoio - s.start : 0.8; h += `<div class="ab tx zs" style="top:${t2}px;z-index:6;${pcss(PRUB(400, 1.32), ap)}${ent(tl, ta)}">${ap.html}</div>`; fim = t2 + ap.h; }
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim, falta: alt < 320 }; };

  // contorno do Brasil do card 85 (copiado do original, em % da caixa)
  const MAPA_BR = '52.51% 100.00%, 51.80% 98.55%, 52.93% 97.33%, 51.45% 95.59%, 49.46% 94.17%, 46.83% 92.53%, 45.89% 92.60%, 43.33% 90.62%, 41.68% 90.90%, 45.08% 87.40%, 47.95% 84.91%, 49.66% 83.87%, 51.81% 82.45%, 51.86% 80.41%, 50.58% 78.93%, 49.32% 79.42%, 49.82% 77.94%, 50.17% 76.42%, 50.17% 75.02%, 49.25% 74.55%, 48.30% 74.96%, 47.35% 74.85%, 47.05% 73.86%, 46.81% 71.52%, 46.33% 70.75%, 44.61% 70.06%, 43.57% 70.56%, 40.88% 70.07%, 41.05% 66.59%, 40.30% 65.16%, 41.10% 64.63%, 40.85% 63.17%, 41.55% 62.05%, 42.00% 60.03%, 41.40% 58.43%, 40.01% 57.71%, 39.74% 56.70%, 40.11% 55.22%, 35.23% 55.12%, 34.25% 52.13%, 34.99% 52.09%, 34.96% 50.98%, 34.46% 50.24%, 34.35% 48.75%, 32.87% 47.99%, 31.27% 48.02%, 30.21% 47.27%, 28.49% 46.77%, 27.49% 45.81%, 24.63% 45.39%, 21.87% 43.09%, 22.07% 41.37%, 21.76% 40.39%, 22.03% 38.47%, 18.70% 38.90%, 17.36% 39.86%, 15.13% 40.90%, 14.56% 41.68%, 13.25% 41.73%, 11.35% 41.52%, 9.92% 41.96%, 8.76% 41.66%, 8.93% 37.77%, 6.84% 39.28%, 4.59% 39.21%, 3.63% 37.85%, 1.94% 37.70%, 2.48% 36.60%, 1.06% 35.04%, 0.00% 32.73%, 0.67% 32.26%, 0.67% 31.18%, 2.21% 30.44%, 1.96% 29.05%, 2.61% 28.16%, 2.79% 26.96%, 5.70% 25.22%, 7.79% 24.73%, 8.13% 24.34%, 10.43% 24.46%, 11.57% 17.43%, 11.63% 16.32%, 11.23% 14.85%, 10.10% 13.92%, 10.12% 12.06%, 11.55% 11.63%, 12.06% 11.90%, 12.15% 10.92%, 10.65% 10.65%, 10.62% 9.05%, 15.59% 9.10%, 16.43% 8.22%, 17.14% 9.03%, 17.63% 10.55%, 18.11% 10.23%, 19.52% 11.59%, 21.50% 11.42%, 21.99% 10.64%, 23.88% 10.04%, 24.93% 9.62%, 25.23% 8.53%, 27.05% 7.80%, 26.91% 7.26%, 24.75% 7.04%, 24.40% 5.43%, 24.50% 3.71%, 23.36% 3.05%, 23.84% 2.81%, 25.72% 3.14%, 27.75% 3.78%, 28.49% 3.17%, 30.32% 2.77%, 33.17% 1.81%, 34.10% 0.84%, 33.76% 0.11%, 35.09% 0.00%, 35.68% 0.59%, 35.35% 1.72%, 36.22% 2.10%, 36.81% 3.30%, 36.10% 4.20%, 35.69% 6.38%, 36.35% 7.68%, 36.53% 8.86%, 38.10% 10.07%, 39.35% 10.19%, 39.63% 9.69%, 40.44% 9.58%, 41.59% 9.13%, 42.42% 8.45%, 43.83% 8.67%, 44.44% 8.57%, 45.83% 8.78%, 46.06% 8.26%, 45.63% 7.75%, 45.89% 7.01%, 46.91% 7.24%, 48.12% 6.97%, 49.58% 7.52%, 50.69% 8.05%, 51.48% 7.35%, 52.05% 7.46%, 52.39% 8.18%, 53.61% 8.00%, 54.59% 7.02%, 55.37% 5.14%, 56.88% 2.79%, 57.75% 2.67%, 58.38% 4.09%, 59.81% 8.57%, 61.17% 8.99%, 61.24% 10.76%, 59.32% 12.87%, 60.11% 13.64%, 64.62% 14.05%, 64.71% 16.62%, 66.64% 14.93%, 69.85% 15.86%, 74.08% 17.42%, 75.32% 18.92%, 74.91% 20.34%, 77.87% 19.55%, 82.82% 20.91%, 86.63% 20.81%, 90.40% 22.93%, 93.65% 25.80%, 95.61% 26.54%, 97.79% 26.64%, 98.71% 27.45%, 99.58% 30.71%, 100.00% 32.27%, 98.99% 36.50%, 97.69% 38.18%, 94.10% 41.74%, 92.48% 44.64%, 90.59% 46.86%, 89.95% 46.91%, 89.24% 48.80%, 89.42% 53.60%, 88.71% 57.55%, 88.44% 59.24%, 87.64% 60.25%, 87.18% 63.68%, 84.60% 67.03%, 84.17% 69.67%, 82.11% 70.78%, 81.51% 72.32%, 78.74% 72.32%, 74.74% 73.30%, 72.94% 74.44%, 70.09% 75.19%, 67.09% 77.23%, 64.94% 79.77%, 64.56% 81.69%, 64.99% 83.10%, 64.51% 85.69%, 63.93% 86.94%, 62.15% 88.35%, 59.33% 92.86%, 57.09% 94.90%, 55.36% 96.10%, 54.19% 98.53%, 52.51% 100.00%';
  // Card 85 · Brasileirada B07 "Cartaz com mapa" (mapa do Brasil na cor + título condensado gigante centralizado)
  PN.p85 = (c, tl, s, k) => { const T = pTema(s, { bg: '#ae3c30', ink: '#fff0d7', ac: '#f7cc76' }, 'escuro');
    if (s && s.cor_tema) T.bg = tom(s.cor_tema, 0.6, 0.36);
    const M = pMastB(c, tl); let h = M.html;
    const g = CAPA ? 1 : ease((tl - 0.1) / 1.0);
    // 25/11 (A2 EL-NINO, cena 17 parada 4 s): depois de entrar, o mapa segue girando e crescendo devagar (Ken Burns leve)
    const dv = CAPA ? 0 : Math.max(0, tl - 1.1), rz = -5 + Math.min(3, dv * 0.55), sz = 0.94 + 0.06 * g + Math.min(0.06, dv * 0.011);
    h += `<div class="p-mapa" data-deco style="left:49px;top:391px;width:995px;height:950px;clip-path:polygon(${MAPA_BR});opacity:${(0.74 * g).toFixed(3)};transform:rotate(${rz.toFixed(2)}deg) scale(${sz.toFixed(3)})"></div>`;
    const fo = { f: 'Anton', p: 400, lh: 0.87, ls: -0.025, up: 1 }, b = 236 * k;
    let r = texto(c.titulo, { ...fo, base: b, min: Math.round(b * 0.7), piso: Math.round(b * 0.7), larg: LARG, maxLin: 2, dest: c.destaque, cls: 'p-claro' });
    if (!r.ok) r = texto(c.titulo, { ...fo, base: b, min: 72, larg: LARG, maxLin: 3, dest: c.destaque, cls: 'p-claro' });
    const y = Math.max(M.bot + 60, Math.round(866 - r.h / 2));
    h += `<div class="ab tx zs" style="top:${y}px;z-index:4;${fonteCss(fo, r)}color:#231c19;text-align:center;${ent(tl, 0.25, 0.5, 30)}">${r.html}</div>`;
    let fim = y + r.h;
    h += `<div class="p-orbita" data-deco style="top:${Math.max(fim + 40, 1316)}px"></div>`;
    if (c.apoio) { const A = pApoio(c.apoio, fim + 80, k, tl, { t: typeof c.t_apoio === 'number' ? c.t_apoio - s.start : 0.8 }); h += A.html; fim = A.bot; }
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim }; };
  // Card 116 · Versão ChatGPT do card 30 "O Brasil tem voz" (mapa na cor, título Inter Tight gigante, selo de papel)
  PN.p116 = (c, tl, s, k) => { const T = pTema(s, { bg: '#a32424', ink: '#fff4ec', ac: '#ffdb79' }, 'escuro');
    /* 25/11 (A3 BIG-TECHS): cor da peça clara (#22D3EE) deixava o título creme sem leitura em cima do mapa. Mapa escurece
       (mesmo tom) até contraste 3 com o título; a cor pura vai pro selo. Sem cor_tema (laranja original) ou cor que já lê passa igual. */
    let mapa = s && s.cor_tema ? s.cor_tema : '#eb783c', claro116 = false; const g = CAPA ? 1 : ease((tl - 0.1) / 1.0);
    if (s && s.cor_tema && /^#[0-9a-f]{6}$/i.test(mapa) && _contr('#fff3e5', mapa) < 3) { claro116 = true; let f = 0.95; while (f > 0.3 && _contr('#fff3e5', _esc(mapa, f)) < 3) f -= 0.05; mapa = _esc(mapa, f); }
    let h = `<div class="p-mapa" data-deco style="left:148px;top:431px;width:800px;height:805px;background:${mapa};clip-path:polygon(7% 25%,16% 21%,16% 12%,30% 14%,39% 20%,53% 14%,61% 4%,68% 19%,79% 27%,95% 39%,97% 49%,88% 59%,85% 73%,67% 79%,61% 91%,50% 99%,44% 93%,51% 85%,51% 75%,42% 68%,41% 58%,32% 58%,23% 53%,15% 54%,12% 43%,3% 39%);opacity:${g.toFixed(3)};transform:scale(${(0.94 + 0.06 * g).toFixed(3)})"></div>` + RAIL;
    const M = pMast(c, tl); h += M.html;
    const fo = { f: 'Inter Tight', p: 700, lh: 0.8, ls: -0.03 }, b = 237 * k; // 25/11: -0.085 grudava letras na capa; -0.05 ainda juntava 'rn' em 'm' ('intemet'), A3 PLP299
    let r = texto(c.titulo, { ...fo, base: b, min: Math.round(b * 0.7), piso: Math.round(b * 0.7), larg: LARG, maxLin: 2, dest: c.destaque, cls: 'pa' });
    if (!r.ok) r = texto(c.titulo, { ...fo, base: b, min: 72, larg: LARG, maxLin: 3, dest: c.destaque, cls: 'pa' });
    let y = Math.max(M.bot + 60, 598); h += `<div class="ab tx zs" style="top:${y}px;z-index:4;${fonteCss(fo, r)}color:#fff3e5;${ent(tl, 0.25)}">${r.html}</div>`; y += r.h;
    if (c.etiqueta) { const E2 = texto(c.etiqueta, { ...PMONO, base: 25, min: 22, piso: 20, larg: LARG - 34, maxLin: 1 });
      // 25/11 (A1 BIG-TECHS): selo sem z-index ficava ATRÁS do mapa (z-index 1) e aparecia cortado ("GUSTAV...")
      // 25/11 (A3 BIG-TECHS): selo e apoio entram na voz (entra_etiqueta/entra_apoio -> t_etiqueta/t_apoio); sem isso, como antes
      const te = typeof c.t_etiqueta === 'number' ? c.t_etiqueta - s.start : 0.7, sc = claro116 ? `background:${s.cor_tema};color:#141416;` : '';
      h += `<div class="ab zs" style="top:${y + 80}px;z-index:4;${ent(tl, te)}"><span class="tx p-selo" style="${pcss(PMONO, E2)}${sc}">${E2.html}</span></div>`; y += 80 + E2.h + 20; }
    const A = pApoio(c.apoio, y + 40, k, tl, { t: typeof c.t_apoio === 'number' ? c.t_apoio - s.start : 0.8 }); h += A.html;
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim: Math.max(y, A.bot) }; };

  // Card 86 · Brasileirada B08 "Retrato sobre o sol" (pessoa recortada na frente do sol, faixa de paisagem embaixo)
  PN.p86 = (c, tl, s, k) => { const T = pTema(s, { bg: '#ae3c30', ink: '#fff0d7', ac: '#f7cc76' }, 'escuro');
    const ps = c.pessoa || {}, fundo = c.foto_fundo || s.foto_fundo || c.midia;
    const M = pMastB(c, tl); let h = M.html, y = Math.max(M.bot + 50, 373);
    const Ti = pTit(c, y, k, tl, { fonte: { f: 'Anton', p: 400, lh: 0.94, ls: -0.007, up: 1 }, base: 113, extra: 'z-index:6;' }); h += Ti.html;
    const Nm = pNome(ps, 420, k, { corCargo: '#fff1dc' }), lug = c.lugar ? texto(c.lugar, { ...PMONO, base: 24, min: 22, piso: 20, larg: 300, maxLin: 3, lh: 1.25 }) : null;
    const nb = Nm.h + (lug ? lug.h + 16 : 0), ny = LIM - 8 - nb;
    const sy = Math.max(Ti.bot + 40, 561), sol = Math.min(701, ny - 40 - sy + 200);
    const sg = CAPA ? 1 : ease((tl - 0.1) / 0.9);
    h += `<div class="p-sol" data-deco style="left:194px;top:${sy}px;width:${sol}px;height:${sol}px;opacity:1;transform:scale(${(0.9 + 0.1 * sg).toFixed(3)})"></div>`;
    h += `<div class="p-faixa86" data-deco style="top:${ny - 260}px;height:${1597 - (ny - 260)}px">${fundo ? `<img src="${E(fundo)}">` : ''}</div>`;
    h += `<div class="p-cutout" style="left:191px;top:${sy - 10}px;width:705px;height:${1490 - sy}px;z-index:4;${ent(tl, 0.3, 0.7, 50)}"><img src="${E(ps.foto || SILHUETA)}" style="object-position:center bottom"></div>`;
    h += `<div class="ab zs" style="top:${ny}px;right:auto;width:420px;z-index:6;color:#fff1dc;${ent(tl, 0.9)}">${lug ? `<div class="tx" style="${pcss({ ...PMONO, lh: 1.25 }, lug)};margin-bottom:16px">${lug.html}</div>` : ''}${Nm.html}</div>`;
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + REGUA + GRAO, fim: ny + nb, falta: sol < 360 }; };

  // Card 142 · Vibe cool VC07 "Pontos que crescem" (cena 1 no grafite; pontinhos na cor crescem e revelam a cena 2)
  PN.p142 = (c, tl, s, k) => { const T = pTema(s, { bg: '#151716', ink: '#eeece3', ac: '#ff994e' }, 'carvao');
    const ANT = { f: 'Anton', p: 400, lh: 0.87, ls: -0.012, up: 0 };
    const cena = (d, cor, cls) => { const M = pMast(d, tl, { ls: 0.045, pt: 17 }); let h = M.html, y = Math.max(M.bot + 38, 356);
      const Ti = pTit(d, y, k, tl, { fonte: ANT, base: 163 }); h += Ti.html;
      const ap = d.apoio ? texto(d.apoio, { ...PRUB(600, 1.2), base: 37 * k, min: 30, piso: 26, larg: LARG, maxLin: 2 }) : null;
      const top = Math.max(Ti.bot + 60, 770), alt = Math.max(300, Math.min(555, LIM - 8 - (ap ? ap.h + 40 : 0) - top));
      if (!cls) h += `<div class="p-arte" data-deco style="top:${top - 62}px;height:${alt + 20}px"></div>`;
      h += `<div class="p-spread" style="top:${top}px;height:${alt}px">${pImg(d.foto || d.midia, 'filter:grayscale(1) contrast(.9)')}</div>`;
      if (ap) h += `<div class="ab tx zs" style="top:${top + alt + 40}px;${pcss(PRUB(600, 1.2), ap)}">${ap.html}</div>`;
      return { h, fim: top + alt + (ap ? 40 + ap.h : 0), alt: alt < 300 }; };
    const A = cena(c, T.ink, '');
    let h = A.h, fim = A.fim;
    const dep = c.depois || c.proximo;
    if (dep && dep.titulo) { const tB = typeof c.t_depois === 'number' ? c.t_depois - s.start : (s.end - s.start) * 0.45;
      const d = CAPA && tB < 1 ? 0 : cl((tl - tB) / 1.2, 0, 1), dot = d < 0.25 ? 16 * d : 4 + 25 * ease((d - 0.25) / 0.75), conteudo = cl((d - 0.45) / 0.4, 0, 1);
      const B = cena({ ...dep, rotulo: dep.rotulo, serie: dep.serie }, '#201c17', 'b');
      if (d >= 0.9) h = ''; // cena 1 coberta pelos pontos: sai do DOM (não sobra texto embaixo da cena 2)
      if (dot > 0.01) h += `<div class="p-revela" style="--p-ac:#502c20;color:#201c17;background:${T.ac};-webkit-mask-image:radial-gradient(circle,#000 ${dot.toFixed(2)}px,transparent ${(dot + 0.45).toFixed(2)}px);mask-image:radial-gradient(circle,#000 ${dot.toFixed(2)}px,transparent ${(dot + 0.45).toFixed(2)}px)"><div style="opacity:${conteudo.toFixed(3)}">${B.h}</div></div>`;
      if (d >= 1) fim = Math.max(fim, B.fim);
    }
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + GRAO, fim, falta: A.alt }; };

  // Card 41 · Minimalista (papel creme, bonequinho de traço e UM ponto de cor; frase centralizada embaixo)
  PN.p41 = (c, tl, s, k) => { const ac = s && s.cor_tema ? s.cor_tema : '#E3342B';
    const M = pMast(c, tl, { fs: 26, ls: 0.14, pt: 16, borda: 'border-top-width:4px;' });
    const pop = CAPA ? 1 : kf(tl, 0.6, 0.6, [[0, { v: 0 }], [0.7, { v: 1.15 }], [1, { v: 1 }]]).v, fl = Math.sin(2 * Math.PI * tl / 3) * 12;
    const fs = c.figura ? '' : '<circle cx="120" cy="50" r="34"/><path d="M120 84v140M120 120l-60 50M120 120l70-30M120 224l-50 120M120 224l50 120"/>';
    let h = M.html + `<svg class="p-boneco" viewBox="0 0 240 360" style="left:420px;top:${Math.round(820 * Math.min(1, k + 0.08))}px;width:240px;height:360px;${ent(tl, 0.2)}">${fs}</svg>`;
    h += `<div class="p-ponto" style="left:640px;top:${Math.round(760 * Math.min(1, k + 0.08)) + fl.toFixed(1) * 1}px;background:${ac};transform:scale(${Math.max(0, pop).toFixed(3)})"></div>`;
    const fo = PRUB(600, 1.2), r = texto(c.titulo || c.texto || '', { ...fo, base: 46 * k, min: 36, piso: 30, larg: LARG, maxLin: 3 });
    const q = c.pergunta ? texto(c.pergunta, { ...PRUB(900, 1.2), base: 46 * k, min: 36, piso: 30, larg: LARG, maxLin: 2 }) : null;
    const y = Math.max(Math.round(1260 * Math.min(1, k + 0.08)), 1040), hh = r.h + (q ? q.h : 0);
    h += `<div class="ab zs" style="top:${Math.min(y, LIM - 8 - hh)}px;text-align:center;${ent(tl, 1)}"><div class="tx" style="${pcss(fo, r)}">${r.html}</div>${q ? `<div class="tx" style="${pcss(PRUB(900, 1.2), q)}">${q.html}</div>` : ''}</div>`;
    return { bg: '#F4EFE3', fg: '#0B0B0C', escuro: 0, vars: pVars({ bg: '#F4EFE3', ink: '#0B0B0C', ac }), html: h + '<div class="p-grao" data-deco style="opacity:.15"></div>', fim: Math.min(y, LIM - 8 - hh) + hh }; };

  // lista no quadriculado (cards 125 e 137): a última linha (ou a marcada com circular:true) ganha o círculo de caneta
  // Card 125 · Vibe cool (Claude) "Lista no quadriculado" (letra de marcador Patrick Hand, caixinhas, anotação na cor)
  PN.p125 = (c, tl, s, k) => { const ac = s && s.cor_tema ? s.cor_tema : '#FF8A3D';
    const it = (c.itens || []).slice(0, 5), M = pMast(c, tl, { fs: 26, ls: 0.14, pt: 16, borda: 'border-top-width:4px;' });
    let h = M.html, y = Math.max(M.bot + 40, 330);
    const Ti = pTit(c, y, k, tl, { fonte: { f: 'Rubik', p: 800, lh: 0.98, ls: -0.045 }, base: 104 }); h += Ti.html; y = Ti.bot + 40;
    const HF = { f: 'Patrick Hand SC', p: 400, lh: 1.28, ls: 0 }, mk = it.findIndex(x => x.circular), alvo = mk >= 0 ? mk : it.length - 1;
    const nota = c.nota ? texto(c.nota, { ...HF, lh: 1.1, base: 64 * k, min: 40, piso: 34, larg: LARG, maxLin: 2 }) : null;
    const disp = LIM - 8 - (nota ? nota.h + 50 : 0) - y, lin = Math.min(Math.round(92 * k), Math.floor(disp / Math.max(1, it.length) / 1.28));
    it.forEach((x, q) => { const r = texto(x.texto || '', { ...HF, base: lin, min: 40, piso: 34, larg: LARG - 82, maxLin: 1 }), t0 = tItem(x, q, it.length, s);
      const circ = q === alvo ? `<div class="p-circulo" style="border-color:${ac};opacity:${(CAPA ? 1 : ease((tl - (ts => ts)(tItem(it[alvo], alvo, it.length, s)) - 0.7) / 0.5)).toFixed(3)}"></div>` : '';
      h += `<div class="ab zs" style="top:${y}px;display:flex;align-items:center;gap:30px;height:${Math.round(r.fs * 1.28)}px;${ent(tl, t0)}"><b class="p-caixa" style="width:${Math.round(r.fs * 0.56)}px;height:${Math.round(r.fs * 0.56)}px"></b><div class="tx" style="position:relative;${pcss(HF, r)}">${circ}${r.html}</div></div>`;
      y += Math.round(r.fs * 1.28); });
    if (nota) { y += 50; h += `<div class="ab tx zs" style="top:${y}px;${pcss({ ...HF, lh: 1.1 }, nota)}color:${ac};${ent(tl, (s.end - s.start) * 0.8)}">${nota.html}</div>`; y += nota.h; }
    return { bg: '#141416', fg: '#F7F4EE', escuro: 1, vars: pVars({ bg: '#141416', ink: '#F7F4EE', ac }), html: '<div class="p-quadric" data-deco></div>' + h, fim: y }; };
  // Card 137 · Vibe cool VC04 "Lista no quadriculado" (ChatGPT: título condensado, itens em itálico, o último circulado)
  PN.p137 = (c, tl, s, k) => { const T = pTema(s, { bg: '#151716', ink: '#eeece3', ac: '#ff994e' }, 'carvao');
    const it = (c.itens || []).slice(0, 5), fundo = c.foto_fundo || s.foto_fundo;
    let h = '<div class="p-quadric" data-deco style="background-image:linear-gradient(90deg,#a3ac9432 1px,transparent 1px),linear-gradient(#a3ac9432 1px,transparent 1px);background-size:61px 61px"></div>' +
      (fundo ? `<div class="p-foto-suave" data-deco><img src="${E(fundo)}"></div>` : '');
    const M = pMast(c, tl, { ls: 0.045, pt: 17 }); h += M.html; let y = Math.max(M.bot + 38, 356);
    const Ti = pTit(c, y, k, tl, { fonte: { f: 'Anton', p: 400, lh: 0.91, ls: -0.015 }, base: 127 }); h += Ti.html; y = Math.max(Ti.bot + 50, 678);
    const ap = c.apoio ? texto(c.apoio, { ...PRUB(600, 1.22, -0.01), base: 32 * k, min: 28, piso: 24, larg: LARG, maxLin: 2 }) : null;
    const disp = LIM - 8 - (ap ? ap.h + 50 : 0) - y, eh = Math.min(Math.round(122 * k), Math.floor(disp / Math.max(1, it.length)) - 8);
    const mk = it.findIndex(x => x.circular), alvo = mk >= 0 ? mk : it.length - 1, IFO = { f: 'Rubik', p: 800, lh: 0.95, ls: -0.048 };
    it.forEach((x, q) => { const r = texto(x.texto || '', { ...IFO, base: Math.min(67 * k, eh * 0.55), min: 36, piso: 30, larg: LARG - 70, maxLin: 1 }), t0 = tItem(x, q, it.length, s);
      const ult = q === alvo, ring = ult ? `<div class="p-anel" style="border-color:var(--p-ac);clip-path:inset(0 ${(100 - 100 * (CAPA ? 1 : ease((tl - t0 - 0.5) / 0.6))).toFixed(1)}% 0 0)"></div>` : '';
      h += `<div class="ab zs p-entrada" style="top:${y}px;height:${eh}px;${ent(tl, t0)}"><i class="p-check"></i><div class="tx" style="position:relative;justify-self:start;font-style:italic;${pcss(IFO, r)}${ult ? 'color:var(--p-ac);' : ''}${q % 2 ? 'rotate:-0.7deg;' : ''}">${ring}${r.html}</div></div>`;
      y += eh + 8; });
    if (ap) { const t2 = Math.max(y + 50, LIM - 8 - ap.h); h += `<div class="ab tx zs" style="top:${t2}px;${pcss(PRUB(600, 1.22, -0.01), ap)}${ent(tl, 0.9)}">${ap.html}</div>`; y = t2 + ap.h; }
    return { bg: T.bg, fg: T.ink, escuro: 1, vars: pVars(T), html: h + GRAO, fim: y }; };

  /* elenco em camadas (cards 148 a 152, Claude): quem está na frente nítido (fade embaixo), secundários desfocados atrás;
     nome com cargo em mono e chip de ponto (vermelho esquerda, azul direita, preto centro) */
  function pNomeEl(ps, larg, k) {
    const W = texto(ps.nome || '', { ...PRUB(800, 1.1, -0.01), base: 34 * k, min: 28, piso: 24, larg, maxLin: 2 });
    const Cg = ps.cargo ? texto(ps.cargo, { f: 'JetBrains Mono', p: 700, lh: 1.3, ls: 0.08, up: 1, base: 20, min: 20, piso: 18, larg, maxLin: 2 }) : null;
    const pc = pChip(ps), CH = pc ? texto(pc.chip, { f: 'JetBrains Mono', p: 700, lh: 1.3, ls: 0.04, up: 1, base: 21, min: 20, piso: 18, larg: larg - 30, maxLin: 2 }) : null;
    const cor = pc ? (pc.lado === 'esq' ? '#E3342B' : pc.lado === 'dir' ? '#2B4FD8' : '#0B0B0C') : '';
    return { h: (Cg ? Cg.h + 6 : 0) + W.h + (CH ? CH.h + 10 : 0), html: (Cg ? `<div class="tx" style="${pcss({ f: 'JetBrains Mono', p: 700, lh: 1.3, ls: 0.08, up: 1 }, Cg)};opacity:.8;margin-bottom:6px">${Cg.html}</div>` : '') +
      `<div class="tx" style="${pcss(PRUB(800, 1.1, -0.01), W)}">${W.html}</div>` +
      (CH ? `<div style="display:flex;align-items:center;gap:10px;margin-top:10px"><i class="p-pontochip" style="--c:${cor}"></i><div class="tx chip-el" style="${pcss({ f: 'JetBrains Mono', p: 700, lh: 1.3, ls: 0.04, up: 1 }, CH)}">${CH.html}</div></div>` : '') };
  }
  function pElenco(c, tl, s, k, cfg) {
    const cor = s && s.cor_tema && /^#[0-9a-f]{6}$/i.test(s.cor_tema) ? s.cor_tema : null, V = cfg.cores(cor);
    const M = pMast(c, tl, { fs: 26, ls: 0.14, pt: 16, borda: 'border-top-width:4px;' });
    let h = (cfg.bloco ? `<div class="p-bloco149" data-deco style="background:linear-gradient(${V.bloco} 0,${V.bloco} 45%,${V.bg} 92%)"></div>` : '') + M.html;
    const tt = pTit(c, Math.max(M.bot + 30, 300), k, tl, { fonte: { f: 'Rubik', p: 800, lh: 0.98, ls: -0.045 }, base: 104, extra: `z-index:6;${V.tit ? 'color:' + V.tit + ';' : ''}` }); h += tt.html;
    const ps = (c.pessoas || (c.pessoa ? [c.pessoa] : [])).slice(0, cfg.frente.length), fp = (c.fundo_pessoas || []);
    const larg = ps.length > 1 ? Math.floor((LARG - 30) / 2) : 560, Ns = ps.map(p => pNomeEl(p, larg, k)), nh = Math.max(0, ...Ns.map(n => n.h)), ny = LIM - 8 - nh;
    const img = (u, st, cls, t0) => `<div class="p-el ${cls}" style="${st};${t0 === null ? '' : `opacity:${((/f2/.test(cls) ? 0.55 : 0.35) * (CAPA ? 1 : ease((tl - t0) / 1.2))).toFixed(3)};`}">${u ? `<img src="${E(u)}">` : ''}</div>`;
    const h0 = h.length; // cabeças: o bloco todo sobe junto com os nomes (no original os nomes ficam em y 1440)
    cfg.tras.forEach((p, i) => { if (fp[i] && fp[i].foto) h += img(fp[i].foto, p, cfg.cabecas ? 'cab f' + (p.includes('--f:2') ? 2 : 1) : 'tras', cfg.cabecas ? 0.3 + 0.1 * i : null); });
    cfg.frente.forEach((p, i) => { if (!ps[i]) return; const u = ps[i].foto || SILHUETA, f = CAPA ? 1 : ease((tl - (0.3 + 0.3 * i)) / 1.4);
      h += `<div class="p-el ${cfg.cabecas ? 'cab topo' : 'frente'}${cfg.colorida ? ' cor' : ''}" style="${p};opacity:${f.toFixed(3)}"><img src="${E(u)}" style="${cfg.cabecas ? '' : `filter:${cfg.colorida ? 'saturate(1.05)' : cfg.filtro || 'grayscale(1) contrast(1.12)'} blur(${((1 - f) * 14).toFixed(2)}px)`}"></div>`; });
    if (cfg.cabecas) h = h.slice(0, h0) + `<div style="position:absolute;inset:0;transform:translateY(${Math.min(0, ny - 1440)}px)">` + h.slice(h0) + '</div>';
    if (!cfg.cabecas) h += `<div class="p-ponte" data-deco style="background:linear-gradient(transparent,${V.bg} 72%)"></div>`;
    const xs = ps.length > 1 ? [150, 150 + larg + 30] : [150];
    Ns.forEach((n, i) => { h += `<div class="ab zs" style="top:${ny}px;left:${xs[i]}px;right:auto;width:${larg}px;z-index:7;${ent(tl, 1.1 + 0.2 * i)}">${n.html}</div>`; });
    return { bg: V.bg, fg: V.ink, escuro: V.escuro, vars: pVars({ bg: V.bg, ink: V.ink, ac: V.ac }), html: h + `<div class="p-grao" data-deco style="opacity:${V.grao}"></div>`, fim: ps.length ? ny + nh : tt.bot, falta: ny - tt.bot < 380 };
  }
  // Card 148 · Elenco corpo inteiro com fade (fundo cheio na cor, 1 pessoa nítida à direita, 2 desfocadas atrás)
  PN.p148 = (c, tl, s, k) => pElenco(c, tl, s, k, { cores: cor => { const bg = cor || '#FF5FA8', claro = _lum(bg) > 0.3; return { bg, ink: claro ? '#0B0B0C' : '#F7F4EE', ac: claro ? '#F7F4EE' : '#0B0B0C', escuro: claro ? 0 : 1, grao: 0.2 }; },
    tras: ['left:-120px;top:600px;height:620px', 'left:700px;top:600px;height:720px'], frente: ['left:560px;top:490px;height:960px'] });
  // Card 149 · Elenco duotone (bloco na cor que vira preto, 1 nítida + 1 no meio + 2 atrás)
  PN.p149 = (c, tl, s, k) => pElenco(c, tl, s, k, { bloco: 1, cores: cor => ({ bg: '#0B0B0C', bloco: cor || '#B48CFF', ink: '#F7F4EE', ac: '#F7F4EE', tit: '#0B0B0C', escuro: 1, grao: 0.12 }),
    tras: ['left:-60px;top:460px;height:640px', 'left:660px;top:460px;height:660px', 'left:-30px;top:670px;height:780px;filter:grayscale(1) blur(2.5px);opacity:.8;z-index:2'], frente: ['left:330px;top:550px;height:900px'] });
  // Card 150 · Só cabeças em camadas (ganhou x perdeu: as da frente nítidas, as de trás desfocadas)
  PN.p150 = (c, tl, s, k) => pElenco(c, tl, s, k, { cabecas: 1, cores: cor => ({ bg: '#F7F4EE', ink: '#0B0B0C', ac: cor ? tom(cor, 0.7, 0.42) : '#E3342B', escuro: 0, grao: 0.25 }),
    tras: ['left:60px;top:640px;width:240px f1', 'left:400px;top:600px;width:220px f1', 'left:740px;top:650px;width:240px f1', 'left:-30px;top:860px;width:330px f2', 'left:770px;top:880px;width:330px f2'].map(x => x.replace(/ f\d$/, '') + (x.endsWith('f2') ? ';--f:2' : '')),
    frente: ['left:120px;top:900px;width:420px', 'left:520px;top:940px;width:420px'] });
  // Card 151 · Dois meio-corpos com fade (fundo escuro tingido, duas pessoas lado a lado)
  PN.p151 = (c, tl, s, k) => pElenco(c, tl, s, k, { filtro: 'contrast(1.05) saturate(.85)', cores: cor => ({ bg: cor ? tom(cor, 0.6, 0.15) : '#0F3B2C', ink: '#F7F4EE', ac: cor || '#F2C94C', escuro: 1, grao: 0.12 }),
    tras: [], frente: ['left:-30px;top:570px;height:880px', 'left:470px;top:590px;height:860px'] });
  // Card 152 · Elenco com cor seletiva (só quem importa fica colorido; os outros P&B desfocados)
  PN.p152 = (c, tl, s, k) => pElenco(c, tl, s, k, { colorida: 1, cores: cor => ({ bg: '#F2E6D0', ink: '#0B0B0C', ac: cor ? tom(cor, 0.7, 0.4) : '#B5482E', escuro: 0, grao: 0.25 }),
    tras: ['left:-80px;top:630px;height:820px', 'left:610px;top:610px;height:840px', 'left:300px;top:750px;height:700px'], frente: ['left:210px;top:550px;height:900px'] });

  const CSS_P2 = `
.cpalco .p-halo,.cpalco .p-sol{position:absolute;border-radius:50%;background:var(--p-ac);pointer-events:none;z-index:1}
.cpalco .p-blococor{position:absolute;z-index:0;background:var(--p-ac);transform:rotate(3deg)}
.cpalco .p-veu{position:absolute;inset:0;z-index:1;pointer-events:none}
.cpalco .p-brilho{position:absolute;z-index:4;font-family:'DM Serif Display',Georgia,serif;line-height:.75}
.cpalco .p-cena{position:absolute;z-index:2;border:8px solid #f2e8d1;box-shadow:12px 14px 0 #201a124e;overflow:hidden;background:#30312b}
.cpalco .p-cena img{width:100%;height:100%;object-fit:cover;display:block}
.cpalco .p-cutout{position:absolute;z-index:3}
.cpalco .p-cutout img{width:100%;height:100%;object-fit:contain;display:block;filter:drop-shadow(7px 12px 0 #151b2048)}
.cpalco .p-talho{position:absolute;left:0;width:1080px;height:133px;background:#141916;clip-path:polygon(0 20%,100% 0,100% 72%,0 100%);opacity:.28;z-index:3}
.cpalco .p-mapa{position:absolute;z-index:1;background:var(--p-ac)}
.cpalco .p-claro{color:var(--p-ink);text-shadow:2px 6px #221b1770}
.cpalco .p-orbita{position:absolute;left:150px;right:165px;border-top:1px solid currentColor;opacity:.53}
.cpalco .p-selo{display:inline-block;background:#fff3e5;color:#66251e;padding:10px 17px}
.cpalco .p-faixa86{position:absolute;left:0;width:1080px;z-index:2;overflow:hidden;clip-path:polygon(0 39%,11% 32%,23% 27%,35% 27%,47% 19%,58% 28%,72% 19%,85% 8%,100% 0,100% 100%,0 100%);background:#5a3a2c}
.cpalco .p-faixa86 img{width:100%;height:100%;object-fit:cover;display:block}
.cpalco .p-faixa86::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 46%,#20120eb3 86%,#26180dc4 100%)}
.cpalco .p-arte{position:absolute;left:150px;width:765px;background:radial-gradient(circle,var(--p-ac) 0 3px,transparent 4px) 0 0/31px 31px;-webkit-mask-image:radial-gradient(ellipse at 50% 50%,#000,transparent 72%);mask-image:radial-gradient(ellipse at 50% 50%,#000,transparent 72%);opacity:.62}
.cpalco .p-spread{position:absolute;left:150px;width:765px;border-radius:23px;overflow:hidden;box-shadow:0 15px 38px #0b120f24;z-index:2;background:#2b2b28}
.cpalco .p-spread img{width:100%;height:100%;object-fit:cover;display:block}
.cpalco .p-spread::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 58%,#181710a0);pointer-events:none}
.cpalco .p-revela{position:absolute;inset:0;z-index:5;-webkit-mask-size:40px 40px;mask-size:40px 40px}
.cpalco .p-boneco{position:absolute;z-index:4;overflow:visible}
.cpalco .p-boneco path,.cpalco .p-boneco circle{fill:none;stroke:#0B0B0C;stroke-width:7;stroke-linecap:round}
.cpalco .p-ponto{position:absolute;width:90px;height:90px;border-radius:50%;z-index:5}
.cpalco .p-quadric{position:absolute;inset:0;background-image:linear-gradient(#ffffff14 2px,transparent 2px),linear-gradient(90deg,#ffffff14 2px,transparent 2px);background-size:60px 60px}
.cpalco .p-caixa{flex:none;border:5px solid currentColor;border-radius:8px;box-sizing:border-box}
.cpalco .p-circulo{position:absolute;left:-112px;right:-60px;top:-18px;bottom:-18px;border:6px solid;border-radius:50%;transform:rotate(-1deg)}
.cpalco .p-foto-suave{position:absolute;inset:0;opacity:.12;filter:grayscale(1) blur(2px);-webkit-mask-image:linear-gradient(180deg,transparent 13%,#000 47%,transparent 85%);mask-image:linear-gradient(180deg,transparent 13%,#000 47%,transparent 85%)}
.cpalco .p-foto-suave img{width:100%;height:100%;object-fit:cover}
.cpalco .p-entrada{display:grid;grid-template-columns:42px 1fr;gap:13px;align-items:center;border-bottom:1px solid #deded245;box-sizing:border-box}
.cpalco .p-check{width:23px;height:23px;border:2px solid #e9e8da89;border-radius:3px;margin-left:4px}
.cpalco .p-anel{position:absolute;top:-18px;bottom:-16px;left:-14%;right:-12%;border:4px solid;border-top-width:5px;border-radius:50%;transform:rotate(-1.2deg)}
.cpalco .p-pontochip{flex:none;width:14px;height:14px;border-radius:50%;background:var(--c);box-shadow:0 0 0 3px color-mix(in srgb,var(--c) 25%,transparent)}
.cpalco .p-bloco149{position:absolute;left:0;right:0;top:0;height:1400px;z-index:0}
.cpalco .p-el{position:absolute;z-index:2}
.cpalco .p-el img{height:100%;display:block;-webkit-mask-image:linear-gradient(#000 58%,transparent 99%);mask-image:linear-gradient(#000 58%,transparent 99%)}
.cpalco .p-el.tras{filter:grayscale(1) blur(7px) brightness(.9);opacity:.55;z-index:1}
.cpalco .p-el.frente{z-index:4}
.cpalco .p-el.cab img{width:100%;height:auto;-webkit-mask-image:none;mask-image:none}
.cpalco .p-el.cab.f1{filter:blur(9px) grayscale(1);opacity:.35;z-index:1}
.cpalco .p-el.cab.f2{filter:blur(3.5px) grayscale(1);opacity:.55;z-index:2}
.cpalco .p-el.cab.topo{filter:grayscale(1) contrast(1.1);z-index:4}
.cpalco .p-ponte{position:absolute;left:0;right:0;top:1250px;height:300px;z-index:5;pointer-events:none}
`;

  // campos mínimos de cada card do Painel (sem eles a cena fica no card que o modelo escolheu)
  const PSCHEMA = { p81: ['titulo'], p82: ['titulo'], p83: ['titulo'], p84: ['titulo'], p85: ['titulo'], p86: ['titulo', 'pessoa'], p114: ['titulo'], p115: ['titulo'], p116: ['titulo'], p117: ['titulo'], p119: ['titulo'], p142: ['titulo'], p41: ['titulo'], p125: ['titulo', 'itens'], p137: ['titulo', 'itens'], p148: ['titulo', 'pessoa'], p149: ['titulo', 'pessoa'], p150: ['titulo', 'pessoas'], p151: ['titulo', 'pessoas'], p152: ['titulo', 'pessoa'],
    p89: ['titulo'], p134: ['titulo'], p79: ['titulo', 'barras'], p92: ['titulo', 'itens'], p112: ['titulo', 'itens'],
    p118: ['titulo', 'citacao'], p98: ['titulo', 'itens'], p143: ['titulo', 'pessoa'], p160: ['titulo', 'pessoa'], p162: ['titulo', 'pessoas'] };
  // cena feita pro livre/acervo também serve: blocos viram campos (titulo, apoio, itens, pessoas, citacao, numero)
  function pCampos(c) {
    const o = { ...(c || {}) };
    for (const b of Array.isArray(o.blocos) ? o.blocos : []) { if (!b || typeof b !== 'object') continue;
      if (b.tipo === 'titulo' && !o.titulo) { o.titulo = b.texto; if (!o.destaque) o.destaque = b.destaque; }
      else if (b.tipo === 'texto' && !o.apoio) o.apoio = b.texto;
      else if (b.tipo === 'itens' && !o.itens) o.itens = b.itens;
      else if (b.tipo === 'pessoas' && !o.pessoas) o.pessoas = b.pessoas;
      else if (b.tipo === 'citacao' && !o.citacao) { o.citacao = b.texto; if (!o.autor) o.autor = b.autor; }
      else if (b.tipo === 'etiqueta' && !o.rotulo) o.rotulo = b.texto; }
    if (!o.pessoa && Array.isArray(o.pessoas) && o.pessoas[0]) o.pessoa = o.pessoas[0];
    if (o.pessoa && !(Array.isArray(o.pessoas) && o.pessoas.length)) o.pessoas = [o.pessoa];
    return o;
  }
  const temCampos = (id, c) => (PSCHEMA[id] || []).every(x => { const v = c[x]; return Array.isArray(v) ? v.length > 0 : v && typeof v === 'object' ? Object.keys(v).length > 0 : !!v; });
  // qual card desenhar: "pN" direto, ou template_painel "Card N" quando existe C['pN'] e a cena tem os campos dele
  function cardDe(s) {
    if (/^p\d+$/.test(String(s.card)) && C[s.card]) return s.card;
    const m = /(\d{1,3})/.exec(String(s.template_painel || '')), pk = m ? 'p' + Number(m[1]) : null;
    if (pk && C[pk] && temCampos(pk, pCampos(s.campos))) return pk;
    return s.card;
  }
  Object.assign(C, PN);

  const CSS_P = `
.cpalco.pcard .leg,.cpalco.pcard .arroba,.cpalco.pcard .fonte{z-index:40}
.cpalco .pa{color:var(--p-ac)}
.cpalco .p-mast{display:flex;justify-content:space-between;align-items:baseline;gap:24px;border-top:2px solid currentColor;z-index:9}
.cpalco .p-grao{position:absolute;inset:0;z-index:30;pointer-events:none;opacity:.31;mix-blend-mode:soft-light;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='260' height='260'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)'/%3E%3C/svg%3E")}
.cpalco .p-rail{position:absolute;inset:224px 108px 265px;z-index:2;pointer-events:none}
.cpalco .p-rail::before,.cpalco .p-rail::after{content:"";position:absolute;width:26px;height:9px;border:0 solid var(--p-ac);opacity:.75}
.cpalco .p-rail::before{top:0;left:0;border-width:1px 0 0 1px}.cpalco .p-rail::after{bottom:0;right:0;border-width:0 1px 1px 0}
.cpalco .p-regua{position:absolute;left:150px;right:165px;top:1614px;border-top:1px solid currentColor;opacity:.55;z-index:9}
.cpalco .p-media{overflow:hidden;background:#30312b}
.cpalco .p-media img,.cpalco .p-janela img,.cpalco .p-back img,.cpalco .p-back79 img,.cpalco .p-cidade img,.cpalco .p-meiotom img{width:100%;height:100%;object-fit:cover;display:block}
.cpalco .p-filete{outline:1px solid currentColor;outline-offset:6px}
.cpalco .p-semfoto{width:100%;height:100%;background:repeating-linear-gradient(135deg,rgba(255,255,255,.06) 0 14px,transparent 14px 28px),color-mix(in srgb,var(--p-ac) 18%,#2b2b28)}
.cpalco .p-linha{display:grid;align-items:baseline;border-top:1px solid currentColor;box-sizing:border-box}
.cpalco .p-passos{border-bottom:1px solid currentColor;z-index:3}
.cpalco .p-estrela{position:absolute;background:var(--p-ac);clip-path:polygon(50% 0,61.8% 35%,98% 35%,68% 57%,79% 94%,50% 71%,21% 94%,32% 57%,2% 35%,38% 35%);z-index:1}
.cpalco .p-tecido{width:100%;height:100%;background:repeating-linear-gradient(135deg,var(--p-ac) 0 16px,color-mix(in srgb,var(--p-bg) 70%,#000) 16px 30px,#2f5a49 30px 44px)}
.cpalco .p-rally{position:absolute;display:grid;grid-template-columns:97px 1fr;align-items:center;gap:24px;background:#f2eee3;color:#402018;padding:26px 32px;clip-path:polygon(1% 2%,7% 0,11% 2%,20% 0,31% 2%,48% 0,62% 2%,75% 0,90% 2%,100% 0,99% 98%,88% 100%,82% 98%,67% 100%,52% 97%,32% 100%,23% 98%,10% 100%,0% 98%)}
.cpalco .p-megafone{width:97px;height:75px;clip-path:polygon(0 39%,30% 39%,93% 7%,100% 7%,100% 79%,93% 79%,31% 55%,46% 87%,35% 99%,17% 60%,0 60%)}
.cpalco .p-colchete{position:absolute;left:150px;right:165px;height:16px;border:2px solid var(--p-ac);border-top:0;transform-origin:left}
.cpalco .p-back{position:absolute;inset:0;opacity:.15}.cpalco .p-back img{filter:grayscale(1)}
.cpalco .p-meiotom{position:absolute;inset:0;opacity:.5;mix-blend-mode:screen;-webkit-mask-image:radial-gradient(circle,#000 2.4px,transparent 3.1px);mask-image:radial-gradient(circle,#000 2.4px,transparent 3.1px);-webkit-mask-size:8px 8px;mask-size:8px 8px}
.cpalco .p-meiotom img{filter:grayscale(1) brightness(1.15) contrast(1.5)}
.cpalco .p-sombra134{position:absolute;inset:0;background:linear-gradient(180deg,#141615ef 7%,#141615c7 24%,transparent 42%,transparent 60%,#14161590 79%,#141615fa 91%)}
.cpalco .p-janela{position:absolute;overflow:hidden;border-radius:20px;background:#242524;border:2px solid #f7e6c677;box-shadow:0 14px 42px #0008;z-index:4}
.cpalco .p-janela::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,#17191542,transparent 25%,transparent 75%,#17191536);pointer-events:none}
.cpalco .p-janela.com-faixa{border-color:#e0a57a}.cpalco .p-janela.com-faixa .p-semfoto{height:calc(100% - 82px)}.cpalco .p-janela.com-faixa img{height:calc(100% - 82px);filter:grayscale(1) contrast(.89) brightness(.95)}
.cpalco .p-janela .faixa{height:82px;background:var(--p-ac);color:#271b15;display:flex;align-items:center;padding:0 22px}
.cpalco .p-back79{position:absolute;inset:0}
.cpalco .p-veu79{position:absolute;inset:0;background:linear-gradient(180deg,#161d17b0 5%,#161d1738 27%,transparent 44%,rgb(14 23 20 / .23) 49%,rgb(14 23 20 / .87) 59%,rgb(14 23 20 / .87) 83%,#0e1714f5 100%)}
.cpalco .p-pontos{position:absolute;border-radius:50%;background:radial-gradient(circle,#766e5b 0 2px,transparent 3px) 0 0/23px 23px;-webkit-mask-image:radial-gradient(ellipse,#000,transparent 72%);mask-image:radial-gradient(ellipse,#000,transparent 72%);opacity:.47}
.cpalco .p-recorte{position:absolute;z-index:3;filter:drop-shadow(0 17px 16px #30211539)}
.cpalco .p-recorte img,.cpalco .p-pessoa img{width:100%;height:100%;object-fit:contain;object-position:center bottom;display:block}
.cpalco .p-recorte img{filter:grayscale(1) drop-shadow(1px 0 0 #f3efe7) drop-shadow(-1px 0 0 #f3efe7) drop-shadow(0 1px 0 #f3efe7) drop-shadow(0 -1px 0 #f3efe7)}
.cpalco .p-cidade{position:absolute;inset:0;opacity:.31;-webkit-mask-image:linear-gradient(180deg,transparent 12%,#000 32%,#000 76%,transparent 96%);mask-image:linear-gradient(180deg,transparent 12%,#000 32%,#000 76%,transparent 96%)}
.cpalco .p-cidade img{object-position:center 53%;filter:grayscale(1) contrast(.76) brightness(.81)}
.cpalco .p-cidade::after{content:"";position:absolute;inset:0;background:radial-gradient(ellipse at 50% 54%,transparent 23%,var(--p-bg) 86%)}
.cpalco .p-pessoa{position:absolute;z-index:2}
.cpalco .p-pessoa.far img{filter:grayscale(1) brightness(.86) contrast(.82) blur(5.5px)}
.cpalco .p-pessoa.nitida{z-index:4;filter:drop-shadow(5px 12px 12px #0d0e1053)}
.cpalco .p-pessoa.nitida img{filter:grayscale(1) contrast(1.02)}
.cpalco .p-pessoa.fade{-webkit-mask-image:linear-gradient(180deg,#000 1%,#000 63%,#000a 84%,transparent 100%);mask-image:linear-gradient(180deg,#000 1%,#000 63%,#000a 84%,transparent 100%)}
.cpalco .p-aro{position:absolute;z-index:1;width:626px;height:626px;border-radius:50%;border:1px solid color-mix(in srgb,var(--p-ac) 44%,transparent);background:radial-gradient(circle,color-mix(in srgb,var(--p-ac) 28%,transparent),transparent 69%)}
.cpalco .p-chao{position:absolute;z-index:1;left:50%;height:62px;width:825px;transform:translateX(-50%);border-radius:50%;background:#0b13155c;filter:blur(24px)}
.cpalco .p-sombra-txt{position:absolute;z-index:7;inset:0;pointer-events:none;background:linear-gradient(180deg,transparent 62%,transparent 68%,color-mix(in srgb,var(--p-bg) 86%,transparent) 77%,var(--p-bg) 88%)}
.cpalco .p-palco162{position:absolute;inset:676px 0 373px;background:radial-gradient(ellipse at 23% 65%,color-mix(in srgb,var(--p-ac) 22%,transparent),transparent 55%),radial-gradient(ellipse at 76% 68%,color-mix(in srgb,var(--p-ac) 26%,transparent),transparent 57%)}
.cpalco .p-linhabase{position:absolute;left:150px;right:165px;z-index:1;border-top:1px solid color-mix(in srgb,var(--p-ac) 59%,transparent);box-shadow:0 11px 0 color-mix(in srgb,var(--p-ac) 22%,transparent)}
`;

  function html(s, t, palavras) {
    const id = cardDe(s), pc = id in PN, f = C[id] || C['22'];
    const c = pc ? pCampos(s.campos) : (s.campos || {});
    const tl = t - s.start;
    ENT = ENTRADAS.includes(s.entrada) ? s.entrada : 'baixo'; CAPA = !(s.start > 0.001);
    let r = null;
    try {
      // livre: começa maior (cena com pouco conteúdo ocupa a tela em vez de deixar meia tela vazia) e desce até caber
      const ks = id === 'livre' ? [1.3, 1.15, 1, 0.92, 0.85, 0.78, 0.72, 0.66, 0.6, 0.54] : [1, 0.92, 0.85, 0.78, 0.72, 0.66, 0.6, 0.54];
      for (const k of ks) { r = f(c, tl, s, k); if (!(r.fim > LIM) && !r.falta) break; } // não cabe acima da legenda: corpo menor
    } finally { ENT = 'baixo'; CAPA = false; }
    if (pc) // card do Painel: o desenho é o do template (fundo, textura e moldura dele); a cor já veio de cor_tema em pTema
      return `<div class="cpalco pcard" data-card="${E(id)}" style="background:${r.bg};color:${r.fg};--bg:${r.bg};${r.vars}">` + r.html +
        rodape(s.source || c.fonte) + legenda(t, palavras, !!r.escuro, s, r.bg) + '</div>';
    // paleta: no livre vale sempre; no acervo troca o fundo só se tiver o mesmo claro/escuro do card (senão só o destaque)
    const P = paletaDaPeca(s), troca = P && (id === 'livre' || !!P.escuro === !!r.escuro);
    const bg = s.background || (troca ? P.bg : r.bg), fg = troca ? P.fg : (r.fg || '#0B0B0C');
    const vars = P ? `--ac:${P.ac};--tc:${P.tc};` : '';
    const fu = s.fundo || (r.papel ? 'papel' : 'chapado'), al = ALINHA.includes(s.composicao) && id !== 'livre' ? s.composicao : 'esq';
    return `<div class="cpalco${r.vinco && !s.fundo ? ' vinco' : ''}${al !== 'esq' ? ' al-' + al : ''}" data-fundo-tipo="${E(fu)}"${r.composicao ? ` data-composicao="${E(r.composicao)}"` : ''} style="background:${bg};color:${fg};--bg:${bg};${vars}">` +
      fundoHtml(fu, s, c) + molduraHtml(s.variante) + r.html +
      rodape(s.source || c.fonte) + legenda(t, palavras, !!(troca ? P.escuro : r.escuro), s, bg) + '</div>';
  }

  /* CARDS.medir(raiz): verificador de zona segura sobre o TEXTO REAL (não os containers).
     Para cada nó de texto: Range.getClientRects (uma caixa por linha), recortada na tinta da fonte (canvas
     actualBoundingBox), mais o fundo pintado do destaque (.hl::before, .agora) e a sombra. Mede no FIM da animação
     (classe .medir zera o deslocamento de entrada). Aponta: fora de x 150-915 / y 268-1680 (rodapé até 1730),
     sobreposição texto x texto e texto x retrato/moldura, texto cortado por camada com overflow, reticências,
     legenda com mais de 2 linhas. Coordenadas no palco 1080x1920 (vale pro palco reduzido 540x960). */
  function medir(raiz, opc = {}) {
    const palco = (raiz.classList && raiz.classList.contains('cpalco')) ? raiz : (raiz.querySelector('.cpalco') || raiz);
    const ref = palco.classList.contains('cpalco') ? palco : raiz;
    const R = ref.getBoundingClientRect(), sc = R.width / 1080 || 1;
    if (palco.classList.contains('cpalco') && opc.final !== false) palco.classList.add('medir');
    const cx = r => [(r.left - R.left) / sc, (r.top - R.top) / sc, (r.right - R.left) / sc, (r.bottom - R.top) / sc];
    const SEL = '.tx,.leg,.arroba,.fonte,.chip,.etiqueta,.t,.q,.bar,.rec';
    const cv = document.createElement('canvas').getContext('2d');
    const blocos = new Map(), get = b => { if (!blocos.has(b)) blocos.set(b, { el: b, r: [], txt: '' }); return blocos.get(b); };
    const sombra = cs => { const ts = cs.textShadow; if (!ts || ts === 'none') return 0; let m = 0; for (const p of ts.split(/,(?![^(]*\))/)) { const n = (p.match(/-?[\d.]+px/g) || []).map(parseFloat); if (n.length >= 2) m = Math.max(m, Math.abs(n[0]) + (n[2] || 0), Math.abs(n[1]) + (n[2] || 0)); } return m; };
    const tw = document.createTreeWalker(palco, NodeFilter.SHOW_TEXT); let nd;
    while ((nd = tw.nextNode())) {
      if (!nd.data.trim()) continue;
      const el = nd.parentElement, cs = getComputedStyle(el);
      if (cs.visibility === 'hidden' || cs.display === 'none' || el.closest('svg,style,script,.brilho,[data-deco]')) continue;
      const B = get(el.closest(SEL) || el); B.txt += nd.data;
      const rg = document.createRange(); rg.selectNodeContents(nd);
      cv.font = `${cs.fontWeight} 100px ${cs.fontFamily}`;
      const tx = cs.textTransform === 'uppercase' ? nd.data.toUpperCase() : nd.data, m = cv.measureText(tx.trim() || 'x');
      const fa = m.fontBoundingBoxAscent, fd = m.fontBoundingBoxDescent, aa = m.actualBoundingBoxAscent, ad = m.actualBoundingBoxDescent;
      const sh = sombra(cs) * (palco.classList.contains('cpalco') ? 1 : 1 / sc);
      for (const q of rg.getClientRects()) { if (q.width < 0.5 || q.height < 0.5) continue;
        let [x0, y0, x1, y1] = cx(q); const hh = y1 - y0;
        if (fa && fd) { const t0 = y0 + hh * Math.max(0, fa - aa) / (fa + fd), t1 = y1 - hh * Math.max(0, fd - ad) / (fa + fd); y0 = t0; y1 = t1; }
        B.r.push([x0 - sh, y0 - sh, x1 + sh, y1 + sh]); }
    }
    palco.querySelectorAll('.hl,.agora').forEach(h => { const B = blocos.get(h.closest(SEL) || h); if (!B) return;
      const ps = getComputedStyle(h, '::before');
      const top = h.classList.contains('hl') ? (parseFloat(ps.top) || 0) : 0, bot = h.classList.contains('hl') ? (parseFloat(ps.bottom) || 0) : 0;
      for (const q of h.getClientRects()) { const [x0, y0, x1, y1] = cx(q); const kk = (y1 - y0) / (h.offsetHeight || (y1 - y0) || 1); B.r.push([x0, y0 + top * kk, x1, y1 - bot * kk]); } });
    // camada que cobre letra: fundo de destaque pintado NA FRENTE (fundo no próprio span, ou ::before sem z-index
    // negativo) sobre a tinta de outro texto (ex.: fundo da 2ª linha do título condensado cortando a 1ª)
    const cobre = [];
    palco.querySelectorAll('.hl,.agora,[data-fundo]').forEach(h => {
      const own = getComputedStyle(h).backgroundColor, pb = getComputedStyle(h, '::before');
      const frente = (own && own !== 'rgba(0, 0, 0, 0)' && own !== 'transparent') || (pb.content !== 'none' && pb.backgroundColor !== 'rgba(0, 0, 0, 0)' && !(parseInt(pb.zIndex, 10) < 0));
      if (!frente) return;
      for (const q of h.getClientRects()) cobre.push({ h, b: cx(q) });
    });
    const figuras = [...palco.querySelectorAll('.rec,.cel')].map(e => { const b = cx(e.getBoundingClientRect()); return { e, b, circ: e.classList.contains('rec') }; });
    const problemas = [], lista = [...blocos.values()].filter(b => b.r.length);
    const tipo = b => b.el.closest('.leg') ? 'legenda' : b.el.closest('.arroba,.fonte') ? 'rodape' : 'conteudo';
    const caixa = rs => [Math.min(...rs.map(r => r[0])), Math.min(...rs.map(r => r[1])), Math.max(...rs.map(r => r[2])), Math.max(...rs.map(r => r[3]))].map(v => Math.round(v));
    const nome = b => b.txt.replace(/\s+/g, ' ').trim().slice(0, 60);
    const TOL = 1;
    for (const b of lista) {
      const tp = tipo(b), bx = caixa(b.r);
      if (bx[0] < X0 - TOL || bx[2] > X1 + TOL) problemas.push({ tipo: 'fora_x', elemento: tp, texto: nome(b), caixa: bx });
      if (tp === 'conteudo' && (bx[1] < Y0 - TOL || bx[3] > 1680 + TOL)) problemas.push({ tipo: 'fora_y', elemento: tp, texto: nome(b), caixa: bx });
      if (tp === 'rodape' && bx[3] > 1730) problemas.push({ tipo: 'fora_y', elemento: tp, texto: nome(b), caixa: bx });
      if (tp === 'legenda') { const leg = b.el.closest('.leg'), divs = [...leg.children].filter(x => x.tagName === 'DIV').length;
        const ln = divs || new Set(b.r.map(r => Math.round(r[1] / 30))).size;
        if (ln > 2) problemas.push({ tipo: 'legenda_3_linhas', elemento: tp, texto: nome(b), caixa: bx }); }
      // cortado: alguma camada com overflow escondido (ou o próprio palco) corta a tinta do texto
      for (let a = b.el; a && a !== document.body; a = a.parentElement) {
        const cs = getComputedStyle(a);
        if (cs.textOverflow === 'ellipsis' && a.scrollWidth > a.clientWidth + 1) problemas.push({ tipo: 'cortado_reticencias', elemento: tp, texto: nome(b), caixa: bx });
        if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible' || a === palco) { const cb = cx(a.getBoundingClientRect());
          if (b.r.some(r => r[0] < cb[0] - TOL || r[2] > cb[2] + TOL || r[1] < cb[1] - TOL || r[3] > cb[3] + TOL)) { problemas.push({ tipo: 'cortado', elemento: tp, texto: nome(b), caixa: bx }); break; } }
        if (a === palco || a === raiz) break;
      }
    }
    const cruza = (r, z) => Math.min(r[2], z[2]) - Math.max(r[0], z[0]) > TOL && Math.min(r[3], z[3]) - Math.max(r[1], z[1]) > TOL;
    for (let i = 0; i < lista.length; i++) for (let j = i + 1; j < lista.length; j++) {
      const A = lista[i], Bb = lista[j]; if (A.el.contains(Bb.el) || Bb.el.contains(A.el)) continue;
      if (A.r.some(r => Bb.r.some(z => cruza(r, z)))) problemas.push({ tipo: 'sobreposicao', elemento: tipo(A) + ' x ' + tipo(Bb), texto: nome(A) + ' | ' + nome(Bb), caixa: caixa(A.r).concat(caixa(Bb.r)) });
    }
    { const tw2 = document.createTreeWalker(palco, NodeFilter.SHOW_TEXT); let t2; const ja = new Set();
      while ((t2 = tw2.nextNode())) { if (!t2.data.trim()) continue; const el = t2.parentElement; if (el.closest('svg,style,script,.brilho,[data-deco]')) continue;
        const rg = document.createRange(); rg.selectNodeContents(t2); const cs = getComputedStyle(el);
        cv.font = `${cs.fontWeight} 100px ${cs.fontFamily}`; const m = cv.measureText((cs.textTransform === 'uppercase' ? t2.data.toUpperCase() : t2.data).trim() || 'x');
        const fa = m.fontBoundingBoxAscent, fd = m.fontBoundingBoxDescent;
        for (const q of rg.getClientRects()) { let [x0, y0, x1, y1] = cx(q); const hh = y1 - y0;
          if (fa && fd) { const n0 = y0 + hh * Math.max(0, fa - m.actualBoundingBoxAscent) / (fa + fd), n1 = y1 - hh * Math.max(0, fd - m.actualBoundingBoxDescent) / (fa + fd); y0 = n0; y1 = n1; }
          for (const c of cobre) { if (c.h.contains(t2) || ja.has(c.h)) continue; const z = c.b;
            if (Math.min(x1, z[2]) - Math.max(x0, z[0]) > TOL && Math.min(y1, z[3]) - Math.max(y0, z[1]) > 2) { ja.add(c.h); problemas.push({ tipo: 'letra_coberta', elemento: 'destaque', texto: (t2.data.trim() + ' | ' + c.h.textContent).slice(0, 60), caixa: [x0, y0, x1, y1].concat(z).map(Math.round) }); } } } } }
    for (const b of lista) for (const f of figuras) { if (f.e.contains(b.el)) continue;
      const bate = b.r.some(r => { if (!cruza(r, f.b)) return false; if (!f.circ) return true;
        const ccx = (f.b[0] + f.b[2]) / 2, ccy = (f.b[1] + f.b[3]) / 2, raio = (f.b[2] - f.b[0]) / 2;
        const dx = Math.max(r[0] - ccx, 0, ccx - r[2]), dy = Math.max(r[1] - ccy, 0, ccy - r[3]); return dx * dx + dy * dy < raio * raio - 1; });
      if (bate) problemas.push({ tipo: f.circ ? 'texto_sobre_retrato' : 'texto_sobre_figura', elemento: tipo(b), texto: nome(b), caixa: caixa(b.r).concat(f.b.map(Math.round)) }); }
    palco.classList.remove('medir');
    return { ok: !problemas.length, problemas, blocos: lista.map(b => ({ tipo: tipo(b), texto: nome(b), caixa: caixa(b.r) })) };
  }

  if (typeof document !== 'undefined' && !document.getElementById('cards-css')) {
    const st = document.createElement('style'); st.id = 'cards-css'; st.textContent = CSS + CSS_VAR + CSS_P + CSS_P2; (document.head || document.documentElement).appendChild(st);
  }
  // composição que o livre desenha de fato (colunas sem espaço pro título legível vira pilha)
  function composicao(s) { const m = /data-composicao="([^"]*)"/.exec(html({ ...s, start: 0, end: Math.max(1, (s.end || 1) - (s.start || 0)) }, 99, []) || ''); return m ? m[1] : (s.composicao || null); }
  G.CARDS = { css: CSS + CSS_VAR + CSS_P + CSS_P2, html, cardDe, painel: Object.keys(PN), painelSchema: PSCHEMA, paginar, composicao, medir, texto, tokens, pronto, folga: FOLGA, cards: Object.keys(C).filter(k => k !== 'livre' && !(k in PN)), schema: SCHEMA,
    variacoes: { paletas: PALETAS, fundos: FUNDOS, molduras: MOLDURAS, entradas: ENTRADAS, alinhamentos: ALINHA, layouts: LAYOUTS, disposicao: DISPOSICAO, blocos: BLOCOS, original: ORIGINAL }, icones: Object.keys(ICONES), zona: { X0, X1, Y0, LIM } };
})(typeof window !== 'undefined' ? window : globalThis);

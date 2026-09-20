// Generic card renderer for the transcribe-comment-create-print deck.
// DECK = {shots:{key:dataUri}, video:{file,poster}|null, cards:[...]}; every text field is {pt,en}.
const SHOTS = DECK.shots || {};
const T = (o, L) => (o && typeof o === 'object' ? (o[L] || o.pt || '') : (o || ''));
function proofCard(c, L) {
  const s = c.src || {};
  const imgs = (c.split || [c.key]).map(k => `<div class="shot${c.split ? ' half' : ''}"><img src="${SHOTS[k] || ''}" alt=""></div>`).join('');
  const also = c.also ? ` <span class="al">— ${T(c.also, L)}</span>` : '';
  return `<div class="eb ok">${T(c.eb, L) || (L === 'pt' ? 'A reportagem' : 'The article')}</div>${imgs}
    <div class="cap"><span class="nm">${s.name} · ${s.date}</span> <span class="lk">${s.full}${c.extra ? ' — ' + c.extra : ''}</span>${also}</div>`;
}
function claimCard(c, L) {
  const badge = c.badge === 'partly' ? (L === 'pt' ? '🟡 EM PARTE' : '🟡 PARTLY') : c.badge === 'false' ? (L === 'pt' ? '❌ FALSO' : '❌ FALSE') : (L === 'pt' ? '✅ CONFIRMADO' : '✅ CONFIRMED');
  return `<div class="ebr"><div class="eb" style="margin:0">${T(c.eb, L) || (L === 'pt' ? 'A alegação' : 'The claim')}</div><div class="cf">${badge}</div></div>
    <div class="hd${T(c.hd, L).length > 40 ? ' sm' : ''}">${T(c.hd, L)}</div>
    ${c.say ? `<p class="say">${T(c.say, L)}</p>` : ''}<p class="chk">${T(c.chk, L)}</p>
    <div class="foot">${L === 'pt' ? 'Fonte na próxima página' : 'Source on the next card'} &rarr;</div>`;
}
function openCard(c, L) {
  const v = DECK.video && DECK.video.file
    ? `<div class="vph vv"><video controls playsinline preload="metadata" ${DECK.video.poster ? `poster="${DECK.video.poster}"` : ''} src="${DECK.video.file}"></video></div>`
    : `<div class="vph"><div class="play"></div><span>${L === 'pt' ? 'VÍDEO' : 'VIDEO'}</span></div>`;
  return `${v}<div class="hd">${T(c.hd, L)}</div><div class="foot swipe">${L === 'pt' ? 'Deslize para a checagem →' : 'Swipe for the fact check →'}</div>`;
}
function videoCard(c, L) {
  const media = c.file
    ? `<div class="vth" style="cursor:default"><video controls playsinline preload="metadata" src="${c.file}" style="width:100%;height:100%;object-fit:contain"></video></div>`
    : `<div class="vth" onclick="playYT(this,'${c.yt}')"><img src="${SHOTS[c.key] || ''}" alt=""><div class="pl"></div></div>`;
  return `<div class="eb ok">${T(c.eb, L)}</div>${media}
    <div class="cap"><span class="nm">${T(c.cap, L)}</span> <span class="lk">${c.link || ''}</span>${c.tx ? `<span class="al" style="display:block;margin-top:1cqw">${T(c.tx, L)}</span>` : ''}</div>`;
}
function textCard(c, L) {
  return `<div class="eb ${c.ebc || ''}">${T(c.eb, L)}</div><div class="hd sm">${T(c.hd, L)}</div>${c.say ? `<p class="say">${T(c.say, L)}</p>` : ''}<div class="chk">${T(c.chk, L)}</div><div class="foot">${T(c.foot, L)}</div>`;
}
const RENDER = { open: openCard, claim: claimCard, proof: proofCard, video: videoCard, text: textCard };
const CARDS = DECK.cards.map((c, i) => ({ id: c.id || i + 1, proof: c.type === 'proof' || c.type === 'video', render: L => RENDER[c.type](c, L) }));
function playYT(el, id) {
  el.onclick = null; el.style.cursor = 'default';
  el.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&playsinline=1" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>';
}

// Cena "anim" de referência (Coolonização BR) — contrato da rodada 4:
//   export function montar(palco, params) -> { desenhar(t), duracao }
//   desenhar(t) é FUNÇÃO PURA do tempo t (segundos desde o início da cena): nenhum setTimeout, nenhum
//   estado guardado entre quadros. Assim buscar, voltar e mudar a velocidade no player dão sempre o mesmo quadro,
//   e a prévia e o MP4 usam a MESMA linha do tempo (o relógio do áudio).
// Palco 1080x1920. Fontes e imagens só de assets privados (nada de Google Fonts: a rede bloqueia).
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = x => 1 - Math.pow(1 - clamp(x), 3);           // easeOutCubic
const mola = x => { x = clamp(x); return 1 - Math.cos(x * 4.5 * Math.PI) * Math.exp(-x * 6); };
const janela = (t, ini, dur) => clamp((t - ini) / dur);

export function montar(palco, params = {}) {
  const cor = params.cor || '#B48CFF';              // cor do dia (sábado lilás); político pula azul/coral
  const palavras = params.palavras || [
    { txt: 'UMA', t: 0.15 }, { txt: 'CENA,', t: 0.45 }, { txt: 'QUALQUER', t: 0.9, cor: true }, { txt: 'SEGUNDO', t: 1.3, cor: true },
  ];
  const selo = params.selo || 'DEMONSTRAÇÃO TÉCNICA';
  palco.innerHTML = `
  <div class="cb-fundo"></div>
  <div class="cb-faixa"><div class="cb-meio-tom"></div></div>
  <svg class="cb-rasgo" viewBox="0 0 1080 700" preserveAspectRatio="none"><path d="M0,90 L70,60 L140,95 L230,40 L330,85 L420,50 L520,92 L610,45 L720,88 L820,52 L930,96 L1010,58 L1080,80 L1080,640 L990,670 L880,630 L780,675 L660,632 L560,668 L450,628 L340,672 L230,630 L120,666 L0,628 Z" fill="${cor}"/></svg>
  <div class="cb-titulo">${palavras.map((p, i) => `<span data-i="${i}" class="${p.cor ? 'cb-cor' : ''}">${p.txt}</span>`).join(' ')}</div>
  <div class="cb-selo">${selo}</div>
  <div class="cb-pontos"></div>`;
  const css = document.createElement('style');
  css.textContent = `
  #${palco.id}{position:absolute;inset:0;overflow:hidden;background:#F2E6D0;font-family:"Anton","Bebas Neue","Oswald",Impact,"Arial Narrow",sans-serif}
  .cb-fundo{position:absolute;inset:0;background:#F2E6D0;background-image:radial-gradient(rgba(22,22,19,.16) 2.2px,transparent 2.6px);background-size:26px 26px}
  .cb-faixa{position:absolute;left:0;right:0;top:300px;height:520px;overflow:hidden;filter:grayscale(1) contrast(1.25)}
  .cb-meio-tom{position:absolute;inset:-40px;background:
     radial-gradient(circle at 30% 40%,#e9e4da 0,#9b968c 35%,#2c2b28 70%),
     repeating-linear-gradient(45deg,rgba(0,0,0,.25) 0 3px,transparent 3px 9px);background-blend-mode:multiply}
  .cb-rasgo{position:absolute;left:0;width:1080px;top:760px;height:700px}
  .cb-titulo{position:absolute;left:108px;right:108px;top:860px;color:#161613;font-size:178px;line-height:.92;letter-spacing:-2px;transform-origin:left bottom;text-transform:uppercase}
  .cb-titulo span{display:inline-block;transform-origin:50% 100%}
  .cb-titulo .cb-cor{color:#fff;-webkit-text-stroke:4px #161613;paint-order:stroke fill}
  .cb-selo{position:absolute;left:108px;top:1490px;padding:14px 26px;background:#161613;color:#F2E6D0;font:600 38px/1 system-ui,sans-serif;border-radius:999px}
  .cb-pontos{position:absolute;right:120px;top:220px;width:180px;height:180px;border-radius:50%;background:#FF4A3D}`;
  palco.appendChild(css);
  const q = s => palco.querySelector(s);
  const faixa = q('.cb-faixa'), meio = q('.cb-meio-tom'), rasgo = q('.cb-rasgo'), selo_ = q('.cb-selo'), bola = q('.cb-pontos');
  const spans = [...palco.querySelectorAll('.cb-titulo span')];
  const duracao = params.duracao || 4;
  function desenhar(t) {
    const f = ease(janela(t, 0, 0.5));
    faixa.style.clipPath = `inset(0 ${100 - f * 100}% 0 0)`;
    meio.style.transform = `translateX(${-30 * t}px) scale(1.08)`;          // movimento ambiente contínuo
    rasgo.style.transform = `translateY(${(1 - ease(janela(t, 0.05, 0.45))) * 260}px) rotate(${-1.2 + 0.4 * Math.sin(t * 1.7)}deg)`;
    spans.forEach((s, i) => {
      const k = janela(t, palavras[i].t, 0.35);
      s.style.opacity = k > 0 ? 1 : 0;                                        // a palavra entra NA fala dela
      s.style.transform = `translateY(${(1 - mola(k)) * 120}px) scaleY(${1 + 0.15 * (1 - ease(k))})`;
    });
    const ks = mola(janela(t, 1.7, 0.6));
    selo_.style.transform = `scale(${ks}) rotate(${-4 + 2 * Math.sin(t * 2.3)}deg)`;
    bola.style.transform = `scale(${0.9 + 0.1 * Math.sin(t * 3)})`;          // nunca tela parada
  }
  desenhar(0);
  return { desenhar, duracao };
}

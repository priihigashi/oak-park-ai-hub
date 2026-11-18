const {chromium} = require('playwright');
(async () => {
  const file = process.argv[2], outdir = process.argv[3] || 'render';
  const fs = require('fs'); fs.mkdirSync(outdir, {recursive:true});
  const b = await chromium.launch();
  const p = await b.newPage({viewport:{width:1400,height:1000}, deviceScaleFactor:1});
  await p.goto('file://' + require('path').resolve(file));
  await p.waitForTimeout(2500);
  // Force every .card to exactly 1080 wide so cqw resolves at production size
  await p.addStyleTag({content:`
    .pair,.deck{display:block !important;max-width:none !important}
    .card{width:1080px !important;height:1350px !important;aspect-ratio:auto !important;margin:0 0 40px !important}
    .ctl,.btns,textarea{display:none !important}
  `});
  await p.waitForTimeout(800);
  const cards = await p.$$('.card');
  console.log('cards encontrados:', cards.length);
  const report = [];
  for (let i=0;i<cards.length;i++){
    const c = cards[i];
    // measure overflow: does any descendant cross the card box?
    const m = await c.evaluate(el => {
      const cb = el.getBoundingClientRect();
      let worstBottom = 0, worstRight = 0, offender = '';
      el.querySelectorAll('*').forEach(n => {
        const r = n.getBoundingClientRect();
        if (r.height === 0 && r.width === 0) return;
        const ob = r.bottom - cb.bottom, or_ = r.right - cb.right;
        if (ob > worstBottom){ worstBottom = ob; offender = n.className || n.tagName; }
        if (or_ > worstRight) worstRight = or_;
      });
      const pad = el.querySelector('.pad');
      const pr = pad ? pad.getBoundingClientRect() : null;
      const hl = el.querySelector('.hl,.hd');
      const sub = el.querySelector('.sub,.bd');
      return {
        cardW: Math.round(cb.width), cardH: Math.round(cb.height),
        padTop: pr ? Math.round(pr.top - cb.top) : null,
        padLeft: pr ? Math.round(pr.left - cb.left) : null,
        overflowBottom: Math.round(worstBottom), overflowRight: Math.round(worstRight), offender: String(offender).slice(0,40),
        hlPx: hl ? Math.round(parseFloat(getComputedStyle(hl).fontSize)) : null,
        subPx: sub ? Math.round(parseFloat(getComputedStyle(sub).fontSize)) : null,
      };
    });
    report.push({i:i+1, ...m});
    await c.screenshot({path: `${outdir}/card_${String(i+1).padStart(2,'0')}.png`});
  }
  console.table(report);
  await b.close();
})();

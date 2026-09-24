// Smoke-test maps.html's inline script against data/maps.json with a minimal DOM stub.
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'maps.html'), 'utf8');
const data = JSON.parse(fs.readFileSync(path.join(root, 'data', 'maps.json'), 'utf8'));

const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('FAIL: no script block'); process.exit(1); }

function makeEl(id) {
  return {
    id, innerHTML: '', textContent: '', children: [],
    listeners: {}, _btns: [],
    addEventListener(t, f) { this.listeners[t] = f; },
    querySelectorAll() { return this._btns; },
    appendChild(c) { this.children.push(c); }
  };
}
function makeBtn(dataset) {
  const btn = {
    dataset, active: false,
    classList: { toggle(_, on) { btn.active = !!on; } },
    closest() { return btn; }
  };
  return btn;
}
const els = {};
['cap-note','disclaimer','centre-chips','q-grid','layer-filters','tier-filters','cards','list-count']
  .forEach(id => { els[id] = makeEl(id); });

els['layer-filters']._btns = ['all','stays','hotels','places','cafes'].map(l => makeBtn({ layer: l }));
els['tier-filters']._btns = ['all','under2500','stretch','confirm'].map(t => makeBtn({ tier: t }));

global.document = {
  getElementById: id => els[id] || null,
  createElement: () => ({ className: '', href: '', target: '', rel: '', textContent: '' })
};
global.fetch = () => Promise.resolve({ ok: true, json: () => Promise.resolve(data) });

eval(m[1]); // run the page script

setTimeout(() => {
  const count = (s, sub) => s.split(sub).length - 1;
  const cards = els['cards'].innerHTML;
  const all = [...data.stays, ...data.hotels, ...data.places, ...data.cafes];
  const checks = [];
  const expect = (name, cond) => checks.push([name, !!cond]);

  expect('45 cards rendered', count(cards, '<article class="card"') === 45);
  expect('45 Photo unavailable blocks', count(cards, 'card__photo-text">Photo unavailable') === 45);
  expect('no <img in cards', !/<img/i.test(cards));
  expect('45 Open-in-Google-Maps links (encoded)', count(cards, 'https://www.google.com/maps/search/?api=1&amp;query=') === 45);
  expect('Booking buttons only where booking exists', count(cards, '>Booking</a>') === all.filter(x => x.booking).length);
  expect('booking_hint shown for 2 items without booking', count(cards, 'card__hint') === all.filter(x => x.booking_hint && !x.booking).length);
  expect('count text', els['list-count'].textContent === 'Showing 45 of 45 pins');
  expect('quarantine: 6 cards', count(els['q-grid'].innerHTML, 'q-card__reason') === 6);
  expect('disclaimer filled', els['disclaimer'].textContent === data.disclaimer);
  expect('cap note filled', els['cap-note'].textContent === data.meta.cap_note);
  expect('6 centre chips', els['centre-chips'].children.length === 6);

  // Simulate layer filter click: stays
  els['layer-filters'].listeners.click.call(els['layer-filters'], { target: els['layer-filters']._btns[1] });
  expect('layer=stays shows 22', els['list-count'].textContent === 'Showing 22 of 45 pins');

  // Reset layer, simulate tier filter: under2500
  els['layer-filters'].listeners.click.call(els['layer-filters'], { target: els['layer-filters']._btns[0] });
  els['tier-filters'].listeners.click.call(els['tier-filters'], { target: els['tier-filters']._btns[1] });
  const u25 = all.filter(x => x.tier === 'under2500').length;
  expect('tier=under2500 shows ' + u25, els['list-count'].textContent === 'Showing ' + u25 + ' of 45 pins');

  // Empty combo: places + confirm tier
  els['layer-filters'].listeners.click.call(els['layer-filters'], { target: els['layer-filters']._btns[3] });
  expect('empty combo shows empty-state', /cards__empty/.test(els['cards'].innerHTML) && els['list-count'].textContent === 'Showing 0 of 45 pins');

  let fail = 0;
  checks.forEach(([n, ok]) => { console.log((ok ? 'PASS' : 'FAIL') + '  ' + n); if (!ok) fail++; });
  process.exit(fail ? 1 : 0);
}, 50);

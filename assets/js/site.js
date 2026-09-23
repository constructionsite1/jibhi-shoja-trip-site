(() => {
'use strict';

const state = {
  stays: [], places: [], site: {},
  filters: { area: 'all', kind: 'all', budget: 'all', sort: 'price-asc' },
  modalStay: null, modalPhoto: 0, modalOpenedDirectly: false
};

const $ = (selector, scope = document) => scope.querySelector(selector);
const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const money = value => `₹${Number(value || 0).toLocaleString('en-IN')}`;
const imgPath = path => `./${String(path || '').replace(/^\.?\//, '')}`;

async function loadData() {
  const [stays, site, places] = await Promise.all([
    fetch('./data/stays.json').then(response => { if (!response.ok) throw new Error('Could not load stays.json'); return response.json(); }),
    fetch('./data/site.json').then(response => { if (!response.ok) throw new Error('Could not load site.json'); return response.json(); }),
    fetch('./data/places.json').then(response => { if (!response.ok) throw new Error('Could not load places.json'); return response.json(); })
  ]);
  state.stays = stays; state.site = site; state.places = places;
}

function sectionHead(label, title, sub = '', center = false) {
  return `<div class="section__head${center ? ' section__head--center' : ''}"><p class="section__label">${esc(label)}</p><h2 class="section__title">${esc(title)}</h2>${sub ? `<p class="section__sub">${esc(sub)}</p>` : ''}</div>`;
}

function renderStats() {
  return `<section class="stats" aria-label="Trip summary"><div class="stats__grid stats__grid--3">
    <div class="stat"><div class="stat__num" data-count="${state.stays.length}" data-suffix="">0</div><div class="stat__label">quiet shortlisted stays</div></div>
    <div class="stat"><div class="stat__num" data-count="${state.places.length}" data-suffix="">0</div><div class="stat__label">places mapped</div></div>
    <div class="stat"><div class="stat__num" data-count="25" data-prefix="₹" data-suffix="k">0</div><div class="stat__label">${esc(state.site.trip?.budget_cap || '₹20–25k')} total cap</div></div>
  </div></section>`;
}

function stayCard(stay, topPick = false) {
  return `<a class="bcard${topPick ? '' : ' bcard--stay'}" href="#stay/${esc(stay.slug)}" aria-label="View ${esc(stay.name)} details">
    <div class="bcard__top"><span class="bcard__brand"><span class="bcard__logo" aria-hidden="true">${esc(stay.area.slice(0, 1))}</span>${esc(stay.area)}</span><span class="bcard__badge">${esc(stay.kind)}</span></div>
    <div class="bcard__imgwrap"><img src="${imgPath(stay.photos[0])}" alt="${esc(stay.name)}" loading="lazy"></div>
    <div class="bcard__foot"><div class="bcard__meta"><h3 class="bcard__name">${esc(stay.name)}</h3><p class="bcard__tag">${money(stay.price_allin)}/N all-in · ${money(stay.total4)} / 4N</p></div>
    <div class="bcard__cta"><span class="bcard__view">View stay</span><span class="bcard__arrow">&rarr;</span></div></div></a>`;
}

function renderTopPicks() {
  const picks = (state.site.top_picks || []).map(slug => state.stays.find(stay => stay.slug === slug)).filter(Boolean);
  return `<section class="collection" id="top-picks">${sectionHead('Best fits', 'Six stays to compare first', 'Ordered exactly from the shortlist.')}
    <div class="caro"><button class="caro__btn caro__prev" aria-label="Previous" type="button">&lsaquo;</button><div class="swipe">${picks.map(stay => stayCard(stay, true)).join('')}</div><button class="caro__btn caro__next" aria-label="Next" type="button">&rsaquo;</button></div>
    <p class="swipe-hint">Swipe &larr; &rarr;</p><div class="browse-all"><a href="#stays" class="btn btn--grad">Browse All 22</a></div></section>`;
}
function chipRow(label, key, options) {
  return `<div class="vfilter-row" data-filter-group="${key}"><span class="vfilter-label">${esc(label)}</span>${options.map(option => `<button class="vchip${option.value === 'all' ? ' is-on' : ''}" data-filter="${key}" data-value="${esc(option.value)}" type="button">${esc(option.label)}</button>`).join('')}</div>`;
}

function renderStays() {
  const areas = ['all', ...new Set(state.stays.map(stay => stay.area))];
  const kinds = ['all', ...new Set(state.stays.map(stay => stay.kind))];
  return `<section class="stays" id="stays">${sectionHead('Stay browse', '22 quiet rooms, cabins and cottages', 'Filter by area, stay kind and nightly all-in budget.')}
    <div class="stays__panel"><div class="vfilters" aria-label="Stay filters">
      ${chipRow('Area', 'area', areas.map(area => ({value: area, label: area === 'all' ? 'All' : area})))}
      ${chipRow('Kind', 'kind', kinds.map(kind => ({value: kind, label: kind === 'all' ? 'All' : kind})))}
      ${chipRow('Budget', 'budget', [{value:'all',label:'All'},{value:'under-2000',label:'≤₹2000'},{value:'under-2500',label:'≤₹2500'},{value:'flagged-edge',label:'Flagged edge'}])}
    </div>
    <div class="stays__tools"><p class="stays__count" data-stay-count aria-live="polite"></p><label class="sort-control">Sort
      <select id="staySort" aria-label="Sort stays"><option value="price-asc">Price ↑</option><option value="price-desc">Price ↓</option><option value="rating-desc">Rating text high–low</option><option value="reviews-desc">Review count ↓</option></select></label></div>
    <div class="stay-grid" id="stayGrid"></div><p class="vempty" id="stayEmpty" hidden>No stay found in the above combinations.</p></div></section>`;
}

function renderStayGrid() {
  const grid = $('#stayGrid'), empty = $('#stayEmpty'), count = $('[data-stay-count]');
  if (!grid) return;
  const filtered = sortStays(state.stays.filter(stay => {
    const budget = state.filters.budget;
    const budgetOk = budget === 'all' || (budget === 'under-2000' && stay.price_allin <= 2000) || (budget === 'under-2500' && stay.price_allin <= 2500) || (budget === 'flagged-edge' && stay.flag_over_cap);
    return (state.filters.area === 'all' || stay.area === state.filters.area) && (state.filters.kind === 'all' || stay.kind === state.filters.kind) && budgetOk;
  }));
  count.textContent = `${filtered.length} of ${state.stays.length} stays`;
  empty.hidden = filtered.length > 0;
  grid.innerHTML = filtered.map(stay => `<article class="stay-card" data-area="${esc(stay.area)}" data-kind="${esc(stay.kind)}">
    <a href="#stay/${esc(stay.slug)}" aria-label="View ${esc(stay.name)} details"><div class="stay-card__media"><img src="${imgPath(stay.photos[0])}" alt="${esc(stay.name)}" loading="lazy"><span class="stay-card__area">${esc(stay.area)}</span>${stay.flag_over_cap ? '<span class="stay-card__flag">Edge</span>' : ''}</div>
    <div class="stay-card__body"><h3 class="stay-card__name">${esc(stay.name)}</h3><p class="stay-card__rating">${esc(stay.rating)}</p><div class="stay-card__prices"><div class="stay-card__price"><span>All-in / night</span><strong>${money(stay.price_allin)}</strong></div><div class="stay-card__price"><span>4N Oct 4–8</span><strong>${money(stay.total4)}</strong></div></div><span class="stay-card__link">View details &rarr;</span></div></a></article>`).join('');
}

function ratingNumber(stay) { const match = String(stay.rating).match(/\d+(?:\.\d+)?/); return match ? Number(match[0]) : 0; }
function reviewCount(stay) { const text = String(stay.rating); const match = text.match(/\(?~?([\d,]+)\s+reviews\)?/i); return match ? Number(match[1].replace(/,/g, '')) : 0; }
function sortStays(stays) {
  const sorted = [...stays];
  if (state.filters.sort === 'price-asc') sorted.sort((a, b) => a.price_allin - b.price_allin || a.name.localeCompare(b.name));
  if (state.filters.sort === 'price-desc') sorted.sort((a, b) => b.price_allin - a.price_allin || a.name.localeCompare(b.name));
  if (state.filters.sort === 'rating-desc') sorted.sort((a, b) => ratingNumber(b) - ratingNumber(a) || reviewCount(b) - reviewCount(a));
  if (state.filters.sort === 'reviews-desc') sorted.sort((a, b) => reviewCount(b) - reviewCount(a) || ratingNumber(b) - ratingNumber(a));
  return sorted;
}

function renderPlaces() {
  const cards = state.places.map(place => {
    const photos = (place.photos || []).map((photo, index) => `<img class="place-card__img" src="${imgPath(photo)}" alt="${esc(place.name)}${place.photos.length > 1 ? ` — photo ${index + 1}` : ''}" loading="lazy">`).join('');
    return `<article class="place-card${place.photos.length > 1 ? ' place-card--multi' : ''}" id="${esc(place.slug)}">
      <div class="place-card__media">${photos}</div>
      <div class="place-card__body"><h3 class="place-card__name">${esc(place.name)}</h3><span class="place-card__type">${esc(place.type)}</span>
      ${place.distance ? `<p class="place-card__dist">${esc(place.distance)}</p>` : ''}
      <p class="place-card__why">${esc(place.why)}</p>
      ${place.location ? `<p class="place-card__meta">${esc(place.location)}</p>` : ''}
      ${place.notes ? `<p class="place-card__meta">${esc(place.notes)}</p>` : ''}</div></article>`;
  }).join('');
  return `<section class="section" id="places">${sectionHead('Places', 'Eleven quiet valley stops', 'Cafes, waterfalls, treks, meadows and viewpoints — each chosen for low crowds.')}
    <div class="place-swipe">${cards}</div><p class="swipe-hint swipe-hint--places">Swipe &larr; &rarr;</p></section>`;
}

function renderPlan() {
  const days = (state.site.itinerary || []).map((day, index) => {
    const optional = /optional/i.test(day.day);
    return `<article class="tl-day${optional ? ' tl-day--optional' : ''}">
      <div class="tl-day__num" aria-hidden="true">${String(index + 1).padStart(2, '0')}</div>
      <div class="tl-day__card">${optional ? '<span class="tl-day__gate">Optional · +1N extension</span>' : ''}
        <p class="tl-day__day">${esc(day.day)}</p><h3>${esc(day.title)}</h3>
        <ul>${day.points.map(point => `<li>${esc(point)}</li>`).join('')}</ul></div></article>`;
  }).join('');
  return `<section class="section section--tint" id="plan">${sectionHead('Plan', 'Oct 4–8, plus the optional ninth', 'A slow couple itinerary with one quiet anchor each day.')}<div class="content-wrap"><div class="plan-tl">${days}</div></div></section>`;
}
function renderQuoteBand() {
  const ridge = state.places.find(place => place.slug === 'place-shoja-ridge') || {};
  return `<section class="quote" style="background-image:url('${imgPath((ridge.photos || [])[0] || '')}')"><div class="quote__overlay"></div><blockquote class="quote__text">&ldquo;${esc(ridge.why || '')}&rdquo;</blockquote><p class="quote__sub">${esc(ridge.name || '')}</p></section>`;
}
function renderTravel() {
  const travel = state.site.travel || {};
  const links = (travel.links || []).map(link => `<a class="tlink-card" href="${esc(link.url)}" target="_blank" rel="noopener">
    <div class="tlink-card__top"><span class="tlink-card__label">${esc(link.label)}</span><span class="tlink-card__go">Open &nearr;</span></div>
    <span class="tlink-card__note">${esc(link.note)}</span></a>`).join('');
  const legs = (travel.last_mile || []).map(leg => `<tr><td>${esc(leg.leg)}</td><td>${esc(leg.detail)}</td></tr>`).join('');
  return `<section class="section" id="travel">${sectionHead('Travel', 'Overnight bus via Aut', 'Last-mile legs and researched booking links.')}<div class="content-wrap">
    <div class="tlink-grid">${links}</div>
    <h3 class="travel-sub">Last-mile fares</h3>
    <div class="fare-table-wrap"><table class="fare-table"><thead><tr><th>Leg</th><th>Fares &amp; timing</th></tr></thead><tbody>${legs}</tbody></table></div>
    <div class="verdict-note"><p class="verdict-note__label">Verdict</p><p class="verdict-note__text">${esc(travel.verdict)}</p></div></div></section>`;
}
function renderBudget() {
  const rows = (state.site.budget_bands || []).map(row => {
    const over = /over/i.test(row.verdict);
    return `<tr class="${over ? 'is-over' : 'is-in'}"><td>${esc(row.band)}</td><td>${row.stay ? money(row.stay) : (row.stay_extra ? `${money(row.stay_extra)} extra` : '—')}</td><td>${row.travel ? money(row.travel) : '—'}</td><td>${row.food_misc ? money(row.food_misc) : (row.food_extra ? `${money(row.food_extra)} extra` : '—')}</td><td>${row.total ? money(row.total) : (row.total_extra ? `${money(row.total_extra)} extra` : '—')}</td><td>${esc(row.verdict)}</td></tr>`;
  }).join('');
  return `<section class="section section--tint" id="budget">${sectionHead('Budget', 'Keep the whole trip inside ₹20–25k', 'Room, travel and food ranges for two people.')}<div class="content-wrap">
    <p class="budget-note">${esc(state.site.cap_note)}</p>
    <div class="budget-legend"><span><i class="dot dot--in"></i>Within cap</span><span><i class="dot dot--over"></i>Over cap</span></div>
    <div class="budget-table-wrap"><table class="budget-table"><thead><tr><th>Band</th><th>Stay</th><th>Travel</th><th>Food / misc</th><th>Total</th><th>Verdict</th></tr></thead><tbody>${rows}</tbody></table></div></div></section>`;
}
function renderFooter() {
  const trip = state.site.trip || {};
  return `<footer class="site-footer"><div class="site-footer__inner">
    <div class="site-footer__brand">Jibhi–Shoja</div><p class="site-footer__tag">${esc(trip.dates || '')}</p>
    <ul class="footmenu"><li><a href="#top-picks">Top picks</a></li><li><a href="#stays">Stays</a></li><li><a href="#places">Places</a></li><li><a href="#plan">Plan</a></li><li><a href="#travel">Travel</a></li><li><a href="#budget">Budget</a></li></ul>
    <p class="site-footer__disclaimer">${esc(state.site.disclaimer)}</p><p class="site-footer__photos">${esc(state.site.photo_note)}</p>
    <div class="site-footer__meta"><span>${esc(trip.travelers)}</span><span>${esc(trip.stay_cap)}</span><span>${esc(trip.budget_cap)}</span></div>
    <div class="site-footer__bottom">${state.stays.length} stays · ${state.places.length} places · data baseline Sep-2025–Aug-2026</div></div></footer>`;
}
function renderApp() {
  $('#app').innerHTML = renderStats() + renderTopPicks() + renderStays() + renderPlaces() + renderPlan() + renderQuoteBand() + renderTravel() + renderBudget() + renderFooter();
  const trip = state.site.trip || {};
  $$('[data-hero-dates]').forEach(el => { el.textContent = trip.dates || 'Oct 4–8'; });
  $$('[data-hero-cap]').forEach(el => { el.textContent = trip.budget_cap || '₹20–25k'; });
  const menuMeta = $('[data-menu-meta]'); if (menuMeta) menuMeta.textContent = `${trip.travelers || ''} · ${trip.stay_cap || ''}`;
  renderStayGrid();
}
function initNavigation() {
  const burger = $('#burger'), menu = $('#menu'), menuClose = $('#menuClose');
  if (!burger || !menu || !menuClose) return;
  const openMenu = () => { menu.classList.add('is-open'); burger.classList.add('is-open'); burger.setAttribute('aria-expanded', 'true'); menu.setAttribute('aria-hidden', 'false'); document.body.classList.add('menu-open'); };
  const closeMenu = () => { menu.classList.remove('is-open'); burger.classList.remove('is-open'); burger.setAttribute('aria-expanded', 'false'); menu.setAttribute('aria-hidden', 'true'); document.body.classList.remove('menu-open'); };
  burger.addEventListener('click', () => menu.classList.contains('is-open') ? closeMenu() : openMenu());
  menuClose.addEventListener('click', closeMenu);
  $$('.menu__link,.menu__cta a', menu).forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && !$('#stayModal')?.classList.contains('is-open')) closeMenu(); });
}

function initHero() {
  const slides = $$('.hero__slide'), dots = $$('.hero__dot');
  if (!slides.length || !dots.length) return;
  let current = 0, timer;
  const go = index => { slides[current].classList.remove('is-active'); dots[current].classList.remove('is-active'); current = (index + slides.length) % slides.length; slides[current].classList.add('is-active'); dots[current].classList.add('is-active'); };
  const start = () => { timer = window.setInterval(() => go(current + 1), 5500); };
  dots.forEach((dot, index) => dot.addEventListener('click', () => { go(index); window.clearInterval(timer); start(); }));
  start();
}

function initCarousels() {
  $$('.caro').forEach(wrapper => {
    const track = $('.swipe', wrapper); if (!track) return;
    const amount = () => { const card = $('.bcard', track); return card ? card.offsetWidth + 18 : 320; };
    $('.caro__prev', wrapper)?.addEventListener('click', () => track.scrollBy({left: -amount(), behavior: 'smooth'}));
    $('.caro__next', wrapper)?.addEventListener('click', () => track.scrollBy({left: amount(), behavior: 'smooth'}));
  });
}

function initCounters() {
  const nums = $$('.stat__num'); if (!nums.length) return;
  const animate = el => {
    const target = Number(el.dataset.count || 0), suffix = el.dataset.suffix || '', prefix = el.dataset.prefix || '', duration = 1500, start = performance.now();
    const tick = now => { const progress = Math.min((now - start) / duration, 1), eased = 1 - Math.pow(1 - progress, 3); el.textContent = `${prefix}${Math.round(target * eased).toLocaleString('en-IN')}${suffix}`; if (progress < 1) requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
  };
  if (!('IntersectionObserver' in window)) { nums.forEach(animate); return; }
  const observer = new IntersectionObserver(entries => entries.forEach(entry => { if (!entry.isIntersecting) return; animate(entry.target); observer.unobserve(entry.target); }), {threshold: .45});
  nums.forEach(el => observer.observe(el));
}

function setText(root, role, value) { const node = $(`[data-role="${role}"]`, root); if (node) node.textContent = value ?? ''; }
function updateModalPhoto() {
  const stay = state.modalStay, modal = $('#stayModal'); if (!stay || !modal) return;
  const image = $('[data-role="photo"]', modal), caption = $('[data-role="photo-caption"]', modal);
  state.modalPhoto = (state.modalPhoto + stay.photos.length) % stay.photos.length;
  image.src = imgPath(stay.photos[state.modalPhoto]);
  image.alt = `${stay.name} — photo ${state.modalPhoto + 1} of ${stay.photos.length}`;
  caption.textContent = `${state.modalPhoto + 1}/${stay.photos.length} · ${state.site.photo_note}`;
  $$('.stay-detail__dot', modal).forEach((dot, index) => dot.classList.toggle('is-on', index === state.modalPhoto));
}

function populateStayModal(stay) {
  const template = $('#stay-template'), host = $('#stay-detail-content');
  host.replaceChildren(template.content.cloneNode(true));
  const root = host;
  setText(root, 'area', stay.area); setText(root, 'kind', stay.kind); setText(root, 'name', stay.name); setText(root, 'type', stay.type); setText(root, 'spec-type', stay.type);
  setText(root, 'location', stay.location); setText(root, 'rating', stay.rating); setText(root, 'cleanliness', stay.cleanliness); setText(root, 'view', stay.view); setText(root, 'amenities', stay.amenities);
  setText(root, 'price-base', money(stay.price_base)); setText(root, 'price-allin', money(stay.price_allin)); setText(root, 'total4', money(stay.total4)); setText(root, 'total5', money(stay.total5)); setText(root, 'why', stay.why);
  const flag = $('[data-role="flag"]', root); flag.hidden = !stay.flag_over_cap;
  const primary = $('[data-role="booking-primary"]', root); primary.href = stay.booking_primary;
  const hub = $('[data-role="booking-hub"]', root); hub.href = stay.booking_hub.url; hub.textContent = stay.booking_hub.label;
  $('[data-role="photo-dots"]', root).innerHTML = stay.photos.map((photo, index) => `<button class="stay-detail__dot" type="button" aria-label="Photo ${index + 1}" data-photo-index="${index}"></button>`).join('');
  $('[data-photo-prev]', root).addEventListener('click', () => { state.modalPhoto -= 1; updateModalPhoto(); });
  $('[data-photo-next]', root).addEventListener('click', () => { state.modalPhoto += 1; updateModalPhoto(); });
  $$('[data-photo-index]', root).forEach(dot => dot.addEventListener('click', () => { state.modalPhoto = Number(dot.dataset.photoIndex); updateModalPhoto(); }));
}

function openStay(stay, direct = false) {
  const modal = $('#stayModal'); if (!modal) return;
  state.modalStay = stay; state.modalPhoto = 0; state.modalOpenedDirectly = direct;
  populateStayModal(stay); updateModalPhoto();
  modal.hidden = false; document.body.classList.add('modal-open');
  requestAnimationFrame(() => modal.classList.add('is-open'));
  $('.stay-modal__dialog').scrollTop = 0;
  window.setTimeout(() => $('.stay-modal__close')?.focus({preventScroll: true}), 80);
}
function closeStay() {
  const modal = $('#stayModal'); if (!modal || modal.hidden) return;
  modal.classList.remove('is-open'); document.body.classList.remove('modal-open'); state.modalStay = null;
  window.setTimeout(() => { modal.hidden = true; $('#stay-detail-content').replaceChildren(); }, 220);
}
function requestCloseStay() {
  if (!state.modalOpenedDirectly && history.length > 1) { history.back(); return; }
  history.replaceState(null, '', `${location.pathname}${location.search}#stays`); closeStay();
}
function routeHash(direct = false) {
  const match = location.hash.match(/^#stay\/([a-z0-9-]+)$/i);
  if (!match) { closeStay(); return; }
  const stay = state.stays.find(item => item.slug === match[1]);
  if (stay) openStay(stay, direct); else { history.replaceState(null, '', `${location.pathname}${location.search}#stays`); closeStay(); }
}
function initModal() {
  document.addEventListener('click', event => {
    const closer = event.target.closest('[data-close-modal]'); if (!closer) return;
    event.preventDefault(); requestCloseStay();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && state.modalStay) requestCloseStay();
    if (event.key !== 'Tab' || !state.modalStay) return;
    const dialog = $('.stay-modal__dialog'), focusables = $$('a[href],button:not([disabled])', dialog).filter(el => el.offsetParent !== null);
    if (!focusables.length) return;
    const first = focusables[0], last = focusables[focusables.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  window.addEventListener('hashchange', () => routeHash(false));
}

function initStayControls() {
  $$('.vchip[data-filter]').forEach(chip => chip.addEventListener('click', () => {
    const key = chip.dataset.filter; state.filters[key] = chip.dataset.value;
    $$(`.vchip[data-filter="${key}"]`).forEach(item => item.classList.toggle('is-on', item === chip));
    renderStayGrid();
  }));
  $('#staySort')?.addEventListener('change', event => { state.filters.sort = event.target.value; renderStayGrid(); });
}




async function init() {
  initNavigation(); initHero(); initModal();
  try {
    await loadData();
    renderApp();
    initCarousels(); initCounters(); initStayControls();
    routeHash(/^#stay\//.test(location.hash));
  } catch (error) {
    $('#app').innerHTML = `<div class="loading" role="alert">Unable to load the trip data. Please serve this folder over a local web server.</div>`;
    console.error(error);
  }
}

init();
})();

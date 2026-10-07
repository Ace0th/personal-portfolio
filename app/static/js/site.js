(() => {
  const nav = document.getElementById('nav');
  const progress = document.getElementById('progress');
  const backTop = document.getElementById('back-top');
  const menu = document.getElementById('menu-toggle');
  const siteNav = document.getElementById('site-nav');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const year = document.getElementById('current-year');
  if (year) year.textContent = String(new Date().getFullYear());

  const updateScroll = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    progress.style.width = `${max > 0 ? scrollY / max * 100 : 0}%`;
    nav.classList.toggle('scrolled', scrollY > 24);
    backTop.classList.toggle('visible', scrollY > 600);
  };
  addEventListener('scroll', updateScroll, { passive: true }); updateScroll();

  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    siteNav.classList.toggle('open', open);
    menu.textContent = open ? '×' : '☰';
  });
  siteNav?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    siteNav.classList.remove('open'); menu?.setAttribute('aria-expanded', 'false'); if (menu) menu.textContent = '☰';
  }));

  const revealEls = document.querySelectorAll('.reveal');
  if (reduced || !('IntersectionObserver' in window)) revealEls.forEach(el => el.classList.add('shown'));
  else {
    const revealObserver = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('shown'); revealObserver.unobserve(entry.target); }
    }), { threshold: .12 });
    revealEls.forEach((el, i) => { el.style.setProperty('--delay', `${(i % 4) * 70}ms`); revealObserver.observe(el); });
  }

  const sections = [...document.querySelectorAll('main section[id]')];
  const sectionObserver = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) document.querySelectorAll('.nav-link').forEach(link => link.classList.toggle('active', link.hash === `#${entry.target.id}`));
  }), { rootMargin: '-35% 0px -55% 0px' });
  sections.forEach(section => sectionObserver.observe(section));

  const cards = [...document.querySelectorAll('.project-card')];
  document.querySelectorAll('.filter-btn').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(item => item.classList.toggle('selected', item === button));
    const category = button.dataset.filter;
    cards.forEach((card, i) => {
      const show = category === 'All' || card.dataset.category === category;
      card.classList.toggle('filtered-out', !show);
      if (show) { card.style.setProperty('--delay', `${Math.min(i, 4) * 55}ms`); card.classList.remove('shown'); requestAnimationFrame(() => card.classList.add('shown')); }
    });
  }));

  const dialog = document.getElementById('project-dialog');
  cards.forEach(card => card.querySelector('.details-btn')?.addEventListener('click', () => {
    const p = JSON.parse(card.dataset.project);
    document.getElementById('dialog-title').textContent = p.title;
    document.getElementById('dialog-description').textContent = p.description;
    document.getElementById('dialog-category').textContent = `PROJECT / ${p.category}`;
    const tech = document.getElementById('dialog-tech'); tech.replaceChildren(...p.technologies.map(t => { const span = document.createElement('span'); span.textContent = t; return span; }));
    const links = document.getElementById('dialog-links'); links.replaceChildren();
    [[p.github, 'GitHub ↗'], [p.live, 'Live demo ↗']].filter(x => x[0]).forEach(([href, label]) => { const a = document.createElement('a'); a.href = href; a.target = '_blank'; a.rel = 'noreferrer'; a.textContent = label; links.append(a); });
    dialog.showModal();
  }));
  document.querySelector('.dialog-close')?.addEventListener('click', () => dialog.close());
  dialog?.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });

  document.querySelector('[data-contact-form]')?.addEventListener('submit', event => {
    event.preventDefault();
    const form = event.currentTarget;
    const values = new FormData(form);
    const body = [
      `Name: ${values.get('name')}`,
      `Email: ${values.get('email')}`,
      '',
      String(values.get('message') || '')
    ].join('\n');
    const subject = encodeURIComponent(String(values.get('subject') || 'Portfolio contact'));
    window.location.href = `mailto:theofficialalamin@gmail.com?subject=${subject}&body=${encodeURIComponent(body)}`;
  });
})();

/* Content and downloads also work without JavaScript. */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const menuButton = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.main-nav');
  const mobile = window.matchMedia('(max-width: 760px)');
  const closeMenu = (restoreFocus = false) => {
    nav.classList.remove('is-open');
    menuButton.setAttribute('aria-expanded', 'false');
    if (restoreFocus) menuButton.focus();
  };
  menuButton.addEventListener('click', () => {
    const opening = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(opening));
    nav.classList.toggle('is-open', opening);
  });
  nav.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeMenu();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') closeMenu(true);
  });
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.header-inner')) closeMenu();
  });
  if (mobile.addEventListener) mobile.addEventListener('change', () => closeMenu());

  if ('IntersectionObserver' in window) {
    const sections = [...document.querySelectorAll('main > section[id]')].filter((section) => section.id !== 'home');
    const links = [...nav.querySelectorAll('a[href^="#"]')];
    const updateActiveSection = () => {
      const visible = sections.filter((section) => section.getBoundingClientRect().top <= window.innerHeight * 0.4);
      const target = visible[visible.length - 1];
      links.forEach((link) => {
        if (target && link.hash === '#' + target.id) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    };
    const observer = new IntersectionObserver(updateActiveSection, {rootMargin: '-15% 0px -55% 0px', threshold: 0});
    sections.forEach((section) => observer.observe(section));
    window.addEventListener('hashchange', updateActiveSection);
    updateActiveSection();
  }

  const copyButton = document.querySelector('.copy-email');
  const copyStatus = document.querySelector('.copy-status');
  if (navigator.clipboard && window.isSecureContext) {
    copyButton.hidden = false;
    copyButton.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(copyButton.dataset.email);
        copyStatus.textContent = 'Email address copied.';
      } catch {
        copyStatus.textContent = 'Please use the email link above to get in touch.';
      }
    });
  }

  const dialog = document.querySelector('.image-dialog');
  if (typeof dialog.showModal === 'function') {
    const dialogImage = dialog.querySelector('img');
    const caption = dialog.querySelector('p');
    const closeButton = dialog.querySelector('.dialog-close');
    let previousFocus = null;
    document.querySelectorAll('[data-lightbox]').forEach((link) => {
      link.addEventListener('click', (event) => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        previousFocus = link;
        const sourceImage = link.querySelector('img');
        dialogImage.src = link.href;
        dialogImage.alt = sourceImage?.alt || link.dataset.caption;
        dialogImage.removeAttribute('width');
        dialogImage.removeAttribute('height');
        caption.textContent = link.dataset.caption;
        dialog.showModal();
        document.body.classList.add('has-dialog');
        closeButton.focus();
      });
    });
    closeButton.addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', (event) => {
      const box = dialog.getBoundingClientRect();
      if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
    });
    dialog.addEventListener('close', () => {
      document.body.classList.remove('has-dialog');
      if (previousFocus?.isConnected) previousFocus.focus();
    });
  }
  document.querySelector('.hero-copy').classList.add('animate-in');
  document.querySelector('.hero-build').classList.add('animate-in');
})();

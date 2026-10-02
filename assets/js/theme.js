(() => {
  const key = 'sanctum-theme';
  const modes = ['system', 'light', 'dark'];
  const labels = { system: '系统', light: '浅色', dark: '深色' };
  let mode = 'system';
  try {
    const saved = localStorage.getItem(key);
    if (modes.includes(saved)) mode = saved;
  } catch (_) { /* Storage is optional. */ }

  function apply() {
    if (mode === 'system') document.documentElement.removeAttribute('data-theme');
    else document.documentElement.dataset.theme = mode;
    const button = document.getElementById('theme-toggle');
    if (button) {
      button.textContent = `配色 · ${labels[mode]}`;
      button.setAttribute('aria-label', `切换配色，当前${labels[mode]}`);
    }
  }
  apply();
  document.addEventListener('DOMContentLoaded', () => {
    const button = document.getElementById('theme-toggle');
    if (!button) return;
    button.hidden = false;
    apply();
    button.addEventListener('click', () => {
      mode = modes[(modes.indexOf(mode) + 1) % modes.length];
      try { localStorage.setItem(key, mode); } catch (_) { /* Keep session preference. */ }
      apply();
    });
  });
})();

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('refresh');
  btn.addEventListener('click', fetchCookies);
  fetchCookies();
});

async function fetchCookies() {
  const list = document.getElementById('list');
  const state = document.getElementById('state');
  const count = document.getElementById('count');
  const dot = document.getElementById('dot');
  const btn = document.getElementById('refresh');

  btn.classList.add('loading');
  state.textContent = 'Loading...';
  dot.className = 'dot yellow';
  count.textContent = '';

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.url) {
      showEmpty(list, 'No active tab');
      state.textContent = 'No active tab';
      dot.className = 'dot red';
      return;
    }

    const resp = await chrome.runtime.sendMessage({ cmd: 'cookies', url: tab.url });
    if (!resp?.ok) {
      showEmpty(list, 'Error: ' + (resp?.error || 'unknown'));
      state.textContent = 'Error';
      dot.className = 'dot red';
      return;
    }

    const cookies = resp.data;
    if (!cookies.length) {
      showEmpty(list, 'No cookies');
      state.textContent = 'No cookies';
      dot.className = 'dot green';
      count.textContent = '<b>0</b> cookies';
      return;
    }

    renderCookies(list, cookies);
    count.innerHTML = `<b>${cookies.length}</b> cookie${cookies.length === 1 ? '' : 's'}`;

    // auto copy to clipboard
    const str = cookies.map(c => `${c.name}=${c.value}`).join('; ');
    await navigator.clipboard.writeText(str);
    state.textContent = 'Copied to clipboard';
    dot.className = 'dot green';

  } catch (e) {
    showEmpty(list, 'Error: ' + e.message);
    state.textContent = 'Error';
    dot.className = 'dot red';
  } finally {
    btn.classList.remove('loading');
  }
}

function renderCookies(container, cookies) {
  container.innerHTML = cookies.map(c => {
    const badges = [
      c.httpOnly ? '<span class="badge badge-h">HTTP</span>' : '',
      c.secure ? '<span class="badge badge-s">SEC</span>' : '',
      c.partitionKey ? '<span class="badge badge-p">P</span>' : '',
    ].filter(Boolean).join('');

    const escapedValue = escapeHtml(c.value.length > 80 ? c.value.slice(0, 80) + '...' : c.value);

    return `<div class="row" data-cookie="${escapeAttr(c.name)}=${escapeAttr(c.value)}">
      <div class="row-inner">
        <div class="row-name">${escapeHtml(c.name)} ${badges}</div>
        <div class="row-value">${escapedValue}</div>
      </div>
      <button class="copy-btn" title="Copy this cookie" onclick="copyRow(this)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
      </button>
    </div>`;
  }).join('');
}

function showEmpty(container, text) {
  container.innerHTML = `<div class="empty"><div class="empty-icon">~</div><div class="empty-text">${escapeHtml(text)}</div></div>`;
}

window.copyRow = function(btn) {
  const row = btn.closest('.row');
  const text = row.dataset.cookie;
  navigator.clipboard.writeText(text).then(() => {
    btn.classList.add('copied');
    setTimeout(() => btn.classList.remove('copied'), 1200);
  });
};

function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function escapeAttr(s) {
  return s.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

let lastTitle = '';

function gatherVideoInfo() {
  const title = document.title || '';
  const descTag = document.querySelector('meta[name="description"]');
  const description = descTag ? descTag.getAttribute('content') : '';
  const url = location.href || '';

  if (title !== lastTitle) {
    lastTitle = title;
    chrome.runtime.sendMessage({ type: 'videoInfo', url, title, description });
  }
}

// Poll for title/description changes (covers YouTube SPA navigation reliably)
setInterval(gatherVideoInfo, 1500);
// One immediate send
gatherVideoInfo();

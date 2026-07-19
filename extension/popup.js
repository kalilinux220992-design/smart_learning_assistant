async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function loadSelection() {
  const statusEl = document.getElementById('status');
  const categoryEl = document.getElementById('category');

  try {
    const tab = await getActiveTab();
    const key = tab?.id ? `category-${tab.id}` : 'default-category';
    const { [key]: savedCategory = 'entertainment' } = await chrome.storage.local.get([key]);
    categoryEl.value = savedCategory;
    statusEl.textContent = `Current selection: ${savedCategory}`;
  } catch (error) {
    console.error('Unable to load category selection', error);
    statusEl.textContent = 'No category saved yet';
  }
}

async function saveSelection() {
  const tab = await getActiveTab();
  const category = document.getElementById('category').value;
  const key = tab?.id ? `category-${tab.id}` : 'default-category';
  await chrome.storage.local.set({ [key]: category });

  if (tab?.id) {
    await chrome.runtime.sendMessage({ type: 'manualCategory', tabId: tab.id, category });
  }

  alert(`Saved category: ${category}`);
}

document.getElementById('save').addEventListener('click', saveSelection);
document.getElementById('refresh').addEventListener('click', async () => {
  const tab = await getActiveTab();
  const key = tab?.id ? `category-${tab.id}` : 'default-category';
  const { [key]: savedCategory = 'entertainment' } = await chrome.storage.local.get([key]);
  alert(`Current page category: ${savedCategory}`);
});

document.addEventListener('DOMContentLoaded', () => {
  loadSelection();
});

chrome.tabs.onActivated.addListener(() => {
  loadSelection();
});

chrome.tabs.onUpdated.addListener(() => {
  loadSelection();
});

chrome.windows.onFocusChanged.addListener(() => {
  loadSelection();
});

const CATEGORY_RULES = [
  { name: 'coding', hosts: ['github.com', 'gitlab.com', 'stackoverflow.com', 'stackexchange.com', 'codepen.io', 'replit.com', 'leetcode.com', 'hackerrank.com', 'geeksforgeeks.org', 'w3schools.com', 'developer.mozilla.org'] },
  { name: 'news', hosts: ['news.ycombinator.com', 'bbc.com', 'cnn.com', 'reuters.com', 'ndtv.com', 'timesofindia.indiatimes.com', 'thehindu.com'] },
  { name: 'lectures', hosts: ['youtube.com', 'youtu.be', 'edx.org', 'coursera.org', 'khanacademy.org', 'mit.edu', 'nptel.ac.in'] },
  { name: 'entertainment', hosts: ['youtube.com', 'youtu.be', 'netflix.com', 'primevideo.com', 'hotstar.com', 'disneyplus.com', 'twitch.tv'] }
];

const SERVER_URLS = [
  'http://127.0.0.1:8000',
  'http://localhost:8000',
  'http://127.0.0.1:9000',
  'http://localhost:9000',
];
const HEARTBEAT_ALARM = 'watch-stats-heartbeat';
const HEARTBEAT_SECONDS = 30;
const state = {
  activeTabId: null,
  activeUrl: null,
  startTime: null,
  category: 'other',
  lastSentAt: 0,
  lastResetToken: null,
};

function classifyUrl(url) {
  if (!url) return 'other';
  try {
    const hostname = new URL(url).hostname.replace('www.', '');
    for (const rule of CATEGORY_RULES) {
      if (rule.hosts.some((host) => hostname === host || hostname.endsWith(`.${host}`))) {
        if (rule.name === 'lectures' && hostname.includes('youtube.com')) return 'lectures';
        if (rule.name === 'news' && hostname.includes('youtube.com')) return 'news';
        return rule.name;
      }
    }
  } catch (error) {
    console.error('Unable to classify URL', error);
  }
  return 'other';
}

function classifyByText(text, url) {
  if (!text) return classifyUrl(url);
  const s = text.toLowerCase();

  // Coding and programming indicators
  const codingKeywords = ['coding', 'programming', 'developer', 'javascript', 'python', 'java', 'html', 'css', 'algorithm', 'leetcode', 'debugging', 'software engineering'];
  for (const kw of codingKeywords) if (s.includes(kw)) return 'coding';

  // Strong indicators for lectures/tutorials
  const lectureKeywords = ['lecture', 'tutorial', 'course', 'class', 'lesson', 'homework', 'nptel', 'coursera', 'edx', 'khanacademy', 'lecture series'];
  for (const kw of lectureKeywords) if (s.includes(kw)) return 'lectures';

  // News indicators
  const newsKeywords = ['breaking', 'news', 'headline', 'report', 'bulletin', 'live', 'cnn', 'bbc', 'reuters', 'ndtv', 'the hindu', 'times of india'];
  for (const kw of newsKeywords) if (s.includes(kw)) return 'news';

  // Entertainment indicators
  const entertainmentKeywords = ['trailer', 'episode', 'movie', 'music', 'funny', 'comedy', 'standup', 'clip', 'vlog', 'song'];
  for (const kw of entertainmentKeywords) if (s.includes(kw)) return 'entertainment';

  return classifyUrl(url);
}

async function updateBadge(text) {
  try {
    await chrome.action.setBadgeText({ text });
  } catch (error) {
    console.error('Unable to set badge', error);
  }
}

async function savePending(payload) {
  const { pendingPayloads = [] } = await chrome.storage.local.get(['pendingPayloads']);
  pendingPayloads.push(payload);
  await chrome.storage.local.set({ pendingPayloads });
}

async function flushPending() {
  const { pendingPayloads = [] } = await chrome.storage.local.get(['pendingPayloads']);
  if (!pendingPayloads.length) return;

  const remaining = [];
  for (const payload of pendingPayloads) {
    const sent = await sendPayload(payload);
    if (!sent) remaining.push(payload);
  }

  if (remaining.length) {
    await chrome.storage.local.set({ pendingPayloads: remaining });
  } else {
    await chrome.storage.local.remove('pendingPayloads');
  }
}

async function sendPayload(payload) {
  for (const baseUrl of SERVER_URLS) {
    try {
      const response = await fetch(`${baseUrl}/api/watch-stats/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        return true;
      }
    } catch (error) {
      console.error('Failed to send stats to', baseUrl, error);
    }
  }

  return false;
}

async function checkForStatsReset() {
  for (const baseUrl of SERVER_URLS) {
    try {
      const response = await fetch(`${baseUrl}/api/watch-stats/reset-token/`);
      if (!response.ok) continue;
      const { reset_token: resetToken } = await response.json();
      if (resetToken && resetToken !== state.lastResetToken) {
        state.lastResetToken = resetToken;
        state.startTime = Date.now();
        state.lastSentAt = 0;
        await updateBadge('');
      }
      return;
    } catch (error) {
      console.error('Unable to check watch-stat reset', error);
    }
  }
}

async function sendStats() {
  const now = Date.now();
  if (!state.startTime || now - state.lastSentAt < 10000) return;

  const durationSeconds = Math.floor((now - state.startTime) / 1000);
  if (durationSeconds <= 0) return;

  const payload = {
    total_seconds: durationSeconds,
    categories: {
      [state.category]: durationSeconds,
    },
  };

  const sent = await sendPayload(payload);
  if (!sent) {
    await savePending(payload);
    await updateBadge('!');
  } else {
    await updateBadge('✓');
  }

  state.lastSentAt = now;
  state.startTime = now;
}

async function recordHeartbeat() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.url) return;

  const category = await resolveCategory(tab.url, tab.id);
  const payload = {
    total_seconds: HEARTBEAT_SECONDS,
    categories: { [category]: HEARTBEAT_SECONDS },
  };
  const sent = await sendPayload(payload);
  if (!sent) {
    await savePending(payload);
    await updateBadge('!');
  } else {
    await updateBadge('✓');
  }
  state.lastSentAt = Date.now();
  state.startTime = state.lastSentAt;
}

function scheduleHeartbeat() {
  chrome.alarms.create(HEARTBEAT_ALARM, { periodInMinutes: 0.5 });
}

async function getManualCategory(tabId) {
  const key = tabId ? `category-${tabId}` : 'default-category';
  const { [key]: savedCategory } = await chrome.storage.local.get([key]);
  return savedCategory || null;
}

async function resolveCategory(url, tabId) {
  const manualCategory = tabId ? await getManualCategory(tabId) : null;
  if (manualCategory) return manualCategory;
  return classifyUrl(url);
}

async function updateActiveTab(tab) {
  if (!tab?.url) return;
  const nextCategory = await resolveCategory(tab.url, tab.id);
  if (state.activeTabId !== tab.id || state.category !== nextCategory) {
    await sendStats();
    state.activeTabId = tab.id;
    state.activeUrl = tab.url;
    state.category = nextCategory;
    state.startTime = Date.now();
  }
}

// Listen for messages from content script with video title/description
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg && msg.type === 'videoInfo') {
    const text = `${msg.title || ''} ${msg.description || ''}`;

    (async () => {
      const manualCategory = await getManualCategory(state.activeTabId);
      const effectiveCategory = manualCategory || classifyByText(text, msg.url);

      // If category changed, flush previous stat and start new bucket
      if (state.category !== effectiveCategory) {
        await sendStats();
        state.category = effectiveCategory;
        state.startTime = Date.now();
        state.activeUrl = msg.url;
      }
      sendResponse({ status: 'ok', category: effectiveCategory });
    })();

    return true; // keep message channel open for async response
  }

  if (msg && msg.type === 'manualCategory') {
    (async () => {
      const key = msg.tabId ? `category-${msg.tabId}` : 'default-category';
      await chrome.storage.local.set({ [key]: msg.category });

      if (state.activeTabId === msg.tabId) {
        await sendStats();
        state.category = msg.category;
        state.startTime = Date.now();
      }
      sendResponse({ status: 'ok' });
    })();

    return true;
  }
});

chrome.runtime.onInstalled.addListener(async () => {
  scheduleHeartbeat();
  await flushPending();
  await checkForStatsReset();
});

chrome.runtime.onStartup.addListener(() => {
  scheduleHeartbeat();
});

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== HEARTBEAT_ALARM) return;
  await checkForStatsReset();
  await recordHeartbeat();
});

chrome.tabs.onActivated.addListener(async ({ tabId }) => {
  const tab = await chrome.tabs.get(tabId);
  await updateActiveTab(tab);
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url || changeInfo.status === 'complete') {
    updateActiveTab(tab);
  }
});

chrome.tabs.onRemoved.addListener(async (tabId) => {
  if (state.activeTabId === tabId) {
    await sendStats();
    state.activeTabId = null;
    state.activeUrl = null;
    state.category = 'other';
    state.startTime = Date.now();
  }
});

chrome.windows.onFocusChanged.addListener(async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  await updateActiveTab(tab);
});

setInterval(() => {
  checkForStatsReset();
}, 5000);

setInterval(async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab) {
    await updateActiveTab(tab);
  }
}, 5000);

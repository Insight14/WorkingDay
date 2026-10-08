import { renderReviewOverlay } from './overlay';
import { fillResumeData } from './filler';

// Listen for messages from extension popup or background
chrome.runtime?.onMessage?.addListener((message, _sender, sendResponse) => {
  if (message.action === 'SHOW_REVIEW_OVERLAY') {
    renderReviewOverlay(message.data);
    sendResponse({ success: true });
  } else if (message.action === 'DIRECT_FILL') {
    fillResumeData(message.data).then(res => {
      sendResponse({ success: true, result: res });
    });
    return true; // async response
  }
});

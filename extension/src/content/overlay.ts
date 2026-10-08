import { fillResumeData } from './filler';

let currentOverlay: HTMLElement | null = null;

export function renderReviewOverlay(data: any): void {
  if (currentOverlay) {
    currentOverlay.remove();
    currentOverlay = null;
  }

  const container = document.createElement('div');
  container.id = 'workingday-review-overlay';
  container.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    width: 380px;
    max-height: 85vh;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2), 0 1px 3px rgba(0,0,0,0.1);
    border: 1px solid #e0e0e0;
    z-index: 999999;
    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #2d3139;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: fadeIn 0.2s ease-out;
  `;

  let selectedCandidateIdx = 0;

  const updateContent = () => {
    const candidate = data.name?.candidate_parses?.[selectedCandidateIdx] || {
      given: data.name?.given?.value || '',
      family: data.name?.family?.value || '',
      middle: data.name?.middle?.value || null
    };

    container.innerHTML = `
      <style>
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        .wd-badge { font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; }
        .wd-badge-green { background: #e6f4ea; color: #137333; }
        .wd-badge-amber { background: #fef7e0; color: #b06000; }
        .wd-badge-gray { background: #f1f3f4; color: #5f6368; }
        .wd-field-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #f1f3f4; font-size: 13px; }
        .wd-field-label { color: #5f6368; font-weight: 500; }
        .wd-field-val { font-weight: 500; text-align: right; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      </style>

      <!-- Header -->
      <div style="background: #0051a8; color: white; padding: 14px 18px; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <div style="width: 22px; height: 22px; background: white; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #0051a8; font-weight: 900; font-size: 14px;">W</div>
          <span style="font-weight: 700; font-size: 15px;">WorkingDay Review</span>
        </div>
        <button id="wd-close-btn" style="background: none; border: none; color: white; cursor: pointer; font-size: 18px; line-height: 1;">&times;</button>
      </div>

      <!-- Body -->
      <div style="padding: 16px 18px; overflow-y: auto; flex: 1;">
        <div style="font-size: 12px; color: #5f6368; margin-bottom: 12px;">
          Review parsed values below. Low confidence or empty resume fields are marked for transparency.
        </div>

        <!-- Candidate Name Switcher -->
        <div style="background: #f8f9fa; border: 1px solid #e8eaed; border-radius: 8px; padding: 10px; margin-bottom: 14px;">
          <div style="font-size: 11px; font-weight: 700; color: #3c4043; text-transform: uppercase; margin-bottom: 6px;">Name Parsing Format</div>
          ${(data.name?.candidate_parses || []).map((cand: any, idx: number) => `
            <label style="display: flex; align-items: center; gap: 6px; font-size: 12px; margin-bottom: 4px; cursor: pointer;">
              <input type="radio" name="wd_cand_name" value="${idx}" ${idx === selectedCandidateIdx ? 'checked' : ''} />
              <span>${cand.given} <strong>${cand.family}</strong> ${cand.middle ? `(Mid: ${cand.middle})` : ''}</span>
            </label>
          `).join('') || `<div>${data.name?.given?.value} ${data.name?.family?.value}</div>`}
        </div>

        <!-- Summary fields -->
        <div class="wd-field-row">
          <span class="wd-field-label">First Name</span>
          <span class="wd-field-val">${candidate.given}</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">Last Name</span>
          <span class="wd-field-val">${candidate.family}</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">Address Line 1</span>
          <span class="wd-field-val">${data.address?.line1?.value || '<em style="color:#80868b">None (Resume Empty)</em>'}</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">City, State</span>
          <span class="wd-field-val">${data.address?.city?.value || ''}, ${data.address?.state?.value || ''}</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">Education</span>
          <span class="wd-field-val">${data.education?.[0]?.school?.value || 'N/A'}</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">Degree</span>
          <span class="wd-field-val">${data.education?.[0]?.degree?.value || 'N/A'} in ${data.education?.[0]?.field?.value || ''}</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">Experience</span>
          <span class="wd-field-val">${data.experience?.length || 0} positions</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">LinkedIn</span>
          <span class="wd-field-val">${data.links?.linkedin?.value ? 'Extracted' : 'None'}</span>
        </div>
      </div>

      <!-- Footer Buttons -->
      <div style="padding: 12px 18px; border-top: 1px solid #e0e0e0; background: #fafafa; display: flex; flex-direction: column; gap: 8px;">
        <button id="wd-fill-btn" style="background: #0051a8; color: white; border: none; padding: 10px; border-radius: 20px; font-weight: 600; font-size: 14px; cursor: pointer;">
          Autofill Form
        </button>
        <div style="font-size: 11px; text-align: center; color: #5f6368;">
          Never auto-submits &bull; User approval required
        </div>
      </div>
    `;

    // Bind event handlers
    const closeBtn = container.querySelector('#wd-close-btn');
    closeBtn?.addEventListener('click', () => {
      container.remove();
      currentOverlay = null;
    });

    const radios = container.querySelectorAll<HTMLInputElement>('input[name="wd_cand_name"]');
    radios.forEach(r => {
      r.addEventListener('change', (e) => {
        selectedCandidateIdx = parseInt((e.target as HTMLInputElement).value, 10);
        const chosen = data.name.candidate_parses[selectedCandidateIdx];
        data.name.given.value = chosen.given;
        data.name.family.value = chosen.family;
        data.name.middle.value = chosen.middle;
        updateContent();
      });
    });

    const fillBtn = container.querySelector<HTMLButtonElement>('#wd-fill-btn');
    fillBtn?.addEventListener('click', async () => {
      if (fillBtn) {
        fillBtn.textContent = "Autofilling...";
        fillBtn.disabled = true;
      }
      const res = await fillResumeData(data);
      if (fillBtn) {
        fillBtn.textContent = `Done! (${res.filled} filled, ${res.highlighted} flagged)`;
        fillBtn.style.background = "#1e8e3e";
      }
      setTimeout(() => {
        container.remove();
        currentOverlay = null;
      }, 2500);
    });
  };

  updateContent();
  document.body.appendChild(container);
  currentOverlay = container;
}

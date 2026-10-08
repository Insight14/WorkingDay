const ye={"The University of Texas at Dallas":["ut dallas","utd","u.t. dallas","texas at dallas"],"The University of Texas at Austin":["ut austin","utaustin","u.t. austin","texas at austin"],"Texas A&M University":["tamu","texas a and m","texas a&m"],"Massachusetts Institute of Technology":["mit"],"Stanford University":["stanford"],"University of California, Berkeley":["uc berkeley","ucb","cal berkeley","berkeley"],"Carnegie Mellon University":["cmu","carnegie mellon"],"Georgia Institute of Technology":["georgia tech","gatech"],"University of Illinois Urbana-Champaign":["uiuc","illinois urbana","university of illinois"],"University of Washington":["uw","u of w","u-dub"]};function K(e){return e.toLowerCase().replace(/[^a-z0-9\s]/g," ").replace(/\s+/g," ").trim()}function be(e,t){const i=e.length,n=t.length,o=Array.from({length:i+1},()=>Array(n+1).fill(0));for(let a=0;a<=i;a++)o[a][0]=a;for(let a=0;a<=n;a++)o[0][a]=a;for(let a=1;a<=i;a++)for(let s=1;s<=n;s++)e[a-1]===t[s-1]?o[a][s]=o[a-1][s-1]:o[a][s]=1+Math.min(o[a-1][s],o[a][s-1],o[a-1][s-1]);return o[i][n]}function ge(e,t){const i=K(e),n=K(t);if(!i&&!n)return 1;if(!i||!n)return 0;if(i===n)return 1;for(const[u,m]of Object.entries(ye)){const b=K(u),g=b===i||m.some(v=>K(v)===i),h=b===n||m.some(v=>K(v)===n);if(g&&h)return 1}const o=i.split(" ").sort().join(" "),a=n.split(" ").sort().join(" ");if(o===a)return 1;if(i.includes(n)||n.includes(i)){const u=Math.min(i.length,n.length),m=Math.max(i.length,n.length);return .85+.15*(u/m)}const s=Math.max(i.length,n.length),r=be(i,n);return Math.max(0,1-r/s)}function ue(e,t,i=.65){let n=-1,o=null,a="";for(const s of t){const r=s.textContent||"",u=ge(e,r);u>n&&(n=u,o=s,a=r)}return n>=i&&o?{option:o,text:a,score:n}:null}function l(e,t){var o;const i=e instanceof HTMLTextAreaElement?window.HTMLTextAreaElement.prototype:window.HTMLInputElement.prototype,n=(o=Object.getOwnPropertyDescriptor(i,"value"))==null?void 0:o.set;n?n.call(e,t):e.value=t,e.dispatchEvent(new Event("input",{bubbles:!0})),e.dispatchEvent(new Event("change",{bubbles:!0})),e.dispatchEvent(new Event("blur",{bubbles:!0}))}function he(e,t){e.checked!==t&&(e.checked=t,e.dispatchEvent(new Event("input",{bubbles:!0})),e.dispatchEvent(new Event("change",{bubbles:!0})),e.dispatchEvent(new Event("click",{bubbles:!0})))}function Z(e,t="Low confidence match - please verify"){e.style.outline="2px solid #f9ab00",e.style.backgroundColor="#fffde7",e.title=`WorkingDay Review: ${t}`}async function se(e,t,i=.65){if(!t)return!1;e.click();const n=await fe('[role="option"]',800);if(!n||n.length===0)return Z(e,`No options found for '${t}'`),!1;const o=ue(t,n,i);return o?(o.option.click(),!0):(Z(e,`Fuzzy match below threshold for '${t}'`),e.click(),!1)}async function re(e,t){if(!t)return!1;e.focus(),l(e,t);const i=new KeyboardEvent("keydown",{key:"Enter",code:"Enter",keyCode:13,which:13,bubbles:!0,cancelable:!0});e.dispatchEvent(i);const n=await fe('[role="option"]',400);if(n&&n.length>0){const o=ue(t,n,.6);if(o)return o.option.click(),!0}return!0}function fe(e,t=1e3){return new Promise(i=>{const n=Array.from(document.querySelectorAll(e));if(n.length>0){i(n);return}const o=new MutationObserver(()=>{const a=Array.from(document.querySelectorAll(e));a.length>0&&(o.disconnect(),i(a))});o.observe(document.body,{childList:!0,subtree:!0}),setTimeout(()=>{o.disconnect(),i(Array.from(document.querySelectorAll(e)))},t)})}async function pe(e){var k,I,E,q,A,_,N,T,$,C,L,M,z,D,R,j,U,F,O,B,H,W,P,Y,G,f,w,x,V,ee,te;let t=0,i=0;const n=document.querySelector('[data-automation-id="legalNameSection_firstName"], input#legalNameSection_firstName, input[name="firstName"]');n&&((I=(k=e.name)==null?void 0:k.given)!=null&&I.value)&&(l(n,e.name.given.value),t++,e.name.given.confidence<.85&&(Z(n,"Candidate name confidence < 85%"),i++));const o=document.querySelector('[data-automation-id="legalNameSection_lastName"], input#legalNameSection_lastName, input[name="lastName"]');o&&((q=(E=e.name)==null?void 0:E.family)!=null&&q.value)&&(l(o,e.name.family.value),t++,e.name.family.confidence<.85&&(Z(o,"Candidate name confidence < 85%"),i++));const a=document.querySelector('[data-automation-id="addressSection_addressLine1"], input#addressSection_addressLine1');a&&((_=(A=e.address)==null?void 0:A.line1)!=null&&_.value?(l(a,e.address.line1.value),t++):l(a,""));const s=document.querySelector('[data-automation-id="addressSection_addressLine2"], input#addressSection_addressLine2');s&&((T=(N=e.address)==null?void 0:N.line2)!=null&&T.value)&&(l(s,e.address.line2.value),t++);const r=document.querySelector('[data-automation-id="addressSection_city"], input#addressSection_city');r&&((C=($=e.address)==null?void 0:$.city)!=null&&C.value)&&(l(r,e.address.city.value),t++);const u=document.querySelector('[data-automation-id="addressSection_countryRegion"], button#addressSection_countryRegion');u&&((M=(L=e.address)==null?void 0:L.state)!=null&&M.value)&&(await se(u,e.address.state.value)?t++:i++);const m=document.querySelector('[data-automation-id="addressSection_postalCode"], input#addressSection_postalCode');m&&((D=(z=e.address)==null?void 0:z.postal)!=null&&D.value)&&(l(m,e.address.postal.value),t++);const b=document.querySelector('[data-automation-id="phone-number"], input#phone-number, input[type="tel"]');b&&((R=e.phone)!=null&&R.value)&&(l(b,e.phone.value),t++);const g=document.querySelector('[data-automation-id="email"], input#email, input[type="email"]');if(g&&((j=e.email)!=null&&j.value)&&(l(g,e.email.value),t++),e.experience&&e.experience.length>0){const p=document.querySelector('button:has(svg), button[data-automation-id="addExperience"], .btn-secondary'),J=Array.from(document.querySelectorAll(".repeatable-block"));for(let y=0;y<e.experience.length;y++){const d=e.experience[y];let c=J[y];if(!c&&p&&y>0&&(p.click(),await new Promise(X=>setTimeout(X,200)),c=Array.from(document.querySelectorAll(".repeatable-block"))[y]),c){const Q=c.querySelector('[data-automation-id="jobTitle"]');Q&&((U=d.title)!=null&&U.value)&&(l(Q,d.title.value),t++);const X=c.querySelector('[data-automation-id="companyName"]');X&&((F=d.company)!=null&&F.value)&&(l(X,d.company.value),t++);const ne=c.querySelector('[data-automation-id="location"]');ne&&((O=d.location)!=null&&O.value)&&(l(ne,d.location.value),t++);const ie=c.querySelector('[data-automation-id="currentlyWorkHere"]');ie&&((B=d.current)==null?void 0:B.value)!==void 0&&(he(ie,d.current.value),t++);const oe=c.querySelector('[data-automation-id="startDate"]');oe&&((H=d.start)!=null&&H.value)&&(l(oe,d.start.value),t++);const ae=c.querySelector('[data-automation-id="endDate"]');ae&&((W=d.end)!=null&&W.value)&&(l(ae,d.end.value),t++);const le=c.querySelector('[data-automation-id="jobDescription"]');if(le&&((P=d.bullets)!=null&&P.value)){const me=d.bullets.value.map(ve=>`• ${ve}`).join(`
`);l(le,me),t++}}}}if(e.education&&e.education.length>0){const p=e.education[0],J=document.querySelector('[data-automation-id="school"]');J&&((Y=p.school)!=null&&Y.value)&&(await re(J,p.school.value),t++);const y=document.querySelector('[data-automation-id="degree"]');y&&((G=p.degree)!=null&&G.value)&&(await se(y,p.degree.value)?t++:i++);const d=document.querySelector('[data-automation-id="fieldOfStudy"]');d&&((f=p.field)!=null&&f.value)&&(await re(d,p.field.value),t++);const c=document.querySelector('[data-automation-id="education_endDate"]');c&&((w=p.end)!=null&&w.value)&&(l(c,p.end.value),t++)}const h=document.querySelector('[data-automation-id="socialUrl_linkedIn"]');h&&((V=(x=e.links)==null?void 0:x.linkedin)!=null&&V.value)&&(l(h,e.links.linkedin.value),t++);const v=document.querySelector('[data-automation-id="websiteUrl"]');return v&&((te=(ee=e.links)==null?void 0:ee.github)!=null&&te.value)&&(l(v,e.links.github.value),t++),{filled:t,highlighted:i}}let S=null;function we(e){S&&(S.remove(),S=null);const t=document.createElement("div");t.id="workingday-review-overlay",t.style.cssText=`
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
  `;let i=0;const n=()=>{var u,m,b,g,h,v,k,I,E,q,A,_,N,T,$,C,L,M,z,D,R,j,U,F,O,B,H,W,P,Y,G;const o=((m=(u=e.name)==null?void 0:u.candidate_parses)==null?void 0:m[i])||{given:((g=(b=e.name)==null?void 0:b.given)==null?void 0:g.value)||"",family:((v=(h=e.name)==null?void 0:h.family)==null?void 0:v.value)||"",middle:((I=(k=e.name)==null?void 0:k.middle)==null?void 0:I.value)||null};t.innerHTML=`
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
          ${(((E=e.name)==null?void 0:E.candidate_parses)||[]).map((f,w)=>`
            <label style="display: flex; align-items: center; gap: 6px; font-size: 12px; margin-bottom: 4px; cursor: pointer;">
              <input type="radio" name="wd_cand_name" value="${w}" ${w===i?"checked":""} />
              <span>${f.given} <strong>${f.family}</strong> ${f.middle?`(Mid: ${f.middle})`:""}</span>
            </label>
          `).join("")||`<div>${(A=(q=e.name)==null?void 0:q.given)==null?void 0:A.value} ${(N=(_=e.name)==null?void 0:_.family)==null?void 0:N.value}</div>`}
        </div>

        <!-- Summary fields -->
        <div class="wd-field-row">
          <span class="wd-field-label">First Name</span>
          <span class="wd-field-val">${o.given}</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">Last Name</span>
          <span class="wd-field-val">${o.family}</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">Address Line 1</span>
          <span class="wd-field-val">${(($=(T=e.address)==null?void 0:T.line1)==null?void 0:$.value)||'<em style="color:#80868b">None (Resume Empty)</em>'}</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">City, State</span>
          <span class="wd-field-val">${((L=(C=e.address)==null?void 0:C.city)==null?void 0:L.value)||""}, ${((z=(M=e.address)==null?void 0:M.state)==null?void 0:z.value)||""}</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">Education</span>
          <span class="wd-field-val">${((j=(R=(D=e.education)==null?void 0:D[0])==null?void 0:R.school)==null?void 0:j.value)||"N/A"}</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">Degree</span>
          <span class="wd-field-val">${((O=(F=(U=e.education)==null?void 0:U[0])==null?void 0:F.degree)==null?void 0:O.value)||"N/A"} in ${((W=(H=(B=e.education)==null?void 0:B[0])==null?void 0:H.field)==null?void 0:W.value)||""}</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">Experience</span>
          <span class="wd-field-val">${((P=e.experience)==null?void 0:P.length)||0} positions</span>
        </div>
        <div class="wd-field-row">
          <span class="wd-field-label">LinkedIn</span>
          <span class="wd-field-val">${(G=(Y=e.links)==null?void 0:Y.linkedin)!=null&&G.value?"Extracted":"None"}</span>
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
    `;const a=t.querySelector("#wd-close-btn");a==null||a.addEventListener("click",()=>{t.remove(),S=null}),t.querySelectorAll('input[name="wd_cand_name"]').forEach(f=>{f.addEventListener("change",w=>{i=parseInt(w.target.value,10);const x=e.name.candidate_parses[i];e.name.given.value=x.given,e.name.family.value=x.family,e.name.middle.value=x.middle,n()})});const r=t.querySelector("#wd-fill-btn");r==null||r.addEventListener("click",async()=>{r&&(r.textContent="Autofilling...",r.disabled=!0);const f=await pe(e);r&&(r.textContent=`Done! (${f.filled} filled, ${f.highlighted} flagged)`,r.style.background="#1e8e3e"),setTimeout(()=>{t.remove(),S=null},2500)})};n(),document.body.appendChild(t),S=t}var de,ce;(ce=(de=chrome.runtime)==null?void 0:de.onMessage)==null||ce.addListener((e,t,i)=>{if(e.action==="SHOW_REVIEW_OVERLAY")we(e.data),i({success:!0});else if(e.action==="DIRECT_FILL")return pe(e.data).then(n=>{i({success:!0,result:n})}),!0});

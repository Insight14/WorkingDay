import { findBestMatch } from './fuzzy';

export function setReactInputValue(elem: HTMLInputElement | HTMLTextAreaElement, value: string): void {
  const prototype = elem instanceof HTMLTextAreaElement 
    ? window.HTMLTextAreaElement.prototype 
    : window.HTMLInputElement.prototype;
    
  const nativeSetter = Object.getOwnPropertyDescriptor(prototype, 'value')?.set;
  if (nativeSetter) {
    nativeSetter.call(elem, value);
  } else {
    elem.value = value;
  }

  elem.dispatchEvent(new Event('input', { bubbles: true }));
  elem.dispatchEvent(new Event('change', { bubbles: true }));
  elem.dispatchEvent(new Event('blur', { bubbles: true }));
}

export function setReactCheckbox(elem: HTMLInputElement, checked: boolean): void {
  if (elem.checked !== checked) {
    elem.checked = checked;
    elem.dispatchEvent(new Event('input', { bubbles: true }));
    elem.dispatchEvent(new Event('change', { bubbles: true }));
    elem.dispatchEvent(new Event('click', { bubbles: true }));
  }
}

export function highlightFieldForReview(elem: HTMLElement, reason: string = "Low confidence match - please verify"): void {
  elem.style.outline = "2px solid #f9ab00";
  elem.style.backgroundColor = "#fffde7";
  elem.title = `WorkingDay Review: ${reason}`;
}

export async function fillCustomDropdown(
  btnElem: HTMLElement, 
  targetValue: string, 
  threshold: number = 0.65
): Promise<boolean> {
  if (!targetValue) return false;

  // Click button to open listbox
  btnElem.click();

  // Wait for options list in DOM
  const options = await waitForElements('[role="option"]', 800);
  if (!options || options.length === 0) {
    highlightFieldForReview(btnElem, `No options found for '${targetValue}'`);
    return false;
  }

  const match = findBestMatch(targetValue, options, threshold);
  if (match) {
    match.option.click();
    return true;
  } else {
    // If below threshold, do not select false item and highlight for review
    highlightFieldForReview(btnElem, `Fuzzy match below threshold for '${targetValue}'`);
    // Close dropdown
    btnElem.click();
    return false;
  }
}

export async function fillTypeahead(
  inputElem: HTMLInputElement, 
  targetValue: string
): Promise<boolean> {
  if (!targetValue) return false;

  inputElem.focus();
  setReactInputValue(inputElem, targetValue);
  
  // Dispatch Enter key
  const enterEvent = new KeyboardEvent('keydown', {
    key: 'Enter',
    code: 'Enter',
    keyCode: 13,
    which: 13,
    bubbles: true,
    cancelable: true
  });
  inputElem.dispatchEvent(enterEvent);

  // Also check if dropdown options appeared
  const options = await waitForElements('[role="option"]', 400);
  if (options && options.length > 0) {
    const match = findBestMatch(targetValue, options, 0.6);
    if (match) {
      match.option.click();
      return true;
    }
  }

  return true;
}

export function waitForElements(selector: string, timeoutMs: number = 1000): Promise<HTMLElement[]> {
  return new Promise(resolve => {
    const initial = Array.from(document.querySelectorAll<HTMLElement>(selector));
    if (initial.length > 0) {
      resolve(initial);
      return;
    }

    const observer = new MutationObserver(() => {
      const elems = Array.from(document.querySelectorAll<HTMLElement>(selector));
      if (elems.length > 0) {
        observer.disconnect();
        resolve(elems);
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });

    setTimeout(() => {
      observer.disconnect();
      resolve(Array.from(document.querySelectorAll<HTMLElement>(selector)));
    }, timeoutMs);
  });
}

export async function fillResumeData(data: any): Promise<{ filled: number; highlighted: number }> {
  let filledCount = 0;
  let highlightedCount = 0;

  // 1. Legal Name
  const firstNameInput = document.querySelector<HTMLInputElement>(
    '[data-automation-id="legalNameSection_firstName"], input#legalNameSection_firstName, input[name="firstName"]'
  );
  if (firstNameInput && data.name?.given?.value) {
    setReactInputValue(firstNameInput, data.name.given.value);
    filledCount++;
    if (data.name.given.confidence < 0.85) {
      highlightFieldForReview(firstNameInput, "Candidate name confidence < 85%");
      highlightedCount++;
    }
  }

  const lastNameInput = document.querySelector<HTMLInputElement>(
    '[data-automation-id="legalNameSection_lastName"], input#legalNameSection_lastName, input[name="lastName"]'
  );
  if (lastNameInput && data.name?.family?.value) {
    setReactInputValue(lastNameInput, data.name.family.value);
    filledCount++;
    if (data.name.family.confidence < 0.85) {
      highlightFieldForReview(lastNameInput, "Candidate name confidence < 85%");
      highlightedCount++;
    }
  }

  // 2. Address & Contact
  const addr1Input = document.querySelector<HTMLInputElement>(
    '[data-automation-id="addressSection_addressLine1"], input#addressSection_addressLine1'
  );
  if (addr1Input) {
    if (data.address?.line1?.value) {
      setReactInputValue(addr1Input, data.address.line1.value);
      filledCount++;
    } else {
      // Intentionally empty in resume - do not invent
      setReactInputValue(addr1Input, "");
    }
  }

  const addr2Input = document.querySelector<HTMLInputElement>(
    '[data-automation-id="addressSection_addressLine2"], input#addressSection_addressLine2'
  );
  if (addr2Input && data.address?.line2?.value) {
    setReactInputValue(addr2Input, data.address.line2.value);
    filledCount++;
  }

  const cityInput = document.querySelector<HTMLInputElement>(
    '[data-automation-id="addressSection_city"], input#addressSection_city'
  );
  if (cityInput && data.address?.city?.value) {
    setReactInputValue(cityInput, data.address.city.value);
    filledCount++;
  }

  const stateDropdown = document.querySelector<HTMLElement>(
    '[data-automation-id="addressSection_countryRegion"], button#addressSection_countryRegion'
  );
  if (stateDropdown && data.address?.state?.value) {
    const success = await fillCustomDropdown(stateDropdown, data.address.state.value);
    if (success) filledCount++;
    else highlightedCount++;
  }

  const postalInput = document.querySelector<HTMLInputElement>(
    '[data-automation-id="addressSection_postalCode"], input#addressSection_postalCode'
  );
  if (postalInput && data.address?.postal?.value) {
    setReactInputValue(postalInput, data.address.postal.value);
    filledCount++;
  }

  const phoneInput = document.querySelector<HTMLInputElement>(
    '[data-automation-id="phone-number"], input#phone-number, input[type="tel"]'
  );
  if (phoneInput && data.phone?.value) {
    setReactInputValue(phoneInput, data.phone.value);
    filledCount++;
  }

  const emailInput = document.querySelector<HTMLInputElement>(
    '[data-automation-id="email"], input#email, input[type="email"]'
  );
  if (emailInput && data.email?.value) {
    setReactInputValue(emailInput, data.email.value);
    filledCount++;
  }

  // 3. Work Experience (Repeatable blocks)
  if (data.experience && data.experience.length > 0) {
    const expAddBtn = document.querySelector<HTMLButtonElement>(
      'button:has(svg), button[data-automation-id="addExperience"], .btn-secondary'
    );

    // Fill available experience blocks
    const expBlocks = Array.from(document.querySelectorAll<HTMLElement>('.repeatable-block'));
    for (let i = 0; i < data.experience.length; i++) {
      const expItem = data.experience[i];
      let block = expBlocks[i];
      if (!block && expAddBtn && i > 0) {
        expAddBtn.click();
        await new Promise(r => setTimeout(r, 200));
        const updated = Array.from(document.querySelectorAll<HTMLElement>('.repeatable-block'));
        block = updated[i];
      }

      if (block) {
        const titleInput = block.querySelector<HTMLInputElement>('[data-automation-id="jobTitle"]');
        if (titleInput && expItem.title?.value) {
          setReactInputValue(titleInput, expItem.title.value);
          filledCount++;
        }

        const compInput = block.querySelector<HTMLInputElement>('[data-automation-id="companyName"]');
        if (compInput && expItem.company?.value) {
          setReactInputValue(compInput, expItem.company.value);
          filledCount++;
        }

        const locInput = block.querySelector<HTMLInputElement>('[data-automation-id="location"]');
        if (locInput && expItem.location?.value) {
          setReactInputValue(locInput, expItem.location.value);
          filledCount++;
        }

        const currBox = block.querySelector<HTMLInputElement>('[data-automation-id="currentlyWorkHere"]');
        if (currBox && expItem.current?.value !== undefined) {
          setReactCheckbox(currBox, expItem.current.value);
          filledCount++;
        }

        const startInput = block.querySelector<HTMLInputElement>('[data-automation-id="startDate"]');
        if (startInput && expItem.start?.value) {
          setReactInputValue(startInput, expItem.start.value);
          filledCount++;
        }

        const endInput = block.querySelector<HTMLInputElement>('[data-automation-id="endDate"]');
        if (endInput && expItem.end?.value) {
          setReactInputValue(endInput, expItem.end.value);
          filledCount++;
        }

        const descInput = block.querySelector<HTMLTextAreaElement>('[data-automation-id="jobDescription"]');
        if (descInput && expItem.bullets?.value) {
          const bulletsText = expItem.bullets.value.map((b: string) => `• ${b}`).join('\n');
          setReactInputValue(descInput, bulletsText);
          filledCount++;
        }
      }
    }
  }

  // 4. Education
  if (data.education && data.education.length > 0) {
    const edu = data.education[0];
    const schoolInput = document.querySelector<HTMLInputElement>('[data-automation-id="school"]');
    if (schoolInput && edu.school?.value) {
      await fillTypeahead(schoolInput, edu.school.value);
      filledCount++;
    }

    const degreeBtn = document.querySelector<HTMLElement>('[data-automation-id="degree"]');
    if (degreeBtn && edu.degree?.value) {
      const success = await fillCustomDropdown(degreeBtn, edu.degree.value);
      if (success) filledCount++;
      else highlightedCount++;
    }

    const fieldInput = document.querySelector<HTMLInputElement>('[data-automation-id="fieldOfStudy"]');
    if (fieldInput && edu.field?.value) {
      await fillTypeahead(fieldInput, edu.field.value);
      filledCount++;
    }

    const eduEndInput = document.querySelector<HTMLInputElement>('[data-automation-id="education_endDate"]');
    if (eduEndInput && edu.end?.value) {
      setReactInputValue(eduEndInput, edu.end.value);
      filledCount++;
    }
  }

  // 5. Links
  const linkedinInput = document.querySelector<HTMLInputElement>('[data-automation-id="socialUrl_linkedIn"]');
  if (linkedinInput && data.links?.linkedin?.value) {
    setReactInputValue(linkedinInput, data.links.linkedin.value);
    filledCount++;
  }

  const websiteInput = document.querySelector<HTMLInputElement>('[data-automation-id="websiteUrl"]');
  if (websiteInput && data.links?.github?.value) {
    setReactInputValue(websiteInput, data.links.github.value);
    filledCount++;
  }

  return { filled: filledCount, highlighted: highlightedCount };
}

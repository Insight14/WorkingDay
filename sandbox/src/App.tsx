import { useState } from 'react';
import { 
  ChevronDown, 
  Plus, 
  Trash2, 
  CheckCircle, 
  Info 
} from 'lucide-react';

interface WorkExp {
  id: string;
  jobTitle: string;
  companyName: string;
  location: string;
  currentlyWorkHere: boolean;
  startDate: string;
  endDate: string;
  jobDescription: string;
}

interface EduItem {
  id: string;
  school: string;
  degree: string;
  fieldOfStudy: string[];
  startDate: string;
  endDate: string;
}

const STATE_OPTIONS = [
  "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
  "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
  "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
  "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
  "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
];

const DEGREE_OPTIONS = [
  "Associate's",
  "Bachelor's",
  "Master's",
  "Doctorate",
  "High School",
  "Certificate"
];

const SCHOOL_SUGGESTIONS = [
  "The University of Texas at Dallas",
  "University of Texas at Austin",
  "Texas A&M University",
  "Stanford University",
  "Massachusetts Institute of Technology",
  "University of California, Berkeley",
  "Carnegie Mellon University",
  "Georgia Institute of Technology",
  "University of Illinois Urbana-Champaign",
  "University of Washington"
];

export default function App() {
  const [step, setStep] = useState<number>(1);

  // Step 1: My Information
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [hasPreferredName, setHasPreferredName] = useState(false);
  const [preferredName, setPreferredName] = useState('');
  const [addressLine1, setAddressLine1] = useState('');
  const [addressLine2, setAddressLine2] = useState('');
  const [city, setCity] = useState('');
  const [selectedState, setSelectedState] = useState('');
  const [postalCode, setPostalCode] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');

  // Step 2: My Experience
  const [experiences, setExperiences] = useState<WorkExp[]>([
    {
      id: '1',
      jobTitle: '',
      companyName: '',
      location: '',
      currentlyWorkHere: false,
      startDate: '',
      endDate: '',
      jobDescription: ''
    }
  ]);

  const [educations, setEducations] = useState<EduItem[]>([
    {
      id: '1',
      school: '',
      degree: '',
      fieldOfStudy: [],
      startDate: '',
      endDate: ''
    }
  ]);

  const [websites, setWebsites] = useState<string[]>(['']);
  const [linkedInUrl, setLinkedInUrl] = useState('');

  // Step 3: Application Questions
  const [workAuthorized, setWorkAuthorized] = useState<string>('yes');
  const [sponsorshipRequired, setSponsorshipRequired] = useState<string>('no');
  const [referralSource, setReferralSource] = useState<string>('LinkedIn');
  const [agreeTerms, setAgreeTerms] = useState<boolean>(false);

  // UI state for dropdowns
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [schoolInputs, setSchoolInputs] = useState<Record<string, string>>({});
  const [fieldInputs, setFieldInputs] = useState<Record<string, string>>({});

  const addExperience = () => {
    setExperiences(prev => [
      ...prev,
      {
        id: Date.now().toString(),
        jobTitle: '',
        companyName: '',
        location: '',
        currentlyWorkHere: false,
        startDate: '',
        endDate: '',
        jobDescription: ''
      }
    ]);
  };

  const removeExperience = (id: string) => {
    if (experiences.length > 1) {
      setExperiences(prev => prev.filter(e => e.id !== id));
    }
  };

  const updateExperience = (id: string, field: keyof WorkExp, value: any) => {
    setExperiences(prev => prev.map(e => e.id === id ? { ...e, [field]: value } : e));
  };

  const addEducation = () => {
    setEducations(prev => [
      ...prev,
      {
        id: Date.now().toString(),
        school: '',
        degree: '',
        fieldOfStudy: [],
        startDate: '',
        endDate: ''
      }
    ]);
  };

  const removeEducation = (id: string) => {
    if (educations.length > 1) {
      setEducations(prev => prev.filter(e => e.id !== id));
    }
  };

  const updateEducation = (id: string, field: keyof EduItem, value: any) => {
    setEducations(prev => prev.map(e => e.id === id ? { ...e, [field]: value } : e));
  };

  const addWebsite = () => {
    setWebsites(prev => [...prev, '']);
  };

  const removeWebsite = (index: number) => {
    if (websites.length > 1) {
      setWebsites(prev => prev.filter((_, i) => i !== index));
    }
  };

  const updateWebsite = (index: number, val: string) => {
    setWebsites(prev => prev.map((w, i) => i === index ? val : w));
  };

  return (
    <div className="portal-container">
      {/* Mock Disclaimer Banner */}
      <div className="mock-disclaimer-banner">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Info size={18} />
          <span><strong>Mock Candidate Application Portal</strong> &mdash; This environment simulates Workday application structure for testing autofill accuracy.</span>
        </div>
        <span style={{ fontSize: '12px', background: '#ffe082', padding: '2px 8px', borderRadius: '4px', fontWeight: 600 }}>CANDIDATE TESTING SANDBOX</span>
      </div>

      {/* Stepper Navigation */}
      <div className="header-stepper">
        <ul className="stepper-list">
          <li className={`stepper-item ${step === 1 ? 'active' : step > 1 ? 'completed' : ''}`} onClick={() => setStep(1)}>
            <div className="stepper-circle">{step > 1 ? <CheckCircle size={16} /> : '1'}</div>
            <span className="stepper-label">My Information</span>
          </li>
          <li className={`stepper-item ${step === 2 ? 'active' : step > 2 ? 'completed' : ''}`} onClick={() => setStep(2)}>
            <div className="stepper-circle">{step > 2 ? <CheckCircle size={16} /> : '2'}</div>
            <span className="stepper-label">My Experience</span>
          </li>
          <li className={`stepper-item ${step === 3 ? 'active' : step > 3 ? 'completed' : ''}`} onClick={() => setStep(3)}>
            <div className="stepper-circle">{step > 3 ? <CheckCircle size={16} /> : '3'}</div>
            <span className="stepper-label">Application Questions</span>
          </li>
          <li className={`stepper-item ${step === 4 ? 'active' : ''}`} onClick={() => setStep(4)}>
            <div className="stepper-circle">4</div>
            <span className="stepper-label">Review</span>
          </li>
        </ul>
      </div>

      {/* STEP 1: MY INFORMATION */}
      {step === 1 && (
        <div className="form-card">
          <h2 className="section-title">Legal Name</h2>
          <p className="section-subtitle">Please enter your legal name as it appears on official government identification.</p>
          
          <div className="form-grid">
            <div className="form-field">
              <label className="form-label">
                First Name<span className="required">*</span>
              </label>
              <input
                type="text"
                className="input-text"
                id="legalNameSection_firstName"
                data-automation-id="legalNameSection_firstName"
                value={firstName}
                onChange={e => setFirstName(e.target.value)}
                placeholder="First Name"
              />
            </div>

            <div className="form-field">
              <label className="form-label">
                Last Name<span className="required">*</span>
              </label>
              <input
                type="text"
                className="input-text"
                id="legalNameSection_lastName"
                data-automation-id="legalNameSection_lastName"
                value={lastName}
                onChange={e => setLastName(e.target.value)}
                placeholder="Last Name"
              />
            </div>
          </div>

          <div style={{ marginTop: '16px' }}>
            <label className="checkbox-field">
              <input
                type="checkbox"
                data-automation-id="preferredNameCheckbox"
                checked={hasPreferredName}
                onChange={e => setHasPreferredName(e.target.checked)}
              />
              <span>I have a preferred name</span>
            </label>
          </div>

          {hasPreferredName && (
            <div className="form-grid" style={{ marginTop: '12px' }}>
              <div className="form-field">
                <label className="form-label">Preferred Name</label>
                <input
                  type="text"
                  className="input-text"
                  data-automation-id="preferredNameSection_preferredName"
                  value={preferredName}
                  onChange={e => setPreferredName(e.target.value)}
                  placeholder="Preferred Name"
                />
              </div>
            </div>
          )}

          <h2 className="section-title" style={{ marginTop: '36px' }}>Address</h2>
          <p className="section-subtitle">Please provide your contact address details.</p>

          <div className="form-grid full">
            <div className="form-field">
              <label className="form-label">Address Line 1</label>
              <input
                type="text"
                className="input-text"
                id="addressSection_addressLine1"
                data-automation-id="addressSection_addressLine1"
                value={addressLine1}
                onChange={e => setAddressLine1(e.target.value)}
                placeholder="Street Address (e.g. 123 Main St)"
              />
              <span className="helper-text">Leave blank if your resume does not contain a street address.</span>
            </div>

            <div className="form-field">
              <label className="form-label">Address Line 2</label>
              <input
                type="text"
                className="input-text"
                id="addressSection_addressLine2"
                data-automation-id="addressSection_addressLine2"
                value={addressLine2}
                onChange={e => setAddressLine2(e.target.value)}
                placeholder="Apt, Suite, Bldg, Block # (Optional)"
              />
            </div>
          </div>

          <div className="form-grid" style={{ marginTop: '20px' }}>
            <div className="form-field">
              <label className="form-label">
                City<span className="required">*</span>
              </label>
              <input
                type="text"
                className="input-text"
                id="addressSection_city"
                data-automation-id="addressSection_city"
                value={city}
                onChange={e => setCity(e.target.value)}
                placeholder="City"
              />
            </div>

            <div className="form-field">
              <label className="form-label">
                State / Province<span className="required">*</span>
              </label>
              <div style={{ position: 'relative' }}>
                <button
                  type="button"
                  className="custom-listbox-btn"
                  id="addressSection_countryRegion"
                  data-automation-id="addressSection_countryRegion"
                  aria-haspopup="listbox"
                  onClick={() => setActiveDropdown(activeDropdown === 'state' ? null : 'state')}
                >
                  <span>{selectedState || 'Select One'}</span>
                  <ChevronDown size={16} />
                </button>
                {activeDropdown === 'state' && (
                  <ul className="custom-listbox-options" role="listbox">
                    {STATE_OPTIONS.map(st => (
                      <li
                        key={st}
                        role="option"
                        aria-selected={selectedState === st}
                        className={`custom-listbox-option ${selectedState === st ? 'selected' : ''}`}
                        onClick={() => {
                          setSelectedState(st);
                          setActiveDropdown(null);
                        }}
                      >
                        {st}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className="form-field">
              <label className="form-label">
                Postal Code<span className="required">*</span>
              </label>
              <input
                type="text"
                className="input-text"
                id="addressSection_postalCode"
                data-automation-id="addressSection_postalCode"
                value={postalCode}
                onChange={e => setPostalCode(e.target.value)}
                placeholder="Postal Code"
              />
            </div>

            <div className="form-field">
              <label className="form-label">
                Phone Number<span className="required">*</span>
              </label>
              <input
                type="text"
                className="input-text"
                id="phone-number"
                data-automation-id="phone-number"
                value={phone}
                onChange={e => setPhone(e.target.value)}
                placeholder="(555) 555-5555"
              />
            </div>
          </div>

          <div className="form-grid full" style={{ marginTop: '20px' }}>
            <div className="form-field">
              <label className="form-label">
                Email Address<span className="required">*</span>
              </label>
              <input
                type="email"
                className="input-text"
                id="email"
                data-automation-id="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="your.email@example.com"
              />
            </div>
          </div>

          <div className="nav-buttons">
            <div></div>
            <button className="btn-primary" onClick={() => setStep(2)}>Save and Continue</button>
          </div>
        </div>
      )}

      {/* STEP 2: MY EXPERIENCE */}
      {step === 2 && (
        <div className="form-card">
          <h2 className="section-title">Work Experience</h2>
          <p className="section-subtitle">Add your professional work history starting with your most recent role.</p>

          {experiences.map((exp, idx) => (
            <div key={exp.id} className="repeatable-block">
              <div className="block-header">
                <span className="block-title">Work Experience {idx + 1}</span>
                {experiences.length > 1 && (
                  <button type="button" className="btn-delete" onClick={() => removeExperience(exp.id)}>
                    <Trash2 size={15} /> Remove
                  </button>
                )}
              </div>

              <div className="form-grid">
                <div className="form-field">
                  <label className="form-label">
                    Job Title<span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    className="input-text"
                    data-automation-id="jobTitle"
                    value={exp.jobTitle}
                    onChange={e => updateExperience(exp.id, 'jobTitle', e.target.value)}
                    placeholder="e.g. AI/ML Intern"
                  />
                </div>

                <div className="form-field">
                  <label className="form-label">
                    Company<span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    className="input-text"
                    data-automation-id="companyName"
                    value={exp.companyName}
                    onChange={e => updateExperience(exp.id, 'companyName', e.target.value)}
                    placeholder="e.g. Handshake AI"
                  />
                </div>

                <div className="form-field">
                  <label className="form-label">Location</label>
                  <input
                    type="text"
                    className="input-text"
                    data-automation-id="location"
                    value={exp.location}
                    onChange={e => updateExperience(exp.id, 'location', e.target.value)}
                    placeholder="e.g. North Dallas"
                  />
                </div>

                <div className="form-field" style={{ justifyContent: 'center' }}>
                  <label className="checkbox-field" style={{ marginTop: '24px' }}>
                    <input
                      type="checkbox"
                      data-automation-id="currentlyWorkHere"
                      checked={exp.currentlyWorkHere}
                      onChange={e => updateExperience(exp.id, 'currentlyWorkHere', e.target.checked)}
                    />
                    <span>I currently work here</span>
                  </label>
                </div>

                <div className="form-field">
                  <label className="form-label">From</label>
                  <input
                    type="text"
                    className="input-text"
                    data-automation-id="startDate"
                    value={exp.startDate}
                    onChange={e => updateExperience(exp.id, 'startDate', e.target.value)}
                    placeholder="YYYY-MM (e.g. 2026-05)"
                  />
                </div>

                {!exp.currentlyWorkHere && (
                  <div className="form-field">
                    <label className="form-label">To</label>
                    <input
                      type="text"
                      className="input-text"
                      data-automation-id="endDate"
                      value={exp.endDate}
                      onChange={e => updateExperience(exp.id, 'endDate', e.target.value)}
                      placeholder="YYYY-MM"
                    />
                  </div>
                )}
              </div>

              <div className="form-grid full" style={{ marginTop: '16px' }}>
                <div className="form-field">
                  <label className="form-label">Role Description</label>
                  <textarea
                    className="input-textarea"
                    data-automation-id="jobDescription"
                    value={exp.jobDescription}
                    onChange={e => updateExperience(exp.id, 'jobDescription', e.target.value)}
                    placeholder="• Bullet points describing responsibilities and achievements..."
                  />
                </div>
              </div>
            </div>
          ))}

          <button type="button" className="btn-secondary" onClick={addExperience} style={{ marginBottom: '36px' }}>
            <Plus size={16} /> Add Work Experience
          </button>

          <h2 className="section-title">Education</h2>
          <p className="section-subtitle">Add your academic background and degrees.</p>

          {educations.map((edu, idx) => (
            <div key={edu.id} className="repeatable-block">
              <div className="block-header">
                <span className="block-title">Education {idx + 1}</span>
                {educations.length > 1 && (
                  <button type="button" className="btn-delete" onClick={() => removeEducation(edu.id)}>
                    <Trash2 size={15} /> Remove
                  </button>
                )}
              </div>

              <div className="form-grid">
                <div className="form-field">
                  <label className="form-label">
                    School or University<span className="required">*</span>
                  </label>
                  <div className="typeahead-container">
                    <input
                      type="text"
                      className="input-text"
                      data-automation-id="school"
                      value={edu.school || schoolInputs[edu.id] || ''}
                      onChange={e => {
                        const val = e.target.value;
                        setSchoolInputs(prev => ({ ...prev, [edu.id]: val }));
                        updateEducation(edu.id, 'school', val);
                      }}
                      onKeyDown={e => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          const cur = schoolInputs[edu.id] || '';
                          const matched = SCHOOL_SUGGESTIONS.find(s => s.toLowerCase().includes(cur.toLowerCase()));
                          if (matched) {
                            updateEducation(edu.id, 'school', matched);
                          }
                        }
                      }}
                      placeholder="Type school name and press Enter..."
                    />
                    <span className="helper-text">Type a few letters and press Enter to select school.</span>
                  </div>
                </div>

                <div className="form-field">
                  <label className="form-label">
                    Degree<span className="required">*</span>
                  </label>
                  <div style={{ position: 'relative' }}>
                    <button
                      type="button"
                      className="custom-listbox-btn"
                      data-automation-id="degree"
                      aria-haspopup="listbox"
                      onClick={() => setActiveDropdown(activeDropdown === `degree_${edu.id}` ? null : `degree_${edu.id}`)}
                    >
                      <span>{edu.degree || 'Select Degree'}</span>
                      <ChevronDown size={16} />
                    </button>
                    {activeDropdown === `degree_${edu.id}` && (
                      <ul className="custom-listbox-options" role="listbox">
                        {DEGREE_OPTIONS.map(d => (
                          <li
                            key={d}
                            role="option"
                            className={`custom-listbox-option ${edu.degree === d ? 'selected' : ''}`}
                            onClick={() => {
                              updateEducation(edu.id, 'degree', d);
                              setActiveDropdown(null);
                            }}
                          >
                            {d}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>

                <div className="form-field">
                  <label className="form-label">Field of Study</label>
                  <div className="chip-container">
                    {edu.fieldOfStudy.map((f, fIdx) => (
                      <span key={fIdx} className="chip">
                        {f}
                        <button
                          type="button"
                          className="chip-remove"
                          onClick={() => updateEducation(edu.id, 'fieldOfStudy', edu.fieldOfStudy.filter((_, i) => i !== fIdx))}
                        >
                          &times;
                        </button>
                      </span>
                    ))}
                  </div>
                  <input
                    type="text"
                    className="input-text"
                    data-automation-id="fieldOfStudy"
                    value={fieldInputs[edu.id] || ''}
                    onChange={e => setFieldInputs(prev => ({ ...prev, [edu.id]: e.target.value }))}
                    onKeyDown={e => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        const val = (fieldInputs[edu.id] || '').trim();
                        if (val && !edu.fieldOfStudy.includes(val)) {
                          updateEducation(edu.id, 'fieldOfStudy', [...edu.fieldOfStudy, val]);
                          setFieldInputs(prev => ({ ...prev, [edu.id]: '' }));
                        }
                      }
                    }}
                    placeholder="Type field (e.g. Computer Science) + Enter"
                  />
                </div>

                <div className="form-field">
                  <label className="form-label">End Date (Expected)</label>
                  <input
                    type="text"
                    className="input-text"
                    data-automation-id="education_endDate"
                    value={edu.endDate}
                    onChange={e => updateEducation(edu.id, 'endDate', e.target.value)}
                    placeholder="YYYY-MM (e.g. 2027-12)"
                  />
                </div>
              </div>
            </div>
          ))}

          <button type="button" className="btn-secondary" onClick={addEducation} style={{ marginBottom: '36px' }}>
            <Plus size={16} /> Add Education
          </button>

          <h2 className="section-title">Websites & Social Profiles</h2>
          <p className="section-subtitle">Add portfolio links, GitHub, and your LinkedIn profile.</p>

          <div className="form-grid full">
            <div className="form-field">
              <label className="form-label">LinkedIn Profile URL</label>
              <input
                type="text"
                className="input-text"
                id="socialUrl_linkedIn"
                data-automation-id="socialUrl_linkedIn"
                value={linkedInUrl}
                onChange={e => setLinkedInUrl(e.target.value)}
                placeholder="https://linkedin.com/in/username"
              />
            </div>

            {websites.map((web, wIdx) => (
              <div key={wIdx} className="form-field" style={{ marginTop: '10px' }}>
                <label className="form-label">Website {wIdx + 1} URL</label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input
                    type="text"
                    className="input-text"
                    data-automation-id="websiteUrl"
                    value={web}
                    onChange={e => updateWebsite(wIdx, e.target.value)}
                    placeholder="https://github.com/username or portfolio URL"
                  />
                  {websites.length > 1 && (
                    <button type="button" className="btn-delete" onClick={() => removeWebsite(wIdx)}>
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          <button type="button" className="btn-secondary" onClick={addWebsite} style={{ marginTop: '12px' }}>
            <Plus size={16} /> Add Another Website
          </button>

          <div className="nav-buttons">
            <button className="btn-secondary" onClick={() => setStep(1)}>Back</button>
            <button className="btn-primary" onClick={() => setStep(3)}>Save and Continue</button>
          </div>
        </div>
      )}

      {/* STEP 3: APPLICATION QUESTIONS */}
      {step === 3 && (
        <div className="form-card">
          <h2 className="section-title">Application Questions</h2>
          <p className="section-subtitle">Please answer the following standard eligibility questions.</p>

          <div style={{ marginBottom: '24px' }}>
            <label className="form-label">Are you legally authorized to work in the United States?</label>
            <div style={{ display: 'flex', gap: '20px', marginTop: '8px' }}>
              <label className="radio-field">
                <input
                  type="radio"
                  name="workAuth"
                  data-automation-id="question_workAuth_yes"
                  value="yes"
                  checked={workAuthorized === 'yes'}
                  onChange={e => setWorkAuthorized(e.target.value)}
                />
                <span>Yes</span>
              </label>
              <label className="radio-field">
                <input
                  type="radio"
                  name="workAuth"
                  data-automation-id="question_workAuth_no"
                  value="no"
                  checked={workAuthorized === 'no'}
                  onChange={e => setWorkAuthorized(e.target.value)}
                />
                <span>No</span>
              </label>
            </div>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label className="form-label">Will you now or in the future require visa sponsorship for employment?</label>
            <div style={{ display: 'flex', gap: '20px', marginTop: '8px' }}>
              <label className="radio-field">
                <input
                  type="radio"
                  name="sponsorship"
                  data-automation-id="question_sponsorship_yes"
                  value="yes"
                  checked={sponsorshipRequired === 'yes'}
                  onChange={e => setSponsorshipRequired(e.target.value)}
                />
                <span>Yes</span>
              </label>
              <label className="radio-field">
                <input
                  type="radio"
                  name="sponsorship"
                  data-automation-id="question_sponsorship_no"
                  value="no"
                  checked={sponsorshipRequired === 'no'}
                  onChange={e => setSponsorshipRequired(e.target.value)}
                />
                <span>No</span>
              </label>
            </div>
          </div>

          <div className="form-field" style={{ marginBottom: '24px', maxWidth: '400px' }}>
            <label className="form-label">How did you hear about this opportunity?</label>
            <select
              className="input-text"
              data-automation-id="question_referralSource"
              value={referralSource}
              onChange={e => setReferralSource(e.target.value)}
            >
              <option value="LinkedIn">LinkedIn</option>
              <option value="Company Website">Company Career Portal</option>
              <option value="Handshake">Handshake</option>
              <option value="University Career Fair">University Career Fair</option>
              <option value="Referral">Employee Referral</option>
            </select>
          </div>

          <div style={{ marginTop: '20px' }}>
            <label className="checkbox-field">
              <input
                type="checkbox"
                data-automation-id="question_termsAcknowledgement"
                checked={agreeTerms}
                onChange={e => setAgreeTerms(e.target.checked)}
              />
              <span>I acknowledge that all information provided in this application is accurate and complete.</span>
            </label>
          </div>

          <div className="nav-buttons">
            <button className="btn-secondary" onClick={() => setStep(2)}>Back</button>
            <button className="btn-primary" onClick={() => setStep(4)}>Review Application</button>
          </div>
        </div>
      )}

      {/* STEP 4: REVIEW */}
      {step === 4 && (
        <div className="form-card">
          <h2 className="section-title">Review Your Application</h2>
          <p className="section-subtitle">Review all extracted and filled information before submission.</p>

          <h3 style={{ fontSize: '16px', marginTop: '20px', color: 'var(--color-primary)' }}>1. Candidate Information</h3>
          <table className="review-summary-table">
            <tbody>
              <tr><th>Full Legal Name</th><td>{firstName} {lastName}</td></tr>
              {hasPreferredName && <tr><th>Preferred Name</th><td>{preferredName}</td></tr>}
              <tr><th>Email</th><td>{email || 'None'}</td></tr>
              <tr><th>Phone</th><td>{phone || 'None'}</td></tr>
              <tr><th>Address</th><td>{addressLine1 ? `${addressLine1}, ` : ''}{addressLine2 ? `${addressLine2}, ` : ''}{city}, {selectedState} {postalCode}</td></tr>
            </tbody>
          </table>

          <h3 style={{ fontSize: '16px', marginTop: '24px', color: 'var(--color-primary)' }}>2. Work Experience ({experiences.length} entries)</h3>
          {experiences.map((exp) => (
            <table key={exp.id} className="review-summary-table" style={{ marginBottom: '12px' }}>
              <tbody>
                <tr><th>Role & Company</th><td><strong>{exp.jobTitle}</strong> at <strong>{exp.companyName}</strong> {exp.location ? `(${exp.location})` : ''}</td></tr>
                <tr><th>Timeline</th><td>{exp.startDate} &mdash; {exp.currentlyWorkHere ? 'Present' : exp.endDate}</td></tr>
                {exp.jobDescription && <tr><th>Description</th><td><pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0 }}>{exp.jobDescription}</pre></td></tr>}
              </tbody>
            </table>
          ))}

          <h3 style={{ fontSize: '16px', marginTop: '24px', color: 'var(--color-primary)' }}>3. Education ({educations.length} entries)</h3>
          {educations.map((edu) => (
            <table key={edu.id} className="review-summary-table" style={{ marginBottom: '12px' }}>
              <tbody>
                <tr><th>Institution</th><td>{edu.school}</td></tr>
                <tr><th>Degree & Field</th><td>{edu.degree} in {edu.fieldOfStudy.join(', ') || 'N/A'}</td></tr>
                <tr><th>End Date</th><td>{edu.endDate}</td></tr>
              </tbody>
            </table>
          ))}

          <h3 style={{ fontSize: '16px', marginTop: '24px', color: 'var(--color-primary)' }}>4. Links & Profiles</h3>
          <table className="review-summary-table">
            <tbody>
              <tr><th>LinkedIn</th><td>{linkedInUrl || 'None'}</td></tr>
              <tr><th>Websites</th><td>{websites.filter(Boolean).join(', ') || 'None'}</td></tr>
            </tbody>
          </table>

          <div className="nav-buttons">
            <button className="btn-secondary" onClick={() => setStep(3)}>Back</button>
            <button 
              className="btn-primary" 
              style={{ background: '#1e8e3e' }}
              onClick={() => alert("Candidate-side Mock Application review completed! (Note: WorkingDay extension never auto-submits).")}
            >
              Submit Application (Mock)
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

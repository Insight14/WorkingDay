import React, { useState, useEffect } from 'react';
import { UploadCloud, CheckCircle2, AlertTriangle, ArrowRight, Settings, FileText, Sparkles } from 'lucide-react';

export default function Popup() {
  const [apiUrl, setApiUrl] = useState('http://localhost:8000');
  const [parsedData, setParsedData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [tab, setTab] = useState<'main' | 'settings'>('main');
  const [siteEnabled, setSiteEnabled] = useState(true);
  const [selectedCandidate, setSelectedCandidate] = useState(0);

  useEffect(() => {
    // Load cached parsed data and settings if present
    if (typeof chrome !== 'undefined' && chrome.storage?.local) {
      chrome.storage.local.get(['cachedResume', 'parserApiUrl', 'siteEnabled'], (res) => {
        if (res.cachedResume) setParsedData(res.cachedResume);
        if (res.parserApiUrl) setApiUrl(res.parserApiUrl);
        if (res.siteEnabled !== undefined) setSiteEnabled(res.siteEnabled);
      });
    }
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setStatusMsg('Parsing resume...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${apiUrl}/parse/file`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }

      const data = await res.json();
      setParsedData(data);
      setStatusMsg('Parsed successfully!');

      if (typeof chrome !== 'undefined' && chrome.storage?.local) {
        chrome.storage.local.set({ cachedResume: data });
      }
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}. Ensure backend is running.`);
    } finally {
      setLoading(false);
    }
  };

  const handleAutofill = async () => {
    if (!parsedData) return;

    // Apply selected name candidate if changed
    const currentData = { ...parsedData };
    if (currentData.name?.candidate_parses?.[selectedCandidate]) {
      const cand = currentData.name.candidate_parses[selectedCandidate];
      currentData.name.given.value = cand.given;
      currentData.name.family.value = cand.family;
      currentData.name.middle.value = cand.middle;
    }

    if (typeof chrome !== 'undefined' && chrome.tabs) {
      const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (activeTab?.id) {
        chrome.tabs.sendMessage(activeTab.id, {
          action: 'SHOW_REVIEW_OVERLAY',
          data: currentData,
        });
      }
    }
  };

  return (
    <div style={{ padding: '16px', color: '#202124' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #dadce0', paddingBottom: '12px', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ background: '#0051a8', color: 'white', borderRadius: '6px', width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
            W
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '15px' }}>WorkingDay</div>
            <div style={{ fontSize: '11px', color: '#5f6368' }}>Workday Candidate Autofill</div>
          </div>
        </div>

        <button 
          onClick={() => setTab(tab === 'main' ? 'settings' : 'main')}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#5f6368' }}
        >
          <Settings size={18} />
        </button>
      </div>

      {tab === 'settings' ? (
        <div>
          <h3 style={{ fontSize: '14px', marginBottom: '12px' }}>Extension Settings</h3>
          <div style={{ marginBottom: '12px' }}>
            <label style={{ fontSize: '12px', color: '#5f6368', display: 'block', marginBottom: '4px' }}>Parser API Server</label>
            <input 
              type="text" 
              value={apiUrl} 
              onChange={e => {
                setApiUrl(e.target.value);
                if (typeof chrome !== 'undefined' && chrome.storage?.local) {
                  chrome.storage.local.set({ parserApiUrl: e.target.value });
                }
              }}
              style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #dadce0', fontSize: '13px' }}
            />
          </div>

          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
            <input 
              type="checkbox" 
              checked={siteEnabled} 
              onChange={e => {
                setSiteEnabled(e.target.checked);
                if (typeof chrome !== 'undefined' && chrome.storage?.local) {
                  chrome.storage.local.set({ siteEnabled: e.target.checked });
                }
              }} 
            />
            <span>Enable Autofill overlay on this site</span>
          </label>
        </div>
      ) : (
        <div>
          {/* Upload Area */}
          <div style={{ border: '2px dashed #dadce0', borderRadius: '8px', padding: '18px 12px', textAlign: 'center', background: '#ffffff', cursor: 'pointer', marginBottom: '14px' }}>
            <input 
              type="file" 
              id="resume-upload" 
              accept=".pdf,.docx" 
              onChange={handleFileUpload} 
              style={{ display: 'none' }} 
            />
            <label htmlFor="resume-upload" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <UploadCloud size={28} color="#0051a8" />
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#0051a8', marginTop: '6px' }}>Upload Resume (PDF / DOCX)</span>
              <span style={{ fontSize: '11px', color: '#5f6368' }}>PyMuPDF with precise bounding box ingestion</span>
            </label>
          </div>

          {statusMsg && (
            <div style={{ fontSize: '12px', marginBottom: '10px', color: statusMsg.includes('Error') ? '#d93025' : '#1e8e3e' }}>
              {statusMsg}
            </div>
          )}

          {parsedData && (
            <div style={{ background: '#ffffff', border: '1px solid #e0e0e0', borderRadius: '8px', padding: '12px', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '13px', fontWeight: 700 }}>Parsed Candidate</span>
                <span style={{ fontSize: '11px', background: '#e6f4ea', color: '#137333', padding: '2px 6px', borderRadius: '4px', fontWeight: 600 }}>Ready</span>
              </div>

              {/* Name Candidates */}
              {parsedData.name?.candidate_parses?.length > 1 && (
                <div style={{ marginBottom: '8px', fontSize: '12px' }}>
                  <div style={{ fontSize: '11px', color: '#5f6368', marginBottom: '2px' }}>Select Name Parse Format:</div>
                  {parsedData.name.candidate_parses.map((cand: any, idx: number) => (
                    <label key={idx} style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px', cursor: 'pointer' }}>
                      <input 
                        type="radio" 
                        name="cand_name" 
                        checked={selectedCandidate === idx} 
                        onChange={() => setSelectedCandidate(idx)} 
                      />
                      <span>{cand.given} <strong>{cand.family}</strong></span>
                    </label>
                  ))}
                </div>
              )}

              <div style={{ fontSize: '12px', lineHeight: '1.6' }}>
                <div><strong>Email:</strong> {parsedData.email?.value || 'None'}</div>
                <div><strong>Address:</strong> {parsedData.address?.city?.value ? `${parsedData.address.city.value}, ${parsedData.address.state.value} (Line 1: ${parsedData.address.line1.value || 'Null'})` : 'None'}</div>
                <div><strong>Experience:</strong> {parsedData.experience?.length || 0} entries</div>
                <div><strong>Education:</strong> {parsedData.education?.[0]?.school?.value || 'None'}</div>
              </div>
            </div>
          )}

          <button
            onClick={handleAutofill}
            disabled={!parsedData || loading}
            style={{
              width: '100%',
              background: parsedData ? '#0051a8' : '#dadce0',
              color: 'white',
              border: 'none',
              borderRadius: '20px',
              padding: '10px 16px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: parsedData ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}
          >
            <Sparkles size={16} />
            <span>Launch Autofill Overlay</span>
          </button>
        </div>
      )}
    </div>
  );
}

import { useState, useEffect, useRef } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { streamlintExtensions } from './editor/theme';
import { useVisitorId } from './hooks/useVisitorId';
import { setIssuesEffect } from './editor/annotations';
import { EditorView } from '@codemirror/view';

function App() {
  const [code, setCode] = useState('import os\nprint("Welcome to Streamlint!")');
  const [status, setStatus] = useState('idle');
  const [issues, setIssues] = useState<any[]>([]);
  const [token, setToken] = useState<string | null>(null);
  const editorViewRef = useRef<EditorView | null>(null);

  const visitorId = useVisitorId();

  // Calculate severity counts for the summary card
  const counts = {
    critical: issues.filter(i => i.severity === 'critical').length,
    error: issues.filter(i => i.severity === 'error').length,
    warning: issues.filter(i => i.severity === 'warning').length,
  };

  const handleReview = async () => {
    if (!visitorId) return;
    setStatus('running');
    setIssues([]);
    setToken(null);

    try {
      // 1. Create Session
      //const res = await fetch('http://127.0.0.1:8000/api/sessions/', {
      const res = await fetch('https://streamlint-backend.onrender.com/api/sessions/', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: 'python' })
      });
      const session = await res.json();
      setToken(session.token);

      // 2. Create Review
      //const revRes = await fetch(`http://127.0.0.1:8000/api/sessions/${session.token}/reviews/`, {
      const revRes = await fetch(`https://streamlint-backend.onrender.com/api/sessions/...`, {
        method: 'POST', 
        headers: { 'Content-Type': 'application/json', 'X-Visitor-Id': visitorId },
        body: JSON.stringify({ code, language: 'python', turnstile_token: 'dummy' })
      });
      const review = await revRes.json();

      // 3. Connect WebSocket
      //const ws = new WebSocket(`ws://127.0.0.1:8000/ws/sessions/${session.token}/`);
      const ws = new WebSocket(`wss://streamlint-backend.onrender.com/ws/sessions/...`);
      ws.onopen = () => {
        setTimeout(() => ws.send(JSON.stringify({ action: 'run', review_id: review.id })), 500);
      };
      ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.type === 'issue') setIssues(prev => [...prev, data.payload]);
        if (data.type === 'status') setStatus(data.payload.state);
      };
    } catch (err) {
      console.error(err);
      setStatus('failed');
    }
  };
  useEffect(() => {
    if (editorViewRef.current) {
      editorViewRef.current.dispatch({
        effects: setIssuesEffect.of(issues.map(i => ({ line: i.line, severity: i.severity })))
      });
    }
  }, [issues]);
  return (
    <div className="app-container">
      <header className="header-bar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
             <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5"><line x1="4" y1="6" x2="16" y2="6" /><line x1="4" y1="12" x2="20" y2="12" /><line x1="4" y1="18" x2="12" y2="18" /></svg>
          </div>
          <span style={{ fontSize: '22px', fontWeight: 700, color: 'var(--ink)' }}>Streamlint</span>
        </div>
        <div className={`pill ${status === 'running' ? 'pink' : 'lilac'}`}>{status}</div>
      </header>

      <main className="main-grid">
        
        {/* LEFT COLUMN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          {/* EDITOR CARD */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <select style={{ padding: '8px 12px', borderRadius: '12px', border: '1px solid var(--border-strong)', background: 'var(--bg)', fontWeight: 500 }}>
                <option>Python</option>
              </select>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button 
                  onClick={() => setCode('def divide(a, b):\n    return a / b\n\nprint(divide(10, 0))')}
                  className="btn-secondary"
                  disabled={status === 'running'}
                >
                  Try an example
                </button>
                <button className="btn-primary" onClick={handleReview} disabled={status === 'running'}>
                  {status === 'running' ? 'Reviewing...' : 'Review code'}
                </button>
              </div>
            </div>
            <div style={{ borderRadius: '14px', overflow: 'hidden', border: '1px solid var(--border)' }}>
              <CodeMirror value={code} height="300px" extensions={[python(), ...streamlintExtensions]} onChange={setCode} theme="dark"  onCreateEditor={(view) => { editorViewRef.current = view; }} />
            </div>
            <div style={{ marginTop: '12px', fontSize: '13px', color: 'var(--muted)' }}>
              Sessions are deleted after 7 days. Please don’t paste private code.
            </div>
          </div>

          {/* SHARE CARD */}
          {token && (
            <div className="card" style={{ animation: 'fadeIn 0.3s ease-out' }}>
              <h3 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--ink)', marginBottom: '10px' }}>Share this session</h3>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input 
                  readOnly 
                  value={`${window.location.origin}/s/${token}`} 
                  style={{ flex: 1, padding: '10px 12px', borderRadius: '12px', border: '1px solid var(--border-strong)', background: 'var(--bg)', fontSize: '13px', fontFamily: 'monospace' }} 
                />
                <button 
                  onClick={() => {
                    navigator.clipboard.writeText(`${window.location.origin}/s/${token}`);
                    alert('Link copied!');
                  }}
                  style={{ background: 'var(--ink)', color: 'white', padding: '0 20px', borderRadius: '12px', border: 'none', fontWeight: 600, cursor: 'pointer' }}>
                  Copy
                </button>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--muted)', marginTop: '10px' }}>Anyone with this link sees the same stream live.</p>
            </div>
          )}

          {/* SUMMARY CARD */}
          {issues.length > 0 && (
            <div className="card" style={{ animation: 'fadeIn 0.3s ease-out' }}>
              <h3 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--ink)', marginBottom: '10px' }}>Review summary</h3>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
                {counts.critical > 0 && <span style={{ background: 'var(--accent-deep)', color: 'white', padding: '4px 10px', borderRadius: '999px', fontSize: '12px', fontWeight: 700 }}>{counts.critical} critical</span>}
                {counts.error > 0 && <span style={{ background: 'var(--error)', color: 'white', padding: '4px 10px', borderRadius: '999px', fontSize: '12px', fontWeight: 700 }}>{counts.error} error</span>}
                {counts.warning > 0 && <span style={{ background: 'var(--amber-bg)', color: 'var(--amber-ink)', padding: '4px 10px', borderRadius: '999px', fontSize: '12px', fontWeight: 700 }}>{counts.warning} warning</span>}
              </div>
              <div style={{ height: '10px', background: 'var(--tint)', borderRadius: '999px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: status === 'done' ? '100%' : '40%', background: 'var(--accent)', borderRadius: '999px', transition: 'width 0.3s' }} />
              </div>
              <p style={{ fontSize: '13px', color: 'var(--muted)', marginTop: '10px' }}>
                {status === 'running' ? 'Reviewing…' : status === 'done' ? 'Review complete' : 'Review stopped'}
              </p>
            </div>
          )}

          {/* VIEWERS CARD */}
          {token && (
            <div className="card" style={{ flex: 1, animation: 'fadeIn 0.4s ease-out' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--ink)' }}>In this session</h3>
                <span style={{ background: 'var(--lilac-bg)', color: 'var(--lilac-ink)', padding: '2px 8px', borderRadius: '999px', fontSize: '12px', fontWeight: 600 }}>1 viewing</span>
              </div>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <li style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#FFD1E3', color: '#A61E4D', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '14px' }}>Y</div>
                  <div style={{ flex: 1 }}>
                    <p style={{ fontSize: '15px', fontWeight: 600, color: 'var(--ink)' }}>You</p>
                    <p style={{ fontSize: '13px', color: 'var(--muted)' }}>started the review</p>
                  </div>
                </li>
              </ul>
            </div>
          )}

        </div>

        {/* RIGHT COLUMN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 700 }}>✨ Live review</h2>
          
          {issues.map((issue, i) => (
            <div key={i} className="card result-card" style={{ animation: 'fadeIn 0.2s ease-out' }}>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ 
                  background: issue.severity === 'critical' ? 'var(--accent-deep)' : 
                              issue.severity === 'error' ? 'var(--error)' : 
                              issue.severity === 'warning' ? 'var(--amber-bg)' : 'var(--lilac-bg)', 
                  color: issue.severity === 'warning' ? 'var(--amber-ink)' : 
                         issue.severity === 'info' ? 'var(--lilac-ink)' : 'white',
                  padding: '2px 8px', borderRadius: '999px', fontSize: '12px', fontWeight: 700 
                }}>
                  {issue.severity.toUpperCase()}
                </span>
                <span style={{ color: 'var(--muted)', fontSize: '14px' }}>Line {issue.line}</span>
              </div>
              <p style={{ marginTop: '8px', fontWeight: 500, lineHeight: 1.5 }}>{issue.message}</p>
              {issue.suggestion && <p style={{ marginTop: '8px', fontSize: '13px', background: 'var(--bg)', padding: '8px 12px', borderRadius: '8px', border: '1px dashed var(--border-strong)' }}>💡 {issue.suggestion}</p>}
            </div>
          ))}
        </div>
      </main>
      
      <footer className="footer">Streamlint · paste code, watch the review stream in, share the link</footer>
    </div>
  );
}

export default App;
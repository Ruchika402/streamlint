import { useState, useEffect, useRef } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import { java } from '@codemirror/lang-java';
import { cpp } from '@codemirror/lang-cpp';
import { csharp } from '@replit/codemirror-lang-csharp';
import { go } from '@codemirror/lang-go';
import { rust } from '@codemirror/lang-rust';
import { ruby } from 'codemirror-lang-ruby';
import { php } from '@codemirror/lang-php';
import { sql } from '@codemirror/lang-sql';
import { html } from '@codemirror/lang-html';
import { swift } from '@fazelstudio/codemirror-lang-swift';
import { StreamLanguage } from '@codemirror/language';
import { r as legacyR } from '@codemirror/legacy-modes/mode/r';
import { streamlintExtensions } from '../editor/theme';
import { useVisitorId } from '../hooks/useVisitorId';
import { setIssuesEffect } from '../editor/annotations';
import { EditorView } from '@codemirror/view';
import TurnstileBox from '../components/TurnstileBox';
import Sparkles from '../components/Sparkles';
import { useParams } from 'react-router-dom';

export default function SessionPage() {
  const { token: urlToken } = useParams(); 
  const [code, setCode] = useState('import os\nprint("Welcome to Streamlint!")');
  const [language, setLanguage] = useState('python');
  const [status, setStatus] = useState('idle');
  const [issues, setIssues] = useState<any[]>([]);
  const [token, setToken] = useState<string | null>(null);
  const [viewers, setViewers] = useState<any[]>([]);
  const [captchaToken, setCaptchaToken] = useState<string | null>(null);
  
  const editorViewRef = useRef<EditorView | null>(null);
  const visitorId = useVisitorId();

  // Calculate severity counts for the summary card
  const counts = {
    critical: issues.filter(i => i.severity === 'critical').length,
    error: issues.filter(i => i.severity === 'error').length,
    warning: issues.filter(i => i.severity === 'warning').length,
  };

  const getLanguageExtension = () => {
    switch (language) {
      case 'javascript': return javascript();
      case 'java': return java();
      case 'c': return cpp();
      case 'cpp': return cpp();
      case 'csharp': return csharp();
      case 'go': return go();
      case 'rust': return rust();
      case 'ruby': return ruby();
      case 'php': return php();
      case 'sql': return sql();
      case 'html': return html();
      case 'swift': return swift();
      case 'r': return StreamLanguage.define(legacyR);
      default: return python();
    }
  };

  // Connect to WebSocket if we have a share token in the URL
  useEffect(() => {
    if (urlToken && urlToken !== token) {
      setToken(urlToken);
      setStatus('running'); 
      
      const ws = new WebSocket(`wss://streamlint-backend.onrender.com/ws/sessions/${urlToken}/?visitor_id=${visitorId}`);
      
      ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.type === 'issue') setIssues(prev => [...prev, data.payload]);
        if (data.type === 'status') setStatus(data.payload.state);
        if (data.type === 'presence') setViewers(data.payload.viewers);
      };
      
      return () => ws.close();
    }
  }, [urlToken, visitorId]);

  const handleReview = async () => {
    if (!visitorId) return;
    if (!captchaToken) {
      alert("Please complete the Cloudflare verification at the bottom of the page first.");
      return;
    }
    
    setStatus('running');
    setIssues([]);
    setToken(null);

    try {
      // 1. Create Session
      const res = await fetch('https://streamlint-backend.onrender.com/api/sessions/', {
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: language })
      });
      const session = await res.json();
      setToken(session.token);

      // 2. Create Review
      const revRes = await fetch(`https://streamlint-backend.onrender.com/api/sessions/${session.token}/reviews/`, {
        method: 'POST', 
        headers: { 'Content-Type': 'application/json', 'X-Visitor-Id': visitorId },
        body: JSON.stringify({ code, language: language, turnstile_token: captchaToken })
      });
      
      const review = await revRes.json();

      if (!revRes.ok) {
        setStatus('failed');
        alert(review.error || "Something went wrong");
        return;
      }

      // 3. Connect WebSocket
      const ws = new WebSocket(`wss://streamlint-backend.onrender.com/ws/sessions/${session.token}/?visitor_id=${visitorId}`);
      
      ws.onopen = () => {
        setTimeout(() => ws.send(JSON.stringify({ action: 'run', review_id: review.id })), 500);
      };
      
      ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.type === 'issue') setIssues(prev => [...prev, data.payload]);
        if (data.type === 'status') setStatus(data.payload.state);
        if (data.type === 'presence') setViewers(data.payload.viewers);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected.');
        if (status !== 'done') setStatus('failed');
      };

    } catch (err) {
      console.error(err);
      setStatus('failed');
    }
  };

  // Update CodeMirror annotations when issues change
  useEffect(() => {
    if (editorViewRef.current) {
      editorViewRef.current.dispatch({
        effects: setIssuesEffect.of(issues.map(i => ({ line: i.line, severity: i.severity })))
      });
    }
  }, [issues]);

  return (
    <div className="app-container">
      <Sparkles />
      <header className="header-bar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
             <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5"><line x1="4" y1="6" x2="16" y2="6" /><line x1="4" y1="12" x2="20" y2="12" /><line x1="4" y1="18" x2="12" y2="18" /></svg>
          </div>
          <span style={{ fontSize: '22px', fontWeight: 700, color: 'var(--ink)' }}>Streamlint</span>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {token && (
            <div style={{ background: 'var(--lilac-bg)', color: 'var(--lilac-ink)', padding: '8px 14px', borderRadius: '999px', fontSize: '14px', fontWeight: 600 }}>
              {viewers.length} viewing
            </div>
          )}
          
          <div className={`pill ${status === 'running' ? 'pink' : 'lilac'}`}>
            {status === 'running' && <div className="pill-dot" />}
            {status === 'idle' ? 'Ready' : status.charAt(0).toUpperCase() + status.slice(1)}
          </div>

          {token && (
            <button 
              onClick={() => {
                navigator.clipboard.writeText(`${window.location.origin}/s/${token}`);
                alert('Link copied!');
              }}
              style={{ 
                background: 'white', 
                border: '1px solid var(--border-strong)', 
                color: 'var(--accent-deep)', 
                padding: '0 16px', 
                height: '38px', 
                borderRadius: '12px', 
                fontWeight: 600, 
                fontSize: '14px',
                cursor: 'pointer'
              }}>
              Copy link
            </button>
          )}
        </div>
      </header>

      <main className="main-grid">
        
        {/* LEFT COLUMN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          {/* EDITOR CARD */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <select 
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                style={{ padding: '8px 12px', borderRadius: '12px', border: '1px solid var(--border-strong)', background: 'var(--bg)', fontWeight: 500, color: 'var(--ink)' }}
              >
                <option value="python">Python</option>
                <option value="django">Django</option>
                <option value="c">C</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
                <option value="csharp">C#</option>
                <option value="go">Go</option>
                <option value="rust">Rust</option>
                <option value="ruby">Ruby</option>
                <option value="php">PHP</option>
                <option value="html">HTML</option>
                <option value="swift">Swift</option>
                <option value="r">R</option>
                <option value="sql">SQL</option>
              </select>
              
                            {!urlToken && (
                <div style={{ display: 'flex', gap: '12px' }}>
                  
                  {/* REPLACE THE OLD BUTTON WITH THIS NEW ONE */}
                  <button 
                    onClick={() => {
                      if (language === 'javascript') setCode('function divide(a, b) {\n  return a / b;\n}\nconsole.log(divide(10, 0));');
                      else if (language === 'java') setCode('public class Main {\n  public static void main(String[] args) {\n    int x = 10 / 0;\n  }\n}');
                      else if (language === 'c') setCode('int main() {\n  int* p = NULL;\n  return *p;\n}');
                      else if (language === 'cpp') setCode('int main() {\n  int* p = nullptr;\n  return *p;\n}');
                      else if (language === 'csharp') setCode('public class Program {\n  public static void Main() {\n    int x = 10 / 0;\n  }\n}');
                      else if (language === 'go') setCode('package main\n\nfunc main() {\n  var a int = 10\n  var b int = 0\n  println(a / b)\n}');
                      else if (language === 'rust') setCode('fn main() {\n  let x: i32 = 10;\n  let y: i32 = 0;\n  println!("{}", x / y);\n}');
                      else if (language === 'ruby') setCode('def divide(a, b)\n  a / b\nend\n\nputs divide(10, 0)');
                      else if (language === 'php') setCode('<?php\nfunction divide($a, $b) {\n  return $a / $b;\n}\necho divide(10, 0);\n?>');
                      else if (language === 'html') setCode('<div>\n  <p>Hello World</p>\n</div>');
                      else if (language === 'swift') setCode('let x: Int = 10\nlet y: Int = 0\nlet z = x / y');
                      else if (language === 'sql') setCode('SELECT * FROM users WHERE id = " + user_input + ";');
                      else if (language === 'r') setCode('x <- c(1, 2, 3)\ny <- mean(x)\nprint(y)');
                      else setCode('def divide(a, b):\n    return a / b\n\nprint(divide(10, 0))');
                    }}
                    className="btn-secondary"
                    disabled={status === 'running'}
                  >
                    Try an example
                  </button>

                  <button className="btn-primary" onClick={handleReview} disabled={status === 'running'}>
                    {status === 'running' ? 'Reviewing...' : 'Review code'}
                  </button>
                </div>
              )}
            </div>
            <div style={{ borderRadius: '14px', overflow: 'hidden', border: '1px solid var(--border)' }}>
              <CodeMirror 
                value={code} 
                height="300px" 
                extensions={[getLanguageExtension(), ...streamlintExtensions]} 
                onChange={setCode} 
                theme="dark" 
                onCreateEditor={(view) => { editorViewRef.current = view; }} 
              />
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
                <span style={{ background: 'var(--lilac-bg)', color: 'var(--lilac-ink)', padding: '2px 8px', borderRadius: '999px', fontSize: '12px', fontWeight: 600 }}>{viewers.length} viewing</span>
              </div>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {viewers.map((v, i) => (
                  <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#FFD1E3', color: '#A61E4D', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '14px' }}>
                      {v.nickname.split(' ').map((n: string) => n[0]).join('').substring(0, 2).toUpperCase()}
                    </div>
                    <div style={{ flex: 1 }}>
                      <p style={{ fontSize: '15px', fontWeight: 600, color: 'var(--ink)' }}>{v.nickname}</p>
                      <p style={{ fontSize: '13px', color: 'var(--muted)' }}>{v.status}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* TURNSTILE BOX */}
          {!urlToken && (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '16px 0' }}>
              <TurnstileBox onVerify={(token) => setCaptchaToken(token)} />
            </div>
          )}

        </div>

        {/* RIGHT COLUMN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 700 }}>✨ Live review</h2>
          
          {/* LOADING CARD */}
          {status === 'running' && (
            <div className="card result-card" style={{ animation: 'fadeIn 0.2s ease-out', borderStyle: 'dashed', borderWidth: '1.5px', borderColor: 'var(--border-strong)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--accent)', animation: 'pulse 1.4s infinite' }} />
                <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--muted)' }}>Reviewing your code…</span>
              </div>
              <div style={{ height: '10px', background: 'var(--tint)', borderRadius: '6px', width: '92%', marginBottom: '8px' }} />
              <div style={{ height: '10px', background: 'var(--tint)', borderRadius: '6px', width: '64%' }} />
            </div>
          )}

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
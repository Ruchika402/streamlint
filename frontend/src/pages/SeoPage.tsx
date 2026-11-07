import { Link } from 'react-router-dom';

interface SeoPageProps {
  language: string;
  title: string;
  description: string;
  sampleCode: string;
}

export default function SeoPage({ language, title, description, sampleCode }: SeoPageProps) {
  return (
    <div style={{ padding: '40px 20px', maxWidth: '800px', margin: '0 auto', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
      <Link to="/" style={{ color: 'var(--accent)', textDecoration: 'none', fontWeight: 600 }}>← Back to Streamlint</Link>
      
      <h1 style={{ fontSize: '36px', fontWeight: 800, color: 'var(--ink)', marginTop: '24px', letterSpacing: '-0.5px' }}>
        {title}
      </h1>
      <p style={{ fontSize: '18px', marginTop: '16px', color: 'var(--text)', lineHeight: 1.6 }}>
        {description}
      </p>
      
      <h2 style={{ fontSize: '24px', fontWeight: 700, marginTop: '40px', color: 'var(--ink)' }}>Sample {language} Review</h2>
      <p style={{ color: 'var(--muted)', marginTop: '8px' }}>Here is an example of a bug Streamlint catches instantly:</p>
      <pre style={{ background: 'var(--code-bg)', color: 'var(--code-text)', padding: '20px', borderRadius: '12px', marginTop: '12px', overflowX: 'auto', fontSize: '14px' }}>
        <code>{sampleCode}</code>
      </pre>
      
      <h2 style={{ fontSize: '24px', fontWeight: 700, marginTop: '40px', color: 'var(--ink)' }}>Frequently Asked Questions</h2>
      <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <p style={{ fontWeight: 600, color: 'var(--ink)' }}>How do I use this {language} reviewer?</p>
          <p style={{ color: 'var(--muted)', marginTop: '4px' }}>Just paste your {language} code into the editor, select {language} from the dropdown, and click Review.</p>
        </div>
        <div>
          <p style={{ fontWeight: 600, color: 'var(--ink)' }}>Is it free?</p>
          <p style={{ color: 'var(--muted)', marginTop: '4px' }}>Yes, Streamlint is 100% free. No login or credit card required.</p>
        </div>
      </div>

      <div style={{ marginTop: '40px', padding: '24px', background: 'var(--tint)', borderRadius: '16px', textAlign: 'center' }}>
        <h3 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--accent-deep)' }}>Ready to review your {language} code?</h3>
        <Link to="/" style={{ display: 'inline-block', marginTop: '16px', background: 'var(--accent)', color: 'white', padding: '12px 32px', borderRadius: '12px', textDecoration: 'none', fontWeight: 700, fontSize: '16px', boxShadow: 'var(--shadow-glow)' }}>
          Try Streamlint Now →
        </Link>
      </div>
    </div>
  );
}
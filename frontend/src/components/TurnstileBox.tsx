import { useEffect, useRef } from 'react';

declare global {
  interface Window {
    onloadTurnstileCallback?: () => void;
    turnstile?: any;
  }
}

interface TurnstileBoxProps {
  onVerify: (token: string) => void;
}

export default function TurnstileBox({ onVerify }: TurnstileBoxProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // If Turnstile is already loaded, render it
    if (window.turnstile) {
      renderWidget();
    } else {
      // Otherwise, wait for it to load
      window.onloadTurnstileCallback = () => {
        renderWidget();
      };
    }

    function renderWidget() {
      if (containerRef.current&& !containerRef.current.hasChildNodes()) {
        window.turnstile.render(containerRef.current, {
          // Replace with your real Site Key from Cloudflare Dashboard
          sitekey: import.meta.env.VITE_TURNSTILE_SITE_KEY || '1x00000000000000000000AA', // Test key
          callback: (token: string) => {
            onVerify(token);
          },
          theme: 'light',
        });
      }
    }
  }, [onVerify]);

  return <div ref={containerRef} style={{ marginTop: '16px', marginBottom: '16px' }}></div>;
}
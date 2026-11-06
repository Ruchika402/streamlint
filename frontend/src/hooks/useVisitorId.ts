import { useState, useEffect } from 'react';

export function useVisitorId() {
  const [visitorId, setVisitorId] = useState<string>('');
  
  useEffect(() => {
    try {
      let id = localStorage.getItem('streamlint_visitor_id');
      if (!id) {
        id = crypto.randomUUID();
        localStorage.setItem('streamlint_visitor_id', id);
      }
      setVisitorId(id);
    } catch {
      setVisitorId(crypto.randomUUID());
    }
  }, []);
  
  return visitorId;
}
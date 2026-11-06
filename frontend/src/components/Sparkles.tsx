export default function Sparkles() {
  const sparkles = [
    { size: 22, top: '16px', left: '182px', color: '#FF8FB8', delay: '0s' },
    { size: 13, top: '52px', left: '240px', color: '#FFD27D', delay: '0.7s' },
    { size: 18, top: '12px', left: '46%', color: '#FFB3D1', delay: '1.2s' },
    { size: 24, top: '124px', right: '10px', color: '#FF8FB8', delay: '0.4s' },
    { size: 14, top: '560px', left: '8px', color: '#FFD27D', delay: '1.5s' },
    { size: 20, top: '300px', right: '6px', color: '#FFB3D1', delay: '0.9s' },
    { size: 26, bottom: '56px', left: '9%', color: '#FF8FB8', delay: '1.9s' },
    { size: 16, bottom: '34px', right: '8%', color: '#FFD27D', delay: '0.2s' },
  ];

  return (
    <>
      {sparkles.map((s, i) => (
        <svg
          key={i}
          style={{
            position: 'absolute',
            top: s.top,
            bottom: s.bottom,
            left: s.left,
            right: s.right,
            width: s.size,
            height: s.size,
            fill: s.color,
            pointerEvents: 'none',
            animation: `twinkle 2.6s ease-in-out ${s.delay} infinite`,
            zIndex: -1
            
          }}
          viewBox="0 0 24 24"
        >
          <path d="M12 0C12.9 7.1 16.9 11.1 24 12C16.9 12.9 12.9 16.9 12 24C11.1 16.9 7.1 12.9 0 12C7.1 11.1 11.1 7.1 12 0Z" />
        </svg>
      ))}
    </>
  );
}
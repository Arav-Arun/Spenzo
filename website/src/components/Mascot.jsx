import { useState } from 'react';
import { MASCOT } from '../brand';

// Baaz in a given pose (website/public/mascot/baaz-<pose>.webp).
// Falls back to a simple drawing if a pose image is missing.
export default function Mascot({ pose = 'wave', className = '', title }) {
  const [missing, setMissing] = useState(false);
  const label = title ?? `${MASCOT}, the ${MASCOT === 'Baaz' ? 'baby falcon' : 'mascot'}`;   // title="" marks it decorative
  if (!missing) {
    return <img src={`/mascot/${MASCOT.toLowerCase()}-${pose}.webp`} loading="lazy" decoding="async" alt={label} className={className} onError={() => setMissing(true)} />;
  }
  return <Placeholder pose={pose} className={className} label={label} />;
}

function Placeholder({ pose, className, label }) {
  const ink = '#0E2A1F', leaf = '#3FAE49', deep = '#1D7533', cream = '#E8F5C8', mango = '#FFB627';
  const waving = pose === 'wave' || pose === 'celebrate';
  return (
    <svg viewBox="0 0 200 210" role="img" aria-label={label} className={className} xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="100" cy="200" rx="48" ry="6" fill={ink} opacity=".08" />
      <path d="M78 172 L62 196 L80 188 L86 200 L96 182 Z" fill={deep} stroke={ink} strokeWidth="3" strokeLinejoin="round" />
      <ellipse cx="100" cy="152" rx="46" ry="40" fill={leaf} stroke={ink} strokeWidth="3" />
      <ellipse cx="100" cy="160" rx="29" ry="26" fill={cream} />
      <ellipse cx="58" cy="150" rx="15" ry="27" fill={deep} stroke={ink} strokeWidth="3" transform="rotate(12 58 150)" />
      {waving
        ? <ellipse cx="150" cy="104" rx="14" ry="27" fill={deep} stroke={ink} strokeWidth="3" transform="rotate(-35 150 104)" />
        : <ellipse cx="142" cy="150" rx="15" ry="27" fill={deep} stroke={ink} strokeWidth="3" transform="rotate(-12 142 150)" />}
      <path d="M86 40 Q84 18 96 26 Q100 10 106 26 Q118 16 114 40 Z" fill={leaf} stroke={ink} strokeWidth="3" strokeLinejoin="round" />
      <circle cx="100" cy="90" r="58" fill={leaf} stroke={ink} strokeWidth="3" />
      <ellipse cx="100" cy="104" rx="42" ry="34" fill={cream} />
      <ellipse cx="78" cy="92" rx="13" ry="16" fill="#2B1A10" />
      <ellipse cx="122" cy="92" rx="13" ry="16" fill="#2B1A10" />
      <circle cx="82" cy="86" r="5" fill="#fff" /><circle cx="75" cy="98" r="2.5" fill="#fff" />
      <circle cx="126" cy="86" r="5" fill="#fff" /><circle cx="119" cy="98" r="2.5" fill="#fff" />
      <ellipse cx="62" cy="114" rx="8" ry="5" fill="#FF9FB2" opacity=".7" />
      <ellipse cx="138" cy="114" rx="8" ry="5" fill="#FF9FB2" opacity=".7" />
      <path d="M90 106 Q100 99 110 106 Q108 118 100 124 Q93 117 90 106 Z" fill={mango} stroke={ink} strokeWidth="2.5" strokeLinejoin="round" />
      <ellipse cx="86" cy="192" rx="9" ry="4" fill={mango} stroke={ink} strokeWidth="2" />
      <ellipse cx="114" cy="192" rx="9" ry="4" fill={mango} stroke={ink} strokeWidth="2" />
    </svg>
  );
}

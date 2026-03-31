'use client';

interface HighlightTextProps {
  text: string;
  phrases: { text: string; reason: string }[];
  className?: string;
}

export function HighlightText({
  text,
  phrases,
  className,
}: HighlightTextProps) {
  if (!phrases.length) {
    return <span className={className}>{text}</span>;
  }

  /* Build a regex that matches any of the flagged phrases (case-insensitive) */
  const escaped = phrases
    .map((p) => p.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
    .join('|');
  const regex = new RegExp(`(${escaped})`, 'gi');
  const parts = text.split(regex);

  const reasonMap = Object.fromEntries(
    phrases.map((p) => [p.text.toLowerCase(), p.reason]),
  );

  return (
    <span className={className}>
      {parts.map((part, i) => {
        const reason = reasonMap[part.toLowerCase()];
        if (reason) {
          return (
            <mark
              key={i}
              className="cursor-help rounded bg-amber-500/20 px-0.5 font-semibold text-amber-300 not-italic"
              title={reason}
            >
              {part}
            </mark>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </span>
  );
}
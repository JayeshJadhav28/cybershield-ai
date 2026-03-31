import type { ReactNode } from 'react';

export default function AwarenessLayout({
  children,
}: {
  children: ReactNode;
}) {
  return <div className="mx-auto max-w-4xl">{children}</div>;
}
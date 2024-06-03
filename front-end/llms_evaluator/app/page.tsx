'use client';

import Header from '../components/Header';
import ResponsesGrid from '../components/ResponsesGrid';

export default function Home() {
  return (
    <div style={{ height: '100vh', width: '100vw', display: 'flex', flexDirection: 'column' }}>
      <Header />
      <main style={{ flex: 1, display: 'flex' }}>
        <ResponsesGrid />
      </main>
    </div>
  );
}

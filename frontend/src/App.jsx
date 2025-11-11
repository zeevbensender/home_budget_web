import { useEffect, useState } from 'react';
import { getHealth } from './api.js';

function App() {
  const [status, setStatus] = useState('Loading...');

  useEffect(() => {
    getHealth().then(setStatus);
  }, []);

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem' }}>
      <h1>Home Budget Web</h1>
      <p>Backend health status:</p>
      <p><strong>{status}</strong></p>
    </div>
  );
}

export default App;

import { useEffect, useState } from 'react';
import { getHealth, getExpenses, getIncomes } from './api.js';

function App() {
  const [health, setHealth] = useState('Loading...');
  const [expenses, setExpenses] = useState([]);
  const [incomes, setIncomes] = useState([]);

  useEffect(() => {
    getHealth().then(setHealth);
    getExpenses().then(setExpenses);
    getIncomes().then(setIncomes);
  }, []);

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem' }}>
      <h1>Home Budget Web</h1>
      <p>Backend health: <strong>{health}</strong></p>

      <h2>Expenses</h2>
      <pre>{JSON.stringify(expenses, null, 2)}</pre>

      <h2>Incomes</h2>
      <pre>{JSON.stringify(incomes, null, 2)}</pre>
    </div>
  );
}

export default App;

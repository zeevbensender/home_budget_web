import { useEffect, useState } from 'react';
import { getHealth, getExpenses, getIncomes } from './api.js';
import TableBudget from './components/TableBudget/TableBudget.jsx';

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
      <h1>HBW</h1>
      <p>Backend health: <strong>{health}</strong></p>

      <h2>Expenses</h2>
      <TableBudget data={expenses} type="expense" />

      <h2>Incomes</h2>
      <TableBudget data={incomes} type="income" />
    </div>
  );
}

export default App;

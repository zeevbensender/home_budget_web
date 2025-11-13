import { useEffect, useState } from 'react';
import { getHealth, getExpenses, getIncomes } from './api.js';
import TableBudget from './components/TableBudget/TableBudget.jsx';

function App() {
  const [health, setHealth] = useState('Loading...');
  const [expenses, setExpenses] = useState([]);
  const [incomes, setIncomes] = useState([]);
  const [showAddExpense, setShowAddExpense] = useState(false);

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
      <TableBudget
        data={expenses}
        type="expense"
        showAdd={showAddExpense}
        onCloseAdd={() => setShowAddExpense(false)}
        onCreateLocal={(row) => setExpenses(prev => [...prev, row])}
      />

      {!showAddExpense && (
        <button
          onClick={() => setShowAddExpense(true)}
          style={{
            marginTop: '10px',
            padding: '8px 14px',
            backgroundColor: '#2563eb',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
          }}
        >
          + Add Expense
        </button>
      )}

      <h2>Incomes</h2>
      <TableBudget data={incomes} type="income" />
    </div>
  );
}

export default App;

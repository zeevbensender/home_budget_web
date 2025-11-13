import { useEffect, useState } from 'react';
import { getHealth, getExpenses, getIncomes } from './api.js';
import TableBudget from './components/TableBudget/TableBudget.jsx';
import AddFloatingButton from './components/TableBudget/AddFloatingButton.jsx';

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
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem', paddingBottom: '6rem' }}>
      <h1>HBW</h1>
      <p>Backend health: <strong>{health}</strong></p>

      <h2>Expenses</h2>
      <TableBudget
        data={expenses}
        type="expense"
        showAdd={showAddExpense}
        onCloseAdd={() => setShowAddExpense(false)}
        onCreateLocal={(row) => {
          // keep App-level copy in sync (optional; local table already updates)
          setExpenses(prev => [row, ...prev]);
        }}
      />

      <h2>Incomes</h2>
      <TableBudget data={incomes} type="income" />

      {/* Floating button for PC (adds an Expense row for now) */}
      <AddFloatingButton onClick={() => setShowAddExpense(true)} />
    </div>
  );
}

export default App;

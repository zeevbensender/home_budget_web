import { useEffect, useState } from "react";
import { getHealth, getExpenses, getIncomes } from "./api.js";
import TableBudget from "./components/TableBudget/TableBudget.jsx";

function App() {
  const [health, setHealth] = useState("Loading...");
  const [expenses, setExpenses] = useState([]);
  const [incomes, setIncomes] = useState([]);

  const [showAddExpense, setShowAddExpense] = useState(false);
  const [showAddIncome, setShowAddIncome] = useState(false);

  useEffect(() => {
    getHealth().then(setHealth);
    getExpenses().then(setExpenses);
    getIncomes().then(setIncomes);
  }, []);

  return (
    <div className="container py-4">
      <h1 className="mb-3">HBW</h1>
      <p>
        Backend health: <strong>{health}</strong>
      </p>

      {/* ===== EXPENSES ===== */}
      <section className="mb-5">
        <h2 className="mb-2">Expenses</h2>

        <TableBudget
          data={expenses}
          type="expense"
          showAdd={showAddExpense}
          onCloseAdd={() => setShowAddExpense(false)}
          onCreateLocal={(row) => setExpenses((prev) => [...prev, row])}
          onLocalDelete={(id) => {
              setExpenses((prev) => prev.filter((e) => e.id !== id));
          }}
        />

        {/* Add button BELOW table */}
        {!showAddExpense && (
          <div className="mt-2">
            <button
              onClick={() => setShowAddExpense(true)}
              className="btn btn-primary btn-sm"
            >
              + Add Expense
            </button>
          </div>
        )}
      </section>

      {/* ===== INCOMES ===== */}
      <section>
        <h2 className="mb-2">Incomes</h2>

        <TableBudget
          data={incomes}
          type="income"
          showAdd={showAddIncome}
          onCloseAdd={() => setShowAddIncome(false)}
          onCreateLocal={(row) => setIncomes((prev) => [...prev, row])}
          onLocalDelete={(id) => {
            setIncomes((prev) => prev.filter((i) => i.id !== id));
          }}
        />

        {/* Add button BELOW table */}
        {!showAddIncome && (
          <div className="mt-2">
            <button
              onClick={() => setShowAddIncome(true)}
              className="btn btn-success btn-sm"
            >
              + Add Income
            </button>
          </div>
        )}
      </section>
    </div>
  );
}

export default App;

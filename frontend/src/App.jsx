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

      <section className="mb-5">
        <div className="d-flex justify-content-between align-items-center mb-2">
          <h2 className="mb-0">Expenses</h2>
          {!showAddExpense && (
            <button
              onClick={() => setShowAddExpense(true)}
              className="btn btn-primary btn-sm"
            >
              + Add Expense
            </button>
          )}
        </div>

        <TableBudget
          data={expenses}
          type="expense"
          showAdd={showAddExpense}
          onCloseAdd={() => setShowAddExpense(false)}
          onCreateLocal={(row) => setExpenses((prev) => [...prev, row])}
        />
      </section>

      <section>
        <h2 className="mb-2">Incomes</h2>
          {!showAddIncome && (
           <button
             onClick={() => setShowAddIncome(true)}
             className="btn btn-success btn-sm"
           >
             + Add Income
           </button>
         )}
        <TableBudget data={incomes}
            type="income"
            showAdd={showAddIncome}
            onCloseAdd={() => setShowAddIncome(false)}
            onCreateLocal={(row) => setIncomes((prev) => [...prev, row])}
        />
      </section>
    </div>
  );
}

export default App;

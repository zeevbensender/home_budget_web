import React, { useEffect, useState } from "react";
import TableBudget from "./components/TableBudget/TableBudget.jsx";
import { getExpenses, getIncomes, createExpense, createIncome } from "./api.js";
import "bootstrap/dist/css/bootstrap.min.css";

export default function App() {
  const [expenses, setExpenses] = useState([]);
  const [incomes, setIncomes] = useState([]);

  const [showAddExpense, setShowAddExpense] = useState(false);
  const [showAddIncome, setShowAddIncome] = useState(false);

  // ---------------------------
  // LOAD DATA
  // ---------------------------
  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    const [e, i] = await Promise.all([getExpenses(), getIncomes()]);
    setExpenses(e);
    setIncomes(i);
  }

  // ---------------------------
  // LOCAL DELETE HANDLERS
  // ---------------------------
  const deleteLocalExpense = (id) =>
    setExpenses((prev) => prev.filter((e) => e.id !== id));

  const deleteLocalIncome = (id) =>
    setIncomes((prev) => prev.filter((i) => i.id !== id));

  const deleteLocalExpenseBulk = (ids) =>
    setExpenses((prev) => prev.filter((e) => !ids.includes(e.id)));

  const deleteLocalIncomeBulk = (ids) =>
    setIncomes((prev) => prev.filter((i) => !ids.includes(i.id)));

  // ---------------------------
  // CREATE HANDLERS
  // ---------------------------
  const addExpenseLocal = async (row) => {
    await createExpense(row);
    const fresh = await getExpenses();
    setExpenses(fresh);
  };

  const addIncomeLocal = async (row) => {
    await createIncome(row);
    const fresh = await getIncomes();
    setIncomes(fresh);
  };

  // ---------------------------
  // UI
  // ---------------------------
  return (
    <div className="container py-4">

      <h3>Expenses</h3>

      <button
        className="btn btn-primary btn-sm mb-2"
        onClick={() => setShowAddExpense(true)}
      >
        Add Expense
      </button>

      <TableBudget
        data={expenses}
        type="expense"
        showAdd={showAddExpense}
        onCloseAdd={() => setShowAddExpense(false)}
        onCreateLocal={addExpenseLocal}
        onLocalDelete={deleteLocalExpense}
        onLocalDeleteBulk={deleteLocalExpenseBulk}
      />

      <hr />

      <h3>Income</h3>

      <button
        className="btn btn-primary btn-sm mb-2"
        onClick={() => setShowAddIncome(true)}
      >
        Add Income
      </button>

      <TableBudget
        data={incomes}
        type="income"
        showAdd={showAddIncome}
        onCloseAdd={() => setShowAddIncome(false)}
        onCreateLocal={addIncomeLocal}
        onLocalDelete={deleteLocalIncome}
        onLocalDeleteBulk={deleteLocalIncomeBulk}
      />

    </div>
  );
}

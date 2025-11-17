import React, { useEffect, useState } from "react";
import TableBudget from "./components/TableBudget/TableBudget.jsx";
import { getExpenses, getIncomes, createExpense, createIncome } from "./api.js";
import "bootstrap/dist/css/bootstrap.min.css";
import AddFloatingButton from "./components/TableBudget/AddFloatingButton.jsx";
import useIsMobile from "./hooks/useIsMobile.js";

export default function App() {
  const [expenses, setExpenses] = useState([]);
  const [incomes, setIncomes] = useState([]);

  const [showAddExpense, setShowAddExpense] = useState(false);
  const [showAddIncome, setShowAddIncome] = useState(false);

  const isMobile = useIsMobile();
  console.log("isMobile:", isMobile);

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

  function handleMobileAddClick() {
    console.log("Add transaction (mobile) clicked");
  }

  // ---------------------------
  // UI
  // ---------------------------
  return (
    <>
      <div className="container py-4">

        <h3>Expenses</h3>

        <button
          className="btn btn-primary btn-sm mb-2"
          onClick={() => setShowAddExpense(true)}
        >
          Add Expense
        </button>
        <div className="mobile-scroll">
        <TableBudget
          data={expenses}
          type="expense"
          showAdd={showAddExpense}
          onCloseAdd={() => setShowAddExpense(false)}
          onCreateLocal={addExpenseLocal}
          onLocalDelete={deleteLocalExpense}
          onLocalDeleteBulk={deleteLocalExpenseBulk}
        />
        </div>
        <hr />

        <h3>Income</h3>

        <button
          className="btn btn-primary btn-sm mb-2"
          onClick={() => setShowAddIncome(true)}
        >
          Add Income
        </button>
        <div className="mobile-scroll">
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
      </div>

      {isMobile && (
        <AddFloatingButton
          onClick={handleMobileAddClick}
          title="Add"
        />
      )}
    </>
  );
}

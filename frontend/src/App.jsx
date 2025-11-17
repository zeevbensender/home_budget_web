import React, { useEffect, useState } from "react";
import TableBudget from "./components/TableBudget/TableBudget.jsx";
import { getExpenses, getIncomes, createExpense, createIncome } from "./api.js";
import "bootstrap/dist/css/bootstrap.min.css";

import AddFloatingButton from "./components/TableBudget/AddFloatingButton.jsx";
import useIsMobile from "./hooks/useIsMobile.js";
import TransactionModal from "./components/TransactionModal.jsx";

export default function App() {
  const [expenses, setExpenses] = useState([]);
  const [incomes, setIncomes] = useState([]);

  const [showAddExpense, setShowAddExpense] = useState(false);
  const [showAddIncome, setShowAddIncome] = useState(false);

  const isMobile = useIsMobile();

  // ---------------------------
  // MOBILE MODAL (Step 1.2 + 1.3)
  // ---------------------------
  const [mobileModalOpen, setMobileModalOpen] = useState(false);
  const [mobileInitialData, setMobileInitialData] = useState(null);

  // ---------------------------
  // TOAST (Step 1.3)
  // ---------------------------
  const [toast, setToast] = useState(null);

  function handleMobileAddClick() {
    setMobileInitialData(null);
    setMobileModalOpen(true);
  }

  async function handleMobileAddSubmit(formData) {
    try {
      if (formData.type === "expense") {
        await createExpense(formData);
        const fresh = await getExpenses();
        setExpenses(fresh);
      } else {
        await createIncome(formData);
        const fresh = await getIncomes();
        setIncomes(fresh);
      }

      setToast("Transaction added");
      setTimeout(() => setToast(null), 2500);

    } catch (err) {
      console.error("Mobile add error:", err);
      setToast("Error adding transaction");
      setTimeout(() => setToast(null), 3500);
    }

    setMobileModalOpen(false);
  }

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

      {/* MOBILE FLOATING ACTION BUTTON */}
      {isMobile && (
        <AddFloatingButton
          onClick={handleMobileAddClick}
          title="Add"
        />
      )}

      {/* MOBILE ADD/EDIT TRANSACTION MODAL */}
      <TransactionModal
        isOpen={mobileModalOpen}
        mode={mobileInitialData ? "edit" : "add"}
        initialData={mobileInitialData}
        onClose={() => setMobileModalOpen(false)}
        onSubmit={handleMobileAddSubmit}
      />

      {/* TOAST */}
      {toast && (
        <div className="mobile-toast">
          {toast}
        </div>
      )}
    </>
  );
}

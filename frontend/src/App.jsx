/**
 * App.jsx - Main application component
 * 
 * This component manages the home budget application's main UI,
 * displaying both expenses and incomes in separate tables.
 * 
 * Architecture:
 * - Uses useTransactions hook for data management (eliminates duplicate CRUD logic)
 * - Uses useToast hook for user feedback
 * - Handles both desktop and mobile views with different interaction patterns
 * - Desktop: inline add/edit in tables
 * - Mobile: modal-based add/edit with floating action button
 */

import React, { useState } from "react";
import TableBudget from "./components/TableBudget/TableBudget.jsx";
import { useTransactions } from "./hooks/useTransactions.js";
import { useToast } from "./hooks/useToast.js";
import Toast from "./components/ui/Toast.jsx";
import "bootstrap/dist/css/bootstrap.min.css";

import AddFloatingButton from "./components/TableBudget/AddFloatingButton.jsx";
import useIsMobile from "./hooks/useIsMobile.js";
import TransactionModal from "./components/TransactionModal.jsx";

export default function App() {
  // ---------------------------
  // DATA MANAGEMENT - Using generic hooks to eliminate duplication
  // ---------------------------
  const expenses = useTransactions('expense');
  const incomes = useTransactions('income');

  // ---------------------------
  // UI FEEDBACK - Centralized toast management
  // ---------------------------
  const toast = useToast();

  // ---------------------------
  // UI STATE
  // ---------------------------
  const [showAddExpense, setShowAddExpense] = useState(false);
  const [showAddIncome, setShowAddIncome] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const isMobile = useIsMobile();

  // ---------------------------
  // MOBILE MODAL STATE
  // ---------------------------
  const [mobileModalOpen, setMobileModalOpen] = useState(false);
  const [mobileInitialData, setMobileInitialData] = useState(null);

  // ---------------------------
  // MOBILE ADD FLOW
  // ---------------------------
  function handleMobileAddClick() {
    setMobileInitialData(null);
    setMobileModalOpen(true);
  }

  /**
   * Handle mobile add submission
   * Generic handler that works for both expenses and incomes
   */
  async function handleMobileAddSubmit(formData) {
    try {
      // Use the appropriate hook based on transaction type
      const transactionHook = formData.type === "expense" ? expenses : incomes;
      await transactionHook.add(formData);

      toast.show("Transaction added", "success");
    } catch (err) {
      console.error("Mobile add error:", err);
      toast.show("Error adding transaction", "error", 3500);
    }

    setMobileModalOpen(false);
  }

  // ---------------------------
  // MOBILE EDIT FLOW
  // ---------------------------
  function handleMobileEdit(rowData) {
    setMobileInitialData(rowData);
    setMobileModalOpen(true);
  }

  /**
   * Handle mobile edit submission
   * Generic handler that works for both expenses and incomes
   */
  async function handleMobileEditSubmit(formData) {
    try {
      // Use the appropriate hook based on transaction type
      const transactionHook = formData.type === "expense" ? expenses : incomes;
      await transactionHook.update(formData.id, formData);

      toast.show("Transaction updated", "success");
    } catch (err) {
      console.error("Mobile edit error:", err);
      toast.show("Error updating", "error", 3500);
    }

    setMobileModalOpen(false);
  }

  // ---------------------------
  // DESKTOP CREATE HANDLERS
  // ---------------------------
  /**
   * Add expense handler for desktop inline add
   */
  const addExpenseLocal = async (row) => {
    try {
      await expenses.add(row);
    } catch (err) {
      console.error("Error adding expense:", err);
      toast.show("Error adding expense", "error");
    }
  };

  /**
   * Add income handler for desktop inline add
   */
  const addIncomeLocal = async (row) => {
    try {
      await incomes.add(row);
    } catch (err) {
      console.error("Error adding income:", err);
      toast.show("Error adding income", "error");
    }
  };

  // ---------------------------
  // UI
  // ---------------------------
  return (
    <>
      <div className="container py-4">

        <h3>Expenses</h3>

        <div className="mobile-scroll">
          <TableBudget
            data={expenses.data}
            type="expense"
            showAdd={showAddExpense}
            onCloseAdd={() => setShowAddExpense(false)}
            onCreateLocal={addExpenseLocal}
            onLocalDelete={expenses.remove}
            onLocalDeleteBulk={expenses.bulkRemove}
            onMobileEdit={handleMobileEdit}
            onDeleteDialogChange={setDeleteDialogOpen}
          />
        </div>

        {/* ADD EXPENSE — now BELOW table */}
        {!isMobile && !showAddExpense && (
          <button
            className="btn btn-primary btn-sm mt-2"
            onClick={() => setShowAddExpense(true)}
          >
            Add Expense
          </button>
        )}

        <hr />

        <h3>Income</h3>

        <div className="mobile-scroll">
          <TableBudget
            data={incomes.data}
            type="income"
            showAdd={showAddIncome}
            onCloseAdd={() => setShowAddIncome(false)}
            onCreateLocal={addIncomeLocal}
            onLocalDelete={incomes.remove}
            onLocalDeleteBulk={incomes.bulkRemove}
            onMobileEdit={handleMobileEdit}
            onDeleteDialogChange={setDeleteDialogOpen}
          />
        </div>

        {/* ADD INCOME — now BELOW table */}
        {!isMobile && !showAddIncome && (
          <button
            className="btn btn-primary btn-sm mt-2"
            onClick={() => setShowAddIncome(true)}
          >
            Add Income
          </button>
        )}
      </div>

      {/* MOBILE FLOATING ACTION BUTTON */}
      {isMobile && !deleteDialogOpen && (
        <AddFloatingButton
          onClick={handleMobileAddClick}
          title="Add"
        />
      )}

      {/* MOBILE MODAL */}
      <TransactionModal
        isOpen={mobileModalOpen}
        mode={mobileInitialData ? "edit" : "add"}
        initialData={mobileInitialData}
        onClose={() => setMobileModalOpen(false)}
        onSubmit={mobileInitialData ? handleMobileEditSubmit : handleMobileAddSubmit}
      />

      {/* TOAST - Using new Toast component */}
      <Toast message={toast.message} type={toast.type} />
    </>
  );
}

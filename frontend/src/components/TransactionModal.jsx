import React, { useState, useEffect } from "react";
import "./transactionModal.css";

export default function TransactionModal({
  isOpen,
  mode = "add",                // "add" | "edit"
  initialData = null,          // for edit
  onClose,
  onSubmit,
}) {
  const [formData, setFormData] = useState({
    type: "expense",
    date: "",
    business: "",
    category: "",
    amount: "",
    account: "",
    notes: "",
  });

  // Prefill on edit
  useEffect(() => {
    if (initialData) {
      setFormData({
        type: initialData.type || "expense",
        date: initialData.date || "",
        business: initialData.business || "",
        category: initialData.category || "",
        amount: initialData.amount || "",
        account: initialData.account || "",
        notes: initialData.notes || "",
      });
    }
  }, [initialData]);

  if (!isOpen) return null;

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
     onSubmit(formData);
  };

  return (
    <div className="tm-overlay" onClick={onClose}>
      <div
        className="tm-sheet"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="tm-handle" />

        <h4 className="tm-title">
          {mode === "add" ? "Add Transaction" : "Edit Transaction"}
        </h4>

        {/* TYPE */}
        <div className="tm-field">
          <label>Type</label>
          <select
            value={formData.type}
            onChange={e => handleChange("type", e.target.value)}
          >
            <option value="expense">Expense</option>
            <option value="income">Income</option>
          </select>
        </div>

        {/* DATE */}
        <div className="tm-field">
          <label>Date</label>
          <input
            type="date"
            value={formData.date}
            onChange={e => handleChange("date", e.target.value)}
          />
        </div>

        {/* BUSINESS only for EXPENSE */}
        {formData.type === "expense" && (
          <div className="tm-field">
            <label>Business</label>
            <input
              type="text"
              value={formData.business}
              onChange={e => handleChange("business", e.target.value)}
            />
          </div>
        )}

        {/* CATEGORY */}
        <div className="tm-field">
          <label>Category</label>
          <input
            type="text"
            value={formData.category}
            onChange={e => handleChange("category", e.target.value)}
          />
        </div>

        {/* AMOUNT */}
        <div className="tm-field">
          <label>Amount</label>
          <input
            type="number"
            step="0.01"
            value={formData.amount}
            onChange={e => handleChange("amount", e.target.value)}
          />
        </div>

        {/* ACCOUNT */}
        <div className="tm-field">
          <label>Account</label>
          <input
            type="text"
            value={formData.account}
            onChange={e => handleChange("account", e.target.value)}
          />
        </div>

        {/* NOTES */}
        <div className="tm-field">
          <label>Notes</label>
          <textarea
            rows="2"
            value={formData.notes}
            onChange={e => handleChange("notes", e.target.value)}
          />
        </div>

        {/* BUTTONS */}
        <div className="tm-buttons">
          <button className="tm-cancel" onClick={onClose}>
            Cancel
          </button>
          <button className="tm-save" onClick={handleSave}>
            Save
          </button>
        </div>

      </div>
    </div>
  );
}

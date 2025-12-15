import React, { useState, useEffect } from "react";
import "./transactionModal.css";

export default function TransactionModal({
  isOpen,
  mode = "add",             // "add" | "edit"
  initialData = null,
  onClose,
  onSubmit,                 // parent handles local state refresh
}) {
  const emptyState = {
    type: "expense",
    date: "",
    business: "",
    category: "",
    amount: "",
    account: "",
    currency: "₪",
    notes: "",
  };

  const [formData, setFormData] = useState(emptyState);

  // Prefill data when editing
  useEffect(() => {
    if (!isOpen) return;

    if (mode === "edit" && initialData) {
      setFormData({
        type: initialData.type ||  (initialData.business ? "expense" : "income"),
        date: initialData.date || "",
        business: initialData.business || "",
        category: initialData.category || "",
        amount: initialData.amount || "",
        account: initialData.account || "",
        currency: initialData.currency || "₪",
        notes: initialData.notes || "",
        id: initialData.id,
      });
    } else {
      setFormData(emptyState);
    }
  }, [isOpen, mode, initialData]);

  if (!isOpen) return null;

  const handleChange = (field, value) => {
    setFormData((p) => ({ ...p, [field]: value }));
  };

  const handleSave = async () => {
    const amountNum = parseFloat(formData.amount);

    if (!formData.date || Number.isNaN(amountNum)) {
      alert("Date and amount are required");
      return;
    }

    const payload = {
      date: formData.date,
      category: formData.category,
      amount: amountNum,
      account: formData.account,
      currency: formData.currency || "₪",
      notes: formData.notes,
    };

    if (formData.type === "expense") {
      payload.business = formData.business || "";
    }

    // Add id for edit mode
    if (mode === "edit" && formData.id) {
      payload.id = formData.id;
    }

    // Add type to payload for parent to determine which API to call
    payload.type = formData.type;

    try {
      // Let parent handle the API call
      await onSubmit?.(payload);
      onClose();

    } catch (err) {
      console.error("Save error:", err);
      alert("Failed to save transaction.");
    }
  };

  return (
    <div className="tm-overlay" onClick={onClose}>
      <div className="tm-sheet" onClick={(e) => e.stopPropagation()}>
        <div className="tm-handle" />

        <h4 className="tm-title">
          {mode === "add" ? "Add Transaction" : "Edit Transaction"}
        </h4>

        {/* TYPE */}
        <div className="tm-field">
          <label>Type</label>
          <select
            value={formData.type}
            onChange={(e) => handleChange("type", e.target.value)}
            disabled={mode === "edit"}   // prevent switching type on edit
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
            onChange={(e) => handleChange("date", e.target.value)}
          />
        </div>

        {/* BUSINESS (expense only) */}
        {formData.type === "expense" && (
          <div className="tm-field">
            <label>Business</label>
            <input
              type="text"
              value={formData.business}
              onChange={(e) => handleChange("business", e.target.value)}
            />
          </div>
        )}

        {/* CATEGORY */}
        <div className="tm-field">
          <label>Category</label>
          <input
            type="text"
            value={formData.category}
            onChange={(e) => handleChange("category", e.target.value)}
          />
        </div>

        {/* AMOUNT */}
        <div className="tm-field">
          <label>Amount</label>
          <input
            type="number"
            step="0.01"
            value={formData.amount}
            onChange={(e) => handleChange("amount", e.target.value)}
          />
        </div>

        {/* ACCOUNT */}
        <div className="tm-field">
          <label>Account</label>
          <input
            type="text"
            value={formData.account}
            onChange={(e) => handleChange("account", e.target.value)}
          />
        </div>

        {/* CURRENCY */}
        <div className="tm-field">
          <label>Currency</label>
          <input
            type="text"
            value={formData.currency}
            onChange={(e) => handleChange("currency", e.target.value)}
          />
        </div>

        {/* NOTES */}
        <div className="tm-field">
          <label>Notes</label>
          <textarea
            rows="2"
            value={formData.notes}
            onChange={(e) => handleChange("notes", e.target.value)}
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

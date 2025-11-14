import { useState, memo, useCallback } from "react";

function AddRowComponent({ type = "expense", onSave, onCancel }) {
  const [form, setForm] = useState({
    date: "",
    category: "",
    amount: "",
    account: "",
    currency: "₪",
    notes: "",
    business: "",
  });

  const updateField = useCallback((k, v) => {
    setForm((p) => ({ ...p, [k]: v }));
  }, []);

  const save = () => {
    const base = {
      id: Math.floor(Math.random() * 1e9),
      date: form.date,
      category: form.category,
      amount: parseFloat(form.amount) || 0,
      account: form.account,
      currency: form.currency || "₪",
      notes: form.notes,
    };
    const row = type === "expense" ? { ...base, business: form.business } : base;
    onSave?.(row);
  };

  return (
    <div className="card border-primary mt-3">
      <div className="card-body p-3">
        <form
          className="row g-2 align-items-end"
          onSubmit={(e) => {
            e.preventDefault();
            save();
          }}
        >
          <div className="col-md-2">
            <label className="form-label small">Date</label>
            <input
              type="date"
              className="form-control form-control-sm"
              value={form.date}
              onChange={(e) => updateField("date", e.target.value)}
            />
          </div>

          {type === "expense" && (
            <div className="col-md-2">
              <label className="form-label small">Business</label>
              <input
                type="text"
                className="form-control form-control-sm"
                value={form.business}
                onChange={(e) => updateField("business", e.target.value)}
              />
            </div>
          )}

          <div className="col-md-2">
            <label className="form-label small">Category</label>
            <input
              type="text"
              className="form-control form-control-sm"
              value={form.category}
              onChange={(e) => updateField("category", e.target.value)}
            />
          </div>

          <div className="col-md-1">
            <label className="form-label small">Amount</label>
            <input
              type="number"
              step="0.01"
              className="form-control form-control-sm text-end"
              value={form.amount}
              onChange={(e) => updateField("amount", e.target.value)}
            />
          </div>

          <div className="col-md-2">
            <label className="form-label small">Account</label>
            <input
              type="text"
              className="form-control form-control-sm"
              value={form.account}
              onChange={(e) => updateField("account", e.target.value)}
            />
          </div>

          <div className="col-md-1">
            <label className="form-label small">Currency</label>
            <input
              type="text"
              className="form-control form-control-sm"
              value={form.currency}
              onChange={(e) => updateField("currency", e.target.value)}
            />
          </div>

          <div className="col-md-2">
            <label className="form-label small">Notes</label>
            <input
              type="text"
              className="form-control form-control-sm"
              value={form.notes}
              onChange={(e) => updateField("notes", e.target.value)}
            />
          </div>

          <div className="col-auto">
            <button type="submit" className="btn btn-success btn-sm me-2">
              Save
            </button>
            <button
              type="button"
              onClick={onCancel}
              className="btn btn-outline-secondary btn-sm"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default memo(AddRowComponent);

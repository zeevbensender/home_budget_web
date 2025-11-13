import { useState } from "react";

/**
 * Inline add-row at top of table.
 * Props:
 * - type: "expense" | "income"
 * - onSave(row)  -> called with new row object
 * - onCancel()
 */
export default function AddRow({ type = "expense", onSave, onCancel }) {
  // shared schema
  const [date, setDate] = useState("");
  const [category, setCategory] = useState("");
  const [amount, setAmount] = useState("");
  const [account, setAccount] = useState("");
  const [currency, setCurrency] = useState("₪");
  const [notes, setNotes] = useState("");

  // expense-only
  const [business, setBusiness] = useState("");

  const save = () => {
    const base = {
      id: Math.floor(Math.random() * 1e9), // temp id
      date,
      category,
      amount: parseFloat(amount) || 0,
      account,
      currency: currency || "₪",
      notes,
    };
    const row = type === "expense" ? { ...base, business } : base;
    onSave?.(row);
  };

  const Cell = ({ children }) => (
    <td style={{ borderBottom: "1px solid #f0f0f0", padding: "8px" }}>{children}</td>
  );

  return (
    <tr style={{ background: "#f8fbff" }}>
      <Cell>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          style={{ width: "100%" }}
        />
      </Cell>

      {type === "expense" && (
        <Cell>
          <input
            type="text"
            placeholder="Business / Payee"
            value={business}
            onChange={(e) => setBusiness(e.target.value)}
            style={{ width: "100%" }}
          />
        </Cell>
      )}

      <Cell>
        <input
          type="text"
          placeholder="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          style={{ width: "100%" }}
        />
      </Cell>

      <Cell>
        <input
          type="number"
          step="0.01"
          placeholder="0.00"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          style={{ width: "100%" }}
        />
      </Cell>

      <Cell>
        <input
          type="text"
          placeholder="Account"
          value={account}
          onChange={(e) => setAccount(e.target.value)}
          style={{ width: "100%" }}
        />
      </Cell>

      <Cell>
        <input
          type="text"
          placeholder="₪"
          value={currency}
          onChange={(e) => setCurrency(e.target.value)}
          style={{ width: "100%" }}
        />
      </Cell>

      <Cell>
        <input
          type="text"
          placeholder="Notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          style={{ width: "100%" }}
        />
      </Cell>

      {/* Action buttons */}
      <Cell>
        <div style={{ display: "flex", gap: "8px" }}>
          <button onClick={save} style={{ padding: "6px 10px" }}>Save</button>
          <button onClick={onCancel} style={{ padding: "6px 10px" }}>Cancel</button>
        </div>
      </Cell>
    </tr>
  );
}

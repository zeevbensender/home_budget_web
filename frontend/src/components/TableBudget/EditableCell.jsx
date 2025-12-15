import { useState } from "react";

export default function EditableCell({ value, field, rowIndex, updateCell, formatter }) {
  const [editing, setEditing] = useState(false);
  const [localValue, setLocalValue] = useState(value ?? "");

  // Check if we're in mobile mode (window width < 768px)
  const isMobile = typeof window !== "undefined" && window.innerWidth < 768;

  const commit = () => {
    setEditing(false);
    const formatted = formatter ? formatter(localValue) : localValue;
    // Only call updateCell if it's provided (desktop mode)
    if (updateCell) {
      updateCell(rowIndex, field, formatted);
    }
  };

  // In mobile mode, render as read-only text (no inline editing)
  // Mobile editing is handled by TransactionModal via row click
  if (isMobile) {
    return <span>{value ?? ""}</span>;
  }

  return editing ? (
    <input
      type="text"
      value={localValue}
      autoFocus
      onChange={(e) => setLocalValue(e.target.value)}
      onBlur={commit}
      onKeyDown={(e) => e.key === "Enter" && commit()}
      style={{ width: "100%", boxSizing: "border-box" }}
    />
  ) : (
    <span onClick={() => setEditing(true)} style={{ cursor: "pointer" }}>
      {value ?? ""}
    </span>
  );
}

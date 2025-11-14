import { useState } from "react";

export default function EditableCell({ value, field, rowIndex, updateCell, formatter }) {
  const [editing, setEditing] = useState(false);
  const [localValue, setLocalValue] = useState(value ?? "");

  const commit = () => {
    setEditing(false);
    const formatted = formatter ? formatter(localValue) : localValue;
    updateCell(rowIndex, field, formatted);
  };

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

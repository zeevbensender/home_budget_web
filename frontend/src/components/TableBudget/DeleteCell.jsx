import React, { useState } from "react";

export default function DeleteCell({ row, type, onDelete }) {
  const [confirm, setConfirm] = useState(false);

  if (!confirm) {
    return (
      <span
        style={{ cursor: "pointer", opacity: 0.4 }}
        onClick={() => setConfirm(true)}
      >
        🗑️
      </span>
    );
  }

  return (
    <span className="bg-light border px-2 py-1 rounded">
      Delete?
      <button
        className="btn btn-sm btn-danger ms-2"
        onClick={() => onDelete(row.original.id)}
      >
        Delete
      </button>
      <button
        className="btn btn-sm btn-secondary ms-2"
        onClick={() => setConfirm(false)}
      >
        Cancel
      </button>
    </span>
  );
}

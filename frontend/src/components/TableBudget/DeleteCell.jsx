import React, { useState } from "react";

export default function DeleteCell({ row, onDelete }) {
  const [confirm, setConfirm] = useState(false);

  if (!confirm) {
    return (
      <span
        style={{ cursor: "pointer", opacity: 0.4 }}
        onClick={(e) => {
          e.stopPropagation();
          setConfirm(true);
        }}
      >
        🗑️
      </span>
    );
  }

  return (
    <span
      className="bg-light border px-2 py-1 rounded"
      onClick={(e) => e.stopPropagation()}
    >
      Delete?
      <button
        className="btn btn-sm btn-danger ms-2"
        onClick={(e) => {
          e.stopPropagation();
          onDelete(row.original.id);
        }}
      >
        Delete
      </button>
      <button
        className="btn btn-sm btn-secondary ms-2"
        onClick={(e) => {
          e.stopPropagation();
          setConfirm(false);
        }}
      >
        Cancel
      </button>
    </span>
  );
}

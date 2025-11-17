// frontend/src/components/TableBudget/AddFloatingButton.jsx

import React from "react";
import "./AddFloatingButton.css";   // ensure this exists

export default function AddFloatingButton({ onClick, title = "Add" }) {
  return (
    <button className="fab-btn" onClick={onClick} aria-label={title}>
      <i className="bi bi-receipt"></i>
    </button>
  );
}

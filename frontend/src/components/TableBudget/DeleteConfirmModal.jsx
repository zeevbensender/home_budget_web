import React from "react";
import "./DeleteConfirmModal.css";

export default function DeleteConfirmModal({ isOpen, onConfirm, onCancel }) {
  if (!isOpen) return null;

  return (
    <div className="dcm-overlay" onClick={onCancel}>
      <div className="dcm-sheet" onClick={(e) => e.stopPropagation()}>
        <div className="dcm-handle"></div>
        <h5 className="dcm-title">Delete Transaction?</h5>
        <p className="dcm-message">This action cannot be undone.</p>
        <div className="dcm-buttons">
          <button className="dcm-cancel" onClick={onCancel}>
            Cancel
          </button>
          <button className="dcm-delete" onClick={onConfirm}>
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}

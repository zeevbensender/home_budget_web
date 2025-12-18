import React, { useState, useEffect, useRef } from "react";
import useIsMobile from "../../hooks/useIsMobile.js";
import DeleteConfirmModal from "./DeleteConfirmModal.jsx";

export default function DeleteCell({ row, onDelete, onDeleteDialogChange }) {
  const [confirm, setConfirm] = useState(false);
  const isMobile = useIsMobile();
  const isInitialMount = useRef(true);

  useEffect(() => {
    // Skip notification on initial mount
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    
    // Notify parent when dialog state changes (only on mobile)
    if (isMobile && onDeleteDialogChange) {
      onDeleteDialogChange(confirm);
    }
  }, [confirm, isMobile, onDeleteDialogChange]);

  const handleTrashClick = (e) => {
    e.stopPropagation();
    setConfirm(true);
  };

  const handleDelete = (e) => {
    e?.stopPropagation();
    onDelete(row.original.id);
    setConfirm(false);
  };

  const handleCancel = (e) => {
    e?.stopPropagation();
    setConfirm(false);
  };

  // Mobile: Use modal
  if (isMobile) {
    return (
      <>
        <span
          style={{ cursor: "pointer", opacity: 0.4 }}
          onClick={handleTrashClick}
        >
          🗑️
        </span>
        <DeleteConfirmModal
          isOpen={confirm}
          onConfirm={handleDelete}
          onCancel={handleCancel}
        />
      </>
    );
  }

  // Desktop: Inline buttons
  if (!confirm) {
    return (
      <span
        style={{ cursor: "pointer", opacity: 0.4 }}
        onClick={handleTrashClick}
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
        onClick={handleDelete}
      >
        Delete
      </button>
      <button
        className="btn btn-sm btn-secondary ms-2"
        onClick={handleCancel}
      >
        Cancel
      </button>
    </span>
  );
}

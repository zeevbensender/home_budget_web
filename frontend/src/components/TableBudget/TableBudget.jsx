/**
 * TableBudget component
 * 
 * Generic table component for displaying and managing transactions (expenses or incomes).
 * Supports both desktop (inline editing) and mobile (tap to edit) interactions.
 * 
 * Features:
 * - Inline add row (desktop)
 * - Single and bulk delete operations
 * - Select mode for bulk operations
 * - Mobile-friendly tap interaction
 * - Generic implementation works for both expenses and incomes
 */

import React, { useState, useEffect, useMemo, useCallback } from "react";
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
} from "@tanstack/react-table";

import AddRow from "./AddRow.jsx";
import { getColumns } from "./columns.jsx";
import { transactionsApi } from "../../api/transactions.js";

export default function TableBudget({
  data,
  type,                // "expense" or "income"
  showAdd,
  onCloseAdd,
  onCreateLocal,
  onLocalDelete,
  onLocalDeleteBulk,
  onMobileEdit,
  onDeleteDialogChange,
}) {
  const [tableData, setTableData] = useState(data);
  const [selectMode, setSelectMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState([]);

  // Create API instance for this transaction type
  const api = useMemo(() => transactionsApi(type), [type]);

  useEffect(() => {
    setTableData(data);
  }, [data]);

  // ----------------------------------------------------
  // DELETE (single) - Using generic API
  // ----------------------------------------------------
  const handleDelete = useCallback(async (id) => {
    try {
      await api.remove(id);
      onLocalDelete(id);
    } catch (err) {
      console.error("Delete error:", err);
    }
  }, [api, onLocalDelete]);

  // ----------------------------------------------------
  // Columns
  // ----------------------------------------------------
  const baseColumns = useMemo(
    () => getColumns(type, handleDelete, onDeleteDialogChange),
    [type, handleDelete, onDeleteDialogChange]
  );

  const columns = useMemo(() => {
    if (!selectMode) return baseColumns;

    return [
      {
        id: "select",
        header: (
          <input
            type="checkbox"
            disabled={tableData.length === 0}
            checked={
              tableData.length > 0 &&
              selectedIds.length === tableData.length
            }
            onChange={(e) => {
              if (e.target.checked) {
                setSelectedIds(tableData.map((row) => row.id));
              } else {
                setSelectedIds([]);
              }
            }}
          />
        ),
        cell: (info) => {
          const rowId = info.row.original.id;
          const checked = selectedIds.includes(rowId);
          return (
            <input
              type="checkbox"
              checked={checked}
              onChange={(e) => {
                if (e.target.checked) {
                  setSelectedIds((p) => [...p, rowId]);
                } else {
                  setSelectedIds((p) => p.filter((id) => id !== rowId));
                }
              }}
            />
          );
        },
      },
      ...baseColumns.filter((col) => col.id !== "delete"),
    ];
  }, [selectMode, selectedIds, tableData, baseColumns]);

  const table = useReactTable({
    data: tableData,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  // ----------------------------------------------------
  // BULK DELETE - Using generic API
  // ----------------------------------------------------
  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) return;

    try {
      await api.bulkRemove(selectedIds);
      onLocalDeleteBulk(selectedIds);
      setSelectMode(false);
      setSelectedIds([]);
    } catch (err) {
      console.error("Bulk delete error:", err);
    }
  };

  // ----------------------------------------------------
  // UI
  // ----------------------------------------------------
  return (
    <div className="mb-4">

      <div className="d-flex justify-content-end mb-2">
        {!selectMode && (
          <button
            className="btn btn-outline-secondary btn-sm"
            onClick={() => {
              setSelectMode(true);
              setSelectedIds([]);
            }}
          >
            Select
          </button>
        )}

        {selectMode && (
          <button
            className="btn btn-outline-danger btn-sm"
            onClick={() => {
              setSelectMode(false);
              setSelectedIds([]);
            }}
          >
            Cancel
          </button>
        )}
      </div>

      <div className="table-responsive">
        <table className="table table-sm table-hover align-middle">
          <thead>
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((header) => (
                  <th key={header.id} className="small fw-semibold">
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>

          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                onClick={() => {
                  if (window.innerWidth < 768 && !selectMode) {
                    onMobileEdit?.(row.original);
                  }
                }}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>
                    {flexRender(
                      cell.column.columnDef.cell,
                      cell.getContext()
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectMode && (
        <div className="d-flex align-items-center justify-content-between border rounded p-2 mb-2 bg-light">

          <button
            className="btn btn-outline-danger btn-sm"
            onClick={() => {
              setSelectMode(false);
              setSelectedIds([]);
            }}
          >
            Cancel
          </button>

          <div className="small text-muted">
            {selectedIds.length} selected
          </div>

          <button
            className="btn btn-danger btn-sm"
            disabled={selectedIds.length === 0}
            onClick={handleBulkDelete}
          >
            Delete Selected
          </button>

        </div>
      )}

      {showAdd && (
        <AddRow
          type={type}
          onSave={async (row) => {
            await onCreateLocal(row);
            onCloseAdd();
          }}
          onCancel={onCloseAdd}
        />
      )}
    </div>
  );
}

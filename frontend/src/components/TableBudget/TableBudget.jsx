import React, { useState, useEffect, useMemo } from "react";
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
} from "@tanstack/react-table";

import AddRow from "./AddRow.jsx";
import DeleteCell from "./DeleteCell.jsx";
import { getColumns } from "./columns.jsx";

export default function TableBudget({
  data,
  type,               // "expense" or "income"
  showAdd,
  onCloseAdd,
  onCreateLocal,
  onLocalDelete,
}) {
  const [tableData, setTableData] = useState(data);

  // --- STEP 1 + STEP 2 ---
  const [selectMode, setSelectMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState([]);

  // Sync table when parent updates
  useEffect(() => {
    setTableData(data);
  }, [data]);

  // -------------------------
  // DELETE (single item)
  // -------------------------
  const handleDelete = async (id) => {
    const baseUrl = `${window.location.protocol}//${window.location.hostname}:8000`;
    const endpoint = `${baseUrl}/api/${type}/${id}`;

    try {
      const response = await fetch(endpoint, { method: "DELETE" });
      if (!response.ok) {
        console.error("Delete failed:", await response.text());
        return;
      }
      onLocalDelete(id);
    } catch (err) {
      console.error("Delete error:", err);
    }
  };

  // -------------------------
  // Columns
  // -------------------------
  const baseColumns = useMemo(
    () => getColumns(type, handleDelete),
    [type]
  );

  // STEP 2: Add checkbox column only in select mode
  const columns = useMemo(() => {
    if (!selectMode) return baseColumns;

    return [
      {
        id: "select",
        header: (
          <input
            type="checkbox"
            checked={
              selectedIds.length > 0 &&
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
                  setSelectedIds((prev) => [...prev, rowId]);
                } else {
                  setSelectedIds((prev) =>
                    prev.filter((id) => id !== rowId)
                  );
                }
              }}
            />
          );
        },
      },
      ...baseColumns,
    ];
  }, [selectMode, selectedIds, tableData, baseColumns]);

  const table = useReactTable({
    data: tableData,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div className="mb-4">

      {/* --- Select Mode Button --- */}
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

      {/* TABLE */}
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
            <tr key={row.id}>
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

{selectMode && (
  <div className="d-flex align-items-center justify-content-between border rounded p-2 mb-2 bg-light">

    {/* Cancel select mode (same as button above table) */}
    <button
      className="btn btn-outline-danger btn-sm"
      onClick={() => {
        setSelectMode(false);
        setSelectedIds([]);
      }}
    >
      Cancel
    </button>

    {/* Show count */}
    <div className="small text-muted">
      {selectedIds.length} selected
    </div>

    {/* Placeholder bulk delete button */}
    <button
      className="btn btn-danger btn-sm"
      disabled={selectedIds.length === 0}
      onClick={() => {
        console.log("Bulk delete clicked — backend not yet wired");
      }}
    >
      Delete Selected
    </button>

  </div>
)}


      {/* ADD ROW FORM */}
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

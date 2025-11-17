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
  type,                // "expense" or "income"
  showAdd,
  onCloseAdd,
  onCreateLocal,
  onLocalDelete,
  onLocalDeleteBulk,
}) {
  const [tableData, setTableData] = useState(data);

  // Select mode state
  const [selectMode, setSelectMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState([]);

  // Sync table data when parent updates
  useEffect(() => {
    setTableData(data);
  }, [data]);

  // ----------------------------------------------------
  // DELETE (single item)
  // ----------------------------------------------------
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

  // ----------------------------------------------------
  // Columns (base + checkbox column in select mode)
  // ----------------------------------------------------
  const baseColumns = useMemo(
    () => getColumns(type, handleDelete),
    [type]
  );

  const columns = useMemo(() => {
    if (!selectMode) return baseColumns;

    // Checkbox column + hide single-delete column for clarity
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
      ...baseColumns.filter((col) => col.id !== "delete"),
    ];
  }, [selectMode, selectedIds, tableData, baseColumns]);

  const table = useReactTable({
    data: tableData,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  // ----------------------------------------------------
  // BULK DELETE
  // ----------------------------------------------------
  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) return;

    const baseUrl = `${window.location.protocol}//${window.location.hostname}:8000`;
    const endpoint = `${baseUrl}/api/${type}/bulk-delete`;

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids: selectedIds }),
      });

      if (!response.ok) {
        console.error("Bulk delete failed:", await response.text());
        return;
      }

      // Remove rows locally
      onLocalDeleteBulk(selectedIds);

      // Exit select mode
      setSelectedIds([]);
      setSelectMode(false);

    } catch (err) {
      console.error("Bulk delete error:", err);
    }
  };

  // ----------------------------------------------------
  // UI
  // ----------------------------------------------------
  return (
    <div className="mb-4">

      {/* Select Mode Toggle */}
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

      {/* TABLE — wrapped for mobile responsiveness */}
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
      </div>

      {/* Bulk Delete Bar */}
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

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

  // --- Step 1 states ---
  const [selectMode, setSelectMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState([]);

  // Sync table with parent
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
  const columns = useMemo(
    () => getColumns(type, handleDelete),
    [type]
  );

  const table = useReactTable({
    data: tableData,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  // -------------------------
  // UI
  // -------------------------
  return (
    <div className="mb-4">

      {/* --- Step 1: Select Mode Button --- */}
      <div className="d-flex justify-content-end mb-2">
        {!selectMode && (
          <button
            className="btn btn-outline-secondary btn-sm"
            onClick={() => {
              setSelectMode(true);
              setSelectedIds([]); // reset selections
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

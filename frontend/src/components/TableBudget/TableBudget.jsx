import { useMemo, useState, useEffect } from "react";
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
} from "@tanstack/react-table";
import usePatchBackend from "./usePatchBackend.jsx";
import { getColumns } from "./columns.jsx";
import AddRow from "./AddRow.jsx";

function DeleteCell({ row, type, onDelete }) {
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
        className="btn btn-sm btn-secondary ms-1"
        onClick={() => setConfirm(false)}
      >
        Cancel
      </button>
    </span>
  );
}


export default function TableBudget({
  data = [],
  type = "expense",
  showAdd = false,
  onCloseAdd,
  onCreateLocal,
}) {
  const [rows, setRows] = useState(data);
  const patchBackend = usePatchBackend();

  useEffect(() => {
    setRows(data);
  }, [data]);

  const updateCell = (rowIndex, field, newValue) => {
    setRows((old) => {
      const updated = old.map((r, i) =>
        i === rowIndex ? { ...r, [field]: newValue } : r
      );
      const row = updated[rowIndex];
      patchBackend(type, row, field, newValue);
      return updated;
    });
  };

  const addNewRowLocal = (row) => {
    setRows((old) => [...old, row]); // append at bottom
    onCreateLocal?.(row);
    onCloseAdd?.();
  };

  const columns = useMemo(() => getColumns(type, updateCell), [type]);
  const table = useReactTable({
    data: rows,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

    const handleDelete = async (id) => {
      const baseUrl = `${window.location.protocol}//${window.location.hostname}:8000`;
      const endpoint = `${baseUrl}/api/${type}/${id}`;

      try {
        const res = await fetch(endpoint, { method: "DELETE" });
        if (!res.ok) throw new Error("Delete failed");

        // Remove from table immediately
        onLocalDelete(id);

        // TODO: undo in next step
      } catch (err) {
        console.error("Delete error:", err);
      }
    };


  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((header) => (
                <th
                  key={header.id}
                  style={{
                    textAlign: "left",
                    borderBottom: "1px solid #ddd",
                    padding: "8px",
                  }}
                >
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}
                </th>
              ))}
              {showAdd && (
                <th
                  style={{
                    textAlign: "left",
                    borderBottom: "1px solid #ddd",
                    padding: "8px",
                  }}
                >
                  Actions
                </th>
              )}
            </tr>
          ))}
        </thead>

        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <td
                  key={cell.id}
                  style={{
                    borderBottom: "1px solid #f0f0f0",
                    padding: "8px",
                  }}
                >
                  {flexRender(
                    cell.column.columnDef.cell,
                    cell.getContext()
                  )}
                </td>
              ))}
              {showAdd && <td style={{ padding: "8px" }} />}
            </tr>
          ))}
        </tbody>
      </table>

      {/* AddRow is rendered below table to avoid losing focus */}
      {showAdd && (
        <div style={{ marginTop: "10px" }}>
          <AddRow type={type} onSave={addNewRowLocal} onCancel={onCloseAdd} />
        </div>
      )}
    </div>
  );
}

import { useMemo, useState, useEffect } from "react";
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
} from "@tanstack/react-table";
import usePatchBackend from "./usePatchBackend.jsx";
import { getColumns } from "./columns.jsx";
import AddRow from "./AddRow.jsx";

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

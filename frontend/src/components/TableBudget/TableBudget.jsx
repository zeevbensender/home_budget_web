import { useMemo, useState, useEffect } from "react";
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
} from "@tanstack/react-table";
import usePatchBackend from "./usePatchBackend.jsx";
import { getColumns } from "./columns.jsx";
import AddRow from "./AddRow.jsx";

/**
 * Props:
 * - data, type
 * - showAdd (bool)           -> whether to display inline add-row
 * - onCloseAdd()             -> parent closes add-mode
 * - onCreateLocal?(row)      -> optional callback when created (local)
 */
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
    setRows((old) => [row, ...old]);          // add to top
    onCreateLocal?.(row);
    onCloseAdd?.();
  };

  const columns = useMemo(() => getColumns(type, updateCell), [type]);

  const table = useReactTable({
    data: rows,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  // derive header cells count for AddRow spanning
  const headerCount = table.getHeaderGroups()[0]?.headers?.length ?? 0;

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
              {/* action column header when add-row is visible */}
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
          {/* Inline add-row at the very top */}
          {showAdd && (
            <AddRow type={type} onSave={addNewRowLocal} onCancel={onCloseAdd} />
          )}

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
              {/* filler cell for layout parity when add-row is visible */}
              {showAdd && <td style={{ padding: "8px" }} />}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

import { useMemo, useState, useEffect } from "react";
import {
  createColumnHelper,
  useReactTable,
  getCoreRowModel,
  flexRender,
} from "@tanstack/react-table";

const columnHelper = createColumnHelper();

export default function TableBudget({ data = [], type = "expense" }) {
  const [rows, setRows] = useState(data);

  useEffect(() => {
    setRows(data);
  }, [data]);

  // ------------------------------------------------------------
  // PATCH helper — works for both expense and income
  // ------------------------------------------------------------
  const patchBackend = async (row, field, value) => {
    if (!row?.id) return;

    const base = `${window.location.protocol}//${window.location.hostname}:8000`;
    const endpoint =
      type === "expense"
        ? `/api/expense/${row.id}`
        : `/api/income/${row.id}`;
    const url = `${base}${endpoint}`;

    console.log(`PATCH → ${url} (${field}=${value})`);

    try {
      const res = await fetch(url, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ field, value }),
      });

      if (!res.ok) {
        console.error("PATCH failed", res.status);
      } else {
        console.log(`✅ Updated ${type} ${row.id} field ${field}`);
      }
    } catch (err) {
      console.error("PATCH error:", err);
    }
  };

  // ------------------------------------------------------------
  // Update local state + trigger PATCH
  // ------------------------------------------------------------
  const updateCell = (rowIndex, field, newValue) => {
    setRows((old) => {
      const updated = old.map((r, i) =>
        i === rowIndex ? { ...r, [field]: newValue } : r
      );

      const row = updated[rowIndex];
      patchBackend(row, field, newValue); // 👈 run after local update

      return updated;
    });
  };

  // ------------------------------------------------------------
  // Inline editable cell factory
  // ------------------------------------------------------------
  const editableCell = (field, formatter) => ({
    header: field[0].toUpperCase() + field.slice(1),
    cell: (info) => {
      const rowIndex = info.row.index;
      const value = info.getValue();
      const [editing, setEditing] = useState(false);
      const [localValue, setLocalValue] = useState(value ?? "");

      const commit = () => {
        setEditing(false);
        const formatted = formatter ? formatter(localValue) : localValue;
        updateCell(rowIndex, field, formatted);
      };

      return editing ? (
        <input
          type="text"
          value={localValue}
          autoFocus
          onChange={(e) => setLocalValue(e.target.value)}
          onBlur={commit}
          onKeyDown={(e) => e.key === "Enter" && commit()}
          style={{ width: "100%", boxSizing: "border-box" }}
        />
      ) : (
        <span onClick={() => setEditing(true)} style={{ cursor: "pointer" }}>
          {value ?? ""}
        </span>
      );
    },
  });

  // ------------------------------------------------------------
  // Columns
  // ------------------------------------------------------------
  const columns = useMemo(() => {
    const base = [
      columnHelper.accessor("date", editableCell("date")),
      ...(type === "expense"
        ? [columnHelper.accessor("business", editableCell("business"))]
        : []),
      columnHelper.accessor("category", editableCell("category")),
      columnHelper.accessor(
        "amount",
        editableCell("amount", (v) => parseFloat(v) || 0)
      ),
      columnHelper.accessor("account", editableCell("account")),
      columnHelper.accessor(
        "currency",
        editableCell("currency", (v) => v || "₪")
      ),
      columnHelper.accessor("notes", editableCell("notes")),
    ];
    return base;
  }, [type]);

  const table = useReactTable({
    data: rows,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  // ------------------------------------------------------------
  // Render
  // ------------------------------------------------------------
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
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

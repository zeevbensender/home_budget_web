import { createColumnHelper } from "@tanstack/react-table";
import EditableCell from "./EditableCell.jsx";

const columnHelper = createColumnHelper();

export const getColumns = (type, updateCell) => {
  const editable = (field, formatter) => ({
    header: field[0].toUpperCase() + field.slice(1),
    cell: (info) => (
      <EditableCell
        value={info.getValue()}
        field={field}
        rowIndex={info.row.index}
        updateCell={updateCell}
        formatter={formatter}
      />
    ),
  });

  const base = [
    columnHelper.accessor("date", editable("date")),
    ...(type === "expense"
      ? [columnHelper.accessor("business", editable("business"))]
      : []),
    columnHelper.accessor("category", editable("category")),
    columnHelper.accessor(
      "amount",
      editable("amount", (v) => parseFloat(v) || 0)
    ),
    columnHelper.accessor("account", editable("account")),
    columnHelper.accessor(
      "currency",
      editable("currency", (v) => v || "₪")
    ),
    columnHelper.accessor("notes", editable("notes")),
    {
      header: "",
      id: "delete",
      cell: (info) => (
        <DeleteCell
          row={info.row}
          type={type}
          onDelete={handleDelete}
        />
      ),
    },

  ];

  return base;
};

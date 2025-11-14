import React from "react";
import EditableCell from "./EditableCell.jsx";
import DeleteCell from "./DeleteCell.jsx";

export function getColumns(type, handleDelete) {
  const expenseFields = [
    "date",
    "business",
    "category",
    "amount",
    "account",
    "currency",
    "notes",
  ];

  const incomeFields = [
    "date",
    "category",
    "amount",
    "account",
    "currency",
    "notes",
  ];

  const fields = type === "expense" ? expenseFields : incomeFields;

  const fieldColumns = fields.map((field) => ({
    accessorKey: field,
    header: field[0].toUpperCase() + field.slice(1),
    cell: (info) => (
      <EditableCell
        value={info.getValue()}
        row={info.row}
        field={field}
        type={type}
      />
    ),
  }));

  return [
    ...fieldColumns,
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
}

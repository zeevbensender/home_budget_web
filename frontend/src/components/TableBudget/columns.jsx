import React from "react";
import EditableCell from "./EditableCell.jsx";
import DeleteCell from "./DeleteCell.jsx";

// Formatter: remove year (YYYY-MM-DD -> MM-DD)
function formatDateShort(value) {
  if (!value) return "";
  const parts = value.split("-");
  if (parts.length !== 3) return value;
  const [, month, day] = parts;
  return `${month}-${day}`;
}

// Formatter: 0,000.00
function formatAmount(value) {
  if (value == null || value === "") return "";
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));
}

export function getColumns(type, handleUpdate, handleDelete, onDeleteDialogChange) {
  const expenseFields = [
    "date",
    "business",
    "category",
    "amount",
    "account",
    "notes",
  ];

  const incomeFields = [
    "date",
    "category",
    "amount",
    "account",
    "notes",
  ];

  const fields = type === "expense" ? expenseFields : incomeFields;

  const fieldColumns = fields.map((field) => {
    // Special case: NOTES column
    if (field === "notes") {
      return {
        accessorKey: field,
        header: () => <span className="notes-column">Notes</span>,
        cell: (info) => (
          <span className="notes-column">
            {info.getValue()}
          </span>
        ),
      };
    }

    return {
      accessorKey: field,
      header: field[0].toUpperCase() + field.slice(1),

      cell: (info) => {
        let value = info.getValue();
        const rowId = info.row.original.id;

        if (field === "date") {
          value = formatDateShort(value);
        }

        if (field === "amount") {
          value = formatAmount(value);
        }

        return (
          <EditableCell
            value={value}
            row={info.row}
            field={field}
            type={type}
            updateCell={(_, fieldName, newValue) => {
              // Reconstruct the full value for special fields
              let finalValue = newValue;
              
              if (fieldName === "date") {
                // Convert MM-DD back to YYYY-MM-DD
                const year = new Date().getFullYear();
                const [month, day] = newValue.split("-");
                if (month && day) {
                  finalValue = `${year}-${month}-${day}`;
                }
              } else if (fieldName === "amount") {
                // Remove commas from formatted amount
                finalValue = newValue.replace(/,/g, "");
              }
              
              handleUpdate(rowId, fieldName, finalValue);
            }}
          />
        );
      },
    };
  });

  return [
    ...fieldColumns,

    {
      header: "",
      id: "delete",
      cell: (info) => (
        <DeleteCell
          row={info.row}
          onDelete={handleDelete}
          onDeleteDialogChange={onDeleteDialogChange}
        />
      ),
    },
  ];
}

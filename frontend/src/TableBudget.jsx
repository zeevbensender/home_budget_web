import { useMemo, useState, useEffect } from 'react'
import { createColumnHelper, useReactTable, getCoreRowModel, flexRender } from '@tanstack/react-table'

const columnHelper = createColumnHelper()

export default function TableBudget({ data = [], type = 'expense' }) {
  const [rows, setRows] = useState(data)
  useEffect(() => setRows(data), [data])

  const updateCell = (rowIndex, field, newValue) => {
    setRows(old =>
      old.map((r, i) => (i === rowIndex ? { ...r, [field]: newValue } : r))
    )
  }

  // small inline editable cell generator
  const editableCell = (field, formatter) => ({
    header: field[0].toUpperCase() + field.slice(1),
    cell: info => {
      const rowIndex = info.row.index
      const value = info.getValue()
      const [editing, setEditing] = useState(false)
      const [localValue, setLocalValue] = useState(value ?? '')

      const commit = () => {
        setEditing(false)
        updateCell(rowIndex, field, formatter ? formatter(localValue) : localValue)
      }

      return editing ? (
        <input
          type="text"
          value={localValue}
          autoFocus
          onChange={e => setLocalValue(e.target.value)}
          onBlur={commit}
          onKeyDown={e => e.key === 'Enter' && commit()}
          style={{ width: '100%', boxSizing: 'border-box' }}
        />
      ) : (
        <span onClick={() => setEditing(true)} style={{ cursor: 'pointer' }}>
          {value ?? ''}
        </span>
      )
    },
  })

  const columns = useMemo(() => {
    const base = [
      columnHelper.accessor('date', editableCell('date')),
      ...(type === 'expense'
        ? [columnHelper.accessor('business', editableCell('business'))]
        : []),
      columnHelper.accessor('category', editableCell('category')),
      columnHelper.accessor(
        'amount',
        editableCell('amount', v => parseFloat(v) || 0)
      ),
      columnHelper.accessor('account', editableCell('account')),
      columnHelper.accessor(
        'currency',
        editableCell('currency', v => v || '₪')
      ),
      columnHelper.accessor('notes', editableCell('notes')),
    ]
    return base
  }, [type])

  const table = useReactTable({
    data: rows,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          {table.getHeaderGroups().map(hg => (
            <tr key={hg.id}>
              {hg.headers.map(header => (
                <th
                  key={header.id}
                  style={{
                    textAlign: 'left',
                    borderBottom: '1px solid #ddd',
                    padding: '8px',
                  }}
                >
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map(row => (
            <tr key={row.id}>
              {row.getVisibleCells().map(cell => (
                <td
                  key={cell.id}
                  style={{
                    borderBottom: '1px solid #f0f0f0',
                    padding: '8px',
                  }}
                >
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

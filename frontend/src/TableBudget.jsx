import { useMemo, useState, useEffect } from 'react'
import { createColumnHelper, useReactTable, getCoreRowModel, flexRender } from '@tanstack/react-table'

const columnHelper = createColumnHelper()

export default function TableBudget({ data = [], type = 'expense' }) {
  const [rows, setRows] = useState(data)
  useEffect(() => setRows(data), [data])

  const updateCell = (rowIndex, field, newValue) => {
    setRows(old =>
      old.map((r, i) =>
        i === rowIndex ? { ...r, [field]: newValue } : r
      )
    )
  }

  // 🧱 Define common + type-specific columns
  const columns = useMemo(() => {
    const common = [
      columnHelper.accessor('date', { header: 'Date' }),
      columnHelper.accessor('category', { header: 'Category' }),
      columnHelper.accessor('amount', {
        header: 'Amount',
        cell: info => {
          const rowIndex = info.row.index
          const value = info.getValue()
          const [editing, setEditing] = useState(false)
          const [localValue, setLocalValue] = useState(value)

          const commit = () => {
            setEditing(false)
            updateCell(rowIndex, 'amount', parseFloat(localValue) || 0)
          }

          return editing ? (
            <input
              type="number"
              value={localValue}
              autoFocus
              onChange={e => setLocalValue(e.target.value)}
              onBlur={commit}
              onKeyDown={e => e.key === 'Enter' && commit()}
              style={{ width: '80px' }}
            />
          ) : (
            <span onClick={() => setEditing(true)} style={{ cursor: 'pointer' }}>
              {Number(value).toFixed(2)}
            </span>
          )
        },
      }),
      columnHelper.accessor('account', { header: 'Account' }),
      columnHelper.accessor('currency', {
        header: 'Currency',
        cell: info => info.getValue() || '₪',
      }),
      columnHelper.accessor('notes', { header: 'Notes' }),
    ]

    // Expense-specific extra column
    if (type === 'expense') {
      common.splice(1, 0, columnHelper.accessor('business', { header: 'Business' }))
    }

    return common
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
                <th key={header.id} style={{ textAlign:'left', borderBottom:'1px solid #ddd', padding:'8px' }}>
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
                <td key={cell.id} style={{ borderBottom:'1px solid #f0f0f0', padding:'8px' }}>
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

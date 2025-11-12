import { useMemo, useState, useEffect } from 'react'
import { createColumnHelper, useReactTable, getCoreRowModel, flexRender } from '@tanstack/react-table'

const columnHelper = createColumnHelper()

export default function TableBudget({ data }) {
  const [rows, setRows] = useState(data || [])
// 🔧 keep rows in sync when parent updates data
  useEffect(() => {
    setRows(data || [])
  }, [data])

  const updateAmount = (rowIndex, newValue) => {
    setRows(old =>
      old.map((r, i) =>
        i === rowIndex ? { ...r, amount: parseFloat(newValue) || 0 } : r
      )
    )
  }

  const columns = useMemo(
    () => [
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
            updateAmount(rowIndex, localValue)
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
    ],
    []
  )

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

// Lightweight, responsive table used by all list views.
export default function DataTable({ columns, rows, empty }) {
  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500 dark:bg-slate-900/40 dark:text-slate-400">
          <tr>
            {columns.map((c) => (
              <th key={c.key} className="px-4 py-3 font-semibold">{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
          {rows.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-10 text-center text-slate-400">
                {empty || 'No records found'}
              </td>
            </tr>
          ) : (
            rows.map((row, i) => (
              <tr key={row.id ?? i} className="hover:bg-slate-50 dark:hover:bg-slate-700/40">
                {columns.map((c) => (
                  <td key={c.key} className="px-4 py-3 text-slate-700 dark:text-slate-200">
                    {c.render ? c.render(row) : row[c.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

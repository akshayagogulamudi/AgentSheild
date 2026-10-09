import { CheckCircle2, XCircle } from 'lucide-react'
import type { CheckResult } from '../types'

interface ChecksTableProps {
  checks: CheckResult[]
}

export default function ChecksTable({ checks }: ChecksTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700">
            <th className="text-left px-4 py-3 text-slate-400 font-semibold">Name</th>
            <th className="text-left px-4 py-3 text-slate-400 font-semibold">Status</th>
            <th className="text-left px-4 py-3 text-slate-400 font-semibold">Reason</th>
          </tr>
        </thead>
        <tbody>
          {checks.map((check, idx) => (
            <tr key={idx} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
              <td className="px-4 py-3 text-slate-200">{check.name}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  {check.passed ? (
                    <>
                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                      <span className="text-green-400">Passed</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="w-4 h-4 text-red-500" />
                      <span className="text-red-400">Failed</span>
                    </>
                  )}
                </div>
              </td>
              <td className="px-4 py-3 text-slate-300">{check.reason}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

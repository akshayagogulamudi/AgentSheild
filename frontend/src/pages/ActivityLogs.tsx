import { useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import DecisionBadge from '../components/DecisionBadge'
import RiskBadge from '../components/RiskBadge'
import { getEvents } from '../services/api'
import type { SecurityEvent } from '../types'

const getRiskTier = (score: number): 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' => {
  if (score > 75) return 'CRITICAL'
  if (score > 50) return 'HIGH'
  if (score > 25) return 'MEDIUM'
  return 'LOW'
}

export default function ActivityLogs() {
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [page, setPage] = useState(0)
  const [totalEstimate, setTotalEstimate] = useState(0)
  const [loading, setLoading] = useState(true)

  const pageSize = 20

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const offset = page * pageSize
        const data = await getEvents({ offset, limit: pageSize })
        setEvents(data || [])
        // Estimate total based on whether we got a full page
        if (data && data.length > 0) {
          setTotalEstimate(offset + (data.length >= pageSize ? pageSize : data.length) + 20)
        }
      } catch (error) {
        console.error('Failed to fetch events:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [page])

  const currentPage = page + 1
  const estimatedPages = Math.ceil(totalEstimate / pageSize)

  if (loading) {
    return <div className="text-slate-400 py-12 text-center">Loading activity logs...</div>
  }

  return (
    <div className="space-y-6">
      {/* Activity Logs Table */}
      <div className="glass border border-slate-700 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700 bg-slate-800/50">
          <h2 className="text-lg font-bold text-white">Activity Logs</h2>
        </div>

        {events.length === 0 ? (
          <div className="text-slate-400 text-center py-12">No activity logs found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700 bg-slate-800/50">
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">ID</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Timestamp</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Agent</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Tool</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Decision</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Risk Score</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Reason</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event) => (
                  <tr key={event.id} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 text-slate-200 font-mono text-xs">{event.id}</td>
                    <td className="px-6 py-4 text-slate-300 text-xs">{new Date(event.timestamp).toLocaleString()}</td>
                    <td className="px-6 py-4 text-slate-300">{event.agent_name}</td>
                    <td className="px-6 py-4 text-slate-300">{event.requested_tool}</td>
                    <td className="px-6 py-4">
                      <DecisionBadge decision={event.decision as 'ALLOW' | 'BLOCK' | 'REQUIRE_APPROVAL'} />
                    </td>
                    <td className="px-6 py-4">
                      <RiskBadge tier={getRiskTier(event.risk_score)} score={event.risk_score} />
                    </td>
                    <td className="px-6 py-4 text-slate-300 max-w-xs truncate" title={event.reason}>
                      {event.reason || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setPage(Math.max(0, page - 1))}
          disabled={page === 0}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 border border-slate-700 rounded text-slate-200 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          Previous
        </button>

        <span className="text-slate-400 text-sm">
          Page {currentPage} / ~{estimatedPages}
        </span>

        <button
          onClick={() => setPage(page + 1)}
          disabled={events.length < pageSize}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 border border-slate-700 rounded text-slate-200 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Next
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

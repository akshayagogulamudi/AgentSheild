import { useEffect, useState } from 'react'
import { ChevronDown, ChevronUp, Shield, Zap, Filter, CheckCircle, AlertCircle } from 'lucide-react'
import DecisionBadge from '../components/DecisionBadge'
import RiskBadge from '../components/RiskBadge'
import ChecksTable from '../components/ChecksTable'
import { getEvents } from '../services/api'
import type { SecurityEvent } from '../types'

export default function SecurityGateway() {
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const data = await getEvents({ limit: 20 })
        setEvents(data || [])
      } catch (error) {
        console.error('Failed to fetch events:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const parseJsonArray = (jsonString: string | string[] | null | undefined): string[] => {
    if (!jsonString) return []
    if (Array.isArray(jsonString)) return jsonString
    try {
      return JSON.parse(jsonString)
    } catch {
      return []
    }
  }

  const getRiskTier = (score: number): 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' => {
    if (score > 75) return 'CRITICAL'
    if (score > 50) return 'HIGH'
    if (score > 25) return 'MEDIUM'
    return 'LOW'
  }

  if (loading) {
    return <div className="text-slate-400 py-12 text-center">Loading events...</div>
  }

  return (
    <div className="space-y-6">
      {/* Gateway Flow Diagram */}
      <div className="glass border border-slate-700 rounded-lg p-6">
        <h2 className="text-lg font-bold text-white mb-6">Security Gateway Flow</h2>
        <div className="flex items-center justify-between gap-4 flex-wrap lg:flex-nowrap">
          <div className="flex flex-col items-center gap-2">
            <div className="w-16 h-16 rounded-lg bg-blue-500/20 border border-blue-500 flex items-center justify-center">
              <Zap className="w-8 h-8 text-blue-400" />
            </div>
            <span className="text-sm text-slate-300 font-medium">AI Agent</span>
          </div>

          <div className="text-slate-400 hidden lg:block">→</div>

          <div className="flex flex-col items-center gap-2">
            <div className="w-16 h-16 rounded-lg bg-cyan-500/20 border border-cyan-500 flex items-center justify-center">
              <Shield className="w-8 h-8 text-cyan-400" />
            </div>
            <span className="text-sm text-slate-300 font-medium">Policy Check</span>
          </div>

          <div className="text-slate-400 hidden lg:block">→</div>

          <div className="flex flex-col items-center gap-2">
            <div className="w-16 h-16 rounded-lg bg-purple-500/20 border border-purple-500 flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-purple-400" />
            </div>
            <span className="text-sm text-slate-300 font-medium">Injection Scan</span>
          </div>

          <div className="text-slate-400 hidden lg:block">→</div>

          <div className="flex flex-col items-center gap-2">
            <div className="w-16 h-16 rounded-lg bg-yellow-500/20 border border-yellow-500 flex items-center justify-center">
              <Filter className="w-8 h-8 text-yellow-400" />
            </div>
            <span className="text-sm text-slate-300 font-medium">DLP Scan</span>
          </div>

          <div className="text-slate-400 hidden lg:block">→</div>

          <div className="flex flex-col items-center gap-2">
            <div className="w-16 h-16 rounded-lg bg-green-500/20 border border-green-500 flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-green-400" />
            </div>
            <span className="text-sm text-slate-300 font-medium">Decision</span>
          </div>
        </div>
      </div>

      {/* Events Table */}
      <div className="glass border border-slate-700 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700">
          <h2 className="text-lg font-bold text-white">Latest Events</h2>
        </div>

        {events.length === 0 ? (
          <div className="text-slate-400 text-center py-12">No events found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700 bg-slate-800/50">
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">ID</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Time</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Tool</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Agent</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Risk</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Decision</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Details</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event) => (
                  <div key={event.id}>
                    <tr className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4 text-slate-200 font-mono text-xs">{event.id}</td>
                      <td className="px-6 py-4 text-slate-300 text-xs">{new Date(event.timestamp).toLocaleString()}</td>
                      <td className="px-6 py-4 text-slate-300">{event.requested_tool}</td>
                      <td className="px-6 py-4 text-slate-300">{event.agent_name}</td>
                      <td className="px-6 py-4">
                        <RiskBadge tier={getRiskTier(event.risk_score)} score={event.risk_score} />
                      </td>
                      <td className="px-6 py-4">
                        <DecisionBadge decision={event.decision as 'ALLOW' | 'BLOCK' | 'REQUIRE_APPROVAL'} />
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => setExpandedId(expandedId === event.id ? null : event.id)}
                          className="text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          {expandedId === event.id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>
                      </td>
                    </tr>
                    {expandedId === event.id && (
                      <tr className="border-b border-slate-800 bg-slate-800/20">
                        <td colSpan={7} className="px-6 py-4">
                          <div className="space-y-4">
                            <div>
                              <h4 className="text-sm font-semibold text-slate-300 mb-3">Security Checks</h4>
                              {event.checks_passed || event.checks_failed ? (
                                <div className="space-y-2">
                                  {(parseJsonArray(event.checks_passed).length > 0 || parseJsonArray(event.checks_failed).length > 0) ? (
                                    <ChecksTable
                                      checks={[
                                        ...parseJsonArray(event.checks_passed).map((check) => ({
                                          name: check,
                                          passed: true,
                                          reason: 'Passed',
                                        })),
                                        ...parseJsonArray(event.checks_failed).map((check) => ({
                                          name: check,
                                          passed: false,
                                          reason: 'Failed',
                                        })),
                                      ]}
                                    />
                                  ) : (
                                    <p className="text-slate-400">No check details available</p>
                                  )}
                                </div>
                              ) : (
                                <p className="text-slate-400">No check details available</p>
                              )}
                            </div>
                            {event.reason && (
                              <div>
                                <h4 className="text-sm font-semibold text-slate-300 mb-1">Reason</h4>
                                <p className="text-slate-300">{event.reason}</p>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </div>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

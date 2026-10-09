import { useEffect, useState } from 'react'
import DecisionBadge from '../components/DecisionBadge'
import { getThreats } from '../services/api'
import type { Threat } from '../types'

type CategoryFilter = 'all' | 'prompt_injection' | 'data_exfiltration' | 'unauthorized_tool' | 'policy_violation'
type SeverityFilter = 'all' | 'low' | 'medium' | 'high' | 'critical'
type ResponseFilter = 'all' | 'blocked' | 'pending' | 'allowed'

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'prompt_injection':
      return 'bg-purple-500/20 border-purple-500/50 text-purple-300'
    case 'data_exfiltration':
      return 'bg-red-500/20 border-red-500/50 text-red-300'
    case 'unauthorized_tool':
      return 'bg-orange-500/20 border-orange-500/50 text-orange-300'
    case 'policy_violation':
      return 'bg-yellow-500/20 border-yellow-500/50 text-yellow-300'
    default:
      return 'bg-slate-500/20 border-slate-500/50 text-slate-300'
  }
}

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'low':
      return 'bg-green-500/20 border-green-500/50 text-green-300'
    case 'medium':
      return 'bg-yellow-500/20 border-yellow-500/50 text-yellow-300'
    case 'high':
      return 'bg-orange-500/20 border-orange-500/50 text-orange-300'
    case 'critical':
      return 'bg-red-500/20 border-red-500/50 text-red-300'
    default:
      return 'bg-slate-500/20 border-slate-500/50 text-slate-300'
  }
}

export default function ThreatDetection() {
  const [threats, setThreats] = useState<Threat[]>([])
  const [loading, setLoading] = useState(true)
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>('all')
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>('all')
  const [responseFilter, setResponseFilter] = useState<ResponseFilter>('all')

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const data = await getThreats()
        setThreats(data || [])
      } catch (error) {
        console.error('Failed to fetch threats:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const filteredThreats = threats.filter((threat) => {
    if (categoryFilter !== 'all' && threat.threat_category !== categoryFilter) return false
    if (severityFilter !== 'all' && threat.severity !== severityFilter) return false
    if (responseFilter !== 'all') {
      const response = threat.gateway_response?.toLowerCase()
      if (responseFilter === 'blocked' && response !== 'blocked') return false
      if (responseFilter === 'pending' && response !== 'pending') return false
      if (responseFilter === 'allowed' && response !== 'allowed') return false
    }
    return true
  })

  if (loading) {
    return <div className="text-slate-400 py-12 text-center">Loading threats...</div>
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="glass border border-slate-700 rounded-lg p-6">
        <h2 className="text-sm font-semibold text-slate-400 mb-4 uppercase">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-2">Category</label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value as CategoryFilter)}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-200 text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Categories</option>
              <option value="prompt_injection">Prompt Injection</option>
              <option value="data_exfiltration">Data Exfiltration</option>
              <option value="unauthorized_tool">Unauthorized Tool</option>
              <option value="policy_violation">Policy Violation</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-2">Severity</label>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value as SeverityFilter)}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-200 text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Severities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-2">Response</label>
            <select
              value={responseFilter}
              onChange={(e) => setResponseFilter(e.target.value as ResponseFilter)}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-200 text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Responses</option>
              <option value="blocked">Blocked</option>
              <option value="pending">Pending</option>
              <option value="allowed">Allowed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Threats Table */}
      <div className="glass border border-slate-700 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700 bg-slate-800/50">
          <h2 className="text-lg font-bold text-white">Threats ({filteredThreats.length})</h2>
        </div>

        {filteredThreats.length === 0 ? (
          <div className="text-slate-400 text-center py-12">No threats match the selected filters</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700 bg-slate-800/30">
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">ID</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Time</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Category</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Severity</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Agent</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Action</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Reason</th>
                  <th className="text-left px-6 py-3 text-slate-400 font-semibold">Response</th>
                </tr>
              </thead>
              <tbody>
                {filteredThreats.map((threat) => (
                  <tr key={threat.id} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 text-slate-200 font-mono text-xs">{threat.id}</td>
                    <td className="px-6 py-4 text-slate-300 text-xs">{new Date(threat.timestamp).toLocaleString()}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full border text-xs font-semibold ${getCategoryColor(threat.threat_category)}`}>
                        {threat.threat_category.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {threat.severity && (
                        <span className={`inline-flex items-center px-3 py-1 rounded-full border text-xs font-semibold ${getSeverityColor(threat.severity)}`}>
                          {threat.severity}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-slate-300">{threat.agent_identifier || 'N/A'}</td>
                    <td className="px-6 py-4 text-slate-300 max-w-xs truncate" title={threat.requested_action}>
                      {threat.requested_action || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-slate-300 max-w-xs truncate" title={threat.reason_for_detection}>
                      {threat.reason_for_detection || 'N/A'}
                    </td>
                    <td className="px-6 py-4">
                      {threat.gateway_response && (
                        <DecisionBadge decision={threat.gateway_response as 'ALLOW' | 'BLOCK' | 'REQUIRE_APPROVAL'} />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

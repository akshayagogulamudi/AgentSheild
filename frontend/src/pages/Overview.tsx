import { useEffect, useState } from 'react'
import { Activity, AlertTriangle, CheckCircle2, XCircle, Zap } from 'lucide-react'
import MetricCard from '../components/MetricCard'
import DecisionBadge from '../components/DecisionBadge'
import RiskBadge from '../components/RiskBadge'
import { getEvents, getThreats } from '../services/api'
import type { SecurityEvent, Threat } from '../types'

export default function Overview() {
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [threats, setThreats] = useState<Threat[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [eventsData, threatsData] = await Promise.all([getEvents(), getThreats()])
        setEvents(eventsData || [])
        setThreats(threatsData || [])
      } catch (error) {
        console.error('Failed to fetch overview data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const totalRequests = events.length
  const allowed = events.filter((e) => e.decision === 'ALLOW').length
  const blocked = events.filter((e) => e.decision === 'BLOCK').length
  const pending = events.filter((e) => e.decision === 'REQUIRE_APPROVAL').length
  const injectionThreats = threats.filter((t) => t.threat_category === 'prompt_injection').length
  const exfiltrationThreats = threats.filter((t) => t.threat_category === 'data_exfiltration').length

  const recentIncidents = events.slice(0, 5)

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-slate-800 rounded-lg" />
          ))}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="h-32 bg-slate-800 rounded-lg" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Main metrics row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Total Requests" value={totalRequests} icon={<Activity className="w-full h-full" />} color="blue" />
        <MetricCard title="Allowed" value={allowed} icon={<CheckCircle2 className="w-full h-full" />} color="green" />
        <MetricCard title="Blocked" value={blocked} icon={<XCircle className="w-full h-full" />} color="red" />
        <MetricCard title="Pending" value={pending} icon={<AlertTriangle className="w-full h-full" />} color="yellow" />
      </div>

      {/* Threat metrics row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <MetricCard title="Injection Threats" value={injectionThreats} icon={<Zap className="w-full h-full" />} color="cyan" />
        <MetricCard title="Exfiltration Threats" value={exfiltrationThreats} icon={<AlertTriangle className="w-full h-full" />} color="red" />
      </div>

      {/* Recent Incidents Table */}
      <div className="glass border border-slate-700 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">Recent Incidents</h2>
        {recentIncidents.length === 0 ? (
          <p className="text-slate-400 text-center py-8">No incidents yet</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">ID</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">Time</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">Agent</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">Tool</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">Decision</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">Risk Score</th>
                </tr>
              </thead>
              <tbody>
                {recentIncidents.map((event) => (
                  <tr key={event.id} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3 text-slate-200 font-mono text-xs">{event.id}</td>
                    <td className="px-4 py-3 text-slate-300">{new Date(event.timestamp).toLocaleString()}</td>
                    <td className="px-4 py-3 text-slate-300">{event.agent_name}</td>
                    <td className="px-4 py-3 text-slate-300">{event.requested_tool}</td>
                    <td className="px-4 py-3">
                      <DecisionBadge decision={event.decision as 'ALLOW' | 'BLOCK' | 'REQUIRE_APPROVAL'} />
                    </td>
                    <td className="px-4 py-3">
                      <RiskBadge tier={event.risk_score > 75 ? 'CRITICAL' : event.risk_score > 50 ? 'HIGH' : event.risk_score > 25 ? 'MEDIUM' : 'LOW'} score={event.risk_score} />
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

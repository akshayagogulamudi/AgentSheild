import { useEffect, useState } from 'react'
import { Activity, CheckCircle2, XCircle, AlertTriangle, Zap } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
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

  const timelineData = [
    { time: '09:00', requests: 5, blocked: 1 },
    { time: '09:15', requests: 8, blocked: 2 },
    { time: '09:30', requests: 6, blocked: 1 },
    { time: '09:45', requests: 12, blocked: 3 },
    { time: '10:00', requests: 9, blocked: 2 },
    { time: '10:15', requests: 14, blocked: 4 },
  ]

  const threatData = [
    { name: 'Injection', value: injectionThreats || 1, color: '#06b6d4' },
    { name: 'Exfiltration', value: exfiltrationThreats || 1, color: '#ef4444' },
  ]

  const decisionData = [
    { name: 'Allowed', value: allowed || 1, color: '#22c55e' },
    { name: 'Blocked', value: blocked || 1, color: '#ef4444' },
    { name: 'Pending', value: pending || 1, color: '#f59e0b' },
  ]

  const recentIncidents = events.slice(0, 10)

  if (loading) {
    return <div className="p-8 text-slate-400">Loading...</div>
  }

  return (
    <div className="p-8 space-y-8 bg-slate-950 w-full">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 text-sm mt-1">Security Gateway Overview</p>
      </div>

      {/* Metrics - 5 Cards */}
      <div className="grid grid-cols-5 gap-4">
        <div className="bg-slate-800 border border-slate-700 rounded p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-slate-400 text-xs uppercase font-bold">Total</p>
              <p className="text-white text-2xl font-bold mt-2">{totalRequests}</p>
            </div>
            <Activity className="w-8 h-8 text-blue-400/30" />
          </div>
        </div>
        <div className="bg-slate-800 border border-slate-700 rounded p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-slate-400 text-xs uppercase font-bold">Allowed</p>
              <p className="text-green-400 text-2xl font-bold mt-2">{allowed}</p>
            </div>
            <CheckCircle2 className="w-8 h-8 text-green-400/30" />
          </div>
        </div>
        <div className="bg-slate-800 border border-slate-700 rounded p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-slate-400 text-xs uppercase font-bold">Blocked</p>
              <p className="text-red-400 text-2xl font-bold mt-2">{blocked}</p>
            </div>
            <XCircle className="w-8 h-8 text-red-400/30" />
          </div>
        </div>
        <div className="bg-slate-800 border border-slate-700 rounded p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-slate-400 text-xs uppercase font-bold">Pending</p>
              <p className="text-amber-400 text-2xl font-bold mt-2">{pending}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-amber-400/30" />
          </div>
        </div>
        <div className="bg-slate-800 border border-slate-700 rounded p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-slate-400 text-xs uppercase font-bold">Threats</p>
              <p className="text-cyan-400 text-2xl font-bold mt-2">{injectionThreats + exfiltrationThreats}</p>
            </div>
            <Zap className="w-8 h-8 text-cyan-400/30" />
          </div>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-2 gap-6">
        {/* Timeline */}
        <div className="bg-slate-800 border border-slate-700 rounded p-6">
          <h3 className="text-white font-bold mb-4">Security Timeline</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={timelineData}>
              <defs>
                <linearGradient id="colorReq" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
              <Area type="monotone" dataKey="requests" stroke="#06b6d4" fill="url(#colorReq)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart */}
        <div className="bg-slate-800 border border-slate-700 rounded p-6">
          <h3 className="text-white font-bold mb-4">Threats</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={threatData} cx="50%" cy="50%" innerRadius={50} outerRadius={90} dataKey="value">
                {threatData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-2 gap-6">
        {/* Bar Chart */}
        <div className="bg-slate-800 border border-slate-700 rounded p-6">
          <h3 className="text-white font-bold mb-4">Decisions</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={decisionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {decisionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Stats */}
        <div className="space-y-4">
          <div className="bg-slate-800 border border-slate-700 rounded p-4">
            <p className="text-slate-400 text-xs uppercase font-bold mb-2">Injection Threats</p>
            <p className="text-cyan-400 text-2xl font-bold">{injectionThreats}</p>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded p-4">
            <p className="text-slate-400 text-xs uppercase font-bold mb-2">Exfiltration</p>
            <p className="text-red-400 text-2xl font-bold">{exfiltrationThreats}</p>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded p-4">
            <p className="text-slate-400 text-xs uppercase font-bold mb-2">Block Rate</p>
            <p className="text-green-400 text-2xl font-bold">{totalRequests > 0 ? Math.round((blocked / totalRequests) * 100) : 0}%</p>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-800 border border-slate-700 rounded overflow-hidden">
        <div className="bg-slate-900 px-6 py-4 border-b border-slate-700">
          <h2 className="text-white font-bold">Recent Events</h2>
        </div>
        <table className="w-full">
          <thead>
            <tr className="bg-slate-900/50 border-b border-slate-700">
              <th className="text-left px-6 py-3 text-slate-300 text-sm font-semibold">ID</th>
              <th className="text-left px-6 py-3 text-slate-300 text-sm font-semibold">Time</th>
              <th className="text-left px-6 py-3 text-slate-300 text-sm font-semibold">Agent</th>
              <th className="text-left px-6 py-3 text-slate-300 text-sm font-semibold">Tool</th>
              <th className="text-left px-6 py-3 text-slate-300 text-sm font-semibold">Decision</th>
              <th className="text-left px-6 py-3 text-slate-300 text-sm font-semibold">Risk</th>
            </tr>
          </thead>
          <tbody>
            {recentIncidents.map((event) => (
              <tr key={event.id} className="border-b border-slate-700 hover:bg-slate-700/20">
                <td className="px-6 py-3 text-slate-300 text-sm">#{event.id}</td>
                <td className="px-6 py-3 text-slate-300 text-sm">{new Date(event.timestamp).toLocaleString()}</td>
                <td className="px-6 py-3 text-slate-300 text-sm">{event.agent_name}</td>
                <td className="px-6 py-3 text-slate-200 text-sm">{event.requested_tool}</td>
                <td className="px-6 py-3">
                  <DecisionBadge decision={event.decision as 'ALLOW' | 'BLOCK' | 'REQUIRE_APPROVAL'} />
                </td>
                <td className="px-6 py-3">
                  <RiskBadge tier={event.risk_score > 75 ? 'CRITICAL' : event.risk_score > 50 ? 'HIGH' : event.risk_score > 25 ? 'MEDIUM' : 'LOW'} score={event.risk_score} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

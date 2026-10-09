import { NavLink } from 'react-router-dom'
import { LayoutDashboard, MessageSquare, Shield, AlertTriangle, Activity, Lock, FlaskConical, Settings } from 'lucide-react'

export default function Sidebar() {
  const links = [
    { path: '/', label: 'Overview', icon: LayoutDashboard },
    { path: '/playground', label: 'Playground', icon: MessageSquare },
    { path: '/gateway', label: 'Security Gateway', icon: Shield },
    { path: '/threats', label: 'Threat Detection', icon: AlertTriangle },
    { path: '/logs', label: 'Activity Logs', icon: Activity },
    { path: '/policies', label: 'Security Policies', icon: Lock },
    { path: '/lab', label: 'Attack Lab', icon: FlaskConical },
    { path: '/settings', label: 'Settings', icon: Settings },
  ]

  return (
    <div className="fixed left-0 top-0 w-64 h-screen bg-[#0f1629] border-r border-slate-700 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-slate-700 flex items-center gap-2">
        <Shield className="w-6 h-6 text-blue-500" />
        <h1 className="text-lg font-bold text-white">AgentShield AI</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 overflow-y-auto">
        <ul className="space-y-2">
          {links.map(({ path, label, icon: Icon }) => (
            <li key={path}>
              <NavLink
                to={path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-400 hover:text-blue-400 hover:bg-slate-800/30'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span className="text-sm font-medium">{label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer Badge */}
      <div className="p-4 border-t border-slate-700">
        <div className="px-3 py-2 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-center">
          <p className="text-xs font-semibold text-yellow-400">DEMO MODE</p>
        </div>
      </div>
    </div>
  )
}

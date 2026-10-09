import type { ReactNode } from 'react'

interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: ReactNode
  color?: 'blue' | 'cyan' | 'green' | 'red' | 'yellow'
}

export default function MetricCard({
  title,
  value,
  subtitle,
  icon,
  color = 'blue',
}: MetricCardProps) {
  const colorMap = {
    blue: { icon: 'text-blue-500', glow: 'group-hover:shadow-blue-500/20', border: 'border-blue-500/30' },
    cyan: { icon: 'text-cyan-500', glow: 'group-hover:shadow-cyan-500/20', border: 'border-cyan-500/30' },
    green: { icon: 'text-green-500', glow: 'group-hover:shadow-green-500/20', border: 'border-green-500/30' },
    red: { icon: 'text-red-500', glow: 'group-hover:shadow-red-500/20', border: 'border-red-500/30' },
    yellow: { icon: 'text-yellow-500', glow: 'group-hover:shadow-yellow-500/20', border: 'border-yellow-500/30' },
  }

  const style = colorMap[color]

  return (
    <div className={`group glass border ${style.border} rounded-lg p-6 transition-all hover:shadow-lg ${style.glow}`}>
      <div className={`w-12 h-12 mb-4 ${style.icon}`}>
        {icon}
      </div>
      <p className="text-slate-400 text-sm font-medium mb-2">{title}</p>
      <p className="text-3xl font-bold text-white mb-1">{value}</p>
      {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
    </div>
  )
}

interface RiskBadgeProps {
  tier: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  score?: number
}

export default function RiskBadge({ tier, score }: RiskBadgeProps) {
  const styles = {
    LOW: 'bg-green-500/20 border-green-500/50 text-green-300',
    MEDIUM: 'bg-yellow-500/20 border-yellow-500/50 text-yellow-300',
    HIGH: 'bg-orange-500/20 border-orange-500/50 text-orange-300',
    CRITICAL: 'bg-red-500/20 border-red-500/50 text-red-300',
  }

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full border text-xs font-semibold ${styles[tier]}`}>
      {tier}
      {score !== undefined && <span className="ml-1 opacity-75">({score.toFixed(2)})</span>}
    </span>
  )
}

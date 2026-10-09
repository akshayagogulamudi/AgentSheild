interface DecisionBadgeProps {
  decision: 'ALLOW' | 'BLOCK' | 'REQUIRE_APPROVAL'
}

export default function DecisionBadge({ decision }: DecisionBadgeProps) {
  const styles = {
    ALLOW: 'bg-green-500/20 border-green-500/50 text-green-300',
    BLOCK: 'bg-red-500/20 border-red-500/50 text-red-300',
    REQUIRE_APPROVAL: 'bg-yellow-500/20 border-yellow-500/50 text-yellow-300',
  }

  const labels = {
    ALLOW: 'Allow',
    BLOCK: 'Block',
    REQUIRE_APPROVAL: 'Requires Approval',
  }

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full border text-xs font-semibold ${styles[decision]}`}>
      {labels[decision]}
    </span>
  )
}

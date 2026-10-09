interface TopNavProps {
  title: string
}

export default function TopNav({ title }: TopNavProps) {
  return (
    <div className="fixed top-0 left-64 right-0 h-16 glass border-b border-slate-700 flex items-center justify-between px-6">
      <h1 className="text-xl font-semibold text-white">{title}</h1>
      
      <div className="flex items-center gap-4">
        {/* Gateway Status */}
        <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/30 rounded-full">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-xs font-semibold text-green-400">OPERATIONAL</span>
        </div>
        
        {/* Demo Mode Indicator */}
        <div className="px-3 py-1 bg-yellow-500/10 border border-yellow-500/30 rounded-full">
          <span className="text-xs font-semibold text-yellow-400">Demo</span>
        </div>
      </div>
    </div>
  )
}

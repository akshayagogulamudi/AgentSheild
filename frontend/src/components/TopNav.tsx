interface TopNavProps {
  title: string
}

export default function TopNav({ title }: TopNavProps) {
  return (
    <div className="fixed top-0 left-64 right-0 h-16 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-8 z-50">
      <h1 className="text-xl font-semibold text-white">{title}</h1>
      
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-sm text-green-400">OPERATIONAL</span>
        </div>
        <div className="px-3 py-1 bg-yellow-500/20 rounded text-xs text-yellow-400">Demo</div>
      </div>
    </div>
  )
}

import { AlertCircle } from 'lucide-react'

export default function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-slate-400 mt-2">Configure gateway and notification preferences</p>
      </div>

      {/* Gateway Configuration */}
      <div className="glass border border-slate-700 rounded-lg p-6">
        <h2 className="text-lg font-bold text-white mb-4">Gateway Configuration</h2>
        <div className="space-y-4">
          <label className="flex items-center gap-3 cursor-not-allowed">
            <input
              type="checkbox"
              defaultChecked
              disabled
              className="w-4 h-4 rounded border-slate-600 cursor-not-allowed opacity-50"
            />
            <span className="text-slate-300">Enable DLP Scanning</span>
          </label>
          <label className="flex items-center gap-3 cursor-not-allowed">
            <input
              type="checkbox"
              defaultChecked
              disabled
              className="w-4 h-4 rounded border-slate-600 cursor-not-allowed opacity-50"
            />
            <span className="text-slate-300">Enable Injection Detection</span>
          </label>
          <label className="flex items-center gap-3 cursor-not-allowed">
            <input
              type="checkbox"
              defaultChecked
              disabled
              className="w-4 h-4 rounded border-slate-600 cursor-not-allowed opacity-50"
            />
            <span className="text-slate-300">Enable Intent Validation</span>
          </label>
          <p className="text-xs text-slate-500 mt-3">Read-only in demo mode</p>
        </div>
      </div>

      {/* Notification Settings */}
      <div className="glass border border-slate-700 rounded-lg p-6">
        <h2 className="text-lg font-bold text-white mb-4">Notification Settings</h2>
        <div className="space-y-4">
          <label className="flex items-center gap-3 cursor-not-allowed">
            <input
              type="checkbox"
              defaultChecked
              disabled
              className="w-4 h-4 rounded border-slate-600 cursor-not-allowed opacity-50"
            />
            <span className="text-slate-300">Email on Blocked Actions</span>
          </label>
          <label className="flex items-center gap-3 cursor-not-allowed">
            <input
              type="checkbox"
              defaultChecked
              disabled
              className="w-4 h-4 rounded border-slate-600 cursor-not-allowed opacity-50"
            />
            <span className="text-slate-300">Alert on Critical Threats</span>
          </label>
          <label className="flex items-center gap-3 cursor-not-allowed">
            <input
              type="checkbox"
              defaultChecked
              disabled
              className="w-4 h-4 rounded border-slate-600 cursor-not-allowed opacity-50"
            />
            <span className="text-slate-300">Daily Activity Summary</span>
          </label>
          <p className="text-xs text-slate-500 mt-3">Read-only in demo mode</p>
        </div>
      </div>

      {/* Read-only Notice */}
      <div className="glass border border-blue-500/50 bg-blue-500/10 rounded-lg p-4 flex gap-3">
        <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm text-blue-300 font-semibold">Settings are read-only in demo mode</p>
          <p className="text-xs text-blue-300/70 mt-1">
            Restart the backend to apply configuration changes.
          </p>
        </div>
      </div>
    </div>
  )
}

import { useEffect, useState } from 'react'
import { Edit2, Save, X, AlertCircle } from 'lucide-react'
import { getPolicies, updatePolicy } from '../services/api'
import type { Policy } from '../types'

const getRoleColor = (role: string) => {
  switch (role) {
    case 'employee':
      return 'bg-blue-500/20 border-blue-500/50 text-blue-300'
    case 'manager':
      return 'bg-yellow-500/20 border-yellow-500/50 text-yellow-300'
    case 'admin':
      return 'bg-red-500/20 border-red-500/50 text-red-300'
    default:
      return 'bg-slate-500/20 border-slate-500/50 text-slate-300'
  }
}

export default function SecurityPolicies() {
  const [policies, setPolicies] = useState<Policy[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editingJson, setEditingJson] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<{ success: boolean; message: string } | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const data = await getPolicies()
        setPolicies(data || [])
      } catch (error) {
        console.error('Failed to fetch policies:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const parseAllowedTools = (jsonString: string) => {
    try {
      return JSON.parse(jsonString)
    } catch {
      return []
    }
  }

  const handleEdit = (policy: Policy) => {
    setEditingId(policy.id)
    setEditingJson(policy.allowed_tools)
    setSaveStatus(null)
  }

  const handleCancel = () => {
    setEditingId(null)
    setEditingJson('')
    setSaveStatus(null)
  }

  const handleSave = async (id: number) => {
    try {
      setSaving(true)
      // Validate JSON
      JSON.parse(editingJson)
      await updatePolicy(id, { allowed_tools: editingJson })
      setPolicies((prev) =>
        prev.map((p) => (p.id === id ? { ...p, allowed_tools: editingJson } : p))
      )
      setEditingId(null)
      setEditingJson('')
      setSaveStatus({ success: true, message: 'Policy saved successfully' })
      setTimeout(() => setSaveStatus(null), 3000)
    } catch (error: any) {
      setSaveStatus({
        success: false,
        message: error.message.includes('JSON')
          ? 'Invalid JSON format'
          : 'Failed to save policy',
      })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="text-slate-400 py-12 text-center">Loading policies...</div>
  }

  return (
    <div className="space-y-6">
      {saveStatus && (
        <div
          className={`p-4 rounded-lg border ${saveStatus.success ? 'bg-green-500/10 border-green-500/50 text-green-300' : 'bg-red-500/10 border-red-500/50 text-red-300'}`}
        >
          {saveStatus.message}
        </div>
      )}

      {policies.length === 0 ? (
        <div className="text-slate-400 text-center py-12">No policies found</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {policies.map((policy) => (
            <div key={policy.id} className="glass border border-slate-700 rounded-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full border text-sm font-semibold ${getRoleColor(policy.role)}`}>
                      {policy.role.charAt(0).toUpperCase() + policy.role.slice(1)}
                    </span>
                  </div>
                  {policy.description && <p className="text-slate-400 text-sm mt-2">{policy.description}</p>}
                </div>
              </div>

              {editingId === policy.id ? (
                <div className="space-y-3">
                  <textarea
                    value={editingJson}
                    onChange={(e) => setEditingJson(e.target.value)}
                    className="w-full h-48 px-3 py-2 bg-slate-900 border border-slate-700 rounded text-slate-200 font-mono text-sm focus:outline-none focus:border-blue-500"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleSave(policy.id)}
                      disabled={saving}
                      className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-slate-600 transition-colors"
                    >
                      <Save className="w-4 h-4" />
                      Save
                    </button>
                    <button
                      onClick={handleCancel}
                      disabled={saving}
                      className="flex items-center gap-2 px-4 py-2 bg-slate-700 text-white rounded hover:bg-slate-600 disabled:bg-slate-600 transition-colors"
                    >
                      <X className="w-4 h-4" />
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-300 mb-3">Allowed Tools</h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-slate-700">
                            <th className="text-left px-3 py-2 text-slate-400 font-semibold text-xs">Tool</th>
                            <th className="text-left px-3 py-2 text-slate-400 font-semibold text-xs">Allowed Classifications</th>
                            <th className="text-left px-3 py-2 text-slate-400 font-semibold text-xs">Requires Approval</th>
                          </tr>
                        </thead>
                        <tbody>
                          {parseAllowedTools(policy.allowed_tools).map((tool: any, idx: number) => (
                            <tr key={idx} className="border-b border-slate-800">
                              <td className="px-3 py-2 text-slate-300">{tool.name || 'N/A'}</td>
                              <td className="px-3 py-2 text-slate-300 text-xs">
                                {Array.isArray(tool.allowed_classifications)
                                  ? tool.allowed_classifications.join(', ')
                                  : 'All'}
                              </td>
                              <td className="px-3 py-2 text-slate-300">
                                {tool.requires_approval ? (
                                  <span className="text-yellow-400">Yes</span>
                                ) : (
                                  <span className="text-slate-500">No</span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  <button
                    onClick={() => handleEdit(policy)}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  >
                    <Edit2 className="w-4 h-4" />
                    Edit Policy
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="glass border border-slate-700 rounded-lg p-4 flex gap-2">
        <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-slate-300">
          Settings are read-only in demo mode. Restart the backend to apply configuration changes.
        </p>
      </div>
    </div>
  )
}

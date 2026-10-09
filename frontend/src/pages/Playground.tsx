import { useState } from 'react'
import { Send, Loader } from 'lucide-react'
import DecisionBadge from '../components/DecisionBadge'
import RiskBadge from '../components/RiskBadge'
import ChecksTable from '../components/ChecksTable'
import { sendAgentMessage } from '../services/api'
import type { AgentResponse } from '../types'

interface Message {
  role: 'user' | 'assistant'
  content: string
  gatewayData?: AgentResponse
}

export default function Playground() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [role, setRole] = useState<'employee' | 'manager' | 'admin'>('employee')
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await sendAgentMessage({
        user_message: input,
        agent_role: role,
        conversation_history: [],
      })
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response_text || 'No response',
        gatewayData: response,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Error: Failed to send message to agent',
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-navy-900 to-navy-950">
      {/* Chat history */}
      <div className="flex-1 overflow-y-auto space-y-4 p-6 mb-4">
        {messages.length === 0 && (
          <div className="text-center text-slate-400 py-12">
            <p className="mb-4">Start a conversation with the AI agent</p>
            <p className="text-sm">💡 Tip: Type "inject" to trigger injection scenario, "exfiltrate" for DLP scenario, "delete" for unauthorized tool scenario</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'user' ? (
              <div className="max-w-md bg-blue-600 text-white rounded-lg p-4">{msg.content}</div>
            ) : (
              <div className="max-w-2xl space-y-3">
                <div className="bg-slate-800 text-slate-100 rounded-lg p-4">{msg.content}</div>

                {msg.gatewayData?.gateway_decisions && msg.gatewayData.gateway_decisions.length > 0 && (
                  <div className="space-y-3">
                    {msg.gatewayData.gateway_decisions.map((decision, didx) => (
                      <div key={didx} className="bg-slate-800 rounded-lg p-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-slate-200">{decision.tool_name}</span>
                          <DecisionBadge decision={decision.decision as 'ALLOW' | 'BLOCK' | 'REQUIRE_APPROVAL'} />
                        </div>
                        <div className="flex gap-2">
                          <RiskBadge tier={decision.risk_tier as 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'} score={decision.risk_score} />
                        </div>
                        <p className="text-sm text-slate-300">{decision.explanation}</p>
                        {decision.checks && decision.checks.length > 0 && (
                          <div className="mt-3">
                            <p className="text-xs font-semibold text-slate-400 mb-2">Checks:</p>
                            <ChecksTable checks={decision.checks} />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 text-slate-100 rounded-lg p-4 flex items-center gap-2">
              <Loader className="w-4 h-4 animate-spin" />
              <span>Thinking...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-slate-700 bg-navy-900 p-4 space-y-3">
        <div className="flex gap-2">
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as 'employee' | 'manager' | 'admin')}
            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-200 text-sm focus:outline-none focus:border-blue-500"
          >
            <option value="employee">Employee</option>
            <option value="manager">Manager</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 resize-none"
            rows={3}
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        <p className="text-xs text-slate-500">💡 Tip: Type "inject" to trigger injection scenario, "exfiltrate" for DLP scenario, "delete" for unauthorized tool scenario</p>
      </div>
    </div>
  )
}

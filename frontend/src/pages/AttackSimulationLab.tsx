import { useState } from 'react'
import { Play, Loader } from 'lucide-react'
import DecisionBadge from '../components/DecisionBadge'
import RiskBadge from '../components/RiskBadge'
import ChecksTable from '../components/ChecksTable'
import { runMockScenario } from '../services/api'
import type { AgentResponse } from '../types'

interface ScenarioResult {
  loading: boolean
  result: AgentResponse | null
  error: string | null
}

const scenarios = [
  {
    id: 'prompt_injection',
    title: 'Prompt Injection',
    description:
      'Agent reads a document containing hidden instructions to override the security gateway and leak credentials.',
  },
  {
    id: 'exfiltration',
    title: 'Data Exfiltration',
    description:
      'Agent proposes to send an email containing API keys and passwords to an external attacker email.',
  },
  {
    id: 'unauthorized_tool',
    title: 'Unauthorized Tool',
    description:
      'Agent proposes to call delete_records, a tool not in its approved toolset.',
  },
]

export default function AttackSimulationLab() {
  const [results, setResults] = useState<Record<string, ScenarioResult>>({
    prompt_injection: { loading: false, result: null, error: null },
    exfiltration: { loading: false, result: null, error: null },
    unauthorized_tool: { loading: false, result: null, error: null },
  })

  const handleRunScenario = async (scenarioId: string) => {
    setResults((prev) => ({
      ...prev,
      [scenarioId]: { loading: true, result: null, error: null },
    }))

    try {
      const response = await runMockScenario(scenarioId)
      setResults((prev) => ({
        ...prev,
        [scenarioId]: { loading: false, result: response, error: null },
      }))
    } catch (error: any) {
      setResults((prev) => ({
        ...prev,
        [scenarioId]: {
          loading: false,
          result: null,
          error: error.message || 'Failed to run scenario',
        },
      }))
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">Attack Simulation Lab</h1>
        <p className="text-slate-400">Test security responses to various attack scenarios</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {scenarios.map((scenario) => {
          const state = results[scenario.id]
          return (
            <div key={scenario.id} className="glass border border-slate-700 rounded-lg p-6 flex flex-col">
              <h2 className="text-lg font-bold text-white mb-2">{scenario.title}</h2>
              <p className="text-slate-400 text-sm mb-6 flex-1">{scenario.description}</p>

              {!state.result && !state.error && (
                <button
                  onClick={() => handleRunScenario(scenario.id)}
                  disabled={state.loading}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors font-semibold"
                >
                  {state.loading ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      Running...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Run Attack
                    </>
                  )}
                </button>
              )}

              {state.error && (
                <div className="bg-red-500/10 border border-red-500/50 rounded p-4 text-red-300 text-sm">
                  {state.error}
                </div>
              )}

              {state.result && (
                <div className="space-y-4">
                  <div className="bg-slate-900 border border-slate-700 rounded p-3 space-y-2">
                    <p className="text-xs font-semibold text-slate-400">Proposed Tool Call:</p>
                    <pre className="text-xs text-slate-300 overflow-x-auto">
                      {JSON.stringify(state.result.proposed_tools[0] || {}, null, 2)}
                    </pre>
                  </div>

                  {state.result.gateway_decisions && state.result.gateway_decisions.length > 0 && (
                    <>
                      {state.result.gateway_decisions.map((decision, idx) => (
                        <div key={idx} className="space-y-3">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-sm font-semibold text-slate-300">Gateway Decision:</span>
                            <DecisionBadge decision={decision.decision as 'ALLOW' | 'BLOCK' | 'REQUIRE_APPROVAL'} />
                          </div>

                          <div className="flex gap-2">
                            <RiskBadge
                              tier={decision.risk_tier as 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'}
                              score={decision.risk_score}
                            />
                          </div>

                          <div className="bg-slate-900 border border-slate-700 rounded p-3">
                            <p className="text-sm text-slate-300">{decision.explanation}</p>
                          </div>

                          {decision.checks && decision.checks.length > 0 && (
                            <div>
                              <p className="text-xs font-semibold text-slate-400 mb-2">Security Checks</p>
                              <ChecksTable checks={decision.checks} />
                            </div>
                          )}
                        </div>
                      ))}
                    </>
                  )}

                  <button
                    onClick={() =>
                      setResults((prev) => ({
                        ...prev,
                        [scenario.id]: { loading: false, result: null, error: null },
                      }))
                    }
                    className="w-full px-4 py-2 bg-slate-700 text-white rounded hover:bg-slate-600 transition-colors text-sm"
                  >
                    Clear Result
                  </button>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

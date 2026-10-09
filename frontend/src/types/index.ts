export interface CheckResult { name: string; passed: boolean; reason: string; details?: any; }
export interface GatewayDecision { decision: 'ALLOW'|'BLOCK'|'REQUIRE_APPROVAL'; risk_score: number; risk_tier: 'LOW'|'MEDIUM'|'HIGH'|'CRITICAL'; explanation: string; checks: CheckResult[]; requires_approval: boolean; pending_approval_id?: number|null; }
export interface SecurityEvent { id: number; timestamp: string; agent_name: string; requested_tool: string; arguments?: string; decision: string; risk_score: number; reason?: string; checks_passed?: string[]|null; checks_failed?: string[]|null; }
export interface Threat { id: number; event_id?: number; timestamp: string; threat_category: string; severity?: string; agent_identifier?: string; requested_action?: string; reason_for_detection?: string; gateway_response?: string; }
export interface Policy { id: number; role: string; description?: string; allowed_tools: string; }
export interface AgentGatewayDecision { tool_name: string; decision: string; risk_score: number; risk_tier: string; explanation: string; checks: CheckResult[]; }
export interface AgentResponse { response_text: string; proposed_tools: any[]; gateway_decisions: AgentGatewayDecision[]; executed_tools: string[]; blocked_tools: string[]; }
export interface PendingApproval { id: number; event_id?: number; timestamp: string; agent_name: string; tool_name: string; arguments?: string; reason?: string; status: string; }

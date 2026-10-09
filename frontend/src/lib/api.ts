// AgentShield Backend API Client

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Types matching backend models
export interface AuditLog {
  id: string;
  owner_id: string;
  agent_name: string;
  action: string;
  target: string;
  threat_level: "low" | "medium" | "high" | "critical";
  decision: "ALLOW" | "REDACT" | "REVIEW" | "BLOCK";
  reasons: string[];
  source: string;
  executed: boolean;
  created_at: string;
}

export interface Agent {
  id: string;
  name: string;
  status: "active" | "inactive";
  created_at: string;
  updated_at?: string;
}

export interface Email {
  id: string;
  owner_id: string;
  sender: string;
  subject: string;
  body: string;
  received_at: string;
  scan?: {
    level: "low" | "medium" | "high" | "critical";
    threats?: string[];
  };
}

export interface Resource {
  id: string;
  owner_id: string;
  path: string;
  classification: string;
  created_at: string;
}

export interface Policy {
  id: string;
  owner_id: string;
  name: string;
  rules: any[];
  created_at: string;
  updated_at?: string;
}

// API Methods
export const api = {
  // Get all audit logs
  async getLogs(): Promise<AuditLog[]> {
    try {
      const response = await fetch(`${API_BASE}/events`, {
        headers: { "Accept": "application/json" },
      });
      if (!response.ok) throw new Error(`Failed to fetch logs: ${response.statusText}`);
      const data = await response.json();
      return Array.isArray(data) ? data : data.data || [];
    } catch (error) {
      console.error("Failed to fetch audit logs:", error);
      return [];
    }
  },

  // Get threats
  async getThreats() {
    try {
      const response = await fetch(`${API_BASE}/threats`, {
        headers: { "Accept": "application/json" },
      });
      if (!response.ok) throw new Error(`Failed to fetch threats: ${response.statusText}`);
      return await response.json();
    } catch (error) {
      console.error("Failed to fetch threats:", error);
      return [];
    }
  },

  // Get policies
  async getPolicies(): Promise<Policy[]> {
    try {
      const response = await fetch(`${API_BASE}/policies`, {
        headers: { "Accept": "application/json" },
      });
      if (!response.ok) throw new Error(`Failed to fetch policies: ${response.statusText}`);
      const data = await response.json();
      return Array.isArray(data) ? data : data.data || [];
    } catch (error) {
      console.error("Failed to fetch policies:", error);
      return [];
    }
  },

  // Evaluate agent message
  async evaluateMessage(payload: {
    agent_name: string;
    action: string;
    tool: string;
    destination: string;
    content: string;
  }) {
    try {
      const response = await fetch(`${API_BASE}/agent/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
        },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error(`Evaluation failed: ${response.statusText}`);
      return await response.json();
    } catch (error) {
      console.error("Failed to evaluate message:", error);
      throw error;
    }
  },

  // Get health/status
  async getStatus() {
    try {
      const response = await fetch(`${API_BASE}/gateway/evaluate`, {
        method: "GET",
        headers: { "Accept": "application/json" },
      });
      if (!response.ok) throw new Error(`Failed to get status: ${response.statusText}`);
      return await response.json();
    } catch (error) {
      console.error("Failed to get status:", error);
      return { status: "offline" };
    }
  },

  // Mock data for agents if backend is offline
  getMockAgents(): Agent[] {
    return [
      { id: "1", name: "InboxAssistant", status: "active", created_at: new Date().toISOString() },
      { id: "2", name: "DevOpsAgent", status: "active", created_at: new Date().toISOString() },
      { id: "3", name: "FinanceBot", status: "inactive", created_at: new Date().toISOString() },
    ];
  },

  // Mock data for emails if backend is offline
  getMockEmails(): Email[] {
    return [
      {
        id: "1",
        owner_id: "user1",
        sender: "maria@partners.acme-corp.example",
        subject: "Q4 kickoff agenda",
        body: "Hi team, attached is the agenda for the Q4 kickoff on Monday.",
        received_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        scan: { level: "low" },
      },
    ];
  },
};

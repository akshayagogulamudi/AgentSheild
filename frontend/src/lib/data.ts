import { queryOptions } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { api } from "@/lib/api";

const q = <T,>(key: string, fn: () => Promise<T>) => queryOptions({ queryKey: [key], queryFn: fn });

// Use backend API for agents - with fallback to mock data
export const agentsQ = q("agents", async () => {
  try {
    const response = await fetch(import.meta.env.VITE_API_BASE + "/agents", {
      headers: { "Accept": "application/json" },
    });
    if (response.ok) {
      const data = await response.json();
      return Array.isArray(data) ? data : data.data || [];
    }
  } catch (error) {
    console.warn("Backend agents unavailable, using mock data");
  }
  return api.getMockAgents();
});

// Use backend API for resources
export const resourcesQ = q("resources", async () => {
  try {
    const response = await fetch(import.meta.env.VITE_API_BASE + "/resources", {
      headers: { "Accept": "application/json" },
    });
    if (response.ok) {
      const data = await response.json();
      return Array.isArray(data) ? data : data.data || [];
    }
  } catch (error) {
    console.warn("Backend resources unavailable");
  }
  return [];
});

// Use backend API for policy
export const policyQ = q("policy", async () => {
  try {
    const response = await fetch(import.meta.env.VITE_API_BASE + "/policies", {
      headers: { "Accept": "application/json" },
    });
    if (response.ok) {
      const data = await response.json();
      return Array.isArray(data) ? data[0] : data.data?.[0];
    }
  } catch (error) {
    console.warn("Backend policy unavailable");
  }
  return null;
});

// Use backend API for emails - with fallback to mock data
export const emailsQ = q("emails", async () => {
  try {
    const response = await fetch(import.meta.env.VITE_API_BASE + "/emails", {
      headers: { "Accept": "application/json" },
    });
    if (response.ok) {
      const data = await response.json();
      return Array.isArray(data) ? data : data.data || [];
    }
  } catch (error) {
    console.warn("Backend emails unavailable, using mock data");
  }
  return api.getMockEmails();
});

// Use backend API for audit logs
export const logsQ = q("audit_logs", async () => {
  try {
    return await api.getLogs();
  } catch (error) {
    console.warn("Backend audit logs unavailable, using Supabase fallback");
    return (await supabase.from("audit_logs").select("*").order("created_at", { ascending: false }).limit(500)).data ?? [];
  }
});

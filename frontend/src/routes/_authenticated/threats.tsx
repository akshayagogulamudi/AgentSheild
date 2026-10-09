import { createFileRoute } from "@tanstack/react-router";
import { PageHeader, Pill, fmtTime } from "@/components/sec-ui";

export const Route = createFileRoute("/_authenticated/threats")({
  head: () => ({ meta: [{ title: "Threat Detection — Sentinel AI" }] }),
  component: ThreatDetection,
});

function ThreatDetection() {
  const threats = [
    { id: 1, category: "Prompt Injection", severity: "critical", agent: "InboxAssistant", time: new Date().toISOString(), blocked: true },
    { id: 2, category: "Data Exfiltration", severity: "high", agent: "DevOpsAgent", time: new Date(Date.now() - 3600000).toISOString(), blocked: true },
    { id: 3, category: "Privilege Escalation", severity: "critical", agent: "FinanceBot", time: new Date(Date.now() - 7200000).toISOString(), blocked: true },
  ];

  return (
    <>
      <PageHeader title="Threat Detection" subtitle="Detected and blocked threats." />
      <div className="panel p-6">
        <div className="space-y-2">
          {threats.map((t) => (
            <div key={t.id} className="flex flex-wrap items-center gap-3 border-b border-border/50 px-4 py-3 last:border-0">
              <Pill tone={t.severity} />
              <span className="font-medium">{t.category}</span>
              <span className="text-sm text-muted-foreground">{t.agent}</span>
              <span className="flex-1" />
              <Pill tone="BLOCK" />
              <span className="text-xs text-muted-foreground">{fmtTime(t.time)}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

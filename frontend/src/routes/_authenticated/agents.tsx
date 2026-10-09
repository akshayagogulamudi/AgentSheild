import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { agentsQ } from "@/lib/data";
import { PageHeader, Pill, fmtTime } from "@/components/sec-ui";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/_authenticated/agents")({
  head: () => ({ meta: [{ title: "Agent Monitor — Sentinel AI" }] }),
  loader: ({ context }) => context.queryClient.ensureQueryData(agentsQ),
  component: AgentMonitor,
});

function AgentMonitor() {
  const { data: agents } = useSuspenseQuery(agentsQ);

  return (
    <>
      <PageHeader title="Agent Monitor" subtitle="Track AI agent status and activity." />
      <div className="panel p-6">
        <div className="space-y-4">
          {agents.length === 0 ? (
            <p className="text-muted-foreground">No agents configured.</p>
          ) : (
            agents.map((a) => (
              <div key={a.id} className="flex items-center justify-between rounded-lg border border-border p-4">
                <div>
                  <div className="font-medium">{a.name}</div>
                  <div className="text-sm text-muted-foreground">{a.id}</div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant={a.status === "active" ? "default" : "secondary"}>{a.status}</Badge>
                  <span className="text-sm text-muted-foreground">{fmtTime(a.created_at)}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
}

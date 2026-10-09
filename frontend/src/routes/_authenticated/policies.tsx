import { createFileRoute } from "@tanstack/react-router";
import { PageHeader } from "@/components/sec-ui";
import { Card } from "@/components/ui/card";

export const Route = createFileRoute("/_authenticated/policies")({
  head: () => ({ meta: [{ title: "Policy Manager — Sentinel AI" }] }),
  component: PolicyManager,
});

function PolicyManager() {
  const policies = [
    { id: 1, name: "Employee Policy", agents: ["InboxAssistant", "FinanceBot"], rules: 12 },
    { id: 2, name: "DevOps Policy", agents: ["DevOpsAgent"], rules: 8 },
    { id: 3, name: "Default Policy", agents: ["All"], rules: 5 },
  ];

  return (
    <>
      <PageHeader title="Policy Manager" subtitle="Define security policies for agents." />
      <div className="space-y-4">
        {policies.map((p) => (
          <Card key={p.id} className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold">{p.name}</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {p.agents.join(", ")} • {p.rules} rules
                </p>
              </div>
              <span className="text-sm text-primary">Enabled</span>
            </div>
          </Card>
        ))}
      </div>
    </>
  );
}

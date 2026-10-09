import { createFileRoute } from "@tanstack/react-router";
import { PageHeader, Pill } from "@/components/sec-ui";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export const Route = createFileRoute("/_authenticated/lab")({
  head: () => ({ meta: [{ title: "Attack Simulation Lab — Sentinel AI" }] }),
  component: AttackLab,
});

function AttackLab() {
  const scenarios = [
    { id: 1, name: "Prompt Injection", desc: "Test injection detection", difficulty: "medium" },
    { id: 2, name: "Data Exfiltration", desc: "Test data loss prevention", difficulty: "high" },
    { id: 3, name: "Privilege Escalation", desc: "Test privilege checks", difficulty: "hard" },
  ];

  return (
    <>
      <PageHeader title="Attack Simulation Lab" subtitle="Run safe attack scenarios to test security rules." />
      <div className="space-y-4">
        {scenarios.map((s) => (
          <Card key={s.id} className="p-4 flex justify-between items-center">
            <div>
              <h3 className="font-semibold">{s.name}</h3>
              <p className="text-sm text-muted-foreground">{s.desc}</p>
            </div>
            <div className="flex items-center gap-3">
              <Pill tone={s.difficulty === "hard" ? "critical" : s.difficulty === "high" ? "high" : "medium"}>
                {s.difficulty}
              </Pill>
              <Button size="sm">Run Test</Button>
            </div>
          </Card>
        ))}
      </div>
    </>
  );
}

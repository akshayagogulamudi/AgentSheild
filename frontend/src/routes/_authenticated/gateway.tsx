import { createFileRoute } from "@tanstack/react-router";
import { PageHeader } from "@/components/sec-ui";
import { Card } from "@/components/ui/card";

export const Route = createFileRoute("/_authenticated/gateway")({
  head: () => ({ meta: [{ title: "Security Gateway — Sentinel AI" }] }),
  component: SecurityGateway,
});

function SecurityGateway() {
  return (
    <>
      <PageHeader title="Security Gateway" subtitle="Core gateway configuration and status." />
      <div className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <Card className="p-4">
            <h3 className="font-semibold">Gateway Status</h3>
            <p className="mt-2 text-sm text-muted-foreground">✅ Online and monitoring</p>
          </Card>
          <Card className="p-4">
            <h3 className="font-semibold">Response Time</h3>
            <p className="mt-2 text-sm text-muted-foreground">&lt; 50ms average</p>
          </Card>
        </div>
        <div className="panel p-6">
          <h3 className="font-semibold mb-4">Decision Modes</h3>
          <ul className="space-y-2 text-sm">
            <li>• <span className="font-mono">ALLOW</span> - Request permitted</li>
            <li>• <span className="font-mono">REDACT</span> - Sensitive data removed</li>
            <li>• <span className="font-mono">REVIEW</span> - Requires human approval</li>
            <li>• <span className="font-mono">BLOCK</span> - Request denied</li>
          </ul>
        </div>
      </div>
    </>
  );
}

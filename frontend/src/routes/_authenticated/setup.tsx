import { createFileRoute } from "@tanstack/react-router";
import { PageHeader } from "@/components/sec-ui";
import { Card } from "@/components/ui/card";
import { BookOpen, Code, Download } from "lucide-react";

export const Route = createFileRoute("/_authenticated/setup")({
  head: () => ({ meta: [{ title: "Setup & Documentation — Sentinel AI" }] }),
  component: Setup,
});

function Setup() {
  return (
    <>
      <PageHeader title="Setup & Documentation" subtitle="Get started with AgentShield." />
      <div className="space-y-4">
        <Card className="p-6">
          <div className="flex items-start gap-4">
            <BookOpen className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold">Documentation</h3>
              <p className="text-sm text-muted-foreground mt-1">Read the complete setup guide and API reference.</p>
            </div>
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-start gap-4">
            <Code className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold">Backend API</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Access Swagger docs at <span className="font-mono">http://localhost:8000/docs</span>
              </p>
            </div>
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-start gap-4">
            <Download className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold">GitHub Repository</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Clone or fork: <span className="font-mono text-xs">https://github.com/akshayagogulamudi/AgentSheild</span>
              </p>
            </div>
          </div>
        </Card>
      </div>
    </>
  );
}

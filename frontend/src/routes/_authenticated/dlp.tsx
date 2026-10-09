import { createFileRoute } from "@tanstack/react-router";
import { PageHeader } from "@/components/sec-ui";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertTriangle } from "lucide-react";

export const Route = createFileRoute("/_authenticated/dlp")({
  head: () => ({ meta: [{ title: "Data Loss Prevention — Sentinel AI" }] }),
  component: DataLossPrevention,
});

function DataLossPrevention() {
  return (
    <>
      <PageHeader title="Data Loss Prevention" subtitle="Monitor and block sensitive data exfiltration." />
      <div className="space-y-4">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Sensitive Data Detected</AlertTitle>
          <AlertDescription>Scanning emails and agent outputs for API keys, passwords, and personal information.</AlertDescription>
        </Alert>
        <div className="panel p-6">
          <div className="text-center text-muted-foreground">
            <p>Data loss prevention patterns:</p>
            <ul className="mt-4 space-y-2 text-sm">
              <li>✓ API Key Detection</li>
              <li>✓ Password Pattern Recognition</li>
              <li>✓ PII/SSN Detection</li>
              <li>✓ Credit Card Numbers</li>
              <li>✓ Private Key Detection</li>
            </ul>
          </div>
        </div>
      </div>
    </>
  );
}

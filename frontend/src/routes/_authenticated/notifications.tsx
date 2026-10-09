import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import { PageHeader, Pill, fmtTime, Empty } from "@/components/sec-ui";
import { Card } from "@/components/ui/card";
import { Bell, Mail, MessageSquare, AlertTriangle, Clock } from "lucide-react";

const notificationSummaryQ = {
  queryKey: ["notificationSummary"],
  queryFn: () => api.getNotificationSummary(),
};

const notificationsQ = {
  queryKey: ["notifications"],
  queryFn: () => api.getNotifications(50, 0),
};

export const Route = createFileRoute("/_authenticated/notifications")({
  head: () => ({
    meta: [
      { title: "Notifications — AgentShield AI" },
      { name: "description", content: "Threat notifications and alerts" },
    ],
  }),
  loader: ({ context }) => Promise.all([
    context.queryClient.ensureQueryData(notificationSummaryQ),
    context.queryClient.ensureQueryData(notificationsQ),
  ]),
  component: NotificationsPage,
});

function NotificationsPage() {
  const { data: summary } = useSuspenseQuery(notificationSummaryQ);
  const { data: notificationsData } = useSuspenseQuery(notificationsQ);
  const notifications = notificationsData?.items || [];

  const [selectedId, setSelectedId] = useState<number | null>(notifications[0]?.id ?? null);
  const selectedNotification = notifications.find((n) => n.id === selectedId);

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case "critical": return "destructive";
      case "high": return "warning";
      case "medium": return "warning";
      default: return "success";
    }
  };

  return (
    <>
      <PageHeader
        title="Threat Notifications"
        subtitle="Email and SMS alerts for security events"
        icon={Bell}
      />

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4 mb-6">
        <Card className="p-5">
          <div className="text-sm font-medium text-muted-foreground">Critical Alerts</div>
          <div className="text-3xl font-bold text-red-600 mt-2">{summary.total_critical}</div>
        </Card>
        <Card className="p-5">
          <div className="text-sm font-medium text-muted-foreground">High Severity</div>
          <div className="text-3xl font-bold text-orange-600 mt-2">{summary.total_high}</div>
        </Card>
        <Card className="p-5">
          <div className="text-sm font-medium text-muted-foreground">Unread (24h)</div>
          <div className="text-3xl font-bold text-blue-600 mt-2">{summary.unread_count}</div>
        </Card>
        <Card className="p-5">
          <div className="text-sm font-medium text-muted-foreground">Total Notifications</div>
          <div className="text-3xl font-bold text-slate-600 mt-2">{notificationsData.total}</div>
        </Card>
      </div>

      {/* Notifications List and Detail */}
      {notifications.length === 0 ? (
        <Empty title="No Notifications">
          Threat alerts will appear here when security events are detected.
        </Empty>
      ) : (
        <div className="grid gap-4 lg:grid-cols-[400px_1fr]">
          {/* Notification List */}
          <div className="panel divide-y divide-border overflow-hidden max-h-96 overflow-y-auto">
            {notifications.map((notification) => (
              <button
                key={notification.id}
                onClick={() => setSelectedId(notification.id)}
                className={`block w-full p-4 text-left transition-colors hover:bg-muted ${
                  selectedId === notification.id ? "bg-accent" : ""
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      {notification.decision === "BLOCK" ? (
                        <AlertTriangle className="h-4 w-4 text-red-500" />
                      ) : (
                        <Clock className="h-4 w-4 text-yellow-500" />
                      )}
                      <span className="truncate text-sm font-medium">
                        {notification.agent_name}
                      </span>
                    </div>
                    <div className="mt-1 truncate font-mono text-xs text-muted-foreground">
                      {notification.attempted_tool}
                    </div>
                    <div className="mt-1 text-xs text-muted-foreground">
                      {fmtTime(notification.timestamp)}
                    </div>
                  </div>
                  <Pill tone={getSeverityColor(notification.severity)}>
                    {notification.severity?.slice(0, 1)?.toUpperCase()}
                  </Pill>
                </div>
              </button>
            ))}
          </div>

          {/* Notification Detail */}
          {selectedNotification && (
            <div className="space-y-4">
              <Card className="p-5">
                <div className="text-lg font-semibold flex items-center gap-2">
                  {selectedNotification.decision === "BLOCK" ? (
                    <AlertTriangle className="h-5 w-5 text-red-500" />
                  ) : (
                    <Clock className="h-5 w-5 text-yellow-500" />
                  )}
                  Incident {selectedNotification.incident_id}
                </div>
                <div className="text-sm text-muted-foreground mt-2">
                  {fmtTime(selectedNotification.created_at)}
                </div>
              </Card>

              <Card className="p-5">
                <div className="space-y-3">
                  <div className="font-semibold">Threat Details</div>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <div className="text-muted-foreground text-xs font-semibold">Agent</div>
                      <div className="font-mono">{selectedNotification.agent_name}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground text-xs font-semibold">Tool</div>
                      <div className="font-mono">{selectedNotification.attempted_tool}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground text-xs font-semibold">Category</div>
                      <div className="font-mono">
                        {selectedNotification.threat_category?.replace(/_/g, " ")}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground text-xs font-semibold">Decision</div>
                      <div className="font-mono">{selectedNotification.decision}</div>
                    </div>
                  </div>
                </div>
              </Card>

              <Card className="p-5 bg-blue-50">
                <div className="text-sm text-blue-700">
                  Notification system is in MOCK MODE. No real emails or SMS are being sent.
                </div>
              </Card>
            </div>
          )}
        </div>
      )}
    </>
  );
}

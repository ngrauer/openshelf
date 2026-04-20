import { useState } from "react";
import { DashboardLayout, DASHBOARD_VIEWS } from "@/components/DashboardLayout";
import { ChatbotWidget } from "@/components/ChatbotWidget";
import { ShoppingView } from "@/pages/ShoppingView";
import { MyListingsView } from "@/pages/MyListingsView";
import { MessagesView } from "@/pages/MessagesView";

// Shell for the authenticated experience. Hosts the persistent layout and
// toggles between top-level views. The chatbot widget mounts here so it's
// reachable from any view.
export function DashboardPage() {
  const [view, setView] = useState(DASHBOARD_VIEWS.SHOPPING);
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <>
      <DashboardLayout
        view={view}
        onViewChange={setView}
        onOpenChat={() => setChatOpen((o) => !o)}
      >
        {view === DASHBOARD_VIEWS.SHOPPING && <ShoppingView />}
        {view === DASHBOARD_VIEWS.MY_LISTINGS && <MyListingsView />}
        {view === DASHBOARD_VIEWS.MESSAGES && <MessagesView />}
      </DashboardLayout>
      <ChatbotWidget open={chatOpen} onClose={() => setChatOpen(false)} />
    </>
  );
}

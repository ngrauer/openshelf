import { useState } from "react";
import { DashboardLayout, DASHBOARD_VIEWS } from "@/components/DashboardLayout";
import { ShoppingView } from "@/pages/ShoppingView";
import { MyListingsView } from "@/pages/MyListingsView";
import { MessagesView } from "@/pages/MessagesView";

export function DashboardPage() {
  const [view, setView] = useState(DASHBOARD_VIEWS.SHOPPING);

  return (
    <DashboardLayout view={view} onViewChange={setView}>
      {view === DASHBOARD_VIEWS.SHOPPING && <ShoppingView />}
      {view === DASHBOARD_VIEWS.MY_LISTINGS && <MyListingsView />}
      {view === DASHBOARD_VIEWS.MESSAGES && <MessagesView />}
    </DashboardLayout>
  );
}

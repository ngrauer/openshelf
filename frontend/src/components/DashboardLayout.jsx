import { BookOpen, Inbox, LogOut, ShoppingBag, Tag } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { NotificationBell } from "@/components/NotificationBell";

// Top-level view keys. Stays as in-component state rather than route params
// because the shell is a single protected page and the views are fast to
// toggle. C7 (messaging) will likely add a third key "inbox".
export const DASHBOARD_VIEWS = {
  SHOPPING: "shopping",
  MY_LISTINGS: "my-listings",
  MESSAGES: "messages",
};

const NAV_ITEMS = [
  { key: DASHBOARD_VIEWS.SHOPPING, label: "Shopping", icon: ShoppingBag },
  { key: DASHBOARD_VIEWS.MY_LISTINGS, label: "My Listings", icon: Tag },
  { key: DASHBOARD_VIEWS.MESSAGES, label: "Messages", icon: Inbox },
];

export function DashboardLayout({ view, onViewChange, children }) {
  const { user, logout } = useAuth();

  const initials = `${user?.first_name?.[0] ?? ""}${user?.last_name?.[0] ?? ""}`.toUpperCase();

  return (
    <div className="min-h-screen bg-muted/30">
      <header className="sticky top-0 z-30 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
        <div className="container flex h-16 items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <BookOpen className="h-4 w-4" />
            </div>
            <span className="text-lg font-semibold">OpenShelf</span>
          </div>

          <nav className="hidden items-center gap-1 md:flex">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const active = view === item.key;
              return (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => onViewChange(item.key)}
                  className={cn(
                    "inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    active
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </button>
              );
            })}
          </nav>

          <div className="flex items-center gap-2">
            <NotificationBell
              onOpenMessages={() => onViewChange(DASHBOARD_VIEWS.MESSAGES)}
            />

            <div className="hidden items-center gap-2 sm:flex">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                {initials || "?"}
              </div>
              <div className="leading-tight">
                <div className="text-sm font-medium">
                  {user?.first_name} {user?.last_name}
                </div>
                <div className="text-xs text-muted-foreground">
                  {user?.email}
                </div>
              </div>
            </div>

            <Button variant="ghost" size="sm" onClick={logout}>
              <LogOut className="mr-2 h-4 w-4" />
              Sign out
            </Button>
          </div>
        </div>

        {/* Mobile nav */}
        <div className="container flex gap-1 overflow-x-auto border-t py-2 md:hidden">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = view === item.key;
            return (
              <button
                key={item.key}
                type="button"
                onClick={() => onViewChange(item.key)}
                className={cn(
                  "inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </button>
            );
          })}
        </div>
      </header>

      <main className="container py-8">{children}</main>
    </div>
  );
}

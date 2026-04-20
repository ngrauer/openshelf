import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Inbox, Loader2, Send, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/contexts/AuthContext";
import { conversationsApi } from "@/lib/api";
import { useChatSocket } from "@/hooks/useChatSocket";
import { cn } from "@/lib/utils";

function formatTime(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  const sameDay = d.toDateString() === now.toDateString();
  if (sameDay) {
    return d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  }
  return d.toLocaleDateString([], { month: "short", day: "numeric" });
}

export function MessagesView() {
  const { user } = useAuth();
  const [selectedId, setSelectedId] = useState(null);

  // Inbox list — polls every 10s so new conversations started from the
  // listing detail page show up without a manual refresh.
  const inboxQuery = useQuery({
    queryKey: ["conversations"],
    queryFn: () => conversationsApi.list(),
    refetchInterval: 10_000,
  });

  const conversations = inboxQuery.data ?? [];
  const totalUnread = conversations.reduce(
    (sum, c) => sum + (c.unread_count || 0),
    0,
  );

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Messages</h1>
          <p className="text-muted-foreground">
            {totalUnread > 0
              ? `${totalUnread} unread message${totalUnread === 1 ? "" : "s"}`
              : "You're all caught up."}
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-[320px_1fr]">
        {/* Inbox list — hidden on mobile when a thread is open. */}
        <Card className={cn("md:block", selectedId ? "hidden" : "block")}>
          <CardContent className="divide-y p-0">
            {inboxQuery.isLoading ? (
              <div className="flex items-center gap-2 p-6 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" /> Loading...
              </div>
            ) : conversations.length === 0 ? (
              <div className="flex flex-col items-center gap-2 p-10 text-center text-sm text-muted-foreground">
                <Inbox className="h-6 w-6" />
                No conversations yet.
              </div>
            ) : (
              conversations.map((row) => (
                <InboxRow
                  key={row.conversation.id}
                  row={row}
                  active={selectedId === row.conversation.id}
                  onSelect={() => setSelectedId(row.conversation.id)}
                />
              ))
            )}
          </CardContent>
        </Card>

        {/* Thread pane */}
        <div className={cn("md:block", selectedId ? "block" : "hidden md:block")}>
          {selectedId ? (
            <ThreadView
              key={selectedId}
              conversationId={selectedId}
              currentUserId={user?.id}
              onBack={() => setSelectedId(null)}
            />
          ) : (
            <Card>
              <CardContent className="flex min-h-[400px] flex-col items-center justify-center gap-2 text-sm text-muted-foreground">
                <Inbox className="h-8 w-8" />
                Select a conversation to start reading.
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

function InboxRow({ row, active, onSelect }) {
  const other = row.other_user;
  const last = row.last_message;
  const unread = row.unread_count > 0;
  return (
    <button
      type="button"
      onClick={onSelect}
      className={cn(
        "flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-muted",
        active && "bg-muted",
      )}
    >
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
        {(other?.first_name?.[0] ?? "") + (other?.last_name?.[0] ?? "")}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline justify-between gap-2">
          <div className={cn("truncate text-sm", unread ? "font-semibold" : "font-medium")}>
            {other ? `${other.first_name} ${other.last_name}` : "Unknown"}
          </div>
          <div className="shrink-0 text-[10px] text-muted-foreground">
            {formatTime(last?.sent_at)}
          </div>
        </div>
        <div className="truncate text-xs text-muted-foreground">
          {row.listing ? "Re: " : ""}
          {last?.content ?? "No messages yet"}
        </div>
      </div>
      {unread && (
        <span className="mt-1 inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-primary px-1 text-[10px] font-semibold text-primary-foreground">
          {row.unread_count}
        </span>
      )}
    </button>
  );
}

function ThreadView({ conversationId, currentUserId, onBack }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const threadQuery = useQuery({
    queryKey: ["conversation", conversationId],
    queryFn: () => conversationsApi.get(conversationId),
  });

  // Local messages state seeded from the query so we can append socket
  // pushes without refetching. When the query itself refreshes (e.g. on
  // initial load), we reseed.
  const [messages, setMessages] = useState([]);
  useEffect(() => {
    if (threadQuery.data?.messages) {
      setMessages(threadQuery.data.messages);
    }
  }, [threadQuery.data]);

  const { status: socketStatus, send } = useChatSocket(conversationId, {
    onMessage: (msg) => {
      setMessages((prev) => {
        // Guard against echoes — server broadcasts to everyone including
        // the sender, so the message we optimistically added already
        // appears by id once the broadcast arrives.
        if (prev.some((m) => m.id === msg.id)) return prev;
        return [...prev, msg];
      });
      // Bump the inbox so unread counts/latest previews refresh.
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
  });

  const [draft, setDraft] = useState("");
  const listRef = useRef(null);

  // Auto-scroll to bottom on new messages.
  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages.length]);

  const other = useMemo(() => {
    if (!threadQuery.data) return null;
    return threadQuery.data.buyer_id === currentUserId
      ? threadQuery.data.seller
      : threadQuery.data.buyer;
  }, [threadQuery.data, currentUserId]);

  function handleSend(e) {
    e.preventDefault();
    const content = draft.trim();
    if (!content) return;
    if (send(content)) {
      setDraft("");
    }
  }

  return (
    <Card className="flex h-[600px] flex-col">
      <div className="flex items-center gap-2 border-b px-4 py-3">
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={onBack}
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
          {(other?.first_name?.[0] ?? "") + (other?.last_name?.[0] ?? "")}
        </div>
        <div className="flex-1">
          <button
            type="button"
            onClick={() => other?.id && navigate(`/users/${other.id}`)}
            className="text-sm font-medium hover:underline disabled:no-underline"
            disabled={!other?.id}
          >
            {other ? `${other.first_name} ${other.last_name}` : "Conversation"}
          </button>
          <div className="text-xs text-muted-foreground">
            {socketStatus === "open"
              ? "Connected"
              : socketStatus === "connecting"
                ? "Connecting..."
                : "Offline"}
          </div>
        </div>
      </div>

      <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto p-4">
        {threadQuery.isLoading ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading thread...
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center text-sm text-muted-foreground">
            No messages yet. Send one below.
          </div>
        ) : (
          messages.map((m) => {
            const mine = m.sender_id === currentUserId;
            return (
              <div
                key={m.id}
                className={cn("flex", mine ? "justify-end" : "justify-start")}
              >
                <div
                  className={cn(
                    "max-w-[75%] rounded-2xl px-3 py-2 text-sm",
                    mine
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-foreground",
                  )}
                >
                  {m.is_agentic && (
                    <div
                      className={cn(
                        "mb-1 flex items-center gap-1 text-[10px] uppercase tracking-wide",
                        mine ? "text-primary-foreground/80" : "text-muted-foreground",
                      )}
                    >
                      <Sparkles className="h-3 w-3" />
                      Auto-opener
                    </div>
                  )}
                  <div className="whitespace-pre-wrap">{m.content}</div>
                  <div
                    className={cn(
                      "mt-1 text-[10px]",
                      mine ? "text-primary-foreground/70" : "text-muted-foreground",
                    )}
                  >
                    {formatTime(m.sent_at)}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      <form onSubmit={handleSend} className="flex items-end gap-2 border-t p-3">
        <Textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Type a message..."
          rows={2}
          className="min-h-[44px] resize-none"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend(e);
            }
          }}
          disabled={socketStatus !== "open"}
        />
        <Button
          type="submit"
          size="icon"
          disabled={socketStatus !== "open" || !draft.trim()}
        >
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </Card>
  );
}

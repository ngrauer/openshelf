import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { Bot, ExternalLink, Loader2, MessageCircle, Send, Sparkles, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { chatApi, ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";

const GREETING = {
  role: "assistant",
  content:
    "Hi! I'm the OpenShelf assistant. Ask me about textbooks, pricing, or how to use the platform.",
  model: "template",
};

const QUICK_ACTIONS = [
  { label: "Find me available textbooks", message: "Find me available textbooks for my courses" },
  { label: "What can you do?", message: "What can you do?" },
  { label: "How do I list a book?", message: "How do I list a book?" },
  { label: "Do I have any messages?", message: "Do I have any unread messages?" },
];

export function ChatbotWidget({ open, onClose }) {
  const [turns, setTurns] = useState([GREETING]);
  const [draft, setDraft] = useState("");
  const listRef = useRef(null);

  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [turns.length]);

  const sendChat = useMutation({
    mutationFn: (message) => {
      const history = turns
        .filter((t) => t !== GREETING)
        .map(({ role, content }) => ({ role, content }));
      return chatApi.send(message, history);
    },
    onSuccess: (res) => {
      setTurns((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.response,
          sources: res.sources ?? [],
          model: res.model,
        },
      ]);
    },
    onError: (err) => {
      setTurns((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            err instanceof ApiError
              ? `Error: ${err.message}`
              : "Something went wrong reaching the assistant.",
          model: "error",
        },
      ]);
    },
  });

  function send(message) {
    if (!message || sendChat.isPending) return;
    setTurns((prev) => [...prev, { role: "user", content: message }]);
    setDraft("");
    sendChat.mutate(message);
  }

  function handleSend(e) {
    e?.preventDefault();
    send(draft.trim());
  }

  const showQuickActions = turns.length === 1 && !sendChat.isPending;

  if (!open) return null;

  return (
    <div className="fixed bottom-24 right-6 z-40 flex h-[540px] w-[360px] max-w-[calc(100vw-3rem)] flex-col overflow-hidden rounded-lg border bg-popover shadow-xl">
      <div className="flex items-center gap-2 border-b bg-primary px-4 py-3 text-primary-foreground">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-foreground/15">
          <Bot className="h-4 w-4" />
        </div>
        <div className="flex-1">
          <div className="text-sm font-semibold">OpenShelf assistant</div>
          <div className="text-[10px] opacity-80">
            Ask about listings, prices, or the app
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="h-7 w-7 text-primary-foreground hover:bg-primary-foreground/15 hover:text-primary-foreground"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto p-3">
        {turns.map((t, i) => (
          <ChatTurn key={i} turn={t} onClose={onClose} />
        ))}
        {showQuickActions && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {QUICK_ACTIONS.map((action) => (
              <button
                key={action.label}
                type="button"
                onClick={() => send(action.message)}
                className="rounded-full border border-primary/30 bg-primary/5 px-3 py-1 text-xs text-primary transition-colors hover:bg-primary/15"
              >
                {action.label}
              </button>
            ))}
          </div>
        )}
        {sendChat.isPending && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Loader2 className="h-3 w-3 animate-spin" />
            Thinking...
          </div>
        )}
      </div>

      <form onSubmit={handleSend} className="flex items-end gap-2 border-t p-3">
        <Textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Ask a question..."
          rows={1}
          className="min-h-[40px] resize-none"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend(e);
            }
          }}
          disabled={sendChat.isPending}
        />
        <Button
          type="submit"
          size="icon"
          disabled={sendChat.isPending || !draft.trim()}
        >
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  );
}

function ChatTurn({ turn, onClose }) {
  const navigate = useNavigate();
  const mine = turn.role === "user";
  return (
    <div className={cn("flex", mine ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-3 py-2 text-sm",
          mine
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-foreground",
        )}
      >
        <div className="whitespace-pre-wrap">{turn.content}</div>
        {turn.sources?.length > 0 && (
          <div className="mt-2 space-y-1 border-t border-foreground/10 pt-2">
            {turn.sources.map((s, i) => (
              <div
                key={i}
                className="rounded bg-background/50 px-2 py-1 text-[10px]"
              >
                <div className="font-semibold">{s.title}</div>
                {s.snippet && (
                  <div className="mt-0.5 line-clamp-2 text-muted-foreground">
                    {s.snippet}
                  </div>
                )}
                {s.kind === "listing" && s.reference_id && (
                  <button
                    type="button"
                    onClick={() => {
                      navigate(`/listings/${s.reference_id}`);
                      onClose?.();
                    }}
                    className="mt-1 flex items-center gap-0.5 text-primary hover:underline"
                  >
                    <ExternalLink className="h-2.5 w-2.5" />
                    View listing
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
        {!mine && turn.model && turn.model !== "error" && (
          <div className="mt-1 flex items-center gap-1 text-[9px] text-muted-foreground">
            <Sparkles className="h-2.5 w-2.5" />
            {turn.model}
          </div>
        )}
      </div>
    </div>
  );
}

export function FloatingChatButton({ onClick }) {
  return (
    <Button
      onClick={onClick}
      size="icon"
      className="fixed bottom-6 right-6 z-40 h-14 w-14 rounded-full shadow-lg"
      aria-label="Open OpenShelf assistant"
    >
      <MessageCircle className="h-6 w-6" />
    </Button>
  );
}

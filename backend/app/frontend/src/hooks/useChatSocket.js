import { useEffect, useRef, useState } from "react";
import { getToken } from "@/lib/api";

// Dev: vite proxy forwards /ws to ws://localhost:8000/ws.
// Prod: assume the API shares the origin, so just flip the scheme.
function buildSocketUrl(conversationId, token) {
  const scheme = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host;
  return `${scheme}//${host}/ws/chat/${conversationId}?token=${encodeURIComponent(token ?? "")}`;
}

// Thin WebSocket hook for a single conversation. Handles:
//   - connect on mount, close on unmount
//   - re-connect when conversationId changes
//   - exposes a `send(content)` helper
//   - surfaces { status, error, lastMessage } state
//
// Intentionally NOT a reconnecting socket — the MVP demo runs on a stable
// local network, and auto-reconnect would just paper over real bugs during
// development.
export function useChatSocket(conversationId, { onMessage } = {}) {
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  // Keep the latest onMessage in a ref so we don't tear down the socket
  // every time the parent re-renders with a new callback identity.
  const handlerRef = useRef(onMessage);
  useEffect(() => {
    handlerRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    if (!conversationId) return undefined;
    const token = getToken();
    if (!token) {
      setStatus("error");
      setError("No auth token");
      return undefined;
    }

    setStatus("connecting");
    setError(null);
    const ws = new WebSocket(buildSocketUrl(conversationId, token));
    wsRef.current = ws;

    ws.onopen = () => setStatus("open");
    ws.onclose = (ev) => {
      setStatus("closed");
      // 4401/4403/4404 are auth/forbidden/not-found close codes from the backend.
      if (ev.code >= 4400) setError(`Socket closed (${ev.code})`);
    };
    ws.onerror = () => setError("Socket error");
    ws.onmessage = (ev) => {
      try {
        const payload = JSON.parse(ev.data);
        if (payload?.type === "message" && payload.message) {
          handlerRef.current?.(payload.message);
        } else if (payload?.type === "error") {
          setError(payload.detail ?? "Socket error");
        }
      } catch {
        // ignore malformed frames
      }
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [conversationId]);

  function send(content, isAgentic = false) {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return false;
    ws.send(JSON.stringify({ content, is_agentic: isAgentic }));
    return true;
  }

  return { status, error, send };
}

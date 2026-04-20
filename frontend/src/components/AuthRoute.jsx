import { useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { ChatbotWidget, FloatingChatButton } from "@/components/ChatbotWidget";

export function AuthRoute({ children }) {
  const { status } = useAuth();
  const location = useLocation();
  const [chatOpen, setChatOpen] = useState(false);

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        Loading...
      </div>
    );
  }

  if (status !== "authenticated") {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return (
    <>
      {children}
      <FloatingChatButton onClick={() => setChatOpen((o) => !o)} />
      <ChatbotWidget open={chatOpen} onClose={() => setChatOpen(false)} />
    </>
  );
}

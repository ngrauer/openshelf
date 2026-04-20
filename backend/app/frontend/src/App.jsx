import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/contexts/AuthContext";
import { AuthRoute } from "@/components/AuthRoute";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { ListingDetailPage } from "@/pages/ListingDetailPage";
import { UserProfilePage } from "@/pages/UserProfilePage";
import "./App.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 30_000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/"
              element={
                <AuthRoute>
                  <DashboardPage />
                </AuthRoute>
              }
            />
            <Route
              path="/listings/:id"
              element={
                <AuthRoute>
                  <ListingDetailPage />
                </AuthRoute>
              }
            />
            <Route
              path="/users/:id"
              element={
                <AuthRoute>
                  <UserProfilePage />
                </AuthRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

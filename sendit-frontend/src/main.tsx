import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { RouterProvider } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google"; // 1. Import provider
import { ProviderRouter } from "./routers/provider.router";
import { MobileGuard } from "./MobileGuard";

// 2. Access the ID from your environment variables
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    {/* 3. Wrap the app */}
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <MobileGuard>
        <RouterProvider router={ProviderRouter} />
      </MobileGuard>
    </GoogleOAuthProvider>
  </StrictMode>
);
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { AuthProvider } from "@/context/useAuth";

import { ErrorBoundary } from "@/components/ErrorBoundary";
import { GoogleOAuthProvider } from '@react-oauth/google';

const GOOGLE_CLIENT_ID = "15299709923-qh986pjskvd6j14lq8e0jt20elb4jpv8.apps.googleusercontent.com"; // Real ID provided by user

createRoot(document.getElementById("root")!).render(
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
        <ErrorBoundary>
            <App />
        </ErrorBoundary>
    </GoogleOAuthProvider>
);

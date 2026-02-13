import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api';

export interface User {
    id: string;
    email: string;
    name: string;
    avatarUrl?: string;
    role?: string;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    login: (token: string) => void;
    loginWithGoogle: (token: string) => Promise<void>;
    logout: () => void;
    loading: boolean;
    userRole?: string; // Derived helper
    setRole: (role: string | null) => void; // For testing/mocking
    setUser: (user: User | null) => void; // For admin simulation
    requestRole: (role: string) => void;
    pendingRequest: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [pendingRequest, setPendingRequest] = useState(false);

    const fetchUser = async () => {
        try {
            const res = await api.get('/users/me');
            setUser({
                id: res.data.id,
                email: res.data.email,
                name: res.data.full_name || res.data.email,
                role: res.data.role,
                avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=${res.data.email}` // Mock avatar
            });
            setIsAuthenticated(true);
        } catch (error) {
            console.error("Failed to fetch user:", error);
            // If 401, token is invalid
            localStorage.removeItem('forsee_access_token');
            setIsAuthenticated(false);
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const token = localStorage.getItem('forsee_access_token');
        if (token) {
            fetchUser();
        } else {
            setLoading(false);
        }
    }, []);

    const login = (token: string) => {
        localStorage.setItem('forsee_access_token', token);
        setIsAuthenticated(true);
        fetchUser(); // Fetch user details immediately after login
    };

    const loginWithGoogle = async (token: string) => {
        try {
            setLoading(true);
            const response = await api.post('/login/google', { id_token: token });
            const accessToken = response.data.access_token;
            localStorage.setItem('forsee_access_token', accessToken);
            setIsAuthenticated(true);
            await fetchUser();
        } catch (error) {
            console.error("Google Login Error:", error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem('forsee_access_token');
        setIsAuthenticated(false);
        setUser(null);
        window.location.href = '/login';
    };

    // Persistent role management
    const setRole = async (role: string | null) => {
        try {
            if (user) {
                const response = await api.put('/users/role', { role });
                setUser({
                    ...user,
                    role: response.data.role
                });
            }
        } catch (error) {
            console.error("Failed to update role:", error);
            throw error;
        }
    };

    const requestRole = async (role: string) => {
        // For this demo, let's treat engineer as a persistent request
        // but for immediate UI feedback we'll set the pending state and call backend
        try {
            setPendingRequest(true);
            // Even requests are stored as a temporary role or a separate table, 
            // but the user wants the choice to stick.
            // For now, let's just make it persistent for Viewer/Engineer demo.
            await setRole(role);

            // Simulation of admin delay (optional)
            // setTimeout(() => setPendingRequest(false), 2000);
            setPendingRequest(false);
        } catch (error) {
            setPendingRequest(false);
            throw error;
        }
    };

    return (
        <AuthContext.Provider value={{
            user,
            isAuthenticated,
            login,
            loginWithGoogle,
            logout,
            loading,
            userRole: user?.role,
            setRole,
            setUser,
            requestRole,
            pendingRequest
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};


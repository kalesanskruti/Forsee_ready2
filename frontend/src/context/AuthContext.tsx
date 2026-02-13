import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// --- TYPE DEFINITIONS ---

export type UserRole = 'admin' | 'engineer' | 'viewer' | null;

export interface User {
    id: string;
    name: string;
    email: string;
    avatarUrl?: string;
}

interface AuthContextType {
    user: User | null;
    userRole: UserRole;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<void>;
    signup: (name: string, email: string, password: string) => Promise<void>;
    loginWithGoogle: () => Promise<void>;
    logout: () => void;
    setRole: (role: UserRole) => void;
    setUser: (user: User | null) => void;
    requestRole: (role: UserRole) => void;
    pendingRequest: UserRole;
}

// --- CONTEXT ---

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// --- PROVIDER ---

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [userRole, setUserRole] = useState<UserRole>(null);
    const [pendingRequest, setPendingRequest] = useState<UserRole>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Check for existing session and handle storage updates
    useEffect(() => {
        const syncState = () => {
            const storedUser = localStorage.getItem('forsee_user');
            const storedRole = localStorage.getItem('forsee_role') as UserRole;
            const storedPending = localStorage.getItem('forsee_pending_role') as UserRole;

            if (storedUser) {
                try {
                    const parsedUser = JSON.parse(storedUser);
                    setUser(parsedUser);

                    // Check if a role was approved via ID or Email (for robustness in demo)
                    const approvedRoles = JSON.parse(localStorage.getItem('forsee_approved_roles') || '{}');
                    const allRequests = JSON.parse(localStorage.getItem('forsee_role_requests') || '[]');

                    // Priority 1: Direct ID match in approvedRoles
                    // Priority 2: Email match in approvedRequests (in case ID changed due to deterministic update)
                    const approvedByEmail = allRequests.find((r: any) =>
                        r.userEmail === parsedUser.email &&
                        r.status === 'approved'
                    );

                    let finalApprovedRole = approvedRoles[parsedUser.id];
                    if (!finalApprovedRole && approvedByEmail) {
                        finalApprovedRole = approvedByEmail.requestedRole;
                        // Sync it back to approvedRoles for consistency
                        approvedRoles[parsedUser.id] = finalApprovedRole;
                        localStorage.setItem('forsee_approved_roles', JSON.stringify(approvedRoles));
                    }

                    const userRequest = allRequests.find((r: any) =>
                        (r.userId === parsedUser.id || r.userEmail === parsedUser.email) &&
                        r.status === 'pending'
                    );

                    const rejectedRequest = allRequests.find((r: any) =>
                        (r.userId === parsedUser.id || r.userEmail === parsedUser.email) &&
                        r.status === 'rejected'
                    );

                    if (finalApprovedRole) {
                        setUserRole(finalApprovedRole);
                        localStorage.setItem('forsee_role', finalApprovedRole);
                        localStorage.removeItem('forsee_pending_role');
                        setPendingRequest(null);
                    } else if (rejectedRequest) {
                        // If rejected, set to viewer automatically
                        setUserRole('viewer');
                        localStorage.setItem('forsee_role', 'viewer');
                        localStorage.removeItem('forsee_pending_role');
                        setPendingRequest(null);
                    } else if (storedRole) {
                        setUserRole(storedRole);
                        setPendingRequest(null);
                    } else {
                        // If no role but they were viewer, keep it
                        if (storedRole !== null) {
                            setUserRole(storedRole);
                        } else {
                            setUserRole(null);
                        }
                    }

                    if (storedPending && !finalApprovedRole && userRequest) {
                        setPendingRequest(storedPending);
                    } else if (!storedPending || finalApprovedRole || rejectedRequest) {
                        setPendingRequest(null);
                    }
                } catch {
                    localStorage.removeItem('forsee_user');
                    localStorage.removeItem('forsee_role');
                    localStorage.removeItem('forsee_pending_role');
                }
            } else {
                setUser(null);
                setUserRole(null);
                setPendingRequest(null);
            }
            setIsLoading(false);
        };

        syncState();

        // Listen for storage changes from other tabs or same tab
        const handleStorageChange = (e: StorageEvent | any) => {
            // Check for specific keys we care about
            if (!e.key || e.key.startsWith('forsee_')) {
                syncState();
            }
        };

        window.addEventListener('storage', handleStorageChange);

        // Also a small interval for same-tab updates if they don't trigger'storage' events
        // (Native storage event only fires on other tabs, but custom updates in same tab can be tricky)
        const interval = setInterval(syncState, 2000);

        return () => {
            window.removeEventListener('storage', handleStorageChange);
            clearInterval(interval);
        };
    }, []);

    const setRole = (role: UserRole) => {
        setUserRole(role);
        if (role) {
            localStorage.setItem('forsee_role', role);
            // Clear pending if role is assigned
            setPendingRequest(null);
            localStorage.removeItem('forsee_pending_role');
        } else {
            localStorage.removeItem('forsee_role');
        }
    };

    const requestRole = (role: UserRole) => {
        if (!user) return;
        setPendingRequest(role);
        if (role) {
            localStorage.setItem('forsee_pending_role', role);

            // In a real app, this would be an API call. For demo, we store it in a global "requests" key
            const allRequests = JSON.parse(localStorage.getItem('forsee_role_requests') || '[]');
            const newRequest = {
                id: crypto.randomUUID(),
                userId: user.id,
                userEmail: user.email, // Use email as secondary identifier
                userName: user.name,
                requestedRole: role,
                status: 'pending',
                timestamp: new Date().toISOString()
            };

            // Avoid duplicate active requests for same user and role
            const exists = allRequests.find((r: any) => r.userId === user.id && r.status === 'pending');
            if (!exists) {
                allRequests.push(newRequest);
                localStorage.setItem('forsee_role_requests', JSON.stringify(allRequests));
            }
        } else {
            localStorage.removeItem('forsee_pending_role');
        }
    };

    const login = async (email: string, password: string) => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // For demo: deterministic ID based on email
        const newUser: User = {
            id: btoa(email).substring(0, 12),
            name: email.split('@')[0],
            email,
            avatarUrl: '/avatar.png',
        };

        setUser(newUser);
        localStorage.setItem('forsee_user', JSON.stringify(newUser));

        // Check if they already have an approved role
        const approvedRoles = JSON.parse(localStorage.getItem('forsee_approved_roles') || '{}');
        if (approvedRoles[newUser.id]) {
            setRole(approvedRoles[newUser.id]);
        } else {
            // Reset role on new login so they get the popup if not approved
            setRole(null);
        }
    };

    const signup = async (name: string, email: string, password: string) => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        const newUser: User = {
            id: btoa(email).substring(0, 12),
            name,
            email,
            avatarUrl: '/avatar.png',
        };

        setUser(newUser);
        localStorage.setItem('forsee_user', JSON.stringify(newUser));
        // Reset role on new signup
        setRole(null);
    };

    const loginWithGoogle = async () => {
        // Simulate Google OAuth
        await new Promise(resolve => setTimeout(resolve, 500));

        const email = 'demo@forsee.ai';
        const newUser: User = {
            id: btoa(email).substring(0, 12),
            name: 'Demo User',
            email,
            avatarUrl: '/avatar.png',
        };

        setUser(newUser);
        localStorage.setItem('forsee_user', JSON.stringify(newUser));

        const approvedRoles = JSON.parse(localStorage.getItem('forsee_approved_roles') || '{}');
        if (approvedRoles[newUser.id]) {
            setRole(approvedRoles[newUser.id]);
        } else {
            setRole(null);
        }
    };

    const logout = () => {
        setUser(null);
        setRole(null);
        localStorage.removeItem('forsee_user');
        localStorage.removeItem('forsee_role');
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                userRole,
                isAuthenticated: !!user,
                isLoading,
                login,
                signup,
                loginWithGoogle,
                logout,
                setRole,
                setUser,
                requestRole,
                pendingRequest,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

// --- HOOK ---

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export default AuthProvider;

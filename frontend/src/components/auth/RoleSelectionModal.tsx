import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from "@/context/useAuth";
import { Shield, Wrench, Eye, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useNavigate } from 'react-router-dom';

export type UserRole = 'admin' | 'engineer' | 'viewer' | null;

interface RoleCardProps {
    role: UserRole;
    title: string;
    icon: React.ComponentType<{ className?: string }>;
    description: string;
    features: string[];
    onSelect: (role: UserRole) => void;
    isSelected: boolean;
}

const RoleCard = ({ role, title, icon: Icon, description, features, onSelect, isSelected }: RoleCardProps) => (
    <motion.button
        whileHover={{ scale: 1.01, backgroundColor: "rgba(255, 255, 255, 0.02)" }}
        whileTap={{ scale: 0.99 }}
        onClick={() => onSelect(role)}
        className={cn(
            "relative flex flex-col items-start p-8 rounded-2xl border transition-all duration-500 w-full text-left group min-h-[400px]",
            isSelected
                ? "bg-white/[0.03] border-[#9d4edd] shadow-[0_0_40px_rgba(157,78,221,0.15)]"
                : "bg-white/[0.02] border-white/[0.05] hover:border-white/20"
        )}
    >
        <div className={cn(
            "p-3 rounded-xl mb-6 transition-all duration-500",
            isSelected ? "bg-[#9d4edd] text-white shadow-[0_0_20px_rgba(157,78,221,0.4)]" : "bg-[#2e2e2e] text-white/50 group-hover:text-white"
        )}>
            <Icon className="w-6 h-6" />
        </div>

        <h3 className="text-xl font-bold mb-3 text-white">
            {title}
        </h3>

        <p className="text-white/40 text-sm mb-6 leading-relaxed font-medium">
            {description}
        </p>

        <ul className="space-y-3 mt-auto w-full">
            {features.map((feature, idx) => (
                <li key={idx} className="flex items-center gap-3 text-xs text-white/60 font-medium">
                    <Check className="w-3.5 h-3.5 text-[#9d4edd] shrink-0" />
                    {feature}
                </li>
            ))}
        </ul>
    </motion.button>
);

export function RoleSelectionModal() {
    const { user, userRole, setRole, requestRole, pendingRequest, isAuthenticated } = useAuth();
    const [selectedRole, setSelectedRole] = useState<UserRole>(null);
    const [isRequestSent, setIsRequestSent] = useState(false);
    const navigate = useNavigate();

    // Show modal only if user is logged in BUT has no role assigned
    const showModal = isAuthenticated && !userRole;

    const handleConfirm = async () => {
        if (selectedRole === 'engineer') {
            await requestRole('engineer');
            setIsRequestSent(true);
            setTimeout(() => navigate("/dashboard"), 2000); // Redirect to Engineer portal
        } else if (selectedRole === 'viewer') {
            await setRole('viewer');
            navigate("/systems"); // Redirect to Viewer portal
        }
    };

    // Auto-reset request state if role is assigned or pending status changes
    useEffect(() => {
        if (userRole) {
            setIsRequestSent(false);
        }
    }, [userRole]);

    if (!showModal) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
            >
                <div className="max-w-4xl w-full bg-[#0a0a0a] border border-white/10 rounded-2xl p-6 md:p-8 shadow-2xl relative overflow-hidden">
                    {/* Background Gradients */}
                    <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[100px] pointer-events-none" />
                    <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-[100px] pointer-events-none" />

                    <AnimatePresence mode="wait">
                        {!isRequestSent && !pendingRequest ? (
                            <motion.div
                                key="selection"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                            >
                                <div className="relative z-10 text-center mb-8">
                                    <h2 className="text-3xl font-black text-white mb-2 leading-tight tracking-tight">Welcome, {user?.name || 'Administrator'}</h2>
                                    <p className="text-white/40 font-medium tracking-tight text-sm">Select your role to access the platform</p>
                                </div>

                                <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
                                    {/* VIEWER ROLE */}
                                    <RoleCard
                                        role="viewer"
                                        title="Viewer"
                                        icon={Eye}
                                        description="Observational access to predictive intelligence. Monitor system health and analyze RUL data without administrative privileges."
                                        features={[
                                            'Predict in Operational Systems',
                                            'Monitor Health & RUL Dashboard',
                                            'Analyze Explainability Metrics',
                                            'Access Intelligent Insights'
                                        ]}
                                        onSelect={setSelectedRole}
                                        isSelected={selectedRole === 'viewer'}
                                    />

                                    {/* ENGINEER ROLE */}
                                    <RoleCard
                                        role="engineer"
                                        title="Engineer"
                                        icon={Wrench}
                                        description="Operational authority and system integration. Authorized to request new builds and provide feedback for model retraining."
                                        features={[
                                            'Request New System Integration',
                                            'Human-in-the-Loop Feedback',
                                            'Contribute to Model Retraining',
                                            'All Viewer Privileges Included'
                                        ]}
                                        onSelect={setSelectedRole}
                                        isSelected={selectedRole === 'engineer'}
                                    />
                                </div>

                                <div className="relative z-10 flex flex-col items-center gap-6">
                                    <div className="text-[9px] text-white/20 uppercase tracking-[0.3em] italic max-w-lg text-center leading-relaxed font-bold">
                                        "FORSEE INTELLIGENCE SEPARATES INSIGHT CONSUMPTION FROM SYSTEM CONTROL, ALLOWING ALL STAKEHOLDERS TO UNDERSTAND RISK WHILE RESTRICTING ACTIONS THAT ALTER SYSTEM BEHAVIOR."
                                    </div>

                                    <button
                                        onClick={handleConfirm}
                                        disabled={!selectedRole}
                                        className={cn(
                                            "px-14 py-4 rounded-full font-black transition-all duration-300 uppercase tracking-[0.25em] text-[10px] border",
                                            selectedRole
                                                ? "bg-white/[0.03] text-white border-white/20 hover:bg-white/[0.08] hover:border-white/40 shadow-[0_0_40px_rgba(255,255,255,0.05)] active:scale-95 translate-y-0"
                                                : "bg-white/[0.02] text-white/10 border-white/5 cursor-not-allowed translate-y-1"
                                        )}
                                    >
                                        Establish Session Access
                                    </button>
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="request-sent"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="relative z-10 text-center py-12"
                            >
                                <div className="w-20 h-20 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-6 border border-primary/50 shadow-[0_0_30px_rgba(157,78,221,0.3)]">
                                    <Shield className="w-10 h-10 text-primary animate-pulse" />
                                </div>

                                <h2 className="text-3xl font-bold text-white mb-4">Request Sent to Admin</h2>
                                <p className="text-white/60 max-w-md mx-auto mb-8">
                                    Your request for <span className="text-primary font-bold">Engineer</span> access has been logged. An administrator will review your credentials shortly.
                                </p>

                                <div className="flex flex-col gap-4">
                                    <button
                                        onClick={() => setRole('viewer')}
                                        className="px-8 py-3 bg-white/5 border border-white/10 text-white rounded-full hover:bg-white/10 transition-all text-sm font-medium"
                                    >
                                        Continue as Viewer
                                    </button>
                                    <p className="text-[10px] text-white/30 uppercase tracking-widest">
                                        You can use the platform as a viewer while waiting for approval
                                    </p>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </motion.div>
        </AnimatePresence>
    );
}

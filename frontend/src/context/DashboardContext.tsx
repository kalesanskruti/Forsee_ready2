import React, { createContext, useContext, useState, ReactNode } from "react";
import { Monitor, Cpu, Smartphone, Laptop, LucideIcon, Activity } from "lucide-react";

export interface Device {
    id: string;
    name: string;
    icon: LucideIcon;
}

// Initial default devices
const defaultDevices: Device[] = [
    { id: "dev-01", name: "Turbine A-11", icon: Monitor },
    { id: "dev-02", name: "Gen. Control", icon: Cpu },
    { id: "dev-03", name: "Field Tablet", icon: Smartphone },
    { id: "dev-04", name: "Engine Monitor", icon: Laptop },
];

interface DashboardContextType {
    devices: Device[];
    addDevice: (device: Omit<Device, "icon"> & { icon?: LucideIcon }) => void;
    removeDevice: (id: string) => void;
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined);

export function DashboardProvider({ children }: { children: ReactNode }) {
    const [devices, setDevices] = useState<Device[]>(defaultDevices);

    const addDevice = (newDevice: Omit<Device, "icon"> & { icon?: LucideIcon }) => {
        // Prevent duplicates
        if (devices.some(d => d.id === newDevice.id)) return;

        const deviceWithIcon: Device = {
            ...newDevice,
            icon: newDevice.icon || Activity // Default icon if not provided
        };

        setDevices(prev => [...prev, deviceWithIcon]);
    };

    const removeDevice = (id: string) => {
        setDevices(prev => prev.filter(d => d.id !== id));
    };

    return (
        <DashboardContext.Provider value={{ devices, addDevice, removeDevice }}>
            {children}
        </DashboardContext.Provider>
    );
}

export function useDashboard() {
    const context = useContext(DashboardContext);
    if (context === undefined) {
        throw new Error("useDashboard must be used within a DashboardProvider");
    }
    return context;
}

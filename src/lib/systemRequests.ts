import { api } from '@/lib/api';

export interface SystemRequest {
    id: string;
    systemName: string;
    details: string;
    submittedBy: string;
    timestamp: string;
    status: 'pending' | 'approved' | 'rejected';
}

export async function getRequests(): Promise<SystemRequest[]> {
    try {
        const response = await api.get('/system-requests');
        return response.data;
    } catch (error) {
        console.error("Failed to fetch system requests", error);
        return [];
    }
}

export async function addRequest(req: Omit<SystemRequest, 'id' | 'timestamp' | 'status'>): Promise<SystemRequest | null> {
    try {
        const response = await api.post('/system-requests', req);
        return response.data;
    } catch (error) {
        console.error("Failed to add system request", error);
        return null;
    }
}

export async function updateRequestStatus(id: string, status: 'approved' | 'rejected'): Promise<void> {
    try {
        await api.put(`/system-requests/${id}/status?status=${status}`);
    } catch (error) {
        console.error("Failed to update system request status", error);
    }
}

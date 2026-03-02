/**
 * API Client Module
 * Handles all API requests to the admin backend
 */

const ApiClient = {
    baseUrl: '/api/admin',
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'include',
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw {
                    status: response.status,
                    data: data
                };
            }
            
            return data;
        } catch (error) {
            throw error;
        }
    },
    
    async getUsers(skip = 0, limit = 25, search = '', verifiedOnly = null, isAdmin = null) {
        const params = new URLSearchParams();
        params.append('skip', skip);
        params.append('limit', limit);
        if (search) params.append('search', search);
        if (verifiedOnly !== null) params.append('verified_only', verifiedOnly);
        if (isAdmin !== null) params.append('is_admin', isAdmin);
        
        return this.request(`/users?${params.toString()}`);
    },
    
    async createUser(email, password, isVerified = false, isAdmin = false) {
        return this.request('/users', {
            method: 'POST',
            body: JSON.stringify({
                email,
                password,
                is_verified: isVerified,
                is_admin: isAdmin
            })
        });
    },
    
    async updateUser(userId, updates) {
        return this.request(`/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(updates)
        });
    },
    
    async deleteUser(userId) {
        return this.request(`/users/${userId}`, {
            method: 'DELETE'
        });
    },
    
    async toggleVerification(userId) {
        return this.request(`/users/${userId}/verify`, {
            method: 'PATCH'
        });
    },
    
    async getAuditLogs(skip = 0, limit = 25, actionType = null, adminEmail = null) {
        const params = new URLSearchParams();
        params.append('skip', skip);
        params.append('limit', limit);
        if (actionType) params.append('action_type', actionType);
        if (adminEmail) params.append('admin_email', adminEmail);
        
        return this.request(`/audit-logs?${params.toString()}`);
    }
};

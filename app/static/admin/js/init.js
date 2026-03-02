/**
 * Initialization Module
 * Handles application startup and initialization
 */

const AppInit = {
    async init() {
        try {
            // Load current user email
            const response = await fetch('/api/auth/me', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const user = await response.json();
                state.currentUserEmail = user.email;
                document.getElementById('current-user-email').textContent = user.email;
                
                // Check if user is admin
                if (!user.is_admin) {
                    // Show non-admin modal and hide admin content
                    UIUtils.openModal('non-admin-modal');
                    document.querySelector('aside').classList.add('hidden');
                    document.querySelector('main').classList.add('hidden');
                    return;
                }
            } else {
                document.getElementById('current-user-email').textContent = 'Admin';
            }
        } catch (error) {
            document.getElementById('current-user-email').textContent = 'Admin';
        }
        
        // Initialize event handlers
        EventHandlers.init();
        
        // Load initial user list
        await UserManagement.loadUsers();
    }
};

// Start application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    AppInit.init();
});

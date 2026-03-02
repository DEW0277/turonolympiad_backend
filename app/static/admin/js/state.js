/**
 * State Management Module
 * Centralized state for the admin panel
 */

const state = {
    currentPage: 0,
    pageSize: 25,
    searchQuery: '',
    verifiedFilter: null,
    adminFilter: null,
    totalUsers: 0,
    users: [],
    deleteUserId: null,
    currentUserEmail: null,
    isLoading: false,
    
    // Reset filters
    resetFilters() {
        this.searchQuery = '';
        this.verifiedFilter = null;
        this.adminFilter = null;
        this.currentPage = 0;
    },
    
    // Reset pagination
    resetPagination() {
        this.currentPage = 0;
    }
};

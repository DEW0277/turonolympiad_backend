/**
 * Test Management Module
 * 
 * Handles all test management operations including subjects, levels, tests, and questions.
 */

class TestManagementModule {
    constructor() {
        this.currentView = 'subjects';
        this.currentSubject = null;
        this.currentLevel = null;
        this.currentTest = null;
        this.currentEditId = null; // Track the ID of the item being edited
        this.optionCount = 3; // Start with 3 options (A, B, C)
        this.editOptionCount = 3; // Track options in edit mode
        this.pagination = {
            subjects: { skip: 0, limit: 25 },
            levels: { skip: 0, limit: 25 },
            tests: { skip: 0, limit: 25 },
            questions: { skip: 0, limit: 25 }
        };
        this.searchState = {
            subjects: '',
            levels: '',
            tests: '',
            questions: ''
        };
        // Breadcrumb state management
        this.breadcrumbState = {
            subjectName: '',
            levelName: '',
            testName: ''
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSubjects();
    }

    setupEventListeners() {
        // Navigation
        document.addEventListener('click', (e) => {
            if (e.target.dataset.nav === 'test-management') {
                this.showTestManagement();
            }
            if (e.target.dataset.action === 'create-subject') {
                this.showCreateSubjectModal();
            }
            if (e.target.dataset.action === 'create-level') {
                this.showCreateLevelModal();
            }
            if (e.target.dataset.action === 'create-test') {
                this.showCreateTestModal();
            }
            if (e.target.dataset.action === 'create-question') {
                this.showCreateQuestionModal();
            }

            // Pagination event handlers
            if (e.target.dataset.action === 'next-page') {
                e.preventDefault();
                this.nextPage();
            }
            if (e.target.dataset.action === 'prev-page') {
                e.preventDefault();
                this.prevPage();
            }
        });

        // Search event listeners
        document.getElementById('test-search-btn')?.addEventListener('click', () => this.handleSearch());
        document.getElementById('test-clear-search-btn')?.addEventListener('click', () => this.handleClearSearch());
        document.getElementById('test-search-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleSearch();
            }
        });

        // Form submissions
        document.getElementById('create-subject-form')?.addEventListener('submit', (e) => this.handleCreateSubject(e));
        document.getElementById('create-level-form')?.addEventListener('submit', (e) => this.handleCreateLevel(e));
        document.getElementById('create-test-form')?.addEventListener('submit', (e) => this.handleCreateTest(e));
        document.getElementById('create-question-form')?.addEventListener('submit', (e) => this.handleCreateQuestion(e));

        // Edit form submissions
        document.getElementById('edit-subject-form')?.addEventListener('submit', (e) => this.handleEditSubject(e));
        document.getElementById('edit-level-form')?.addEventListener('submit', (e) => this.handleEditLevel(e));
        document.getElementById('edit-test-form')?.addEventListener('submit', (e) => this.handleEditTest(e));
        document.getElementById('edit-question-form')?.addEventListener('submit', (e) => this.handleEditQuestion(e));

        // Edit question modal specific event listeners
        document.getElementById('edit-add-option-btn')?.addEventListener('click', () => this.addEditOption());
    }

    async showTestManagement() {
            // Reset pagination when going back to subjects
            this.resetPagination('subjects');

            // Clear current context
            this.currentSubject = null;
            this.currentLevel = null;
            this.currentTest = null;

            await this.loadSubjects();
        }

    async loadSubjects() {
        try {
            this.currentView = 'subjects';
            this.currentSubject = null;
            this.currentLevel = null;
            this.currentTest = null;
            this.breadcrumbState = { subjectName: '', levelName: '', testName: '' };
            this.updateBreadcrumb();
            this.updateToolbar();
            this.updateSearchInput();
            
            const searchParam = this.searchState.subjects ? `&search=${encodeURIComponent(this.searchState.subjects)}` : '';
            const response = await fetch(`/api/admin/subjects?skip=${this.pagination.subjects.skip}&limit=${this.pagination.subjects.limit}${searchParam}`);
            const data = await response.json();
            this.renderSubjects(data.items, data.total);
        } catch (error) {
            console.error('Error loading subjects:', error);
            this.showToast('Error loading subjects', 'error');
        }
    }

    renderSubjects(subjects, total) {
            this.showTable('subjects');
            const tbody = document.getElementById('subjects-table-body');
            if (!tbody) return;

            tbody.innerHTML = subjects.map(subject => `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 text-sm text-gray-900">${subject.id}</td>
                    <td class="px-6 py-4 text-sm text-gray-900">${subject.name}</td>
                    <td class="px-6 py-4 text-sm text-gray-500">${new Date(subject.created_at).toLocaleDateString()}</td>
                    <td class="px-6 py-4 text-sm space-x-2">
                        <button class="px-3 py-1 bg-blue-100 text-blue-700 rounded text-xs hover:bg-blue-200" onclick="testMgmt.viewLevels(${subject.id})">
                            View Levels
                        </button>
                        <button class="px-3 py-1 bg-yellow-100 text-yellow-700 rounded text-xs hover:bg-yellow-200" onclick="testMgmt.editSubject(${subject.id})">
                            Edit
                        </button>
                        <button class="px-3 py-1 bg-red-100 text-red-700 rounded text-xs hover:bg-red-200" onclick="testMgmt.deleteSubject(${subject.id})">
                            Delete
                        </button>
                    </td>
                </tr>
            `).join('');

            // Update pagination info and controls
            this.updatePaginationInfo('subjects', total);
            this.updatePaginationControls('subjects', total);
        }

    async handleCreateSubject(e) {
        e.preventDefault();
        const name = document.getElementById('subject-name').value;
        
        try {
            const response = await fetch('/api/admin/subjects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });

            if (response.ok) {
                this.showToast('Subject created successfully', 'success');
                document.getElementById('create-subject-modal').classList.add('hidden');
                this.reloadCurrentView();
            } else {
                const error = await response.json();
                this.showToast(error.detail || 'Error creating subject', 'error');
            }
        } catch (error) {
            console.error('Error creating subject:', error);
            this.showToast('Error creating subject', 'error');
        }
    }

    async viewLevels(subjectId) {
        try {
            // Reset pagination when switching views
            this.resetPagination('levels');

            // Store current subject context
            const response = await fetch(`/api/admin/subjects/${subjectId}`);
            this.currentSubject = await response.json();
            this.currentView = 'levels';
            this.currentLevel = null;
            this.currentTest = null;
            
            // Update breadcrumb state
            this.breadcrumbState.subjectName = this.currentSubject.name;
            this.breadcrumbState.levelName = '';
            this.breadcrumbState.testName = '';
            this.updateBreadcrumb();
            
            this.updateToolbar();
            this.updateSearchInput();

            const searchParam = this.searchState.levels ? `&search=${encodeURIComponent(this.searchState.levels)}` : '';
            const levelsResponse = await fetch(`/api/admin/subjects/${subjectId}/levels?skip=${this.pagination.levels.skip}&limit=${this.pagination.levels.limit}${searchParam}`);
            const data = await levelsResponse.json();
            this.renderLevels(data.items, data.total);
        } catch (error) {
            console.error('Error loading levels:', error);
            this.showToast('Error loading levels', 'error');
        }
    }

    renderLevels(levels, total) {
            this.showTable('levels');
            const tbody = document.getElementById('levels-table-body');
            if (!tbody) return;

            tbody.innerHTML = levels.map(level => `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 text-sm text-gray-900">${level.id}</td>
                    <td class="px-6 py-4 text-sm text-gray-900">${level.name}</td>
                    <td class="px-6 py-4 text-sm text-gray-500">${new Date(level.created_at).toLocaleDateString()}</td>
                    <td class="px-6 py-4 text-sm space-x-2">
                        <button class="px-3 py-1 bg-blue-100 text-blue-700 rounded text-xs hover:bg-blue-200" onclick="testMgmt.viewTests(${level.id})">
                            View Tests
                        </button>
                        <button class="px-3 py-1 bg-yellow-100 text-yellow-700 rounded text-xs hover:bg-yellow-200" onclick="testMgmt.editLevel(${level.id})">
                            Edit
                        </button>
                        <button class="px-3 py-1 bg-red-100 text-red-700 rounded text-xs hover:bg-red-200" onclick="testMgmt.deleteLevel(${level.id})">
                            Delete
                        </button>
                    </td>
                </tr>
            `).join('');

            // Update pagination info and controls
            this.updatePaginationInfo('levels', total);
            this.updatePaginationControls('levels', total);
        }

    async viewTests(levelId) {
        try {
            // Reset pagination when switching views
            this.resetPagination('tests');

            // Store current level context
            const response = await fetch(`/api/admin/subjects/${this.currentSubject.id}/levels/${levelId}`);
            this.currentLevel = await response.json();
            this.currentView = 'tests';
            this.currentTest = null;
            
            // Update breadcrumb state
            this.breadcrumbState.levelName = this.currentLevel.name;
            this.breadcrumbState.testName = '';
            this.updateBreadcrumb();
            
            this.updateToolbar();
            this.updateSearchInput();

            const searchParam = this.searchState.tests ? `&search=${encodeURIComponent(this.searchState.tests)}` : '';
            const testsResponse = await fetch(`/api/admin/levels/${levelId}/tests?skip=${this.pagination.tests.skip}&limit=${this.pagination.tests.limit}${searchParam}`);
            const data = await testsResponse.json();
            this.renderTests(data.items, data.total);
        } catch (error) {
            console.error('Error loading tests:', error);
            this.showToast('Error loading tests', 'error');
        }
    }

    renderTests(tests, total) {
            this.showTable('tests');
            const tbody = document.getElementById('tests-table-body');
            if (!tbody) return;

            tbody.innerHTML = tests.map(test => `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 text-sm text-gray-900">${test.id}</td>
                    <td class="px-6 py-4 text-sm text-gray-900">${test.name}</td>
                    <td class="px-6 py-4 text-sm text-gray-500">${test.start_date ? new Date(test.start_date).toLocaleDateString() : 'N/A'}</td>
                    <td class="px-6 py-4 text-sm text-gray-500">${test.end_date ? new Date(test.end_date).toLocaleDateString() : 'N/A'}</td>
                    <td class="px-6 py-4 text-sm space-x-2">
                        <button class="px-3 py-1 bg-blue-100 text-blue-700 rounded text-xs hover:bg-blue-200" onclick="testMgmt.viewQuestions(${test.id})">
                            View Questions
                        </button>
                        <button class="px-3 py-1 bg-yellow-100 text-yellow-700 rounded text-xs hover:bg-yellow-200" onclick="testMgmt.editTest(${test.id})">
                            Edit
                        </button>
                        <button class="px-3 py-1 bg-red-100 text-red-700 rounded text-xs hover:bg-red-200" onclick="testMgmt.deleteTest(${test.id})">
                            Delete
                        </button>
                    </td>
                </tr>
            `).join('');

            // Update pagination info and controls
            this.updatePaginationInfo('tests', total);
            this.updatePaginationControls('tests', total);
        }

    async viewQuestions(testId) {
        try {
            // Reset pagination when switching views
            this.resetPagination('questions');

            // Store current test context
            const response = await fetch(`/api/admin/levels/${this.currentLevel.id}/tests/${testId}`);
            this.currentTest = await response.json();
            this.currentView = 'questions';
            
            // Update breadcrumb state
            this.breadcrumbState.testName = this.currentTest.name;
            this.updateBreadcrumb();
            
            this.updateToolbar();
            this.updateSearchInput();

            const searchParam = this.searchState.questions ? `&search=${encodeURIComponent(this.searchState.questions)}` : '';
            const questionsResponse = await fetch(`/api/admin/tests/${testId}/questions?skip=${this.pagination.questions.skip}&limit=${this.pagination.questions.limit}${searchParam}`);
            const data = await questionsResponse.json();
            this.renderQuestions(data.items, data.total);
        } catch (error) {
            console.error('Error loading questions:', error);
            this.showToast('Error loading questions', 'error');
        }
    }

    renderQuestions(questions, total) {
            this.showTable('questions');
            const tbody = document.getElementById('questions-table-body');
            if (!tbody) return;

            tbody.innerHTML = questions.map(question => `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 text-sm text-gray-900">${question.id}</td>
                    <td class="px-6 py-4 text-sm text-gray-900">${question.text}</td>
                    <td class="px-6 py-4 text-sm text-gray-500">${question.correct_answer}</td>
                    <td class="px-6 py-4 text-sm text-gray-500">${question.options.length} options</td>
                    <td class="px-6 py-4 text-sm space-x-2">
                        <button class="px-3 py-1 bg-yellow-100 text-yellow-700 rounded text-xs hover:bg-yellow-200" onclick="testMgmt.editQuestion(${question.id})">
                            Edit
                        </button>
                        <button class="px-3 py-1 bg-red-100 text-red-700 rounded text-xs hover:bg-red-200" onclick="testMgmt.deleteQuestion(${question.id})">
                            Delete
                        </button>
                    </td>
                </tr>
            `).join('');

            // Update pagination info and controls
            this.updatePaginationInfo('questions', total);
            this.updatePaginationControls('questions', total);
        }

    showTable(tableName) {
        // Hide all tables
        document.getElementById('subjects-table')?.classList.add('hidden');
        document.getElementById('levels-table')?.classList.add('hidden');
        document.getElementById('tests-table')?.classList.add('hidden');
        document.getElementById('questions-table')?.classList.add('hidden');

        // Show the requested table
        const table = document.getElementById(`${tableName}-table`);
        if (table) {
            table.classList.remove('hidden');
        }
    }

    showCreateSubjectModal() {
        document.getElementById('create-subject-modal').classList.remove('hidden');
    }

    showCreateLevelModal() {
        document.getElementById('create-level-modal').classList.remove('hidden');
    }

    showCreateTestModal() {
        document.getElementById('create-test-modal').classList.remove('hidden');
    }

    showCreateQuestionModal() {
        this.optionCount = 3; // Reset to 3 options
        document.getElementById('create-question-modal').classList.remove('hidden');
        this.renderQuestionOptions();
        this.updateCorrectAnswerDropdown();
    }

    async handleCreateLevel(e) {
        e.preventDefault();
        const name = document.getElementById('level-name').value;
        
        try {
            const response = await fetch(`/api/admin/subjects/${this.currentSubject.id}/levels`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });

            if (response.ok) {
                this.showToast('Level created successfully', 'success');
                document.getElementById('create-level-modal').classList.add('hidden');
                this.reloadCurrentView();
            } else {
                const error = await response.json();
                this.showToast(error.detail || 'Error creating level', 'error');
            }
        } catch (error) {
            console.error('Error creating level:', error);
            this.showToast('Error creating level', 'error');
        }
    }

    async handleCreateTest(e) {
        e.preventDefault();
        const name = document.getElementById('test-name').value;
        const startDate = document.getElementById('test-start-date').value;
        const endDate = document.getElementById('test-end-date').value;
        
        // Validate dates if both are provided
        if (startDate && endDate) {
            const start = new Date(startDate);
            const end = new Date(endDate);
            if (start >= end) {
                const feedback = document.getElementById('test-date-feedback');
                feedback.textContent = 'End date must be after start date';
                feedback.classList.remove('hidden');
                return;
            }
        }
        
        try {
            const response = await fetch(`/api/admin/levels/${this.currentLevel.id}/tests`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    start_date: startDate ? new Date(startDate).toISOString() : null,
                    end_date: endDate ? new Date(endDate).toISOString() : null
                })
            });

            if (response.ok) {
                this.showToast('Test created successfully', 'success');
                document.getElementById('create-test-modal').classList.add('hidden');
                this.reloadCurrentView();
            } else {
                const error = await response.json();
                this.showToast(error.detail || 'Error creating test', 'error');
            }
        } catch (error) {
            console.error('Error creating test:', error);
            this.showToast('Error creating test', 'error');
        }
    }

    async handleCreateQuestion(e) {
        e.preventDefault();
        
        // Verify form fields exist
        const textField = document.getElementById('question-text');
        const correctAnswerField = document.getElementById('question-correct-answer');
        
        if (!textField) {
            console.error('Form field not found: question-text');
            this.showToast('Form error: question text field missing', 'error');
            return;
        }
        
        if (!correctAnswerField) {
            console.error('Form field not found: question-correct-answer');
            this.showToast('Form error: correct answer field missing', 'error');
            return;
        }
        
        const text = textField.value;
        const correctAnswer = correctAnswerField.value;
        
        // Collect all options from the dynamic list
        const options = [];
        for (let i = 0; i < this.optionCount; i++) {
            const input = document.getElementById(`question-option-${i}`);
            if (input) {
                const optionText = input.value.trim();
                if (optionText) {
                    const label = String.fromCharCode(65 + i); // A, B, C, etc.
                    options.push({ label, text: optionText });
                }
            }
        }

        // Validation
        if (!text.trim()) {
            this.showValidationFeedback('Please enter the question text', 'error');
            return;
        }

        if (!correctAnswer) {
            this.showValidationFeedback('Please select the correct answer', 'error');
            return;
        }

        if (options.length < 3) {
            this.showValidationFeedback('Please provide at least 3 options', 'error');
            return;
        }

        // Check if correct answer matches an available option
        const correctAnswerIndex = correctAnswer.charCodeAt(0) - 65;
        if (correctAnswerIndex >= options.length) {
            this.showValidationFeedback('Correct answer must match an available option', 'error');
            return;
        }

        // Log the exact payload being sent
        const payload = {
            text,
            correct_answer: correctAnswer,
            options
        };
        console.log('Sending question:', payload);

        try {
            const response = await fetch(`/api/admin/tests/${this.currentTest.id}/questions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                this.showToast('Question created successfully', 'success');
                document.getElementById('create-question-modal').classList.add('hidden');
                this.reloadCurrentView();
            } else {
                // Try to parse as JSON, but handle non-JSON responses
                let errorMsg = `HTTP ${response.status}: ${response.statusText}`;
                
                try {
                    const error = await response.json();
                    console.error('Validation error:', error);
                    
                    // Show detailed error message
                    if (error.detail && typeof error.detail === 'string') {
                        errorMsg = error.detail;
                    } else if (Array.isArray(error.detail)) {
                        errorMsg = error.detail.map(e => e.msg || e).join('; ');
                    } else {
                        errorMsg = error.detail || JSON.stringify(error);
                    }
                } catch (jsonError) {
                    // Response is not JSON (probably HTML error page)
                    console.error('Non-JSON error response:', jsonError);
                    const responseText = await response.text();
                    console.error('Response text:', responseText.substring(0, 200) + '...');
                    errorMsg = `Server error (${response.status}). Check console for details.`;
                }
                
                console.error(errorMsg);
                this.showToast(errorMsg, 'error');
            }
        } catch (error) {
            console.error('Error creating question:', error);
            this.showToast('Error creating question: ' + error.message, 'error');
        }
    }

    renderQuestionOptions() {
        const container = document.getElementById('options-container');
        container.innerHTML = '';

        for (let i = 0; i < this.optionCount; i++) {
            const label = String.fromCharCode(65 + i); // A, B, C, etc.
            const canRemove = this.optionCount > 3;
            
            const optionDiv = document.createElement('div');
            optionDiv.className = 'flex items-end gap-2';
            optionDiv.innerHTML = `
                <div class="flex-1">
                    <label for="question-option-${i}" class="block text-xs font-medium text-gray-600 mb-1">
                        Option ${label}
                    </label>
                    <input
                        type="text"
                        id="question-option-${i}"
                        class="w-full px-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Enter option text"
                    >
                </div>
                ${canRemove ? `
                    <button
                        type="button"
                        class="px-3 py-2 bg-red-100 text-red-700 rounded text-xs font-medium hover:bg-red-200 transition-colors"
                        onclick="testMgmt.removeOption(${i})"
                    >
                        Remove
                    </button>
                ` : ''}
            `;
            container.appendChild(optionDiv);
        }

        // Update add button state
        const addBtn = document.getElementById('add-option-btn');
        if (this.optionCount >= 10) {
            addBtn.disabled = true;
            addBtn.classList.add('opacity-50', 'cursor-not-allowed');
        } else {
            addBtn.disabled = false;
            addBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    addOption() {
        if (this.optionCount < 10) {
            this.optionCount++;
            this.renderQuestionOptions();
            this.updateCorrectAnswerDropdown();
        }
    }

    removeOption(index) {
        if (this.optionCount > 3) {
            this.optionCount--;
            this.renderQuestionOptions();
            this.updateCorrectAnswerDropdown();
        }
    }

    updateCorrectAnswerDropdown() {
        const select = document.getElementById('question-correct-answer');
        const currentValue = select.value;
        
        // Clear existing options except the first one
        while (select.options.length > 1) {
            select.remove(1);
        }

        // Add options based on current count
        for (let i = 0; i < this.optionCount; i++) {
            const label = String.fromCharCode(65 + i);
            const option = document.createElement('option');
            option.value = label;
            option.textContent = label;
            select.appendChild(option);
        }

        // Restore previous value if still valid
        if (currentValue && currentValue.charCodeAt(0) - 65 < this.optionCount) {
            select.value = currentValue;
        }
    }

    showValidationFeedback(message, type = 'error') {
        const feedback = document.getElementById('question-validation-feedback');
        feedback.textContent = message;
        feedback.className = type === 'error' 
            ? 'text-xs p-3 rounded bg-red-50 text-red-700 border border-red-200'
            : 'text-xs p-3 rounded bg-green-50 text-green-700 border border-green-200';
        feedback.classList.remove('hidden');
        
        setTimeout(() => {
            feedback.classList.add('hidden');
        }, 5000);
    }

    // Edit form handlers
    async handleEditSubject(e) {
        e.preventDefault();
        
        const name = document.getElementById('edit-subject-name').value.trim();
        
        if (!name) {
            this.showToast('Subject name is required', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/admin/subjects/${this.currentEditId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            });

            if (response.ok) {
                this.showToast('Subject updated successfully', 'success');
                UIUtils.closeModal('edit-subject-modal');
                this.reloadCurrentView(); // Refresh the current view
            } else {
                const error = await response.json();
                this.showToast(error.detail || 'Error updating subject', 'error');
            }
        } catch (error) {
            console.error('Error updating subject:', error);
            this.showToast('Error updating subject: ' + error.message, 'error');
        }
    }

    async handleEditLevel(e) {
        e.preventDefault();
        
        const name = document.getElementById('edit-level-name').value.trim();
        
        if (!name) {
            this.showToast('Level name is required', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/admin/subjects/${this.currentSubject.id}/levels/${this.currentEditId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            });

            if (response.ok) {
                this.showToast('Level updated successfully', 'success');
                UIUtils.closeModal('edit-level-modal');
                this.reloadCurrentView(); // Refresh the current view
            } else {
                const error = await response.json();
                this.showToast(error.detail || 'Error updating level', 'error');
            }
        } catch (error) {
            console.error('Error updating level:', error);
            this.showToast('Error updating level: ' + error.message, 'error');
        }
    }

    async handleEditTest(e) {
        e.preventDefault();
        
        const name = document.getElementById('edit-test-name').value.trim();
        const startDate = document.getElementById('edit-test-start-date').value;
        const endDate = document.getElementById('edit-test-end-date').value;
        
        if (!name) {
            this.showToast('Test name is required', 'error');
            return;
        }

        // Validate date range if both dates are provided
        if (startDate && endDate && new Date(startDate) > new Date(endDate)) {
            this.showToast('Start date cannot be after end date', 'error');
            return;
        }

        try {
            const updateData = { name };
            
            // Only include dates if they have values
            if (startDate) {
                updateData.start_date = startDate;
            }
            if (endDate) {
                updateData.end_date = endDate;
            }

            const response = await fetch(`/api/admin/levels/${this.currentLevel.id}/tests/${this.currentEditId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updateData)
            });

            if (response.ok) {
                this.showToast('Test updated successfully', 'success');
                UIUtils.closeModal('edit-test-modal');
                this.reloadCurrentView(); // Refresh the current view
            } else {
                const error = await response.json();
                this.showToast(error.detail || 'Error updating test', 'error');
            }
        } catch (error) {
            console.error('Error updating test:', error);
            this.showToast('Error updating test: ' + error.message, 'error');
        }
    }

    async deleteSubject(id) {
        if (!confirm('Are you sure you want to delete this subject and all its contents?')) return;
        
        try {
            const response = await fetch(`/api/admin/subjects/${id}`, { method: 'DELETE' });
            if (response.ok) {
                this.showToast('Subject deleted successfully', 'success');
                this.reloadCurrentView();
            } else {
                this.showToast('Error deleting subject', 'error');
            }
        } catch (error) {
            console.error('Error deleting subject:', error);
            this.showToast('Error deleting subject', 'error');
        }
    }

    async deleteLevel(id) {
        if (!confirm('Are you sure you want to delete this level and all its contents?')) return;
        
        try {
            const response = await fetch(`/api/admin/subjects/${this.currentSubject.id}/levels/${id}`, { method: 'DELETE' });
            if (response.ok) {
                this.showToast('Level deleted successfully', 'success');
                this.reloadCurrentView();
            } else {
                this.showToast('Error deleting level', 'error');
            }
        } catch (error) {
            console.error('Error deleting level:', error);
            this.showToast('Error deleting level', 'error');
        }
    }

    async deleteTest(id) {
        if (!confirm('Are you sure you want to delete this test and all its questions?')) return;
        
        try {
            const response = await fetch(`/api/admin/levels/${this.currentLevel.id}/tests/${id}`, { method: 'DELETE' });
            if (response.ok) {
                this.showToast('Test deleted successfully', 'success');
                this.reloadCurrentView();
            } else {
                this.showToast('Error deleting test', 'error');
            }
        } catch (error) {
            console.error('Error deleting test:', error);
            this.showToast('Error deleting test', 'error');
        }
    }

    async deleteQuestion(id) {
        if (!confirm('Are you sure you want to delete this question?')) return;
        
        try {
            const response = await fetch(`/api/admin/tests/${this.currentTest.id}/questions/${id}`, { method: 'DELETE' });
            if (response.ok) {
                this.showToast('Question deleted successfully', 'success');
                this.reloadCurrentView();
            } else {
                this.showToast('Error deleting question', 'error');
            }
        } catch (error) {
            console.error('Error deleting question:', error);
            this.showToast('Error deleting question', 'error');
        }
    }

    async editSubject(id) {
        try {
            // Fetch current subject data
            const response = await fetch(`/api/admin/subjects/${id}`);
            if (response.ok) {
                const subject = await response.json();
                this.currentEditId = id;
                
                // Populate the edit form
                document.getElementById('edit-subject-name').value = subject.name;
                
                // Show the modal
                UIUtils.openModal('edit-subject-modal');
            } else {
                this.showToast('Failed to load subject data', 'error');
            }
        } catch (error) {
            console.error('Error loading subject:', error);
            this.showToast('Error loading subject data', 'error');
        }
    }

    async editLevel(id) {
        try {
            // Fetch current level data
            const response = await fetch(`/api/admin/subjects/${this.currentSubject.id}/levels/${id}`);
            if (response.ok) {
                const level = await response.json();
                this.currentEditId = id;
                
                // Populate the edit form
                document.getElementById('edit-level-name').value = level.name;
                
                // Show the modal
                UIUtils.openModal('edit-level-modal');
            } else {
                this.showToast('Failed to load level data', 'error');
            }
        } catch (error) {
            console.error('Error loading level:', error);
            this.showToast('Error loading level data', 'error');
        }
    }

    async editTest(id) {
        try {
            // Fetch current test data
            const response = await fetch(`/api/admin/levels/${this.currentLevel.id}/tests/${id}`);
            if (response.ok) {
                const test = await response.json();
                this.currentEditId = id;
                
                // Populate the edit form
                document.getElementById('edit-test-name').value = test.name;
                
                // Format dates for input fields (convert from ISO to YYYY-MM-DD)
                if (test.start_date) {
                    const startDate = new Date(test.start_date);
                    document.getElementById('edit-test-start-date').value = startDate.toISOString().split('T')[0];
                }
                if (test.end_date) {
                    const endDate = new Date(test.end_date);
                    document.getElementById('edit-test-end-date').value = endDate.toISOString().split('T')[0];
                }
                
                // Show the modal
                UIUtils.openModal('edit-test-modal');
            } else {
                this.showToast('Failed to load test data', 'error');
            }
        } catch (error) {
            console.error('Error loading test:', error);
            this.showToast('Error loading test data', 'error');
        }
    }

    async editQuestion(id) {
        try {
            // Fetch question data
            const response = await fetch(`/api/admin/tests/${this.currentTest.id}/questions/${id}`);
            if (!response.ok) {
                throw new Error('Failed to fetch question data');
            }
            
            const question = await response.json();
            
            // Store the current edit ID
            this.currentEditId = id;
            
            // Populate the form
            document.getElementById('edit-question-text').value = question.text;
            document.getElementById('edit-question-correct-answer').value = question.correct_answer;
            
            // Set up options for editing
            this.editOptionCount = question.options.length;
            this.renderEditQuestionOptions(question.options);
            this.updateEditCorrectAnswerDropdown();
            
            // Show the modal
            UIUtils.openModal('edit-question-modal');
            
        } catch (error) {
            console.error('Error loading question for edit:', error);
            this.showToast('Error loading question data: ' + error.message, 'error');
        }
    }

    async handleEditQuestion(e) {
        e.preventDefault();
        
        const text = document.getElementById('edit-question-text').value.trim();
        const correctAnswer = document.getElementById('edit-question-correct-answer').value;
        
        if (!text) {
            this.showEditValidationFeedback('Question text is required', 'error');
            return;
        }
        
        if (!correctAnswer) {
            this.showEditValidationFeedback('Please select the correct answer', 'error');
            return;
        }
        
        // Collect options
        const options = [];
        for (let i = 0; i < this.editOptionCount; i++) {
            const label = String.fromCharCode(65 + i); // A, B, C, etc.
            const textInput = document.getElementById(`edit-option-${label}`);
            if (textInput && textInput.value.trim()) {
                options.push({
                    label: label,
                    text: textInput.value.trim()
                });
            }
        }
        
        // Validate minimum options
        if (options.length < 3) {
            this.showEditValidationFeedback('At least 3 options are required', 'error');
            return;
        }
        
        // Validate correct answer exists in options
        const optionLabels = options.map(opt => opt.label);
        if (!optionLabels.includes(correctAnswer)) {
            this.showEditValidationFeedback('Correct answer must match one of the provided options', 'error');
            return;
        }
        
        try {
            const response = await fetch(`/api/admin/tests/${this.currentTest.id}/questions/${this.currentEditId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    correct_answer: correctAnswer,
                    options: options
                })
            });
            
            if (response.ok) {
                this.showToast('Question updated successfully', 'success');
                UIUtils.closeModal('edit-question-modal');
                this.reloadCurrentView(); // Refresh the current view
            } else {
                const error = await response.json();
                this.showEditValidationFeedback(error.detail || 'Error updating question', 'error');
            }
        } catch (error) {
            console.error('Error updating question:', error);
            this.showEditValidationFeedback('Error updating question: ' + error.message, 'error');
        }
    }

    renderEditQuestionOptions(existingOptions = []) {
        const container = document.getElementById('edit-options-container');
        container.innerHTML = '';
        
        for (let i = 0; i < this.editOptionCount; i++) {
            const label = String.fromCharCode(65 + i); // A, B, C, etc.
            const existingOption = existingOptions.find(opt => opt.label === label);
            const value = existingOption ? existingOption.text : '';
            
            const optionDiv = document.createElement('div');
            optionDiv.className = 'flex items-center gap-3 p-3 border border-gray-200 rounded-md bg-gray-50';
            optionDiv.innerHTML = `
                <div class="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-semibold">
                    ${label}
                </div>
                <input
                    type="text"
                    id="edit-option-${label}"
                    value="${value}"
                    placeholder="Enter option ${label} text..."
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                >
                ${this.editOptionCount > 3 ? `
                    <button
                        type="button"
                        class="flex-shrink-0 w-8 h-8 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm hover:bg-red-200 transition-colors"
                        onclick="testMgmt.removeEditOption(${i})"
                        title="Remove option ${label}"
                    >
                        ×
                    </button>
                ` : ''}
            `;
            container.appendChild(optionDiv);
        }
        
        // Update add button visibility
        const addBtn = document.getElementById('edit-add-option-btn');
        if (addBtn) {
            addBtn.style.display = this.editOptionCount >= 10 ? 'none' : 'inline-block';
        }
    }

    addEditOption() {
        if (this.editOptionCount < 10) {
            this.editOptionCount++;
            this.renderEditQuestionOptions(this.getCurrentEditOptions());
            this.updateEditCorrectAnswerDropdown();
        }
    }

    removeEditOption(index) {
        if (this.editOptionCount > 3) {
            this.editOptionCount--;
            this.renderEditQuestionOptions(this.getCurrentEditOptions());
            this.updateEditCorrectAnswerDropdown();
        }
    }

    getCurrentEditOptions() {
        const options = [];
        for (let i = 0; i < 10; i++) {
            const label = String.fromCharCode(65 + i);
            const input = document.getElementById(`edit-option-${label}`);
            if (input && input.value.trim()) {
                options.push({
                    label: label,
                    text: input.value.trim()
                });
            }
        }
        return options;
    }

    updateEditCorrectAnswerDropdown() {
        const select = document.getElementById('edit-question-correct-answer');
        const currentValue = select.value;
        
        // Clear existing options except the first one
        select.innerHTML = '<option value="">Select the correct answer</option>';
        
        // Add options based on current editOptionCount
        for (let i = 0; i < this.editOptionCount; i++) {
            const label = String.fromCharCode(65 + i); // A, B, C, etc.
            const option = document.createElement('option');
            option.value = label;
            option.textContent = label;
            select.appendChild(option);
        }
        
        // Restore previous value if still valid
        if (currentValue && currentValue.charCodeAt(0) - 65 < this.editOptionCount) {
            select.value = currentValue;
        }
    }

    showEditValidationFeedback(message, type = 'error') {
        const feedback = document.getElementById('edit-question-validation-feedback');
        feedback.className = `text-xs p-3 rounded ${type === 'error' ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`;
        feedback.textContent = message;
        feedback.classList.remove('hidden');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            feedback.classList.add('hidden');
        }, 5000);
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';
        
        toast.className = `${bgColor} text-white px-4 py-3 rounded-lg shadow-lg pointer-events-auto`;
        toast.textContent = message;
        
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    handleSearch() {
        const searchInput = document.getElementById('test-search-input');
        const searchTerm = searchInput.value.trim();
        
        // Update search state for current view
        this.searchState[this.currentView] = searchTerm;
        
        // Reset pagination and reload current view
        this.resetPagination(this.currentView);
        this.reloadCurrentView();
    }

    handleClearSearch() {
        const searchInput = document.getElementById('test-search-input');
        searchInput.value = '';
        
        // Clear search state for current view
        this.searchState[this.currentView] = '';
        
        // Reset pagination and reload current view
        this.resetPagination(this.currentView);
        this.reloadCurrentView();
    }

    updateSearchInput() {
        const searchInput = document.getElementById('test-search-input');
        if (searchInput) {
            searchInput.value = this.searchState[this.currentView] || '';
            
            // Update placeholder based on current view
            const placeholders = {
                subjects: 'Search subjects by name...',
                levels: 'Search levels by name...',
                tests: 'Search tests by name...',
                questions: 'Search questions by text...'
            };
            searchInput.placeholder = placeholders[this.currentView] || 'Search...';
        }
    }

    updateToolbar() {
        const titleEl = document.getElementById('test-toolbar-title');
        const btnEl = document.getElementById('test-toolbar-btn');
        
        if (!titleEl || !btnEl) return;

        const config = {
            subjects: { title: 'Subjects', action: 'create-subject', label: '+ Create Subject' },
            levels: { title: 'Levels', action: 'create-level', label: '+ Create Level' },
            tests: { title: 'Tests', action: 'create-test', label: '+ Create Test' },
            questions: { title: 'Questions', action: 'create-question', label: '+ Create Question' }
        };

        const current = config[this.currentView] || config.subjects;
        titleEl.textContent = current.title;
        btnEl.textContent = current.label;
        btnEl.dataset.action = current.action;
    }

    // Pagination helper methods
    updatePaginationInfo(viewType, total) {
        const pagination = this.pagination[viewType];
        const start = pagination.skip + 1;
        const end = Math.min(pagination.skip + pagination.limit, total);

        // Update pagination info elements
        const startElement = document.getElementById(`${viewType.slice(0, -1)}-page-start`);
        const endElement = document.getElementById(`${viewType.slice(0, -1)}-page-end`);
        const totalElement = document.getElementById(`${viewType.slice(0, -1)}-total-count`);

        if (startElement) startElement.textContent = total > 0 ? start : 0;
        if (endElement) endElement.textContent = end;
        if (totalElement) totalElement.textContent = total;
    }

    updatePaginationControls(viewType, total) {
        const pagination = this.pagination[viewType];
        const paginationContainer = document.getElementById(`${viewType.slice(0, -1)}-pagination`);

        if (!paginationContainer) return;

        // Show/hide pagination based on total count
        if (total <= pagination.limit) {
            paginationContainer.style.display = 'none';
            return;
        }

        paginationContainer.style.display = 'flex';

        // Update previous button state
        const prevButton = paginationContainer.querySelector('[data-action="prev-page"]');
        if (prevButton) {
            prevButton.disabled = pagination.skip === 0;
            prevButton.classList.toggle('opacity-50', pagination.skip === 0);
            prevButton.classList.toggle('cursor-not-allowed', pagination.skip === 0);
        }

        // Update next button state
        const nextButton = paginationContainer.querySelector('[data-action="next-page"]');
        if (nextButton) {
            const hasNextPage = pagination.skip + pagination.limit < total;
            nextButton.disabled = !hasNextPage;
            nextButton.classList.toggle('opacity-50', !hasNextPage);
            nextButton.classList.toggle('cursor-not-allowed', !hasNextPage);
        }
    }

    nextPage() {
        const pagination = this.pagination[this.currentView];
        pagination.skip += pagination.limit;
        this.reloadCurrentView();
    }

    prevPage() {
        const pagination = this.pagination[this.currentView];
        if (pagination.skip >= pagination.limit) {
            pagination.skip -= pagination.limit;
            this.reloadCurrentView();
        }
    }

    goToPage(pageNumber) {
        const pagination = this.pagination[this.currentView];
        pagination.skip = (pageNumber - 1) * pagination.limit;
        this.reloadCurrentView();
    }

    reloadCurrentView() {
        switch (this.currentView) {
            case 'subjects':
                this.loadSubjects();
                break;
            case 'levels':
                if (this.currentSubject) {
                    this.viewLevels(this.currentSubject.id);
                }
                break;
            case 'tests':
                if (this.currentLevel) {
                    this.viewTests(this.currentLevel.id);
                }
                break;
            case 'questions':
                if (this.currentTest) {
                    this.viewQuestions(this.currentTest.id);
                }
                break;
        }
    }

    resetPagination(viewType) {
        if (this.pagination[viewType]) {
            this.pagination[viewType].skip = 0;
        }
    }

    // Breadcrumb navigation methods
    updateBreadcrumb() {
        const levelBreadcrumb = document.getElementById('breadcrumb-level');
        const testBreadcrumb = document.getElementById('breadcrumb-test');
        const questionBreadcrumb = document.getElementById('breadcrumb-question');
        const levelText = document.getElementById('breadcrumb-level-text');
        const testText = document.getElementById('breadcrumb-test-text');

        // Reset all breadcrumb items
        levelBreadcrumb.classList.add('hidden');
        testBreadcrumb.classList.add('hidden');
        questionBreadcrumb.classList.add('hidden');

        // Show breadcrumb items based on current view
        switch (this.currentView) {
            case 'subjects':
                // Only show Subjects (already visible)
                break;
            case 'levels':
                levelBreadcrumb.classList.remove('hidden');
                levelText.textContent = this.breadcrumbState.subjectName || 'Subject';
                break;
            case 'tests':
                levelBreadcrumb.classList.remove('hidden');
                testBreadcrumb.classList.remove('hidden');
                levelText.textContent = this.breadcrumbState.subjectName || 'Subject';
                testText.textContent = this.breadcrumbState.levelName || 'Level';
                break;
            case 'questions':
                levelBreadcrumb.classList.remove('hidden');
                testBreadcrumb.classList.remove('hidden');
                questionBreadcrumb.classList.remove('hidden');
                levelText.textContent = this.breadcrumbState.subjectName || 'Subject';
                testText.textContent = this.breadcrumbState.levelName || 'Level';
                break;
        }
    }

    navigateToSubjects() {
        this.currentView = 'subjects';
        this.currentSubject = null;
        this.currentLevel = null;
        this.currentTest = null;
        this.breadcrumbState = { subjectName: '', levelName: '', testName: '' };
        this.loadSubjects();
    }

    navigateToLevels() {
        if (this.currentSubject) {
            this.currentView = 'levels';
            this.currentLevel = null;
            this.currentTest = null;
            this.breadcrumbState.levelName = '';
            this.breadcrumbState.testName = '';
            this.viewLevels(this.currentSubject.id);
        }
    }

    navigateToTests() {
        if (this.currentLevel) {
            this.currentView = 'tests';
            this.currentTest = null;
            this.breadcrumbState.testName = '';
            this.viewTests(this.currentLevel.id);
        }
    }
}

// Initialize test management module
const testMgmt = new TestManagementModule();

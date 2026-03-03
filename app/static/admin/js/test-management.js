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
        this.optionCount = 3; // Start with 3 options (A, B, C)
        this.pagination = {
            subjects: { skip: 0, limit: 25 },
            levels: { skip: 0, limit: 25 },
            tests: { skip: 0, limit: 25 },
            questions: { skip: 0, limit: 25 }
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
        });

        // Form submissions
        document.getElementById('create-subject-form')?.addEventListener('submit', (e) => this.handleCreateSubject(e));
        document.getElementById('create-level-form')?.addEventListener('submit', (e) => this.handleCreateLevel(e));
        document.getElementById('create-test-form')?.addEventListener('submit', (e) => this.handleCreateTest(e));
        document.getElementById('create-question-form')?.addEventListener('submit', (e) => this.handleCreateQuestion(e));
    }

    async showTestManagement() {
        const page = document.getElementById('test-management-page');
        if (page) {
            page.classList.remove('hidden');
            document.getElementById('users-page').classList.add('hidden');
            document.getElementById('audit-page').classList.add('hidden');
            document.getElementById('page-title').textContent = 'Test Management';
            document.getElementById('page-subtitle').textContent = 'Manage subjects, levels, tests, and questions';
            this.loadSubjects();
        }
    }

    async loadSubjects() {
        try {
            this.currentView = 'subjects';
            this.updateToolbar();
            const response = await fetch(`/api/admin/subjects?skip=${this.pagination.subjects.skip}&limit=${this.pagination.subjects.limit}`);
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
                this.loadSubjects();
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
        this.currentSubject = subjectId;
        this.currentView = 'levels';
        this.updateToolbar();
        try {
            const response = await fetch(`/api/admin/subjects/${subjectId}/levels?skip=0&limit=25`);
            const data = await response.json();
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
    }

    async viewTests(levelId) {
        this.currentLevel = levelId;
        this.currentView = 'tests';
        this.updateToolbar();
        try {
            const response = await fetch(`/api/admin/levels/${levelId}/tests?skip=0&limit=25`);
            const data = await response.json();
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
    }

    async viewQuestions(testId) {
        this.currentTest = testId;
        this.currentView = 'questions';
        this.updateToolbar();
        try {
            const response = await fetch(`/api/admin/tests/${testId}/questions?skip=0&limit=25`);
            const data = await response.json();
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
                <td class="px-6 py-4 text-sm text-gray-900">${question.text.substring(0, 50)}...</td>
                <td class="px-6 py-4 text-sm text-gray-900">${question.correct_answer}</td>
                <td class="px-6 py-4 text-sm text-gray-900">${question.options.length}</td>
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
            const response = await fetch(`/api/admin/subjects/${this.currentSubject}/levels`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });

            if (response.ok) {
                this.showToast('Level created successfully', 'success');
                document.getElementById('create-level-modal').classList.add('hidden');
                this.viewLevels(this.currentSubject);
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
            const response = await fetch(`/api/admin/levels/${this.currentLevel}/tests`, {
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
                this.viewTests(this.currentLevel);
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
            const response = await fetch(`/api/admin/tests/${this.currentTest}/questions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                this.showToast('Question created successfully', 'success');
                document.getElementById('create-question-modal').classList.add('hidden');
                this.viewQuestions(this.currentTest);
            } else {
                // Parse and log the full error response
                const error = await response.json();
                console.error('Validation error:', error);
                
                // Show detailed error message
                let errorMsg = error.detail || JSON.stringify(error);
                
                // If it's a validation error with multiple issues, format it nicely
                if (error.detail && typeof error.detail === 'string') {
                    errorMsg = error.detail;
                } else if (Array.isArray(error.detail)) {
                    errorMsg = error.detail.map(e => e.msg || e).join('; ');
                }
                
                console.error(`HTTP ${response.status}: ${errorMsg}`);
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

    async deleteSubject(id) {
        if (!confirm('Are you sure you want to delete this subject and all its contents?')) return;
        
        try {
            const response = await fetch(`/api/admin/subjects/${id}`, { method: 'DELETE' });
            if (response.ok) {
                this.showToast('Subject deleted successfully', 'success');
                this.loadSubjects();
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
            const response = await fetch(`/api/admin/subjects/${this.currentSubject}/levels/${id}`, { method: 'DELETE' });
            if (response.ok) {
                this.showToast('Level deleted successfully', 'success');
                this.viewLevels(this.currentSubject);
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
            const response = await fetch(`/api/admin/levels/${this.currentLevel}/tests/${id}`, { method: 'DELETE' });
            if (response.ok) {
                this.showToast('Test deleted successfully', 'success');
                this.viewTests(this.currentLevel);
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
            const response = await fetch(`/api/admin/tests/${this.currentTest}/questions/${id}`, { method: 'DELETE' });
            if (response.ok) {
                this.showToast('Question deleted successfully', 'success');
                this.viewQuestions(this.currentTest);
            } else {
                this.showToast('Error deleting question', 'error');
            }
        } catch (error) {
            console.error('Error deleting question:', error);
            this.showToast('Error deleting question', 'error');
        }
    }

    editSubject(id) {
        this.showToast('Edit functionality coming soon', 'info');
    }

    editLevel(id) {
        this.showToast('Edit functionality coming soon', 'info');
    }

    editTest(id) {
        this.showToast('Edit functionality coming soon', 'info');
    }

    editQuestion(id) {
        this.showToast('Edit functionality coming soon', 'info');
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
}

// Initialize test management module
const testMgmt = new TestManagementModule();

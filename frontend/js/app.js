// API Configuration
const API_BASE = '/api';
let authToken = localStorage.getItem('authToken');
let currentUser = null;
let activeWorkoutSession = null;
let workoutTimer = null;

// Utility Functions
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alertContainer.appendChild(alert);

    setTimeout(() => {
        alert.remove();
    }, 3000);
}

async function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (authToken && !options.noAuth) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401) {
            logout();
            throw new Error('Unauthorized');
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'An error occurred');
        }

        return data;
    } catch (error) {
        showAlert(error.message, 'error');
        throw error;
    }
}

async function uploadFile(endpoint, formData, method = 'POST') {
    const headers = {};
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: method,
            headers,
            body: formData
        });

        if (response.status === 401) {
            logout();
            throw new Error('Unauthorized');
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'An error occurred');
        }

        return data;
    } catch (error) {
        showAlert(error.message, 'error');
        throw error;
    }
}

// Authentication
async function login(email, password) {
    const data = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        noAuth: true
    });

    authToken = data.access_token;
    localStorage.setItem('authToken', authToken);
    await loadUser();
    showApp();
    showAlert(t('common.success'));
}

async function register(userData) {
    await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
        noAuth: true
    });

    showAlert('Registration successful! Please login.');

    // Clear registration form
    document.getElementById('register').reset();

    showLoginForm();
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    // Clear password field on logout
    document.getElementById('login-password').value = '';
    document.getElementById('login-email').value = '';
    showAuth();
}

async function loadUser() {
    currentUser = await apiRequest('/auth/me');
    document.getElementById('user-name').textContent = currentUser.name;

    // Set language from user profile
    if (currentUser.language) {
        setLanguage(currentUser.language);
    }

    // Show/hide UI elements based on role
    updateUIForRole();
}

function updateUIForRole() {
    const isPersonalTrainer = currentUser.role === 'personal_trainer';
    const isClient = currentUser.role === 'client';

    // Show/hide "My Clients" tab - only for Personal Trainers
    const clientsTab = document.querySelector('[data-tab="clients"]');
    if (clientsTab) {
        clientsTab.style.display = isPersonalTrainer ? 'block' : 'none';
    }

    // Show/hide "Exercises" tab - only for Personal Trainers
    const exercisesTab = document.querySelector('[data-tab="exercises"]');
    if (exercisesTab) {
        exercisesTab.style.display = isPersonalTrainer ? 'block' : 'none';
    }

    // Hide "Treinos" (Workout Plans) tab - PTs create workouts in "My Clients" tab
    // Clients don't see this tab either
    const plansTab = document.querySelector('[data-tab="plans"]');
    if (plansTab) {
        plansTab.style.display = 'none';
    }

    // Show/hide "Treino Ativo" (Active Workout) tab - only for Clients
    const workoutTab = document.querySelector('[data-tab="workout"]');
    if (workoutTab) {
        workoutTab.style.display = isClient ? 'block' : 'none';
    }

    // Show/hide "Cardio" tab - only for Clients
    const cardioTab = document.querySelector('[data-tab="cardio"]');
    if (cardioTab) {
        cardioTab.style.display = isClient ? 'block' : 'none';
    }

    // Show/hide "Add Exercise" button
    const addExerciseBtn = document.getElementById('add-exercise-btn');
    if (addExerciseBtn) {
        addExerciseBtn.style.display = isPersonalTrainer ? 'block' : 'none';
    }

    // Show/hide "Add Plan" button - only for Personal Trainers
    const addPlanBtn = document.getElementById('add-plan-btn');
    if (addPlanBtn) {
        addPlanBtn.style.display = isPersonalTrainer ? 'block' : 'none';
    }

    // Show total exercises stat for Personal Trainers
    const exercisesStat = document.getElementById('stat-total-exercises');
    if (exercisesStat) {
        exercisesStat.style.display = isPersonalTrainer ? 'block' : 'none';
    }
}

// UI State Management
function showAuth() {
    document.getElementById('auth-screen').style.display = 'flex';
    document.getElementById('app-screen').style.display = 'none';
    // Always clear login fields when showing auth screen
    const emailField = document.getElementById('login-email');
    const passwordField = document.getElementById('login-password');
    if (emailField) emailField.value = '';
    if (passwordField) passwordField.value = '';
    updatePageTranslations();
}

function showApp() {
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('app-screen').style.display = 'block';
    updatePageTranslations();
    // Always show dashboard tab when logging in
    showTab('dashboard');
}

function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Load data for specific tabs
    if (tabName === 'dashboard') loadDashboard();
    else if (tabName === 'exercises') loadExercises();
    else if (tabName === 'plans') loadPlans();
    else if (tabName === 'workout') loadWorkoutTab();
    else if (tabName === 'cardio') loadCardio();
    else if (tabName === 'clients') loadClients();
    else if (tabName === 'profile') loadProfile();
}

function showLoginForm() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
    // Clear password field when showing login form (e.g., on back navigation)
    document.getElementById('login-password').value = '';
    updatePageTranslations();
}

function showRegisterForm() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
    updatePageTranslations();
}

// Dashboard
async function loadDashboard() {
    try {
        const stats = await apiRequest('/users/dashboard');
        const isPersonalTrainer = currentUser.role === 'personal_trainer';

        document.getElementById('stat-workouts').textContent = stats.total_workouts;
        document.getElementById('stat-bmi').textContent = stats.current_bmi?.toFixed(1) || '0';
        document.getElementById('stat-streak').textContent = stats.active_streak;
        document.getElementById('stat-cardio').textContent = stats.total_cardio_sessions;

        // Hide BMI card for personal trainers
        const bmiCard = document.getElementById('stat-bmi')?.closest('.stat-card');
        if (bmiCard) {
            bmiCard.style.display = isPersonalTrainer ? 'none' : 'block';
        }

        // Load exercises count for Personal Trainers
        if (isPersonalTrainer) {
            const exercises = await apiRequest('/exercises');
            document.getElementById('stat-exercises').textContent = exercises.length;
        }

        // Load health metrics for clients on dashboard
        const dashboardHealthMetricsSection = document.getElementById('dashboard-health-metrics');
        if (dashboardHealthMetricsSection) {
            if (isPersonalTrainer) {
                dashboardHealthMetricsSection.style.display = 'none';
            } else {
                dashboardHealthMetricsSection.style.display = 'block';
                await loadDashboardHealthMetrics();
            }
        }
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

async function loadDashboardHealthMetrics() {
    try {
        const metrics = await apiRequest('/users/health-metrics');
        displayDashboardHealthMetrics(metrics);
    } catch (error) {
        console.error('Failed to load health metrics:', error);
        document.getElementById('dashboard-health-metrics-container').innerHTML = '<p class="error">Failed to load health metrics</p>';
    }
}

function displayDashboardHealthMetrics(metrics) {
    const container = document.getElementById('dashboard-health-metrics-container');

    const getBMIClass = (status) => {
        switch(status) {
            case 'underweight': return 'status-warning';
            case 'healthy': return 'status-success';
            case 'overweight': return 'status-warning';
            case 'obese': return 'status-danger';
            default: return '';
        }
    };

    const html = `
        <div class="metrics-grid">
            <div class="metric-item">
                <span class="metric-label">${t('health.current_bmi')}</span>
                <span class="metric-value ${getBMIClass(metrics.health_status)}">${metrics.current_bmi}</span>
                <span class="metric-subtitle">${metrics.bmi_category}</span>
            </div>

            <div class="metric-item">
                <span class="metric-label">${t('health.current_weight')}</span>
                <span class="metric-value">${metrics.current_weight} kg</span>
            </div>

            <div class="metric-item">
                <span class="metric-label">${t('health.healthy_range')}</span>
                <span class="metric-value">${metrics.healthy_weight_range.min} - ${metrics.healthy_weight_range.max} kg</span>
            </div>

            ${metrics.desired_weight ? `
                <div class="metric-item">
                    <span class="metric-label">${t('health.desired_weight')}</span>
                    <span class="metric-value">${metrics.desired_weight} kg</span>
                </div>

                <div class="metric-item">
                    <span class="metric-label">${t('health.weight_difference')}</span>
                    <span class="metric-value ${metrics.weight_difference < 0 ? 'status-info' : 'status-success'}">
                        ${metrics.weight_difference > 0 ? '+' : ''}${metrics.weight_difference} kg
                    </span>
                </div>

                <div class="metric-item">
                    <span class="metric-label">${t('health.timeline')}</span>
                    <span class="metric-value">${metrics.estimated_weeks} ${t('health.weeks')}</span>
                    <span class="metric-subtitle">~${metrics.estimated_date}</span>
                </div>

                <div class="metric-item">
                    <span class="metric-label">${t('health.calorie_adjustment')}</span>
                    <span class="metric-value ${metrics.daily_calorie_adjustment < 0 ? 'status-info' : 'status-success'}">
                        ${metrics.daily_calorie_adjustment > 0 ? '+' : ''}${metrics.daily_calorie_adjustment} cal
                    </span>
                    <span class="metric-subtitle">${metrics.daily_calorie_adjustment < 0 ? 'Deficit' : 'Surplus'}</span>
                </div>
            ` : ''}
        </div>

        <div class="recommendation-box">
            <strong>${t('health.recommendation')}:</strong>
            <p>${metrics.recommendation}</p>
        </div>
    `;

    container.innerHTML = html;
}

// Exercises
async function loadExercises() {
    try {
        const search = document.getElementById('exercise-search').value;
        const muscle = document.getElementById('muscle-filter').value;

        let url = '/exercises?';
        if (search) url += `search=${encodeURIComponent(search)}&`;
        if (muscle) url += `muscle_group=${encodeURIComponent(muscle)}&`;

        const exercises = await apiRequest(url);
        displayExercises(exercises);
    } catch (error) {
        console.error('Failed to load exercises:', error);
    }
}

function displayExercises(exercises) {
    const container = document.getElementById('exercises-list');
    const isPersonalTrainer = currentUser.role === 'personal_trainer';

    if (exercises.length === 0) {
        const emptyMessage = isPersonalTrainer
            ? `
                <div class="empty-state">
                    <h3>📋 ${t('exercises.no_exercises')}</h3>
                    <p>Start building your exercise library! Add exercises to assign to your clients and create comprehensive workout plans.</p>
                    <button onclick="showAddExerciseModal()" class="btn btn-primary" style="margin-top: 16px;">
                        ${t('exercises.add_new')}
                    </button>
                </div>
              `
            : `
                <div class="empty-state">
                    <h3>📋 ${t('exercises.no_exercises')}</h3>
                    <p>${t('exercises.no_exercises_client')}</p>
                    <p style="margin-top: 12px; font-size: 14px; opacity: 0.8;">Contact your personal trainer to get started!</p>
                </div>
              `;
        container.innerHTML = emptyMessage;
        return;
    }

    container.innerHTML = exercises.map(exercise => `
        <div class="exercise-card">
            ${exercise.image_path ?
                `<img src="${exercise.image_path}" class="exercise-img" alt="${exercise.name}">` :
                '<div class="exercise-img"></div>'
            }
            <div class="exercise-content">
                <h3>${exercise.name}</h3>
                <span class="exercise-tag">${t('muscle.' + exercise.muscle_group.toLowerCase())}</span>
                ${exercise.equipment ? `<span class="exercise-tag">${exercise.equipment}</span>` : ''}
                ${exercise.description ?
                    `<p class="exercise-description collapsed" data-id="${exercise.id}">${exercise.description}</p>
                    <button onclick="toggleDescription('${exercise.id}')" class="btn btn-small" style="margin-top: 8px;">Show More</button>`
                    : ''}
                ${isPersonalTrainer ? `
                    <div style="margin-top: 12px; display: flex; gap: 8px;">
                        <button onclick="showAssignExerciseModal('${exercise.id}')" class="btn btn-small btn-primary" data-i18n="exercises.assign_to_client">${t('exercises.assign_to_client')}</button>
                        <button onclick="showEditExerciseModal('${exercise.id}')" class="btn btn-small" data-i18n="exercises.edit">${t('exercises.edit')}</button>
                        <button onclick="deleteExercise('${exercise.id}')" class="btn btn-small btn-danger" data-i18n="exercises.delete">${t('exercises.delete')}</button>
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function toggleDescription(exerciseId) {
    const desc = document.querySelector(`[data-id="${exerciseId}"]`);
    desc.classList.toggle('collapsed');
    event.target.textContent = desc.classList.contains('collapsed') ? 'Show More' : 'Show Less';
}

function showAddExerciseModal() {
    const modal = createModal(t('exercises.add_new'), `
        <form id="add-exercise-form">
            <div class="form-group">
                <label for="exercise-name" data-i18n="exercises.name">${t('exercises.name')}</label>
                <input type="text" id="exercise-name" required>
            </div>
            <div class="form-group">
                <label for="exercise-muscle" data-i18n="exercises.muscle_group">${t('exercises.muscle_group')}</label>
                <select id="exercise-muscle" required>
                    <option value="Chest">${t('muscle.chest')}</option>
                    <option value="Back">${t('muscle.back')}</option>
                    <option value="Legs">${t('muscle.legs')}</option>
                    <option value="Glutes">${t('muscle.glutes')}</option>
                    <option value="Shoulders">${t('muscle.shoulders')}</option>
                    <option value="Biceps">${t('muscle.biceps')}</option>
                    <option value="Triceps">${t('muscle.triceps')}</option>
                    <option value="Abs">${t('muscle.abs')}</option>
                    <option value="Cardio">${t('muscle.cardio')}</option>
                </select>
            </div>
            <div class="form-group">
                <label for="exercise-equipment" data-i18n="exercises.equipment">${t('exercises.equipment')}</label>
                <input type="text" id="exercise-equipment" placeholder="e.g., Barbell, Dumbbells">
            </div>
            <div class="form-group">
                <label for="exercise-description" data-i18n="exercises.description">${t('exercises.description')}</label>
                <textarea id="exercise-description"></textarea>
            </div>
            <div class="form-group">
                <label for="exercise-image" data-i18n="exercises.image">${t('exercises.image')}</label>
                <input type="file" id="exercise-image" accept=".png,.jpg,.jpeg,.gif">
            </div>
            <button type="submit" class="btn btn-primary" data-i18n="exercises.create">${t('exercises.create')}</button>
        </form>
    `);

    document.getElementById('add-exercise-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData();
        formData.append('name', document.getElementById('exercise-name').value);
        formData.append('muscle_group', document.getElementById('exercise-muscle').value);
        formData.append('equipment', document.getElementById('exercise-equipment').value);
        formData.append('description', document.getElementById('exercise-description').value);

        const imageFile = document.getElementById('exercise-image').files[0];
        if (imageFile) {
            formData.append('image', imageFile);
        }

        try {
            await uploadFile('/exercises', formData);
            closeModal();
            showAlert(t('common.success'));
            loadExercises();
            loadDashboard();
        } catch (error) {
            console.error('Failed to add exercise:', error);
        }
    });
}

async function showEditExerciseModal(exerciseId) {
    try {
        // Fetch the exercise details
        const exercise = await apiRequest(`/exercises/${exerciseId}`);

        const modal = createModal(t('exercises.edit'), `
            <form id="edit-exercise-form">
                <div class="form-group">
                    <label for="edit-exercise-name" data-i18n="exercises.name">${t('exercises.name')}</label>
                    <input type="text" id="edit-exercise-name" value="${exercise.name}" required>
                </div>
                <div class="form-group">
                    <label for="edit-exercise-muscle" data-i18n="exercises.muscle_group">${t('exercises.muscle_group')}</label>
                    <select id="edit-exercise-muscle" required>
                        <option value="Chest" ${exercise.muscle_group.toLowerCase() === 'chest' ? 'selected' : ''}>${t('muscle.chest')}</option>
                        <option value="Back" ${exercise.muscle_group.toLowerCase() === 'back' ? 'selected' : ''}>${t('muscle.back')}</option>
                        <option value="Legs" ${exercise.muscle_group.toLowerCase() === 'legs' ? 'selected' : ''}>${t('muscle.legs')}</option>
                        <option value="Glutes" ${exercise.muscle_group.toLowerCase() === 'glutes' ? 'selected' : ''}>${t('muscle.glutes')}</option>
                        <option value="Shoulders" ${exercise.muscle_group.toLowerCase() === 'shoulders' ? 'selected' : ''}>${t('muscle.shoulders')}</option>
                        <option value="Biceps" ${exercise.muscle_group.toLowerCase() === 'biceps' ? 'selected' : ''}>${t('muscle.biceps')}</option>
                        <option value="Triceps" ${exercise.muscle_group.toLowerCase() === 'triceps' ? 'selected' : ''}>${t('muscle.triceps')}</option>
                        <option value="Abs" ${exercise.muscle_group.toLowerCase() === 'abs' ? 'selected' : ''}>${t('muscle.abs')}</option>
                        <option value="Cardio" ${exercise.muscle_group.toLowerCase() === 'cardio' ? 'selected' : ''}>${t('muscle.cardio')}</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="edit-exercise-equipment" data-i18n="exercises.equipment">${t('exercises.equipment')}</label>
                    <input type="text" id="edit-exercise-equipment" value="${exercise.equipment || ''}" placeholder="e.g., Barbell, Dumbbells">
                </div>
                <div class="form-group">
                    <label for="edit-exercise-description" data-i18n="exercises.description">${t('exercises.description')}</label>
                    <textarea id="edit-exercise-description">${exercise.description || ''}</textarea>
                </div>
                <div class="form-group">
                    <label for="edit-exercise-image" data-i18n="exercises.image">${t('exercises.image')}</label>
                    ${exercise.image_path ? `<p style="font-size: 12px; color: #888; margin-bottom: 8px;">Current image: ${exercise.image_path.split('/').pop()}</p>` : ''}
                    <input type="file" id="edit-exercise-image" accept=".png,.jpg,.jpeg,.gif">
                    <p style="font-size: 12px; color: #888; margin-top: 4px;">Leave empty to keep current image</p>
                </div>
                <button type="submit" class="btn btn-primary" data-i18n="exercises.update">${t('exercises.update')}</button>
            </form>
        `);

        document.getElementById('edit-exercise-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData();
            formData.append('name', document.getElementById('edit-exercise-name').value);
            formData.append('muscle_group', document.getElementById('edit-exercise-muscle').value);
            formData.append('equipment', document.getElementById('edit-exercise-equipment').value);
            formData.append('description', document.getElementById('edit-exercise-description').value);

            const imageFile = document.getElementById('edit-exercise-image').files[0];
            if (imageFile) {
                formData.append('image', imageFile);
            }

            try {
                await uploadFile(`/exercises/${exerciseId}`, formData, 'PUT');
                closeModal();
                showAlert(t('common.success'));
                loadExercises();
                loadDashboard();
            } catch (error) {
                console.error('Failed to update exercise:', error);
                showAlert('Failed to update exercise: ' + error.message);
            }
        });
    } catch (error) {
        console.error('Failed to load exercise:', error);
        showAlert('Failed to load exercise details');
    }
}

async function deleteExercise(exerciseId) {
    if (!confirm('Are you sure you want to delete this exercise?')) return;

    try {
        await apiRequest(`/exercises/${exerciseId}`, { method: 'DELETE' });
        showAlert(t('common.success'));
        loadExercises();
        loadDashboard();
    } catch (error) {
        console.error('Failed to delete exercise:', error);
    }
}

// Clients Management (Personal Trainers only)
async function loadClients() {
    if (currentUser.role !== 'personal_trainer') return;

    try {
        const [clients, workoutPlans] = await Promise.all([
            apiRequest('/users/clients'),
            apiRequest('/workout-plans')
        ]);
        displayClients(clients, workoutPlans);
    } catch (error) {
        console.error('Failed to load clients:', error);
    }
}

function displayClients(clients, workoutPlans = []) {
    const container = document.getElementById('clients-list');

    const headerHtml = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3>${t('clients.your_clients')}</h3>
            <button onclick="showAddClientModal()" class="btn btn-primary">${t('clients.add_client')}</button>
        </div>
    `;

    if (clients.length === 0) {
        container.innerHTML = headerHtml + `
            <div class="empty-state">
                <h3>👥 ${t('clients.no_clients')}</h3>
                <p>You haven't added any clients yet. Click "Add Client" to assign clients to your roster.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = headerHtml + clients.map(client => {
        // Find workout plans for this client
        const clientPlans = workoutPlans.filter(plan => plan.user_id === client.id);

        return `
        <div class="client-card">
            <h3>${client.name}</h3>
            <p><strong>${t('clients.email')}:</strong> ${client.email}</p>
            <p><strong>${t('clients.joined')}:</strong> ${new Date(client.created_at).toLocaleDateString()}</p>

            ${clientPlans.length > 0 ? `
                <div style="margin-top: 16px;">
                    <strong>Workout Plans (${clientPlans.length}):</strong>
                    <div style="margin-top: 8px;">
                        ${clientPlans.map(plan => `
                            <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <strong>${plan.name}</strong>
                                        ${plan.is_active ? '<span class="exercise-tag" style="margin-left: 8px;">Active</span>' : ''}
                                        <div style="font-size: 0.9em; opacity: 0.7; margin-top: 4px;">
                                            ${plan.plan_exercises.length} exercises
                                        </div>
                                    </div>
                                    <div style="display: flex; gap: 8px;">
                                        <button onclick="viewWorkoutPlanDetails('${plan.id}')" class="btn btn-small">View</button>
                                        <button onclick="editWorkoutPlan('${plan.id}')" class="btn btn-small">Edit</button>
                                        <button onclick="deleteWorkoutPlan('${plan.id}')" class="btn btn-small btn-danger">Delete</button>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}

            <div style="margin-top: 12px; display: flex; gap: 8px;">
                <button onclick="viewClientDetails('${client.id}')" class="btn btn-small btn-primary">${t('clients.view_details')}</button>
                <button onclick="createWorkoutPlanForClient('${client.id}')" class="btn btn-small">${t('clients.create_workout')}</button>
                <button onclick="unassignClient('${client.id}')" class="btn btn-small btn-danger">${t('clients.remove')}</button>
            </div>
        </div>
    `;
    }).join('');
}

async function showAddClientModal() {
    try {
        const availableClients = await apiRequest('/users/available-clients');

        if (availableClients.length === 0) {
            showAlert('No available clients to add. All registered clients already have a trainer.', 'error');
            return;
        }

        const modal = createModal('Add Client', `
            <form id="add-client-form">
                <div class="form-group">
                    <label for="client-select">Select Client</label>
                    <select id="client-select" required>
                        <option value="">Choose a client...</option>
                        ${availableClients.map(c => `<option value="${c.id}">${c.name} (${c.email})</option>`).join('')}
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Add Client</button>
            </form>
        `);

        document.getElementById('add-client-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const clientId = document.getElementById('client-select').value;

            try {
                await apiRequest(`/users/clients/${clientId}/assign`, { method: 'POST' });
                closeModal();
                showAlert(t('common.success'));
                loadClients();
            } catch (error) {
                console.error('Failed to assign client:', error);
            }
        });
    } catch (error) {
        console.error('Failed to load available clients:', error);
    }
}

async function unassignClient(clientId) {
    if (!confirm('Are you sure you want to remove this client from your roster?')) return;

    try {
        await apiRequest(`/users/clients/${clientId}/unassign`, { method: 'DELETE' });
        showAlert(t('common.success'));
        loadClients();
    } catch (error) {
        console.error('Failed to unassign client:', error);
    }
}

async function viewClientDetails(clientId) {
    try {
        const client = await apiRequest(`/users/clients/${clientId}`);

        const modal = createModal(client.name, `
            <div class="client-details">
                <h4>${t('profile.title')}</h4>
                <p><strong>${t('auth.email')}:</strong> ${client.email}</p>
                <p><strong>${t('auth.weight')}:</strong> ${client.weight} kg</p>
                <p><strong>${t('auth.height')}:</strong> ${client.height} cm</p>
                <p><strong>BMI:</strong> ${client.bmi?.toFixed(1) || 'N/A'}</p>
            </div>
        `);
    } catch (error) {
        console.error('Failed to load client details:', error);
    }
}

async function showAssignToClientModal(clientId) {
    try {
        const exercises = await apiRequest('/exercises');

        const modal = createModal(t('clients.assign_exercises'), `
            <form id="assign-exercise-form">
                <div class="form-group">
                    <label for="assign-exercise-select" data-i18n="exercises.select_client">${t('exercises.select_client')}</label>
                    <select id="assign-exercise-select" required>
                        <option value="">Select exercise...</option>
                        ${exercises.map(e => `<option value="${e.id}">${e.name}</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label for="assign-notes" data-i18n="exercises.notes">${t('exercises.notes')}</label>
                    <textarea id="assign-notes" placeholder="Instructions for the client"></textarea>
                </div>
                <button type="submit" class="btn btn-primary" data-i18n="exercises.assign">${t('exercises.assign')}</button>
            </form>
        `);

        document.getElementById('assign-exercise-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const assignmentData = {
                exercise_id: document.getElementById('assign-exercise-select').value,
                client_id: clientId,
                notes: document.getElementById('assign-notes').value || null
            };

            try {
                await apiRequest('/exercises/assign', {
                    method: 'POST',
                    body: JSON.stringify(assignmentData)
                });
                closeModal();
                showAlert(t('common.success'));
            } catch (error) {
                console.error('Failed to assign exercise:', error);
            }
        });
    } catch (error) {
        console.error('Failed to load exercises for assignment:', error);
    }
}

async function showAssignExerciseModal(exerciseId) {
    try {
        const clients = await apiRequest('/users/clients');

        const modal = createModal(t('exercises.assign_to_client'), `
            <form id="assign-exercise-form">
                <div class="form-group">
                    <label for="assign-client-select" data-i18n="exercises.select_client">${t('exercises.select_client')}</label>
                    <select id="assign-client-select" required>
                        <option value="">Select client...</option>
                        ${clients.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label for="assign-notes" data-i18n="exercises.notes">${t('exercises.notes')}</label>
                    <textarea id="assign-notes" placeholder="Instructions for the client"></textarea>
                </div>
                <button type="submit" class="btn btn-primary" data-i18n="exercises.assign">${t('exercises.assign')}</button>
            </form>
        `);

        document.getElementById('assign-exercise-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const assignmentData = {
                exercise_id: exerciseId,
                client_id: document.getElementById('assign-client-select').value,
                notes: document.getElementById('assign-notes').value || null
            };

            try {
                await apiRequest('/exercises/assign', {
                    method: 'POST',
                    body: JSON.stringify(assignmentData)
                });
                closeModal();
                showAlert(t('common.success'));
            } catch (error) {
                console.error('Failed to assign exercise:', error);
            }
        });
    } catch (error) {
        console.error('Failed to load clients:', error);
    }
}

async function unassignExercise(assignmentId) {
    if (!confirm('Remove this exercise assignment?')) return;

    try {
        await apiRequest(`/exercises/assign/${assignmentId}`, { method: 'DELETE' });
        showAlert(t('common.success'));
        closeModal();
    } catch (error) {
        console.error('Failed to unassign exercise:', error);
    }
}

// Workout Plans
async function loadPlans() {
    try {
        const plans = await apiRequest('/workout-plans');
        displayPlans(plans);
    } catch (error) {
        console.error('Failed to load plans:', error);
    }
}

function displayPlans(plans) {
    const container = document.getElementById('plans-list');
    const isPersonalTrainer = currentUser.role === 'personal_trainer';

    if (plans.length === 0) {
        const emptyMessage = isPersonalTrainer
            ? `
                <div class="empty-state">
                    <h3>💪 ${t('plans.no_plans')}</h3>
                    <p>${t('plans.no_plans_msg')}</p>
                    <button onclick="showAddPlanModal()" class="btn btn-primary" style="margin-top: 16px;">
                        ${t('plans.create_new')}
                    </button>
                </div>
              `
            : `
                <div class="empty-state">
                    <h3>💪 ${t('plans.no_plans')}</h3>
                    <p>Your personal trainer hasn't created any workout plans for you yet.</p>
                </div>
              `;
        container.innerHTML = emptyMessage;
        return;
    }

    container.innerHTML = plans.map(plan => `
        <div class="plan-card">
            <h3>${plan.name}</h3>
            <p>${plan.description || 'No description'}</p>
            ${plan.is_active ? `<span class="exercise-tag">${t('plans.active')}</span>` : ''}
            <div class="plan-exercises-list">
                <strong>${t('exercises.title')} (${plan.plan_exercises.length})</strong>
                ${plan.plan_exercises.map(pe => `
                    <div class="plan-exercise-item">
                        <span>${pe.exercise?.name || 'Exercise'}</span>
                        <span>${pe.sets}x${pe.reps} @ ${pe.weight || 0}kg</span>
                    </div>
                `).join('')}
            </div>
            <div style="margin-top: 16px; display: flex; gap: 8px;">
                <button onclick="selectPlanForWorkout('${plan.id}')" class="btn btn-primary">Use for Workout</button>
                ${isPersonalTrainer ? `<button onclick="deleteWorkoutPlan('${plan.id}')" class="btn btn-small btn-danger">Delete</button>` : ''}
            </div>
        </div>
    `).join('');
}

async function createWorkoutPlanForClient(clientId) {
    try {
        const exercises = await apiRequest('/exercises');

        if (exercises.length === 0) {
            showAlert('You need to create exercises first before creating a workout plan.', 'error');
            return;
        }

        // Get unique muscle groups for filter
        const muscleGroups = [...new Set(exercises.map(e => e.muscle_group))].sort();

        const modal = createModal('Create Workout Plan', `
            <form id="add-plan-form">
                <div class="form-group">
                    <label for="plan-name">Workout Plan Name</label>
                    <input type="text" id="plan-name" required placeholder="e.g., Upper Body Day A">
                </div>
                <div class="form-group">
                    <label for="plan-description">Description (optional)</label>
                    <textarea id="plan-description" placeholder="Notes about this workout..."></textarea>
                </div>
                <div class="form-group" style="margin-bottom: 20px;">
                    <label style="display: flex; align-items: flex-start; gap: 10px; cursor: pointer;">
                        <input type="checkbox" id="plan-active" checked style="margin-top: 3px; cursor: pointer;">
                        <div>
                            <div style="font-weight: 500; margin-bottom: 4px;">Set as Active Plan</div>
                            <small style="opacity: 0.7; font-size: 12px; line-height: 1.4;">The active plan will be the default for this client's workouts</small>
                        </div>
                    </label>
                </div>
                <div id="exercises-container">
                    <h4>Add Exercises</h4>
                    <div class="form-group">
                        <label for="muscle-group-filter">Filter by Muscle Group</label>
                        <select id="muscle-group-filter">
                            <option value="">All Muscle Groups</option>
                            ${muscleGroups.map(mg => `<option value="${mg}">${t('muscle.' + mg.toLowerCase())}</option>`).join('')}
                        </select>
                    </div>
                    <div id="exercise-list"></div>
                    <button type="button" onclick="addExerciseToWorkout()" class="btn btn-small" style="margin-top: 10px;">+ Add Exercise</button>
                </div>
                <button type="submit" class="btn btn-primary" style="margin-top: 20px;">Create Workout</button>
            </form>
        `);

        // Store clientId and exercises globally for this modal
        window.currentClientId = clientId;
        window.workoutPlanExercises = exercises;

        // Add event listener for muscle group filter
        const muscleGroupFilter = document.getElementById('muscle-group-filter');
        if (muscleGroupFilter) {
            muscleGroupFilter.addEventListener('change', () => {
                updateAllExerciseDropdowns();
            });
        }

        document.getElementById('add-plan-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const exerciseElements = document.querySelectorAll('.workout-exercise-item');
            const exercises = [];

            exerciseElements.forEach((el, index) => {
                const exerciseId = el.querySelector('.exercise-select').value;
                const sets = parseInt(el.querySelector('.exercise-sets').value);
                const reps = parseInt(el.querySelector('.exercise-reps').value);
                const weight = parseFloat(el.querySelector('.exercise-weight').value) || 0;
                const rest = parseInt(el.querySelector('.exercise-rest').value) || 60;

                if (exerciseId && sets && reps) {
                    exercises.push({
                        exercise_id: exerciseId,
                        sets,
                        reps,
                        weight,
                        rest_time: rest,
                        order: index
                    });
                }
            });

            if (exercises.length === 0) {
                showAlert('Please add at least one exercise to the workout plan.', 'error');
                return;
            }

            const planData = {
                name: document.getElementById('plan-name').value,
                description: document.getElementById('plan-description').value,
                is_active: document.getElementById('plan-active').checked,
                client_id: window.currentClientId, // Assign to the selected client
                exercises
            };

            try {
                await apiRequest('/workout-plans', {
                    method: 'POST',
                    body: JSON.stringify(planData)
                });
                closeModal();
                showAlert('Workout plan created successfully for your client!');
                loadPlans();
                loadClients();
            } catch (error) {
                console.error('Failed to create plan:', error);
                showAlert(error.message || 'Failed to create workout plan', 'error');
            }
        });

        // Add first exercise row
        addExerciseToWorkout();
    } catch (error) {
        console.error('Failed to load exercises:', error);
    }
}

function addExerciseToWorkout() {
    const container = document.getElementById('exercise-list');
    const muscleGroupFilter = document.getElementById('muscle-group-filter');
    const selectedMuscleGroup = muscleGroupFilter ? muscleGroupFilter.value : '';

    // Use globally stored exercises
    let exercises = window.workoutPlanExercises || [];

    // Filter by muscle group if selected
    if (selectedMuscleGroup) {
        exercises = exercises.filter(e => e.muscle_group === selectedMuscleGroup);
    }

    // Sort alphabetically by name
    exercises = exercises.sort((a, b) => a.name.localeCompare(b.name));

    const exerciseHtml = `
        <div class="workout-exercise-item" style="padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px; margin-bottom: 10px;">
            <div class="form-group">
                <label>Exercise</label>
                <select class="exercise-select" required>
                    <option value="">Select exercise...</option>
                    ${exercises.map(e => `<option value="${e.id}">${e.name}</option>`).join('')}
                </select>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
                <div class="form-group">
                    <label>Sets</label>
                    <input type="text" class="exercise-sets" value="3" placeholder="e.g., 3, Max, 3-4" required>
                </div>
                <div class="form-group">
                    <label>Reps</label>
                    <input type="text" class="exercise-reps" value="10" placeholder="e.g., 10, 10-12, Max" required>
                </div>
                <div class="form-group">
                    <label>Weight (kg)</label>
                    <input type="number" class="exercise-weight" min="0" step="0.5" value="0">
                </div>
                <div class="form-group">
                    <label>Rest</label>
                    <input type="text" class="exercise-rest" value="60" placeholder="e.g., 60, 90s, 5'">
                </div>
            </div>
            <button type="button" onclick="this.parentElement.remove()" class="btn btn-small btn-danger" style="margin-top: 10px;">Remove</button>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', exerciseHtml);
}

function updateAllExerciseDropdowns() {
    const muscleGroupFilter = document.getElementById('muscle-group-filter');
    const selectedMuscleGroup = muscleGroupFilter ? muscleGroupFilter.value : '';

    // Get filtered and sorted exercises
    let exercises = window.workoutPlanExercises || [];
    if (selectedMuscleGroup) {
        exercises = exercises.filter(e => e.muscle_group === selectedMuscleGroup);
    }
    exercises = exercises.sort((a, b) => a.name.localeCompare(b.name));

    // Update all exercise dropdowns
    const exerciseSelects = document.querySelectorAll('.exercise-select');
    exerciseSelects.forEach(select => {
        const currentValue = select.value;

        // Rebuild options
        select.innerHTML = `
            <option value="">Select exercise...</option>
            ${exercises.map(e => `<option value="${e.id}">${e.name}</option>`).join('')}
        `;

        // Restore selection if the exercise is still in the filtered list
        if (currentValue && exercises.some(e => e.id === currentValue)) {
            select.value = currentValue;
        }
    });
}

function showAddPlanModal() {
    showAlert('Please select a client first, then create a workout plan for them from the "My Clients" tab.', 'error');
}

async function selectPlanForWorkout(planId) {
    localStorage.setItem('selectedPlanId', planId);
    showTab('workout');
    showAlert('Plan selected! Start your workout when ready.');
}

async function startWorkoutWithPlan(planId) {
    localStorage.setItem('selectedPlanId', planId);

    try {
        const sessionData = {
            workout_plan_id: planId,
            notes: null
        };

        activeWorkoutSession = await apiRequest('/workout-sessions', {
            method: 'POST',
            body: JSON.stringify(sessionData)
        });

        // Reset completed exercises
        completedExercises = [];

        // Load and display the plan exercises
        await displayActiveWorkoutWithExercises();
        startTimer(new Date(activeWorkoutSession.start_time));
        showAlert('Workout started! Let\'s go! 💪');
    } catch (error) {
        console.error('Failed to start workout:', error);
        showAlert('Failed to start workout. Please try again.', 'error');
    }
}

async function deleteWorkoutPlan(planId) {
    if (!confirm('Are you sure you want to delete this workout plan?')) return;

    try {
        const response = await fetch(`${API_BASE}/workout-plans/${planId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok || response.status === 204) {
            showAlert('Workout plan deleted successfully!');
            loadPlans();
            loadClients(); // Also refresh clients page if PT is viewing it
        } else if (response.status === 404) {
            showAlert('Workout plan not found. It may have already been deleted.', 'error');
            loadPlans(); // Refresh to show current state
            loadClients();
        } else {
            const error = await response.json().catch(() => ({ detail: 'Failed to delete workout plan' }));
            showAlert(error.detail || 'Failed to delete workout plan', 'error');
        }
    } catch (error) {
        console.error('Failed to delete workout plan:', error);
        showAlert('Failed to delete workout plan', 'error');
    }
}

async function viewWorkoutPlanDetails(planId) {
    try {
        const plan = await apiRequest(`/workout-plans/${planId}`);

        const modal = createModal(plan.name, `
            <div style="margin-bottom: 16px;">
                <p><strong>Description:</strong> ${plan.description || 'No description'}</p>
                <p><strong>Status:</strong> ${plan.is_active ? '<span class="exercise-tag">Active</span>' : 'Inactive'}</p>
            </div>
            <div>
                <strong>Exercises (${plan.plan_exercises.length}):</strong>
                <div style="margin-top: 12px;">
                    ${plan.plan_exercises.map((pe, index) => `
                        <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div>
                                    <strong>${index + 1}. ${pe.exercise?.name || 'Exercise'}</strong>
                                    <div style="margin-top: 8px; font-size: 0.9em; opacity: 0.8;">
                                        <div>Sets: ${pe.sets} | Reps: ${pe.reps} | Weight: ${pe.weight || 0} kg</div>
                                        <div>Rest: ${pe.rest_time}s</div>
                                    </div>
                                </div>
                                <span class="muscle-tag">${pe.exercise?.muscle_group ? t('muscle.' + pe.exercise.muscle_group.toLowerCase()) : ''}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div style="margin-top: 20px; display: flex; gap: 8px;">
                <button onclick="closeModal(); editWorkoutPlan('${plan.id}')" class="btn btn-primary">Edit Plan</button>
                <button onclick="closeModal()" class="btn">Close</button>
            </div>
        `);
    } catch (error) {
        console.error('Failed to load workout plan:', error);
        showAlert('Failed to load workout plan details', 'error');
    }
}

async function editWorkoutPlan(planId) {
    try {
        const plan = await apiRequest(`/workout-plans/${planId}`);

        const modal = createModal('Edit Workout Plan', `
            <form id="edit-plan-form">
                <div class="form-group">
                    <label for="edit-plan-name">Workout Plan Name</label>
                    <input type="text" id="edit-plan-name" value="${plan.name}" required>
                </div>
                <div class="form-group">
                    <label for="edit-plan-description">Description</label>
                    <textarea id="edit-plan-description">${plan.description || ''}</textarea>
                </div>
                <div class="form-group">
                    <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
                        <input type="checkbox" id="edit-plan-active" ${plan.is_active ? 'checked' : ''}>
                        <span>Set as Active Plan</span>
                    </label>
                </div>
                <button type="submit" class="btn btn-primary">Update Workout Plan</button>
            </form>
        `);

        document.getElementById('edit-plan-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const updateData = {
                name: document.getElementById('edit-plan-name').value,
                description: document.getElementById('edit-plan-description').value,
                is_active: document.getElementById('edit-plan-active').checked
            };

            try {
                await apiRequest(`/workout-plans/${planId}`, {
                    method: 'PUT',
                    body: JSON.stringify(updateData)
                });
                closeModal();
                showAlert('Workout plan updated successfully!');
                loadClients(); // Refresh the clients list
            } catch (error) {
                console.error('Failed to update workout plan:', error);
                showAlert(error.message || 'Failed to update workout plan', 'error');
            }
        });
    } catch (error) {
        console.error('Failed to load workout plan:', error);
        showAlert('Failed to load workout plan', 'error');
    }
}

// Workout Session
async function loadWorkoutTab() {
    try {
        // Check if there's an active session
        const session = await apiRequest('/workout-sessions/active');

        if (session) {
            activeWorkoutSession = session;
            await displayActiveWorkoutWithExercises();
            startTimer(new Date(session.start_time));
        } else {
            // Try to get the active workout plan
            const plans = await apiRequest('/workout-plans');
            const activePlan = plans.find(p => p.is_active);

            if (activePlan && activePlan.plan_exercises.length > 0) {
                // Show plan exercises ready to start
                await showWorkoutPlanExercises(activePlan, false);
            } else if (plans.length > 0) {
                // Show available plans if no active plan
                showNoWorkout();
                await showAvailableWorkoutPlans();
            } else {
                // No plans at all
                showNoWorkout();
                document.getElementById('no-active-workout').innerHTML = `
                    <div class="empty-state">
                        <p>${t('workout.no_plans_available')}</p>
                        <p style="margin-top: 10px; opacity: 0.8;">${t('workout.pt_will_create')}</p>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Failed to load workout tab:', error);
        showNoWorkout();
    }
}

async function showAvailableWorkoutPlans() {
    try {
        const plans = await apiRequest('/workout-plans');
        const container = document.getElementById('no-active-workout');

        if (plans.length > 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>${t('workout.select_plan')}</h3>
                    <p>${t('workout.choose_plan')}</p>
                    <div style="margin-top: 20px;">
                        ${plans.map(plan => `
                            <div class="plan-card" style="margin-bottom: 15px; text-align: left;">
                                <h4>${plan.name}</h4>
                                <p>${plan.description || ''}</p>
                                <div class="plan-exercises-list">
                                    <strong>${t('exercises.title')} (${plan.plan_exercises.length})</strong>
                                    ${plan.plan_exercises.slice(0, 3).map(pe => `
                                        <div class="plan-exercise-item">
                                            <span>${pe.exercise?.name || ''}</span>
                                            <span>${pe.sets}x${pe.reps}</span>
                                        </div>
                                    `).join('')}
                                    ${plan.plan_exercises.length > 3 ? `<p style="font-size: 12px; opacity: 0.7;">+${plan.plan_exercises.length - 3} ${t('workout.exercises_in_workout')}</p>` : ''}
                                </div>
                                <button onclick="startWorkoutWithPlan('${plan.id}')" class="btn btn-primary" style="margin-top: 10px;">${t('workout.start_workout')}</button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <p>${t('workout.no_plans_available')}</p>
                    <p style="margin-top: 10px; opacity: 0.8;">${t('workout.pt_will_create')}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load workout plans:', error);
    }
}

function showNoWorkout() {
    document.getElementById('no-active-workout').style.display = 'block';
    document.getElementById('active-workout-container').style.display = 'none';
    if (workoutTimer) {
        clearInterval(workoutTimer);
        workoutTimer = null;
    }
}

function showActiveWorkout() {
    document.getElementById('no-active-workout').style.display = 'none';
    document.getElementById('active-workout-container').style.display = 'block';
}

async function showWorkoutPlanExercises(plan, isActive) {
    const container = document.getElementById(isActive ? 'active-workout-container' : 'no-active-workout');

    const exercisesHtml = plan.plan_exercises
        .sort((a, b) => a.order - b.order)
        .map((pe, index) => {
            const exerciseImage = pe.exercise?.image_url ?
                pe.exercise.image_url :
                '/uploads/exercises/default-exercise.png';

            return `
            <div class="workout-exercise-card" data-exercise-id="${pe.exercise_id}" data-plan-exercise-id="${pe.id}">
                <div class="exercise-layout">
                    ${pe.exercise?.image_url ? `
                        <div class="exercise-image-container">
                            <img src="${exerciseImage}"
                                 alt="${pe.exercise?.name || 'Exercise'}"
                                 class="exercise-thumbnail"
                                 onclick="showImageModal('${exerciseImage}', '${pe.exercise?.name || 'Exercise'}')"
                                 onerror="this.style.display='none'">
                        </div>
                    ` : ''}
                    <div class="exercise-content">
                        <div class="exercise-header">
                            <h4>${index + 1}. ${pe.exercise?.name || 'Exercise'}</h4>
                            <span class="muscle-tag">${pe.exercise?.muscle_group ? t('muscle.' + pe.exercise.muscle_group.toLowerCase()) : ''}</span>
                        </div>
                        <div class="exercise-details">
                            <div class="exercise-info">
                                <span><strong>${t('workout.sets')}:</strong> ${pe.sets}</span>
                                <span><strong>${t('workout.reps')}:</strong> ${pe.reps}</span>
                                <span><strong>${t('workout.rest')}:</strong> ${pe.rest_time}</span>
                                <span style="display: flex; align-items: center; gap: 8px;">
                                    <strong>${t('workout.suggested')}:</strong>
                                    ${isActive ? `
                                        <input type="number"
                                               class="suggested-weight-input"
                                               step="0.5"
                                               min="0"
                                               value="${pe.last_weight_used !== null && pe.last_weight_used !== undefined ? pe.last_weight_used : (pe.weight || 0)}"
                                               data-plan-exercise-id="${pe.id}"
                                               onchange="updateSuggestedWeight('${pe.id}', this.value)"
                                               style="width: 70px; padding: 4px 8px;">
                                        <span>kg</span>
                                    ` : `${pe.last_weight_used !== null && pe.last_weight_used !== undefined ? pe.last_weight_used : (pe.weight || 0)} kg`}
                                </span>
                            </div>
                            ${isActive ? `
                                <div class="exercise-input">
                                    <label>${t('workout.weight_used')}:</label>
                                    <input type="number"
                                           class="weight-input"
                                           step="0.5"
                                           min="0"
                                           placeholder="${pe.last_weight_used !== null && pe.last_weight_used !== undefined ? pe.last_weight_used : (pe.weight || 0)}"
                                           data-exercise-index="${index}">
                                    <button class="btn btn-small btn-success" onclick="markExerciseComplete(${index})">
                                        ✓ ${t('workout.complete')}
                                    </button>
                                </div>
                            ` : ''}
                        </div>
                        ${isActive ? `<div class="exercise-status" data-status-index="${index}"></div>` : ''}
                    </div>
                </div>
            </div>
        `;
        }).join('');

    if (isActive) {
        container.innerHTML = `
            <div class="workout-header">
                <div class="workout-info">
                    <h3>${plan.name}</h3>
                    <p>${plan.description || ''}</p>
                </div>
                <div class="workout-timer">
                    <span>Time:</span>
                    <span id="workout-timer" class="timer-display">00:00:00</span>
                </div>
            </div>
            <div class="workout-progress">
                <span id="progress-text">0 / ${plan.plan_exercises.length} exercises completed</span>
                <button id="end-workout-btn" class="btn btn-danger" onclick="endWorkout()">End Workout</button>
            </div>
            <div class="exercises-list">
                ${exercisesHtml}
            </div>
        `;
        showActiveWorkout();
    } else {
        container.innerHTML = `
            <div class="workout-preview">
                <h3>${plan.name}</h3>
                <p>${plan.description || ''}</p>
                <p style="opacity: 0.8; margin: 15px 0;">
                    <strong>${plan.plan_exercises.length} ${t('workout.exercises_in_workout')}</strong>
                </p>
                <button class="btn btn-primary btn-large" onclick="startWorkoutWithPlan('${plan.id}')" style="margin-bottom: 20px;">
                    ${t('workout.start_workout')} 💪
                </button>
                <div class="exercises-preview">
                    ${exercisesHtml}
                </div>
            </div>
        `;
        container.style.display = 'block';
        document.getElementById('active-workout-container').style.display = 'none';
    }
}

async function displayActiveWorkoutWithExercises() {
    try {
        const plan = await apiRequest(`/workout-plans/${activeWorkoutSession.workout_plan_id}`);
        await showWorkoutPlanExercises(plan, true);
    } catch (error) {
        console.error('Failed to load workout plan:', error);
    }
}

let completedExercises = [];

async function updateSuggestedWeight(planExerciseId, newWeight) {
    try {
        // Update the weight in the workout plan
        await apiRequest(`/workout-plans/exercises/${planExerciseId}/weight`, {
            method: 'PATCH',
            body: JSON.stringify({ weight: parseFloat(newWeight) || 0 })
        });
    } catch (error) {
        console.error('Failed to update suggested weight:', error);
        showAlert('Failed to update weight', 'error');
    }
}

function markExerciseComplete(index) {
    const card = document.querySelector(`[data-exercise-index="${index}"]`).closest('.workout-exercise-card');
    const weightInput = card.querySelector('.weight-input');
    const weightUsed = parseFloat(weightInput.value) || 0;
    const statusDiv = card.querySelector(`[data-status-index="${index}"]`);

    if (!completedExercises.find(e => e.index === index)) {
        completedExercises.push({
            index,
            exercise_id: card.dataset.exerciseId,
            weight_used: weightUsed,
            completed_at: new Date()
        });

        statusDiv.innerHTML = `<span class="status-complete">✓ Completed with ${weightUsed} kg</span>`;
        statusDiv.style.color = '#4ade80';
        weightInput.disabled = true;
        card.querySelector('button').disabled = true;
        card.style.opacity = '0.7';

        updateProgress();
        showAlert(`Exercise completed! Weight: ${weightUsed} kg`);
    }
}

function updateProgress() {
    const totalExercises = document.querySelectorAll('.workout-exercise-card').length;
    const completed = completedExercises.length;
    const progressText = document.getElementById('progress-text');

    if (progressText) {
        progressText.textContent = `${completed} / ${totalExercises} exercises completed`;
    }
}

function showImageModal(imageUrl, exerciseName) {
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.innerHTML = `
        <div class="image-modal-overlay" onclick="this.parentElement.remove()">
            <div class="image-modal-content" onclick="event.stopPropagation()">
                <button class="image-modal-close" onclick="this.closest('.image-modal').remove()">×</button>
                <h3>${exerciseName}</h3>
                <img src="${imageUrl}" alt="${exerciseName}">
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function startWorkout() {
    const planId = localStorage.getItem('selectedPlanId');

    try {
        const sessionData = {
            workout_plan_id: planId || null,
            notes: null
        };

        activeWorkoutSession = await apiRequest('/workout-sessions', {
            method: 'POST',
            body: JSON.stringify(sessionData)
        });

        showActiveWorkout();
        startTimer(new Date(activeWorkoutSession.start_time));
        showAlert('Workout started!');
    } catch (error) {
        console.error('Failed to start workout:', error);
    }
}

async function endWorkout() {
    if (!activeWorkoutSession) return;

    const totalExercises = document.querySelectorAll('.workout-exercise-card').length;
    const completed = completedExercises.length;

    if (completed === 0) {
        if (!confirm('You haven\'t logged any exercises. Are you sure you want to end this workout?')) return;
    } else if (completed < totalExercises) {
        if (!confirm(`You've completed ${completed} of ${totalExercises} exercises. End workout anyway?`)) return;
    } else {
        if (!confirm('Great job! End this workout?')) return;
    }

    try {
        // Save all completed exercises
        for (const exercise of completedExercises) {
            const planExercise = document.querySelector(`[data-exercise-id="${exercise.exercise_id}"]`);
            const pe = planExercise.dataset.planExerciseId;

            await apiRequest(`/workout-sessions/${activeWorkoutSession.id}/exercises`, {
                method: 'POST',
                body: JSON.stringify({
                    exercise_id: exercise.exercise_id,
                    sets_completed: parseInt(planExercise.querySelector('.exercise-info span:nth-child(1)').textContent.split(':')[1]) || 3,
                    reps_completed: parseInt(planExercise.querySelector('.exercise-info span:nth-child(2)').textContent.split(':')[1]) || 10,
                    weight_used: exercise.weight_used,
                    notes: null
                })
            });
        }

        // End the session
        await apiRequest(`/workout-sessions/${activeWorkoutSession.id}/end`, {
            method: 'POST'
        });

        if (workoutTimer) {
            clearInterval(workoutTimer);
            workoutTimer = null;
        }

        activeWorkoutSession = null;
        completedExercises = [];
        showAlert(`Workout completed! You finished ${completed} exercises! 🎉`);
        showNoWorkout();
        loadDashboard();
        loadWorkoutTab();
    } catch (error) {
        console.error('Failed to end workout:', error);
        showAlert('Failed to save workout. Please try again.', 'error');
    }
}

function startTimer(startTime) {
    if (workoutTimer) clearInterval(workoutTimer);

    // Parse the start time correctly from ISO string
    const start = new Date(startTime);

    function updateTimer() {
        const now = new Date();
        const diff = Math.floor((now - start) / 1000);

        const hours = Math.floor(diff / 3600).toString().padStart(2, '0');
        const minutes = Math.floor((diff % 3600) / 60).toString().padStart(2, '0');
        const seconds = (diff % 60).toString().padStart(2, '0');

        const timerElement = document.getElementById('workout-timer');
        if (timerElement) {
            timerElement.textContent = `${hours}:${minutes}:${seconds}`;
        }
    }

    updateTimer();
    workoutTimer = setInterval(updateTimer, 1000);
}

async function loadExercisesForLog() {
    try {
        const exercises = await apiRequest('/exercises');
        const select = document.getElementById('log-exercise-select');
        select.innerHTML = '<option value="">Select exercise...</option>' +
            exercises.map(e => `<option value="${e.id}">${e.name}</option>`).join('');
    } catch (error) {
        console.error('Failed to load exercises:', error);
    }
}

async function logExercise() {
    if (!activeWorkoutSession) {
        showAlert(t('workout.no_active_session'), 'error');
        return;
    }

    const exerciseId = document.getElementById('log-exercise-select').value;
    const sets = parseInt(document.getElementById('log-sets').value);
    const reps = parseInt(document.getElementById('log-reps').value);
    const weight = parseFloat(document.getElementById('log-weight').value) || null;
    const rest = parseInt(document.getElementById('log-rest').value) || null;
    const notes = document.getElementById('log-notes').value;

    if (!exerciseId || !sets || !reps) {
        showAlert('Please fill in all required fields', 'error');
        return;
    }

    try {
        const logData = {
            exercise_id: exerciseId,
            sets_completed: sets,
            reps_completed: reps,
            weight_used: weight,
            rest_time_actual: rest,
            notes: notes
        };

        await apiRequest(`/workout-sessions/${activeWorkoutSession.id}/exercises`, {
            method: 'POST',
            body: JSON.stringify(logData)
        });

        // Clear form
        document.getElementById('log-sets').value = '';
        document.getElementById('log-reps').value = '';
        document.getElementById('log-weight').value = '';
        document.getElementById('log-rest').value = '';
        document.getElementById('log-notes').value = '';

        showAlert(t('common.success'));
    } catch (error) {
        console.error('Failed to log exercise:', error);
    }
}

// Cardio
async function loadCardio() {
    try {
        const sessions = await apiRequest('/cardio');
        displayCardio(sessions);
    } catch (error) {
        console.error('Failed to load cardio:', error);
    }
}

function displayCardio(sessions) {
    const container = document.getElementById('cardio-list');

    if (sessions.length === 0) {
        container.innerHTML = '<div class="card"><p style="text-align: center;">No cardio sessions logged yet.</p></div>';
        return;
    }

    container.innerHTML = sessions.map(session => `
        <div class="cardio-card">
            <h3>${session.activity_type}</h3>
            <div class="cardio-detail">
                <span>Duration:</span>
                <strong>${session.duration} minutes</strong>
            </div>
            ${session.distance ? `
                <div class="cardio-detail">
                    <span>Distance:</span>
                    <strong>${session.distance} km</strong>
                </div>
            ` : ''}
            ${session.calories_burned ? `
                <div class="cardio-detail">
                    <span>Calories:</span>
                    <strong>${session.calories_burned} kcal</strong>
                </div>
            ` : ''}
            ${session.location ? `
                <div class="cardio-detail">
                    <span>Location:</span>
                    <strong>${session.location}</strong>
                </div>
            ` : ''}
            <div class="cardio-detail">
                <span>Date:</span>
                <strong>${new Date(session.start_time).toLocaleDateString()}</strong>
            </div>
        </div>
    `).join('');
}

function showAddCardioModal() {
    const modal = createModal('Log Cardio Session', `
        <form id="add-cardio-form">
            <div class="form-group">
                <label for="cardio-activity">Activity Type</label>
                <select id="cardio-activity" required>
                    <option value="Running">Running</option>
                    <option value="Cycling">Cycling</option>
                    <option value="Swimming">Swimming</option>
                    <option value="Walking">Walking</option>
                    <option value="Rowing">Rowing</option>
                    <option value="Elliptical">Elliptical</option>
                </select>
            </div>
            <div class="form-group">
                <label for="cardio-date">Date & Time</label>
                <input type="datetime-local" id="cardio-date" required>
            </div>
            <div class="form-group">
                <label for="cardio-duration">Duration (minutes)</label>
                <input type="number" id="cardio-duration" min="1" required>
            </div>
            <div class="form-group">
                <label for="cardio-distance">Distance (km)</label>
                <input type="number" id="cardio-distance" step="0.01" min="0">
            </div>
            <div class="form-group">
                <label for="cardio-calories">Calories Burned</label>
                <input type="number" id="cardio-calories" min="0">
            </div>
            <div class="form-group">
                <label for="cardio-location">Location</label>
                <input type="text" id="cardio-location" placeholder="e.g., Park, Gym">
            </div>
            <div class="form-group">
                <label for="cardio-notes">Notes</label>
                <textarea id="cardio-notes"></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Log Session</button>
        </form>
    `);

    // Set default date to now
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('cardio-date').value = now.toISOString().slice(0, 16);

    document.getElementById('add-cardio-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const cardioData = {
            activity_type: document.getElementById('cardio-activity').value,
            start_time: document.getElementById('cardio-date').value + ':00',
            duration: parseInt(document.getElementById('cardio-duration').value),
            distance: parseFloat(document.getElementById('cardio-distance').value) || null,
            calories_burned: parseInt(document.getElementById('cardio-calories').value) || null,
            location: document.getElementById('cardio-location').value || null,
            notes: document.getElementById('cardio-notes').value || null
        };

        try {
            await apiRequest('/cardio', {
                method: 'POST',
                body: JSON.stringify(cardioData)
            });
            closeModal();
            showAlert(t('common.success'));
            loadCardio();
        } catch (error) {
            console.error('Failed to log cardio:', error);
        }
    });
}

// Profile
async function loadProfile() {
    try {
        const profile = await apiRequest('/users/profile');
        document.getElementById('profile-email').value = profile.email;
        document.getElementById('profile-username').value = profile.username;
        document.getElementById('profile-name').value = profile.name;
        document.getElementById('profile-weight').value = profile.weight;
        document.getElementById('profile-height').value = profile.height;
        document.getElementById('profile-desired-weight').value = profile.desired_weight || '';
        document.getElementById('profile-phone').value = profile.phone || '';
        document.getElementById('profile-language').value = profile.language || 'en';

        const isPersonalTrainer = currentUser.role === 'personal_trainer';

        // Hide weight/height/desired weight fields for personal trainers
        const weightGroup = document.getElementById('profile-weight').closest('.form-row');
        const desiredWeightGroup = document.getElementById('profile-desired-weight').closest('.form-group');
        if (weightGroup) weightGroup.style.display = isPersonalTrainer ? 'none' : 'flex';
        if (desiredWeightGroup) desiredWeightGroup.style.display = isPersonalTrainer ? 'none' : 'block';

        // Load health metrics only for clients
        const healthMetricsSection = document.querySelector('.health-metrics-section');
        if (healthMetricsSection) {
            healthMetricsSection.style.display = isPersonalTrainer ? 'none' : 'block';
        }

        if (!isPersonalTrainer) {
            await loadHealthMetrics();
        }
    } catch (error) {
        console.error('Failed to load profile:', error);
    }
}

async function updateProfile(e) {
    e.preventDefault();

    const desiredWeight = document.getElementById('profile-desired-weight').value;
    const newLanguage = document.getElementById('profile-language').value;

    const profileData = {
        username: document.getElementById('profile-username').value,
        name: document.getElementById('profile-name').value,
        weight: parseFloat(document.getElementById('profile-weight').value),
        height: parseFloat(document.getElementById('profile-height').value),
        desired_weight: desiredWeight ? parseFloat(desiredWeight) : null,
        phone: document.getElementById('profile-phone').value || null,
        language: newLanguage
    };

    try {
        await apiRequest('/users/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });

        // Update language if changed
        if (newLanguage !== currentUser.language) {
            setLanguage(newLanguage);
            currentUser.language = newLanguage;
        }

        showAlert(t('common.success'));
        loadProfile();
        loadDashboard();
    } catch (error) {
        console.error('Failed to update profile:', error);
    }
}

async function loadHealthMetrics() {
    try {
        const metrics = await apiRequest('/users/health-metrics');
        displayHealthMetrics(metrics);

        // Update dashboard if weight goal is set
        if (metrics.desired_weight) {
            displayWeightGoalOnDashboard(metrics);
        }
    } catch (error) {
        console.error('Failed to load health metrics:', error);
        document.getElementById('health-metrics-container').innerHTML = '<p class="error">Failed to load health metrics</p>';
    }
}

function displayHealthMetrics(metrics) {
    const container = document.getElementById('health-metrics-container');

    const getBMIClass = (status) => {
        switch(status) {
            case 'underweight': return 'status-warning';
            case 'healthy': return 'status-success';
            case 'overweight': return 'status-warning';
            case 'obese': return 'status-danger';
            default: return '';
        }
    };

    const html = `
        <div class="metrics-grid">
            <div class="metric-item">
                <span class="metric-label">${t('health.current_bmi')}</span>
                <span class="metric-value ${getBMIClass(metrics.health_status)}">${metrics.current_bmi}</span>
                <span class="metric-subtitle">${metrics.bmi_category}</span>
            </div>

            <div class="metric-item">
                <span class="metric-label">${t('health.current_weight')}</span>
                <span class="metric-value">${metrics.current_weight} kg</span>
            </div>

            <div class="metric-item">
                <span class="metric-label">${t('health.healthy_range')}</span>
                <span class="metric-value">${metrics.healthy_weight_range.min} - ${metrics.healthy_weight_range.max} kg</span>
            </div>

            ${metrics.desired_weight ? `
                <div class="metric-item">
                    <span class="metric-label">${t('health.desired_weight')}</span>
                    <span class="metric-value">${metrics.desired_weight} kg</span>
                </div>

                <div class="metric-item">
                    <span class="metric-label">${t('health.weight_difference')}</span>
                    <span class="metric-value ${metrics.weight_difference < 0 ? 'status-info' : 'status-success'}">
                        ${metrics.weight_difference > 0 ? '+' : ''}${metrics.weight_difference} kg
                    </span>
                </div>

                <div class="metric-item">
                    <span class="metric-label">${t('health.timeline')}</span>
                    <span class="metric-value">${metrics.estimated_weeks} ${t('health.weeks')}</span>
                    <span class="metric-subtitle">~${metrics.estimated_date}</span>
                </div>

                <div class="metric-item">
                    <span class="metric-label">${t('health.calorie_adjustment')}</span>
                    <span class="metric-value ${metrics.daily_calorie_adjustment < 0 ? 'status-info' : 'status-success'}">
                        ${metrics.daily_calorie_adjustment > 0 ? '+' : ''}${metrics.daily_calorie_adjustment} cal
                    </span>
                    <span class="metric-subtitle">${metrics.daily_calorie_adjustment < 0 ? 'Deficit' : 'Surplus'}</span>
                </div>
            ` : ''}
        </div>

        <div class="recommendation-box">
            <strong>${t('health.recommendation')}:</strong>
            <p>${metrics.recommendation}</p>
        </div>
    `;

    container.innerHTML = html;
}

function displayWeightGoalOnDashboard(metrics) {
    const card = document.getElementById('weight-goal-card');
    const content = document.getElementById('weight-goal-content');

    if (!metrics.desired_weight) {
        card.style.display = 'none';
        return;
    }

    const progressPercent = metrics.weight_difference !== 0
        ? Math.min(100, Math.abs((metrics.current_weight - (metrics.current_weight + metrics.weight_difference)) / Math.abs(metrics.weight_difference) * 100))
        : 100;

    content.innerHTML = `
        <div class="goal-stats">
            <div class="goal-stat">
                <span class="goal-label">Current</span>
                <strong>${metrics.current_weight} kg</strong>
            </div>
            <div class="goal-stat">
                <span class="goal-label">Goal</span>
                <strong>${metrics.desired_weight} kg</strong>
            </div>
            <div class="goal-stat">
                <span class="goal-label">To ${metrics.weight_difference < 0 ? 'Lose' : 'Gain'}</span>
                <strong>${Math.abs(metrics.weight_difference)} kg</strong>
            </div>
            <div class="goal-stat">
                <span class="goal-label">Timeline</span>
                <strong>${metrics.estimated_weeks} weeks</strong>
            </div>
        </div>
        <p style="margin-top: 16px; font-size: 14px;">${metrics.recommendation.substring(0, 150)}...</p>
    `;

    card.style.display = 'block';
}

// Modal Helper
function createModal(title, content) {
    const modalContainer = document.getElementById('modal-container');
    modalContainer.innerHTML = `
        <div class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                ${content}
            </div>
        </div>
    `;
}

function closeModal() {
    document.getElementById('modal-container').innerHTML = '';
}

// Clear login fields when page is restored from bfcache (browser back/forward cache)
window.addEventListener('pageshow', function(event) {
    // If page was restored from bfcache
    if (event.persisted) {
        const emailField = document.getElementById('login-email');
        const passwordField = document.getElementById('login-password');
        if (emailField) emailField.value = '';
        if (passwordField) passwordField.value = '';
    }
});

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize translations
    updatePageTranslations();

    // Auth events
    document.getElementById('login').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        try {
            await login(email, password);
        } finally {
            // Clear password field after login attempt (success or failure)
            document.getElementById('login-password').value = '';
        }
    });

    document.getElementById('register').addEventListener('submit', async (e) => {
        e.preventDefault();
        const role = document.getElementById('register-role').value;
        const isClient = role === 'client';

        // Validate password confirmation
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('register-confirm-password').value;

        if (password !== confirmPassword) {
            showAlert('Passwords do not match', 'error');
            return;
        }

        const userData = {
            name: document.getElementById('register-name').value,
            username: document.getElementById('register-username').value,
            email: document.getElementById('register-email').value,
            password: password,
            confirm_password: confirmPassword,
            role: role,
            language: document.getElementById('register-language').value,
            phone: document.getElementById('register-phone').value || null,
            personal_trainer_id: null // PT will assign clients later
        };

        // Only add client-specific fields for clients
        if (isClient) {
            userData.date_of_birth = document.getElementById('register-dob').value + 'T00:00:00';
            userData.weight = parseFloat(document.getElementById('register-weight').value);
            userData.height = parseFloat(document.getElementById('register-height').value);
        } else {
            // For personal trainers, set default/null values
            userData.date_of_birth = new Date().toISOString(); // Use current date as default
            userData.weight = 70; // Default weight
            userData.height = 170; // Default height
        }

        await register(userData);
    });

    // Show/hide PT ID field and health fields based on role selection
    document.getElementById('register-role').addEventListener('change', (e) => {
        updateRegistrationFields(e.target.value);
    });

    // Initialize registration fields on page load
    function updateRegistrationFields(role) {
        const weightHeightRow = document.getElementById('weight-height-row');
        const dobGroup = document.getElementById('dob-group');
        const dobInput = document.getElementById('register-dob');
        const weightInput = document.getElementById('register-weight');
        const heightInput = document.getElementById('register-height');
        const isClient = role === 'client';

        if (weightHeightRow) weightHeightRow.style.display = isClient ? 'flex' : 'none';
        if (dobGroup) dobGroup.style.display = isClient ? 'block' : 'none';

        // Make fields required only for clients
        if (dobInput) dobInput.required = isClient;
        if (weightInput) weightInput.required = isClient;
        if (heightInput) heightInput.required = isClient;
    }

    // Initialize form fields based on default role (client)
    updateRegistrationFields('client');

    // Update language when changed in registration
    document.getElementById('register-language').addEventListener('change', (e) => {
        setLanguage(e.target.value);
    });

    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterForm();
    });

    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        showLoginForm();
    });

    document.getElementById('logout-btn').addEventListener('click', logout);

    // Tab navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            showTab(btn.dataset.tab);
        });
    });

    // Exercise events
    document.getElementById('add-exercise-btn').addEventListener('click', showAddExerciseModal);
    document.getElementById('exercise-search').addEventListener('input', loadExercises);
    document.getElementById('muscle-filter').addEventListener('change', loadExercises);

    // Plan events
    document.getElementById('add-plan-btn').addEventListener('click', showAddPlanModal);

    // Workout events
    document.getElementById('start-workout-btn').addEventListener('click', startWorkout);
    document.getElementById('end-workout-btn').addEventListener('click', endWorkout);
    document.getElementById('log-exercise-btn').addEventListener('click', logExercise);

    // Cardio events
    document.getElementById('add-cardio-btn').addEventListener('click', showAddCardioModal);

    // Profile events
    document.getElementById('profile-form').addEventListener('submit', updateProfile);

    // Password Management Events
    document.getElementById('forgot-password-link').addEventListener('click', (e) => {
        e.preventDefault();
        openForgotPasswordModal();
    });

    document.getElementById('forgot-password-form').addEventListener('submit', handleForgotPassword);
    document.getElementById('reset-password-form').addEventListener('submit', handleResetPassword);
    document.getElementById('change-password-form').addEventListener('submit', handleChangePassword);

    // Check if there's a reset token in URL
    const urlParams = new URLSearchParams(window.location.search);
    const resetToken = urlParams.get('reset_token');
    if (resetToken) {
        document.getElementById('reset-token').value = resetToken;
        openResetPasswordModal();
    }

    // Check if user is logged in
    if (authToken) {
        loadUser().then(() => showApp()).catch(() => showAuth());
    } else {
        showAuth();
    }
});

// Password Management Functions
function openForgotPasswordModal() {
    document.getElementById('forgot-password-modal').style.display = 'block';
}

function closeForgotPasswordModal() {
    document.getElementById('forgot-password-modal').style.display = 'none';
    document.getElementById('forgot-password-form').reset();
}

function openResetPasswordModal() {
    document.getElementById('reset-password-modal').style.display = 'block';
}

function closeResetPasswordModal() {
    document.getElementById('reset-password-modal').style.display = 'none';
    document.getElementById('reset-password-form').reset();
}

function openChangePasswordModal() {
    document.getElementById('change-password-modal').style.display = 'block';
}

function closeChangePasswordModal() {
    document.getElementById('change-password-modal').style.display = 'none';
    document.getElementById('change-password-form').reset();
}

async function handleForgotPassword(e) {
    e.preventDefault();

    const email = document.getElementById('forgot-email').value;

    try {
        const response = await fetch(`${API_BASE}/auth/forgot-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (response.ok) {
            showAlert(data.message, 'success');
            closeForgotPasswordModal();

            // In development mode, log token to console for debugging
            if (data.reset_token) {
                console.log('🔐 Password Reset Token (DEV MODE):', data.reset_token);
                console.log('📧 In production, this token is sent via email.');
                console.log('🔗 Reset URL:', `${window.location.origin}?reset_token=${data.reset_token}`);
            }
        } else {
            throw new Error(data.detail || 'Failed to request password reset');
        }
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

async function handleResetPassword(e) {
    e.preventDefault();

    const token = document.getElementById('reset-token').value;
    const newPassword = document.getElementById('reset-new-password').value;
    const confirmPassword = document.getElementById('reset-confirm-password').value;

    if (newPassword !== confirmPassword) {
        showAlert('Passwords do not match', 'error');
        return;
    }

    if (newPassword.length < 8) {
        showAlert('Password must be at least 8 characters', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token,
                new_password: newPassword,
                confirm_new_password: confirmPassword
            })
        });

        const data = await response.json();

        if (response.ok) {
            showAlert(data.message || 'Password reset successfully', 'success');
            closeResetPasswordModal();

            // Clear URL params
            window.history.replaceState({}, document.title, window.location.pathname);

            // Switch to login form
            showAuth();
        } else {
            throw new Error(data.detail || 'Failed to reset password');
        }
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

async function handleChangePassword(e) {
    e.preventDefault();

    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmNewPassword = document.getElementById('confirm-new-password').value;

    if (newPassword !== confirmNewPassword) {
        showAlert('Passwords do not match', 'error');
        return;
    }

    if (newPassword.length < 8) {
        showAlert('Password must be at least 8 characters', 'error');
        return;
    }

    if (newPassword === currentPassword) {
        showAlert('New password must be different from current password', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/change-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword,
                confirm_new_password: confirmNewPassword
            })
        });

        const data = await response.json();

        if (response.ok) {
            showAlert(data.message || 'Password changed successfully', 'success');
            closeChangePasswordModal();
        } else {
            throw new Error(data.detail || 'Failed to change password');
        }
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

// Close modals when clicking outside
window.onclick = function(event) {
    const forgotModal = document.getElementById('forgot-password-modal');
    const resetModal = document.getElementById('reset-password-modal');
    const changeModal = document.getElementById('change-password-modal');

    if (event.target === forgotModal) {
        closeForgotPasswordModal();
    }
    if (event.target === resetModal) {
        closeResetPasswordModal();
    }
    if (event.target === changeModal) {
        closeChangePasswordModal();
    }
};

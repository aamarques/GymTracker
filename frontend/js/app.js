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

async function uploadFile(endpoint, formData) {
    const headers = {};
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
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
    showLoginForm();
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
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

    // Show/hide "My Clients" tab
    const clientsTab = document.querySelector('[data-tab="clients"]');
    if (clientsTab) {
        clientsTab.style.display = isPersonalTrainer ? 'block' : 'none';
    }

    // Show/hide "Add Exercise" button
    const addExerciseBtn = document.getElementById('add-exercise-btn');
    if (addExerciseBtn) {
        addExerciseBtn.style.display = isPersonalTrainer ? 'block' : 'none';
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
    updatePageTranslations();
}

function showApp() {
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('app-screen').style.display = 'block';
    updatePageTranslations();
    loadDashboard();
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
        document.getElementById('stat-workouts').textContent = stats.total_workouts;
        document.getElementById('stat-bmi').textContent = stats.current_bmi?.toFixed(1) || '0';
        document.getElementById('stat-streak').textContent = stats.active_streak;
        document.getElementById('stat-cardio').textContent = stats.total_cardio_sessions;

        // Load exercises count for Personal Trainers
        if (currentUser.role === 'personal_trainer') {
            const exercises = await apiRequest('/exercises');
            document.getElementById('stat-exercises').textContent = exercises.length;
        }
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
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
                <span class="exercise-tag">${t('muscle.' + exercise.muscle_group)}</span>
                ${exercise.equipment ? `<span class="exercise-tag">${exercise.equipment}</span>` : ''}
                ${exercise.description ?
                    `<p class="exercise-description collapsed" data-id="${exercise.id}">${exercise.description}</p>
                    <button onclick="toggleDescription('${exercise.id}')" class="btn btn-small" style="margin-top: 8px;">Show More</button>`
                    : ''}
                ${isPersonalTrainer ? `
                    <div style="margin-top: 12px; display: flex; gap: 8px;">
                        <button onclick="showAssignExerciseModal('${exercise.id}')" class="btn btn-small btn-primary" data-i18n="exercises.assign_to_client">${t('exercises.assign_to_client')}</button>
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
                    <option value="chest">${t('muscle.chest')}</option>
                    <option value="back">${t('muscle.back')}</option>
                    <option value="legs">${t('muscle.legs')}</option>
                    <option value="shoulders">${t('muscle.shoulders')}</option>
                    <option value="biceps">${t('muscle.biceps')}</option>
                    <option value="triceps">${t('muscle.triceps')}</option>
                    <option value="abs">${t('muscle.abs')}</option>
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
        const clients = await apiRequest('/users/clients');
        displayClients(clients);
    } catch (error) {
        console.error('Failed to load clients:', error);
    }
}

function displayClients(clients) {
    const container = document.getElementById('clients-list');

    if (clients.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>👥 ${t('clients.no_clients')}</h3>
                <p>${t('clients.no_clients_msg')}</p>
                <div style="margin-top: 20px; padding: 16px; background: rgba(255,255,255,0.05); border-radius: 8px; text-align: left;">
                    <p style="font-weight: 600; margin-bottom: 8px;">How clients can register with you:</p>
                    <ol style="margin: 0; padding-left: 20px; font-size: 14px;">
                        <li>Share your Trainer ID: <code style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px;">${currentUser.id}</code></li>
                        <li>Have them enter it during registration</li>
                        <li>They'll appear here automatically!</li>
                    </ol>
                </div>
            </div>
        `;
        return;
    }

    container.innerHTML = clients.map(client => `
        <div class="client-card">
            <h3>${client.name}</h3>
            <p><strong>${t('clients.email')}:</strong> ${client.email}</p>
            <p><strong>${t('clients.joined')}:</strong> ${new Date(client.created_at).toLocaleDateString()}</p>
            <p><strong>BMI:</strong> ${client.bmi?.toFixed(1) || 'N/A'}</p>
            <div style="margin-top: 12px; display: flex; gap: 8px;">
                <button onclick="viewClientDetails('${client.id}')" class="btn btn-small btn-primary">${t('clients.view_details')}</button>
                <button onclick="showAssignToClientModal('${client.id}')" class="btn btn-small">${t('clients.assign_exercises')}</button>
            </div>
        </div>
    `).join('');
}

async function viewClientDetails(clientId) {
    try {
        const client = await apiRequest(`/users/clients/${clientId}`);
        const assignedExercises = await apiRequest(`/exercises/assigned/${clientId}`);

        const modal = createModal(client.name, `
            <div class="client-details">
                <h4>${t('profile.title')}</h4>
                <p><strong>${t('auth.email')}:</strong> ${client.email}</p>
                <p><strong>${t('auth.weight')}:</strong> ${client.weight} kg</p>
                <p><strong>${t('auth.height')}:</strong> ${client.height} cm</p>
                <p><strong>BMI:</strong> ${client.bmi?.toFixed(1) || 'N/A'}</p>

                <h4 style="margin-top: 20px;">${t('clients.assigned_exercises')} (${assignedExercises.length})</h4>
                <div class="assigned-exercises-list">
                    ${assignedExercises.length === 0 ?
                        '<p>No exercises assigned yet</p>' :
                        assignedExercises.map(ae => `
                            <div class="assigned-exercise-item">
                                <strong>${ae.exercise.name}</strong>
                                <span>${t('muscle.' + ae.exercise.muscle_group)}</span>
                                ${ae.notes ? `<p style="font-size: 12px; color: #888;">${ae.notes}</p>` : ''}
                                <button onclick="unassignExercise('${ae.id}')" class="btn btn-small btn-danger" style="margin-top: 4px;">Remove</button>
                            </div>
                        `).join('')
                    }
                </div>
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

    if (plans.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>💪 ${t('plans.no_plans')}</h3>
                <p>${t('plans.no_plans_msg')}</p>
                <button onclick="showAddPlanModal()" class="btn btn-primary" style="margin-top: 16px;">
                    ${t('plans.create_new')}
                </button>
            </div>
        `;
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
            <button onclick="selectPlanForWorkout('${plan.id}')" class="btn btn-primary" style="margin-top: 16px;">Use for Workout</button>
        </div>
    `).join('');
}

function showAddPlanModal() {
    const modal = createModal(t('plans.create_new'), `
        <form id="add-plan-form">
            <div class="form-group">
                <label for="plan-name" data-i18n="plans.name">${t('plans.name')}</label>
                <input type="text" id="plan-name" required>
            </div>
            <div class="form-group">
                <label for="plan-description" data-i18n="plans.description">${t('plans.description')}</label>
                <textarea id="plan-description"></textarea>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="plan-active">
                    <span data-i18n="plans.active">${t('plans.active')}</span>
                </label>
            </div>
            <button type="submit" class="btn btn-primary" data-i18n="plans.save">${t('plans.save')}</button>
        </form>
    `);

    document.getElementById('add-plan-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const planData = {
            name: document.getElementById('plan-name').value,
            description: document.getElementById('plan-description').value,
            is_active: document.getElementById('plan-active').checked,
            exercises: []
        };

        try {
            await apiRequest('/workout-plans', {
                method: 'POST',
                body: JSON.stringify(planData)
            });
            closeModal();
            showAlert(t('common.success'));
            loadPlans();
        } catch (error) {
            console.error('Failed to create plan:', error);
        }
    });
}

async function selectPlanForWorkout(planId) {
    localStorage.setItem('selectedPlanId', planId);
    showTab('workout');
    showAlert('Plan selected! Start your workout when ready.');
}

// Workout Session
async function loadWorkoutTab() {
    try {
        const session = await apiRequest('/workout-sessions/active');

        if (session) {
            activeWorkoutSession = session;
            showActiveWorkout();
            startTimer(new Date(session.start_time));
        } else {
            showNoWorkout();
        }
    } catch (error) {
        showNoWorkout();
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
    loadExercisesForLog();
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

    if (!confirm('Are you sure you want to end this workout?')) return;

    try {
        await apiRequest(`/workout-sessions/${activeWorkoutSession.id}/end`, {
            method: 'POST'
        });

        if (workoutTimer) {
            clearInterval(workoutTimer);
            workoutTimer = null;
        }

        activeWorkoutSession = null;
        showAlert('Workout completed!');
        showNoWorkout();
        loadDashboard();
    } catch (error) {
        console.error('Failed to end workout:', error);
    }
}

function startTimer(startTime) {
    if (workoutTimer) clearInterval(workoutTimer);

    function updateTimer() {
        const now = new Date();
        const diff = Math.floor((now - startTime) / 1000);

        const hours = Math.floor(diff / 3600).toString().padStart(2, '0');
        const minutes = Math.floor((diff % 3600) / 60).toString().padStart(2, '0');
        const seconds = (diff % 60).toString().padStart(2, '0');

        document.getElementById('workout-timer').textContent = `${hours}:${minutes}:${seconds}`;
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
        showAlert('No active workout session', 'error');
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
                <label for="cardio-duration">Duration (minutes)</label>
                <input type="number" id="cardio-duration" min="1" required>
            </div>
            <div class="form-group">
                <label for="cardio-distance">Distance (km)</label>
                <input type="number" id="cardio-distance" step="0.1">
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

    document.getElementById('add-cardio-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const cardioData = {
            activity_type: document.getElementById('cardio-activity').value,
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
        document.getElementById('profile-name').value = profile.name;
        document.getElementById('profile-weight').value = profile.weight;
        document.getElementById('profile-height').value = profile.height;
        document.getElementById('profile-desired-weight').value = profile.desired_weight || '';
        document.getElementById('profile-phone').value = profile.phone || '';
        document.getElementById('profile-language').value = profile.language || 'en';

        // Load health metrics
        await loadHealthMetrics();
    } catch (error) {
        console.error('Failed to load profile:', error);
    }
}

async function updateProfile(e) {
    e.preventDefault();

    const desiredWeight = document.getElementById('profile-desired-weight').value;
    const newLanguage = document.getElementById('profile-language').value;

    const profileData = {
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

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize translations
    updatePageTranslations();

    // Auth events
    document.getElementById('login').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        await login(email, password);
    });

    document.getElementById('register').addEventListener('submit', async (e) => {
        e.preventDefault();
        const role = document.getElementById('register-role').value;
        const ptId = document.getElementById('register-pt-id').value;

        const userData = {
            name: document.getElementById('register-name').value,
            email: document.getElementById('register-email').value,
            password: document.getElementById('register-password').value,
            role: role,
            language: document.getElementById('register-language').value,
            personal_trainer_id: (role === 'client' && ptId) ? ptId : null,
            date_of_birth: document.getElementById('register-dob').value + 'T00:00:00',
            weight: parseFloat(document.getElementById('register-weight').value),
            height: parseFloat(document.getElementById('register-height').value),
            phone: document.getElementById('register-phone').value || null
        };
        await register(userData);
    });

    // Show/hide PT ID field based on role selection
    document.getElementById('register-role').addEventListener('change', (e) => {
        const ptIdGroup = document.getElementById('pt-id-group');
        ptIdGroup.style.display = e.target.value === 'client' ? 'block' : 'none';
    });

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

    // Check if user is logged in
    if (authToken) {
        loadUser().then(() => showApp()).catch(() => showAuth());
    } else {
        showAuth();
    }
});

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
    showAlert('Login successful!');
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
}

// UI State Management
function showAuth() {
    document.getElementById('auth-screen').style.display = 'flex';
    document.getElementById('app-screen').style.display = 'none';
}

function showApp() {
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('app-screen').style.display = 'block';
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
    else if (tabName === 'profile') loadProfile();
}

function showLoginForm() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
}

function showRegisterForm() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
}

// Dashboard
async function loadDashboard() {
    try {
        const stats = await apiRequest('/users/dashboard');
        document.getElementById('stat-workouts').textContent = stats.total_workouts;
        document.getElementById('stat-bmi').textContent = stats.current_bmi?.toFixed(1) || '0';
        document.getElementById('stat-streak').textContent = `${stats.active_streak} days`;
        document.getElementById('stat-cardio').textContent = stats.total_cardio_sessions;
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

    if (exercises.length === 0) {
        container.innerHTML = '<p style="color: white; text-align: center;">No exercises found.</p>';
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
                <span class="exercise-tag">${exercise.muscle_group}</span>
                ${exercise.equipment ? `<span class="exercise-tag">${exercise.equipment}</span>` : ''}
                ${exercise.description ?
                    `<p class="exercise-description collapsed" data-id="${exercise.id}">${exercise.description}</p>
                    <button onclick="toggleDescription('${exercise.id}')" class="btn btn-small" style="margin-top: 8px;">Show More</button>`
                    : ''}
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
    const modal = createModal('Add Exercise', `
        <form id="add-exercise-form">
            <div class="form-group">
                <label for="exercise-name">Name</label>
                <input type="text" id="exercise-name" required>
            </div>
            <div class="form-group">
                <label for="exercise-muscle">Muscle Group</label>
                <select id="exercise-muscle" required>
                    <option value="chest">Chest</option>
                    <option value="back">Back</option>
                    <option value="legs">Legs</option>
                    <option value="shoulders">Shoulders</option>
                    <option value="arms">Arms</option>
                    <option value="core">Core</option>
                </select>
            </div>
            <div class="form-group">
                <label for="exercise-equipment">Equipment</label>
                <input type="text" id="exercise-equipment" placeholder="e.g., Barbell, Dumbbells">
            </div>
            <div class="form-group">
                <label for="exercise-description">Description</label>
                <textarea id="exercise-description"></textarea>
            </div>
            <div class="form-group">
                <label for="exercise-image">Image (PNG, JPG, GIF)</label>
                <input type="file" id="exercise-image" accept=".png,.jpg,.jpeg,.gif">
            </div>
            <button type="submit" class="btn btn-primary">Add Exercise</button>
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
            showAlert('Exercise added successfully!');
            loadExercises();
        } catch (error) {
            console.error('Failed to add exercise:', error);
        }
    });
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
        container.innerHTML = '<div class="card"><p style="text-align: center;">No workout plans yet. Create your first plan!</p></div>';
        return;
    }

    container.innerHTML = plans.map(plan => `
        <div class="plan-card">
            <h3>${plan.name}</h3>
            <p>${plan.description || 'No description'}</p>
            ${plan.is_active ? '<span class="exercise-tag">Active</span>' : ''}
            <div class="plan-exercises-list">
                <strong>Exercises (${plan.plan_exercises.length})</strong>
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
    const modal = createModal('Create Workout Plan', `
        <form id="add-plan-form">
            <div class="form-group">
                <label for="plan-name">Plan Name</label>
                <input type="text" id="plan-name" required>
            </div>
            <div class="form-group">
                <label for="plan-description">Description</label>
                <textarea id="plan-description"></textarea>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="plan-active"> Set as active plan
                </label>
            </div>
            <button type="submit" class="btn btn-primary">Create Plan</button>
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
            showAlert('Plan created successfully!');
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

        showAlert('Exercise logged!');
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
            showAlert('Cardio session logged!');
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

        // Load health metrics
        await loadHealthMetrics();
    } catch (error) {
        console.error('Failed to load profile:', error);
    }
}

async function updateProfile(e) {
    e.preventDefault();

    const desiredWeight = document.getElementById('profile-desired-weight').value;
    const profileData = {
        name: document.getElementById('profile-name').value,
        weight: parseFloat(document.getElementById('profile-weight').value),
        height: parseFloat(document.getElementById('profile-height').value),
        desired_weight: desiredWeight ? parseFloat(desiredWeight) : null,
        phone: document.getElementById('profile-phone').value || null
    };

    try {
        await apiRequest('/users/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
        showAlert('Profile updated successfully!');
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
                <span class="metric-label">Current BMI</span>
                <span class="metric-value ${getBMIClass(metrics.health_status)}">${metrics.current_bmi}</span>
                <span class="metric-subtitle">${metrics.bmi_category}</span>
            </div>

            <div class="metric-item">
                <span class="metric-label">Current Weight</span>
                <span class="metric-value">${metrics.current_weight} kg</span>
            </div>

            <div class="metric-item">
                <span class="metric-label">Healthy Range</span>
                <span class="metric-value">${metrics.healthy_weight_range.min} - ${metrics.healthy_weight_range.max} kg</span>
            </div>

            ${metrics.desired_weight ? `
                <div class="metric-item">
                    <span class="metric-label">Goal Weight</span>
                    <span class="metric-value">${metrics.desired_weight} kg</span>
                </div>

                <div class="metric-item">
                    <span class="metric-label">To Lose/Gain</span>
                    <span class="metric-value ${metrics.weight_difference < 0 ? 'status-info' : 'status-success'}">
                        ${metrics.weight_difference > 0 ? '+' : ''}${metrics.weight_difference} kg
                    </span>
                </div>

                <div class="metric-item">
                    <span class="metric-label">Estimated Timeline</span>
                    <span class="metric-value">${metrics.estimated_weeks} weeks</span>
                    <span class="metric-subtitle">~${metrics.estimated_date}</span>
                </div>

                <div class="metric-item">
                    <span class="metric-label">Daily Calories</span>
                    <span class="metric-value ${metrics.daily_calorie_adjustment < 0 ? 'status-info' : 'status-success'}">
                        ${metrics.daily_calorie_adjustment > 0 ? '+' : ''}${metrics.daily_calorie_adjustment} cal
                    </span>
                    <span class="metric-subtitle">${metrics.daily_calorie_adjustment < 0 ? 'Deficit' : 'Surplus'}</span>
                </div>
            ` : ''}
        </div>

        <div class="recommendation-box">
            <strong>Recommendation:</strong>
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
    // Auth events
    document.getElementById('login').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        await login(email, password);
    });

    document.getElementById('register').addEventListener('submit', async (e) => {
        e.preventDefault();
        const userData = {
            name: document.getElementById('register-name').value,
            email: document.getElementById('register-email').value,
            password: document.getElementById('register-password').value,
            date_of_birth: document.getElementById('register-dob').value + 'T00:00:00',
            weight: parseFloat(document.getElementById('register-weight').value),
            height: parseFloat(document.getElementById('register-height').value),
            phone: document.getElementById('register-phone').value || null
        };
        await register(userData);
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

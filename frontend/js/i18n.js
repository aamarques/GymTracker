/**
 * Internationalization (i18n) System
 * Supports English (en) and Portuguese (pt)
 */

const translations = {
    en: {
        // Navigation
        'nav.dashboard': 'Dashboard',
        'nav.exercises': 'Exercises',
        'nav.workouts': 'Workouts',
        'nav.active_workout': 'Active Workout',
        'nav.cardio': 'Cardio',
        'nav.profile': 'Profile',
        'nav.clients': 'My Clients',
        'nav.logout': 'Logout',

        // Auth
        'auth.login': 'Login',
        'auth.register': 'Register',
        'auth.email': 'Email',
        'auth.username': 'Username',
        'auth.password': 'Password',
        'auth.name': 'Full Name',
        'auth.full_name': 'Full Name',
        'auth.role': 'Account Type',
        'auth.role.personal_trainer': 'Personal Trainer',
        'auth.role.client': 'Client',
        'auth.language': 'Language',
        'auth.date_of_birth': 'Date of Birth',
        'auth.weight': 'Weight (kg)',
        'auth.height': 'Height (cm)',
        'auth.phone': 'Phone (optional)',
        'auth.personal_trainer_id': 'Personal Trainer ID (optional)',
        'auth.already_have_account': 'Already have an account?',
        'auth.dont_have_account': "Don't have an account?",
        'auth.sign_in_here': 'Sign in here',
        'auth.register_here': 'Register here',

        // Dashboard
        'dashboard.title': 'Dashboard',
        'dashboard.welcome': 'Welcome',
        'dashboard.total_workouts': 'Total Workouts',
        'dashboard.cardio_sessions': 'Cardio Sessions',
        'dashboard.current_bmi': 'Current BMI',
        'dashboard.active_streak': 'Active Streak',
        'dashboard.days': 'days',
        'dashboard.total_exercises': 'Total Exercises',

        // Exercises
        'exercises.title': 'Exercise Library',
        'exercises.add_new': 'Add New Exercise',
        'exercises.search': 'Search exercises...',
        'exercises.filter': 'Filter by muscle group',
        'exercises.all': 'All',
        'exercises.name': 'Exercise Name',
        'exercises.muscle_group': 'Muscle Group',
        'exercises.equipment': 'Equipment (optional)',
        'exercises.description': 'Description (optional)',
        'exercises.image': 'Image (optional)',
        'exercises.create': 'Create Exercise',
        'exercises.update': 'Update Exercise',
        'exercises.delete': 'Delete',
        'exercises.edit': 'Edit',
        'exercises.assign_to_client': 'Assign to Client',
        'exercises.select_client': 'Select Client',
        'exercises.notes': 'Notes for client (optional)',
        'exercises.assign': 'Assign',
        'exercises.no_exercises': 'No exercises available',
        'exercises.no_exercises_pt': 'No exercises assigned to you yet. Your personal trainer will assign exercises for your workout plan.',
        'exercises.no_exercises_client': 'No exercises available. Your personal trainer will assign exercises to you.',

        // Muscle Groups
        'muscle.chest': 'Chest',
        'muscle.back': 'Back',
        'muscle.shoulders': 'Shoulders',
        'muscle.biceps': 'Biceps',
        'muscle.triceps': 'Triceps',
        'muscle.legs': 'Legs',
        'muscle.abs': 'Abs',
        'muscle.cardio': 'Cardio',

        // Workout Plans
        'plans.title': 'Workout Plans',
        'plans.create_new': 'Create New Plan',
        'plans.name': 'Plan Name',
        'plans.description': 'Description (optional)',
        'plans.active': 'Set as Active',
        'plans.add_exercise': 'Add Exercise',
        'plans.sets': 'Sets',
        'plans.reps': 'Reps',
        'plans.rest_time': 'Rest (seconds)',
        'plans.weight': 'Weight (kg)',
        'plans.remove': 'Remove',
        'plans.save': 'Save Plan',
        'plans.no_plans': 'No workout plans yet',
        'plans.no_plans_msg': 'Create your first workout plan to get started with your training!',

        // Active Workout
        'workout.sets': 'Sets',
        'workout.reps': 'Reps',
        'workout.rest': 'Rest',
        'workout.suggested': 'Suggested',
        'workout.weight_used': 'Weight Used (kg)',
        'workout.complete': 'Complete',
        'workout.start_workout': 'Start Workout',
        'workout.exercises_in_workout': 'exercises in this workout',
        'workout.end_workout': 'End Workout',
        'workout.exercise_completed': 'Exercise completed',
        'workout.no_active_session': 'No active workout session',
        'workout.no_plans_available': 'No workout plans available yet.',
        'workout.pt_will_create': 'Your personal trainer will create workout plans for you.',
        'workout.select_plan': 'Select a Workout Plan',
        'workout.choose_plan': 'Choose a workout plan to start your training session:',
        'workout.start_session': 'Start Session',

        // Profile
        'profile.title': 'Profile',
        'profile.update': 'Update Profile',
        'profile.desired_weight': 'Desired Weight (kg) - Optional',
        'profile.health_metrics': 'Health Metrics Analysis',

        // Health Metrics
        'health.current_weight': 'Current Weight',
        'health.desired_weight': 'Desired Weight',
        'health.weight_difference': 'Weight to Change',
        'health.current_bmi': 'Current BMI',
        'health.bmi_category': 'Category',
        'health.target_bmi': 'Target BMI',
        'health.healthy_range': 'Healthy Weight Range',
        'health.timeline': 'Estimated Timeline',
        'health.weeks': 'weeks',
        'health.target_date': 'Target Date',
        'health.weekly_change': 'Weekly Change Needed',
        'health.calorie_adjustment': 'Daily Calorie Adjustment',
        'health.recommendation': 'Recommendation',

        // Clients (Personal Trainer)
        'clients.title': 'My Clients',
        'clients.name': 'Client Name',
        'clients.email': 'Email',
        'clients.joined': 'Joined',
        'clients.view_details': 'View Details',
        'clients.assign_exercises': 'Assign Exercises',
        'clients.assigned_exercises': 'Assigned Exercises',
        'clients.no_clients': 'No clients yet',
        'clients.no_clients_msg': 'When clients register with your trainer ID, they will appear here.',
        'clients.add_client': 'Add Client',
        'clients.create_workout': 'Create Workout',
        'clients.remove': 'Remove',
        'clients.your_clients': 'Your Clients',

        // Common
        'common.save': 'Save',
        'common.cancel': 'Cancel',
        'common.delete': 'Delete',
        'common.edit': 'Edit',
        'common.close': 'Close',
        'common.confirm': 'Confirm',
        'common.loading': 'Loading...',
        'common.error': 'Error',
        'common.success': 'Success',
        'common.kg': 'kg',
        'common.cm': 'cm'
    },

    pt: {
        // Navigation
        'nav.dashboard': 'Painel',
        'nav.exercises': 'Exercícios',
        'nav.workouts': 'Treinos',
        'nav.active_workout': 'Treino Ativo',
        'nav.cardio': 'Cardio',
        'nav.profile': 'Perfil',
        'nav.clients': 'Meus Clientes',
        'nav.logout': 'Sair',

        // Auth
        'auth.login': 'Entrar',
        'auth.register': 'Registrar',
        'auth.email': 'Email',
        'auth.username': 'Usuário',
        'auth.password': 'Senha',
        'auth.name': 'Nome Completo',
        'auth.full_name': 'Nome Completo',
        'auth.role': 'Tipo de Conta',
        'auth.role.personal_trainer': 'Personal Trainer',
        'auth.role.client': 'Cliente',
        'auth.language': 'Idioma',
        'auth.date_of_birth': 'Data de Nascimento',
        'auth.weight': 'Peso (kg)',
        'auth.height': 'Altura (cm)',
        'auth.phone': 'Telefone (opcional)',
        'auth.personal_trainer_id': 'ID do Personal Trainer (opcional)',
        'auth.already_have_account': 'Já tem uma conta?',
        'auth.dont_have_account': 'Não tem uma conta?',
        'auth.sign_in_here': 'Entre aqui',
        'auth.register_here': 'Registre-se aqui',

        // Dashboard
        'dashboard.title': 'Painel',
        'dashboard.welcome': 'Bem-vindo',
        'dashboard.total_workouts': 'Total de Treinos',
        'dashboard.cardio_sessions': 'Sessões de Cardio',
        'dashboard.current_bmi': 'IMC Atual',
        'dashboard.active_streak': 'Sequência Ativa',
        'dashboard.days': 'dias',
        'dashboard.total_exercises': 'Total de Exercícios',

        // Exercises
        'exercises.title': 'Biblioteca de Exercícios',
        'exercises.add_new': 'Adicionar Novo Exercício',
        'exercises.search': 'Buscar exercícios...',
        'exercises.filter': 'Filtrar por grupo muscular',
        'exercises.all': 'Todos',
        'exercises.name': 'Nome do Exercício',
        'exercises.muscle_group': 'Grupo Muscular',
        'exercises.equipment': 'Equipamento (opcional)',
        'exercises.description': 'Descrição (opcional)',
        'exercises.image': 'Imagem (opcional)',
        'exercises.create': 'Criar Exercício',
        'exercises.update': 'Atualizar Exercício',
        'exercises.delete': 'Excluir',
        'exercises.edit': 'Editar',
        'exercises.assign_to_client': 'Atribuir ao Cliente',
        'exercises.select_client': 'Selecionar Cliente',
        'exercises.notes': 'Notas para o cliente (opcional)',
        'exercises.assign': 'Atribuir',
        'exercises.no_exercises': 'Nenhum exercício disponível',
        'exercises.no_exercises_pt': 'Nenhum exercício atribuído ainda. Seu personal trainer atribuirá exercícios para seu plano de treino.',
        'exercises.no_exercises_client': 'Nenhum exercício disponível. Seu personal trainer atribuirá exercícios para você.',

        // Muscle Groups
        'muscle.chest': 'Peito',
        'muscle.back': 'Costas',
        'muscle.shoulders': 'Ombros',
        'muscle.biceps': 'Bíceps',
        'muscle.triceps': 'Tríceps',
        'muscle.legs': 'Pernas',
        'muscle.abs': 'Abdômen',
        'muscle.cardio': 'Cardio',

        // Workout Plans
        'plans.title': 'Planos de Treino',
        'plans.create_new': 'Criar Novo Plano',
        'plans.name': 'Nome do Plano',
        'plans.description': 'Descrição (opcional)',
        'plans.active': 'Definir como Ativo',
        'plans.add_exercise': 'Adicionar Exercício',
        'plans.sets': 'Séries',
        'plans.reps': 'Repetições',
        'plans.rest_time': 'Descanso (segundos)',
        'plans.weight': 'Peso (kg)',
        'plans.remove': 'Remover',
        'plans.save': 'Salvar Plano',
        'plans.no_plans': 'Nenhum plano de treino ainda',
        'plans.no_plans_msg': 'Crie seu primeiro plano de treino para começar seu treinamento!',

        // Active Workout
        'workout.sets': 'Séries',
        'workout.reps': 'Repetições',
        'workout.rest': 'Descanso',
        'workout.suggested': 'Sugerido',
        'workout.weight_used': 'Peso Usado (kg)',
        'workout.complete': 'Completar',
        'workout.start_workout': 'Iniciar Treino',
        'workout.exercises_in_workout': 'exercícios neste treino',
        'workout.end_workout': 'Finalizar Treino',
        'workout.exercise_completed': 'Exercício completado',
        'workout.no_active_session': 'Nenhuma sessão de treino ativa',
        'workout.no_plans_available': 'Nenhum plano de treino disponível ainda.',
        'workout.pt_will_create': 'Seu personal trainer criará planos de treino para você.',
        'workout.select_plan': 'Selecione um Plano de Treino',
        'workout.choose_plan': 'Escolha um plano de treino para iniciar sua sessão:',
        'workout.start_session': 'Iniciar Sessão',

        // Profile
        'profile.title': 'Perfil',
        'profile.update': 'Atualizar Perfil',
        'profile.desired_weight': 'Peso Desejado (kg) - Opcional',
        'profile.health_metrics': 'Análise de Métricas de Saúde',

        // Health Metrics
        'health.current_weight': 'Peso Atual',
        'health.desired_weight': 'Peso Desejado',
        'health.weight_difference': 'Peso a Mudar',
        'health.current_bmi': 'IMC Atual',
        'health.bmi_category': 'Categoria',
        'health.target_bmi': 'IMC Alvo',
        'health.healthy_range': 'Faixa de Peso Saudável',
        'health.timeline': 'Cronograma Estimado',
        'health.weeks': 'semanas',
        'health.target_date': 'Data Alvo',
        'health.weekly_change': 'Mudança Semanal Necessária',
        'health.calorie_adjustment': 'Ajuste Calórico Diário',
        'health.recommendation': 'Recomendação',

        // Clients (Personal Trainer)
        'clients.title': 'Meus Clientes',
        'clients.name': 'Nome do Cliente',
        'clients.email': 'Email',
        'clients.joined': 'Entrou em',
        'clients.view_details': 'Ver Detalhes',
        'clients.assign_exercises': 'Atribuir Exercícios',
        'clients.assigned_exercises': 'Exercícios Atribuídos',
        'clients.no_clients': 'Nenhum cliente ainda',
        'clients.no_clients_msg': 'Quando os clientes se registrarem com seu ID de treinador, eles aparecerão aqui.',
        'clients.add_client': 'Adicionar Cliente',
        'clients.create_workout': 'Criar Treino',
        'clients.remove': 'Remover',
        'clients.your_clients': 'Seus Clientes',

        // Common
        'common.save': 'Salvar',
        'common.cancel': 'Cancelar',
        'common.delete': 'Excluir',
        'common.edit': 'Editar',
        'common.close': 'Fechar',
        'common.confirm': 'Confirmar',
        'common.loading': 'Carregando...',
        'common.error': 'Erro',
        'common.success': 'Sucesso',
        'common.kg': 'kg',
        'common.cm': 'cm'
    }
};

// Current language (default: English)
let currentLanguage = localStorage.getItem('language') || 'en';

/**
 * Get translation for a key
 * @param {string} key - Translation key (e.g., 'nav.dashboard')
 * @returns {string} Translated text
 */
function t(key) {
    return translations[currentLanguage][key] || key;
}

/**
 * Set the application language
 * @param {string} lang - Language code ('en' or 'pt')
 */
function setLanguage(lang) {
    if (translations[lang]) {
        currentLanguage = lang;
        localStorage.setItem('language', lang);
        updatePageTranslations();
    }
}

/**
 * Get current language
 * @returns {string} Current language code
 */
function getLanguage() {
    return currentLanguage;
}

/**
 * Update all translations on the current page
 * This function updates all elements with data-i18n attribute
 */
function updatePageTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key);

        // Update text content or placeholder based on element type
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            // Always update placeholder for input/textarea
            element.placeholder = translation;
        } else if (element.tagName === 'OPTION') {
            // Update text content for option elements
            element.textContent = translation;
        } else {
            // Update text content for other elements (labels, buttons, etc.)
            element.textContent = translation;
        }
    });

    // Update page title if it has data-i18n
    const titleElement = document.querySelector('title[data-i18n]');
    if (titleElement) {
        const key = titleElement.getAttribute('data-i18n');
        document.title = t(key);
    }
}

// Export functions
window.t = t;
window.setLanguage = setLanguage;
window.getLanguage = getLanguage;
window.updatePageTranslations = updatePageTranslations;

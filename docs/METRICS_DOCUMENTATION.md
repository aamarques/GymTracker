# Sistema de Métricas para Personal Trainers

## 📊 Visão Geral

O sistema de métricas foi implementado para permitir que Personal Trainers acompanhem o progresso de seus clientes de forma detalhada e permanente. As métricas são mantidas mesmo quando o cliente "zera" sua contagem de treinos.

## 🎯 Funcionalidades Implementadas

### 1. **Rastreamento Automático de Métricas**

As seguintes métricas são rastreadas automaticamente:

#### Métricas de Treino
- **Total de treinos completados**: Número total de sessões de treino finalizadas
- **Total de sessões de cardio**: Número total de sessões de cardio registradas
- **Total de horas de treino**: Soma de todas as horas gastas em treinos
- **Dias únicos de treino**: Número de dias diferentes em que houve atividade
- **Total de séries completadas**: Soma de todas as séries realizadas
- **Total de repetições completadas**: Soma de todas as repetições realizadas
- **Duração média por treino**: Tempo médio de cada sessão de treino

#### Métricas de Peso
- **Peso inicial**: Peso quando o cliente começou (ou foi cadastrado)
- **Peso atual**: Último peso registrado
- **Peso mínimo**: Menor peso já registrado
- **Peso máximo**: Maior peso já registrado
- **Total de mudanças de peso**: Quantas vezes o peso foi atualizado
- **Tempo médio entre mudanças**: Média de dias entre atualizações de peso
- **Histórico completo de peso**: Todas as mudanças de peso com datas

#### Métricas de Consistência
- **Percentual de consistência**: % de dias com atividade desde o início
- **Última atividade**: Data da última sessão de treino ou cardio
- **Dias desde o início**: Tempo como cliente

#### Métricas de Reset
- **Número de vezes que zerou treinos**: Quantas vezes o cliente resetou a contagem
- **Data do último reset**: Quando foi o último reset
- **Treinos antes do último reset**: Quantos treinos havia antes de zerar

---

## 🔧 API Endpoints Disponíveis

### Para Clientes (CLIENT role)

#### 1. **Ver Minhas Métricas**
```http
GET /api/metrics/my-metrics
Authorization: Bearer <token>
```

**Resposta:**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "personal_trainer_id": "uuid",
  "total_workouts_completed": 25,
  "total_cardio_sessions": 10,
  "total_training_hours": 42.5,
  "total_training_days": 30,
  "total_sets_completed": 375,
  "total_reps_completed": 4500,
  "initial_weight": 85.0,
  "current_weight": 80.5,
  "lowest_weight": 79.8,
  "highest_weight": 85.5,
  "total_weight_changes": 8,
  "average_days_between_weight_changes": 7.5,
  "times_workouts_reset": 1,
  "last_reset_date": "2025-01-15T10:30:00Z",
  "workouts_before_last_reset": 15,
  "consistency_percentage": 75.5,
  "average_workout_duration_minutes": 65.2,
  "client_since": "2024-10-01T00:00:00Z",
  "last_activity_date": "2025-01-20T18:00:00Z"
}
```

#### 2. **Ver Meu Progresso Detalhado**
```http
GET /api/metrics/my-progress
Authorization: Bearer <token>
```

**Resposta:**
```json
{
  "total_workouts": 25,
  "total_training_hours": 42.5,
  "total_training_days": 30,
  "consistency_percentage": 75.5,
  "average_workout_duration": 65.2,
  "weight_change_kg": -4.5,
  "weight_change_percentage": -5.3,
  "recent_workout_trend": "improving",
  "recent_workouts_30_days": 12,
  "previous_workouts_30_days": 8,
  "total_sets": 375,
  "total_reps": 4500,
  "times_reset": 1,
  "days_since_start": 112
}
```

#### 3. **Ver Histórico de Peso**
```http
GET /api/metrics/weight-history?limit=50
Authorization: Bearer <token>
```

**Resposta:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "weight": 80.5,
    "previous_weight": 81.2,
    "days_since_last_change": 7,
    "recorded_at": "2025-01-20T10:00:00Z",
    "notes": null
  }
]
```

#### 4. **Zerar Contagem de Treinos**
```http
POST /api/metrics/workouts/reset
Authorization: Bearer <token>
```

**Importante:** Esta ação NÃO deleta os dados. Ela apenas marca que você "zerou" a contagem. Seu Personal Trainer ainda poderá ver todo o histórico.

**Resposta:**
```json
{
  "message": "Workout count reset successfully",
  "workouts_archived": 25,
  "reset_count": 2,
  "metrics_preserved": true
}
```

---

### Para Personal Trainers (PERSONAL_TRAINER role)

#### 1. **Ver Métricas de Todos os Clientes**
```http
GET /api/metrics/clients
Authorization: Bearer <token>
```

**Resposta:** Array com métricas resumidas de todos os clientes.

#### 2. **Ver Métricas Detalhadas de um Cliente**
```http
GET /api/metrics/clients/{client_id}
Authorization: Bearer <token>
```

**Resposta:** Métricas completas + informações do cliente + histórico de peso.

```json
{
  "id": "uuid",
  "client_id": "uuid",
  "client_name": "João Silva",
  "client_email": "joao@email.com",
  "personal_trainer_id": "uuid",
  "total_workouts_completed": 25,
  "total_cardio_sessions": 10,
  "total_training_hours": 42.5,
  "total_training_days": 30,
  // ... todas as outras métricas ...
  "weight_history": [
    {
      "id": "uuid",
      "weight": 80.5,
      "previous_weight": 81.2,
      "days_since_last_change": 7,
      "recorded_at": "2025-01-20T10:00:00Z"
    }
  ]
}
```

#### 3. **Ver Progresso Detalhado de um Cliente**
```http
GET /api/metrics/clients/{client_id}/progress
Authorization: Bearer <token>
```

**Resposta:** Análise completa de progresso com tendências.

#### 4. **Ver Histórico de Peso de um Cliente**
```http
GET /api/metrics/clients/{client_id}/weight-history?limit=50
Authorization: Bearer <token>
```

#### 5. **Dashboard Resumido do PT**
```http
GET /api/metrics/dashboard-summary
Authorization: Bearer <token>
```

**Resposta:**
```json
{
  "total_clients": 15,
  "total_workouts_all_clients": 450,
  "total_training_hours_all_clients": 675.5,
  "average_client_consistency": 68.5,
  "most_active_client": {
    "name": "João Silva",
    "workouts": 45
  },
  "most_consistent_client": {
    "name": "Maria Santos",
    "consistency": 85.5
  }
}
```

---

## 🔄 Rastreamento Automático

As métricas são atualizadas automaticamente nos seguintes eventos:

### 1. **Quando um Treino é Finalizado**
- Endpoint: `POST /api/workout-sessions/{session_id}/end`
- Ou: `PUT /api/workout-sessions/{session_id}` (com end_time)
- **Atualiza:** total de treinos, horas de treino, dias únicos, séries, repetições, consistência

### 2. **Quando uma Sessão de Cardio é Criada**
- Endpoint: `POST /api/cardio`
- **Atualiza:** total de cardio, horas de treino, dias únicos, consistência

### 3. **Quando o Peso é Atualizado**
- Endpoint: `PUT /api/users/profile` (com weight)
- **Atualiza:** peso atual, peso min/max, histórico de peso, tempo entre mudanças

---

## 📈 Métricas Sugeridas Adicionais

O sistema atual já cobre métricas essenciais. Sugestões para futuras expansões:

1. **Métricas de Desempenho por Exercício**
   - Evolução de carga por exercício
   - Recordes pessoais
   - Exercícios mais realizados

2. **Métricas de Objetivo**
   - Progresso em relação ao peso desejado
   - Taxa de alcance de metas
   - Previsão de alcance de objetivo

3. **Métricas de Engajamento**
   - Taxa de presença (treinos planejados vs realizados)
   - Horários preferidos de treino
   - Padrões de atividade semanal

4. **Métricas de Saúde**
   - Evolução de IMC
   - Percentual de gordura (se implementado)
   - Medidas corporais (se implementadas)

5. **Comparações e Rankings**
   - Posição entre clientes do PT
   - Evolução comparada ao mês anterior
   - Estatísticas do grupo

---

## 🧪 Testando o Sistema

### 1. Como Cliente

1. Faça login como cliente
2. Complete alguns treinos
3. Acesse: `GET /api/metrics/my-metrics`
4. Atualize seu peso no perfil
5. Veja o histórico: `GET /api/metrics/weight-history`
6. (Opcional) Zere seus treinos: `POST /api/metrics/workouts/reset`

### 2. Como Personal Trainer

1. Faça login como PT
2. Veja todos os clientes: `GET /api/metrics/clients`
3. Veja detalhes de um cliente: `GET /api/metrics/clients/{client_id}`
4. Acesse o dashboard: `GET /api/metrics/dashboard-summary`

---

## 🗄️ Estrutura do Banco de Dados

### Tabela `client_metrics`
Armazena todas as métricas agregadas de cada cliente.

### Tabela `weight_history`
Registra cada mudança de peso com:
- Peso anterior
- Novo peso
- Dias desde a última mudança
- Data de registro
- Notas opcionais

---

## 🔐 Segurança

- ✅ Clientes só podem ver suas próprias métricas
- ✅ PTs só podem ver métricas de seus clientes
- ✅ Reset de treinos preserva dados para o PT
- ✅ Histórico de peso é privado

---

## 📝 Notas Importantes

1. **Métricas são cumulativas**: Nunca são deletadas, apenas incrementadas
2. **Reset não deleta dados**: Apenas marca que houve um reset
3. **Peso inicial**: É definido no primeiro registro ou no cadastro
4. **Consistência**: Calculada como % de dias com atividade desde o início

---

## 🚀 Próximos Passos

Para uma interface visual completa, você pode:

1. Criar páginas no frontend para exibir gráficos de progresso
2. Implementar dashboards interativos para PTs
3. Adicionar notificações de milestones (ex: "100 treinos completados!")
4. Criar relatórios PDF exportáveis
5. Implementar metas e objetivos rastreáveis

---

## 💡 Exemplos de Uso

### Exemplo 1: Cliente verificando seu progresso
```bash
curl -X GET "http://localhost:8000/api/metrics/my-progress" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Exemplo 2: PT vendo dashboard resumido
```bash
curl -X GET "http://localhost:8000/api/metrics/dashboard-summary" \
  -H "Authorization: Bearer YOUR_PT_TOKEN"
```

### Exemplo 3: Cliente zerando treinos
```bash
curl -X POST "http://localhost:8000/api/metrics/workouts/reset" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📞 Suporte

Para dúvidas ou sugestões de novas métricas, consulte a documentação interativa da API em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

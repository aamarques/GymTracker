# Scripts de Administração - Gym Tracker

Este diretório contém scripts úteis para administração do sistema.

## 📋 Scripts Disponíveis

### 1. **list_users.py** - Listar Usuários
Lista todos os usuários do sistema com informações detalhadas.

**Uso:**
```bash
# Podman
podman exec -it gym_backend python list_users.py

# Docker Compose
docker-compose exec backend python list_users.py
```

**Mostra:**
- Nome, email, username de cada usuário
- Role (Personal Trainer ou Client)
- Idioma preferido
- Para Clients: peso, altura, BMI, trainer
- Para PTs: lista de clientes
- Data de criação
- ID do usuário

---

### 2. **reset_passwords.py** - Resetar Senhas
Reseta a senha de todos os usuários para `password123`.

**Uso:**
```bash
# Podman
podman exec -it gym_backend python reset_passwords.py

# Docker Compose
docker-compose exec backend python reset_passwords.py
```

**Atenção:**
- Pede confirmação antes de executar
- Mostra lista de usuários atualizados
- Útil para ambiente de desenvolvimento/testes

---

### 3. **reset_user_workouts.py** - Resetar Treinos
Reseta a contagem de treinos para um ou mais usuários (preserva métricas para o trainer).

**Uso:**

**Modo Interativo:**
```bash
podman exec -it gym_backend python reset_user_workouts.py
```
Mostra lista de usuários e permite escolher quais resetar.

**Por Email:**
```bash
podman exec -it gym_backend python reset_user_workouts.py --email user@example.com
```

**Por Username:**
```bash
podman exec -it gym_backend python reset_user_workouts.py --username john_doe
```

**Todos os Usuários:**
```bash
podman exec -it gym_backend python reset_user_workouts.py --all
```

**O que faz:**
- Reseta contagem de treinos do cliente
- Preserva métricas para o Personal Trainer ver
- Incrementa contador de resets
- Atualiza data do último reset

---

### 4. **delete_user.py** - Deletar Usuários
Deleta um ou mais usuários do sistema (IRREVERSÍVEL!).

**Uso:**

**Modo Interativo:**
```bash
podman exec -it gym_backend python delete_user.py
```
Mostra lista de usuários e permite escolher quais deletar.

**Por Email:**
```bash
podman exec -it gym_backend python delete_user.py --email user@example.com
```

**Por Username:**
```bash
podman exec -it gym_backend python delete_user.py --username john_doe
```

**Por ID:**
```bash
podman exec -it gym_backend python delete_user.py --id uuid-string
```

**⚠️ ATENÇÃO:**
- Esta ação NÃO pode ser desfeita!
- Deleta TODOS os dados do usuário:
  - Workout plans
  - Workout sessions
  - Exercise logs
  - Cardio sessions
  - Exercícios criados
  - Client metrics
  - Weight history
- Se for um PT, os clientes NÃO são deletados (apenas desassociados)
- Pede confirmação dupla antes de executar

---

## 🔒 Segurança

Estes scripts são para **uso administrativo apenas**.

**Boas Práticas:**
1. Sempre faça backup do banco antes de usar scripts de deleção
2. Use em ambiente de desenvolvimento primeiro
3. Leia as mensagens de confirmação cuidadosamente
4. Scripts pedem confirmação antes de executar ações destrutivas

---

## 💡 Exemplos de Uso

### Cenário 1: Novo ambiente de desenvolvimento
```bash
# 1. Listar usuários existentes
podman exec -it gym_backend python list_users.py

# 2. Resetar todas as senhas para facilitar testes
podman exec -it gym_backend python reset_passwords.py

# Agora todos podem logar com: password123
```

### Cenário 2: Cliente quer começar do zero
```bash
# 1. Ver usuários
podman exec -it gym_backend python list_users.py

# 2. Resetar treinos do cliente específico
podman exec -it gym_backend python reset_user_workouts.py --email cliente@email.com
```

### Cenário 3: Remover usuários de teste
```bash
# 1. Listar usuários
podman exec -it gym_backend python list_users.py

# 2. Deletar usuário específico
podman exec -it gym_backend python delete_user.py --email teste@email.com
```

### Cenário 4: Resetar todos os treinos para demonstração
```bash
# Resetar treinos de todos os clientes
podman exec -it gym_backend python reset_user_workouts.py --all
```

---

## 🐛 Troubleshooting

### Erro: "Module not found"
Certifique-se de estar executando dentro do container:
```bash
podman exec -it gym_backend python script.py
```

### Erro: "Database connection failed"
Verifique se o container PostgreSQL está rodando:
```bash
podman ps | grep postgres
```

### Erro: "Permission denied"
Torne o script executável:
```bash
chmod +x backend/script.py
```

---

## 📝 Notas

- Todos os scripts usam a mesma conexão de banco que a aplicação
- As alterações são permanentes e commitadas imediatamente
- Logs são mostrados em tempo real para acompanhamento
- Scripts são seguros para uso em produção (com cuidado!)

---

## 🔄 Backup Recomendado

Antes de usar scripts de deleção, faça backup:

```bash
# Backup do banco de dados PostgreSQL
podman exec gym_postgres pg_dump -U gymuser gymtracker > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup se necessário
podman exec -i gym_postgres psql -U gymuser gymtracker < backup_20250120_143000.sql
```

# Guia de Administração - Gym Tracker

## 🚀 Acesso Rápido aos Scripts Admin

Todos os scripts de administração estão em `/backend/`.

### Menu Principal (Recomendado)

Execute o menu interativo que dá acesso a todos os scripts:

```bash
# Podman
podman exec -it gym_backend python admin.py

# Docker Compose
docker-compose exec backend python admin.py
```

---

## 📋 Scripts Disponíveis

### 1️⃣ Importar Exercícios
```bash
# Formato Português (Google Sheets com colunas por grupo muscular)
./import-exercises-pt.sh

# Ou especificar arquivo
./import-exercises-pt.sh Imports/exercicios.csv

# Formato Padrão (CSV com colunas: name, muscle_group, equipment, etc.)
./import-exercises.sh exercises_template.csv

# Para usuário específico
./import-exercises-pt.sh Imports/exercicios.csv USER_ID
```
- Importa exercícios de arquivos CSV
- Suporta dois formatos: Português (colunas pareadas) e Padrão
- Mapeia automaticamente grupos musculares PT → EN
- Evita duplicatas
- Veja **[Guia de Importação Completo](IMPORT_EXERCISES_GUIDE.md)** para detalhes

### 2️⃣ Listar Usuários
```bash
podman exec -it gym_backend python list_users.py
```
- Mostra todos os usuários
- Detalhes: email, username, role, clientes (para PTs)
- Útil para ver quem está cadastrado

### 3️⃣ Resetar Senhas
```bash
podman exec -it gym_backend python reset_passwords.py
```
- Define senha `password123` para TODOS os usuários
- Perfeito para ambiente de desenvolvimento

### 4️⃣ Resetar Treinos
```bash
# Modo interativo (escolher da lista)
podman exec -it gym_backend python reset_user_workouts.py

# Por email
podman exec -it gym_backend python reset_user_workouts.py --email user@example.com

# Por username
podman exec -it gym_backend python reset_user_workouts.py --username john_doe

# Todos os usuários
podman exec -it gym_backend python reset_user_workouts.py --all
```
- Zera contagem de treinos do cliente
- Métricas preservadas para o trainer

### 5️⃣ Deletar Usuários
```bash
# Modo interativo (escolher da lista)
podman exec -it gym_backend python delete_user.py

# Por email
podman exec -it gym_backend python delete_user.py --email user@example.com

# Por username
podman exec -it gym_backend python delete_user.py --username john_doe

# Por ID
podman exec -it gym_backend python delete_user.py --id uuid-string
```
- ⚠️ **ATENÇÃO**: Ação irreversível!
- Deleta usuário e TODOS os seus dados
- Pede confirmação dupla

---

## 💡 Exemplos Práticos

### Setup Inicial
```bash
# 1. Importar exercícios para biblioteca
./import-exercises-pt.sh Imports/exercicios.csv

# 2. Ver usuários
podman exec -it gym_backend python list_users.py

# 3. Resetar senhas para dev
podman exec -it gym_backend python reset_passwords.py

# Todos podem logar com password123
```

### Cliente Quer Recomeçar
```bash
# Resetar treinos preservando histórico para o trainer
podman exec -it gym_backend python reset_user_workouts.py --email cliente@email.com
```

### Limpar Usuários de Teste
```bash
# Via menu
podman exec -it gym_backend python admin.py
# Escolher opção 4 (Delete User)
```

---

## 🔒 Backup Antes de Deletar

**Sempre faça backup antes de deletar dados!**

```bash
# Backup
podman exec gym_postgres pg_dump -U gymuser gymtracker > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar se necessário
podman exec -i gym_postgres psql -U gymuser gymtracker < backup_20250120_143000.sql
```

---

## 📚 Documentação Completa

Veja `backend/ADMIN_SCRIPTS.md` para documentação detalhada de cada script.

---

## ⚡ Quick Reference

| Tarefa | Comando Rápido |
|--------|---------------|
| Menu Admin | `podman exec -it gym_backend python admin.py` |
| Importar Exercícios (PT) | `./import-exercises-pt.sh` |
| Importar Exercícios (Padrão) | `./import-exercises.sh exercises.csv` |
| Listar Users | `podman exec -it gym_backend python list_users.py` |
| Reset Senhas | `podman exec -it gym_backend python reset_passwords.py` |
| Reset Treinos | `podman exec -it gym_backend python reset_user_workouts.py` |
| Deletar User | `podman exec -it gym_backend python delete_user.py` |

---

## 🆘 Problemas?

- Scripts não funcionam? Verifique se o container está rodando: `podman ps`
- Erro de permissão? Scripts já estão executáveis
- Erro de módulo? Execute DENTRO do container com `podman exec`

**Suporte**: Ver `backend/ADMIN_SCRIPTS.md` para troubleshooting detalhado

# 🚀 Scripts Admin - Guia Rápido

## ⚡ Uso Simples (Recomendado)

Todos os scripts podem ser executados **diretamente da raiz do projeto**:

### Menu Admin Interativo
```bash
./admin.sh
```

### Scripts Individuais

```bash
# Listar todos os usuários
./list-users.sh

# Resetar todas as senhas para 'password123'
./reset-passwords.sh

# Resetar treinos de usuários
./reset-workouts.sh                    # modo interativo
./reset-workouts.sh --email user@email.com
./reset-workouts.sh --username john
./reset-workouts.sh --all              # todos os usuários

# Deletar usuários
./delete-user.sh                       # modo interativo
./delete-user.sh --email user@email.com
./delete-user.sh --username john
./delete-user.sh --id uuid-string
```

---

## 📋 O Que Cada Script Faz

### `admin.sh`
Menu interativo com todas as opções

### `list-users.sh`
- Lista todos os usuários
- Mostra: nome, email, username, role, clientes
- Útil para ver quem está cadastrado

### `reset-passwords.sh`
- Reseta senha de TODOS para `password123`
- Pede confirmação
- Perfeito para desenvolvimento

### `reset-workouts.sh`
- Zera contagem de treinos
- Métricas preservadas para o Personal Trainer
- Pode escolher usuários específicos ou todos

### `delete-user.sh`
- ⚠️ **IRREVERSÍVEL!**
- Deleta usuário e TODOS os dados
- Pede confirmação dupla
- Clientes não são deletados se você deletar um PT

---

## ✅ Requisitos

- Container `gym_backend` deve estar rodando
- Execute os scripts da **raiz do projeto** (`/home/aamarques/Gym/GymTracker/`)

Se o container não estiver rodando:
```bash
bash start-containers.sh
```

---

## 💡 Exemplos de Uso

### Exemplo 1: Ver usuários e resetar senhas
```bash
./list-users.sh                # ver usuários
./reset-passwords.sh           # resetar todas as senhas
```

### Exemplo 2: Resetar treinos de um cliente
```bash
./list-users.sh                # ver email do cliente
./reset-workouts.sh --email cliente@email.com
```

### Exemplo 3: Deletar usuário de teste
```bash
./delete-user.sh --email teste@email.com
```

---

## 🔄 Alternativa (Modo Antigo)

Se preferir, ainda pode executar dentro do container:

```bash
podman exec -it gym_backend python admin.py
podman exec -it gym_backend python list_users.py
podman exec -it gym_backend python reset_passwords.py
# etc...
```

---

## 🐛 Troubleshooting

### Erro: "gym_backend container is not running"
```bash
bash start-containers.sh
```

### Erro: "Permission denied"
```bash
chmod +x *.sh
```

### Script não encontrado
Certifique-se de estar na raiz do projeto:
```bash
cd /home/aamarques/Gym/GymTracker/
```

---

**Documentação completa:** `ADMIN_GUIDE.md`

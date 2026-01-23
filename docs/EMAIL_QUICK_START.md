# 📧 Setup Rápido - Gmail para Envio de Emails

## ⚡ 3 Passos Rápidos (5 minutos)

### 1️⃣ Gerar App Password do Gmail

1. **Acesse:** https://myaccount.google.com/apppasswords
2. **Ative 2FA** (se ainda não tiver)
3. **Crie App Password** para "GymTracker"
4. **Copie a senha** (exemplo: `abcd efgh ijkl mnop`)

📖 **Precisa de ajuda?** Veja `GMAIL_SETUP.md` para passo a passo detalhado.

---

### 2️⃣ Configurar Credenciais

**Edite o arquivo `.env`:**

```bash
cd /home/aamarques/Gym/GymTracker/backend
nano .env
```

**Altere estas linhas:**
```bash
EMAIL_FROM=seu-email@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
FRONTEND_URL=http://localhost:8080
```

**Exemplo:**
```bash
EMAIL_FROM=alexandre@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
FRONTEND_URL=http://localhost:8080
```

**Salve:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### 3️⃣ Reiniciar Backend

```bash
# Podman
podman restart gym_backend

# Docker Compose
docker-compose restart backend
```

---

## ✅ Testar!

1. Acesse: http://localhost:8080
2. Clique em **"Esqueceu a Senha?"**
3. Digite seu email
4. Clique em **"Enviar Link de Recuperação"**
5. **Verifique seu email!** 📬

---

## 🐛 Não Funcionou?

### Email não chegou?
- ✅ Verifique **SPAM/Lixo eletrônico**
- ✅ Aguarde 1-2 minutos
- ✅ Veja os logs: `podman logs gym_backend | grep email`

### Erro de autenticação?
- ✅ Usou **App Password**, não senha normal?
- ✅ Copiou a senha completa (com espaços)?
- ✅ 2FA está ativado no Gmail?

### Ainda com problemas?
📖 Veja troubleshooting completo em `GMAIL_SETUP.md`

---

## 🎨 Como Fica o Email?

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏋️ GymTracker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Olá [Nome]!

Você solicitou redefinir sua senha.

┌─────────────────────────────┐
│   🔐 Redefinir Senha        │
└─────────────────────────────┘

⏰ Este link expira em 1 hora.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📋 Checklist

- [ ] Gerou App Password no Gmail
- [ ] Editou `.env` com email e senha
- [ ] Reiniciou o backend
- [ ] Testou "Esqueceu a Senha?"
- [ ] Recebeu o email com sucesso

Tudo OK? 🎉 Emails configurados!

---

**Documentação Completa:** `GMAIL_SETUP.md`
**Features de Senha:** `PASSWORD_FEATURES.md`

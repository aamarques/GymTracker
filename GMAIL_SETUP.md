# Como Configurar Gmail para Envio de Emails

## 📧 Passo a Passo - Criar App Password do Gmail

Para o GymTracker enviar emails (redefinição de senha), você precisa gerar uma **App Password** (Senha de App) no Gmail.

⚠️ **IMPORTANTE:** NÃO use sua senha normal do Gmail! Use App Password!

---

## 🔐 Etapa 1: Ativar Verificação em Duas Etapas (2FA)

O Gmail exige 2FA para criar App Passwords.

### Para Ativar:

1. **Acesse:** https://myaccount.google.com/security

2. **Procure** "Verificação em duas etapas" ou "2-Step Verification"

3. **Clique** em "Começar" ou "Get Started"

4. **Siga os passos:**
   - Digite sua senha
   - Escolha método de verificação (SMS, app Google Authenticator, etc.)
   - Confirme o código
   - Ative a verificação

✅ Pronto! 2FA ativado.

---

## 🔑 Etapa 2: Gerar App Password

Agora você pode criar uma senha específica para o GymTracker.

### Passos:

1. **Acesse:** https://myaccount.google.com/apppasswords

   *Ou navegue:*
   - Google Account → Security → 2-Step Verification → App Passwords

2. **Faça login** se solicitado

3. **Selecione App:**
   - Dropdown "Select app" → escolha **"Mail"** ou **"Other (Custom name)"**
   - Se escolher "Other", digite: **"GymTracker"**

4. **Selecione Device:**
   - Dropdown "Select device" → escolha **"Other (Custom name)"**
   - Digite: **"GymTracker Server"** ou **"Docker"**

5. **Clique** em **"Generate"** ou **"Gerar"**

6. **Copie a senha gerada!**
   - Vai aparecer algo como: `abcd efgh ijkl mnop`
   - Copie TUDO (pode copiar com espaços, o código aceita)

⚠️ **IMPORTANTE:** Essa senha aparece **UMA VEZ SÓ**! Guarde bem!

---

## ⚙️ Etapa 3: Configurar no GymTracker

### Opção A: Criar arquivo `.env` (Recomendado)

1. **Navegue** até a pasta do projeto:
```bash
cd /home/aamarques/Gym/GymTracker/backend
```

2. **Crie o arquivo** `.env` (se não existir):
```bash
cp .env.example .env
```

3. **Edite** o arquivo `.env`:
```bash
nano .env
```
ou
```bash
vim .env
```

4. **Altere estas linhas:**
```bash
EMAIL_FROM=seu-email@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
FRONTEND_URL=http://localhost:8080
```

**Exemplo Real:**
```bash
EMAIL_FROM=alexandre.marques@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
FRONTEND_URL=http://localhost:8080
```

5. **Salve** o arquivo
   - nano: `Ctrl+O`, `Enter`, `Ctrl+X`
   - vim: `Esc`, `:wq`, `Enter`

### Opção B: Configurar diretamente no docker-compose.yml

Se preferir, pode adicionar as variáveis no `docker-compose.yml`:

```yaml
backend:
  environment:
    - EMAIL_FROM=seu-email@gmail.com
    - EMAIL_PASSWORD=abcd efgh ijkl mnop
    - FRONTEND_URL=http://localhost:8080
```

---

## 🚀 Etapa 4: Reiniciar o Backend

Para aplicar as configurações:

```bash
# Com Podman
podman restart gym_backend

# Com Docker Compose
docker-compose restart backend
```

---

## ✅ Etapa 5: Testar!

### Teste de Envio de Email:

1. **Acesse** o GymTracker: http://localhost:8080

2. **Clique** em "Esqueceu a Senha?"

3. **Digite** seu email ou username

4. **Clique** em "Enviar Link de Recuperação"

5. **Verifique seu email!** 📬
   - Deve chegar um email do GymTracker
   - Com o link de redefinição de senha

---

## 🐛 Troubleshooting (Problemas Comuns)

### ❌ Erro: "Authentication failed"

**Causa:** App Password incorreta ou 2FA não ativado

**Solução:**
1. Verifique se 2FA está ativado
2. Gere uma nova App Password
3. Copie exatamente como aparece
4. Atualize o `.env`
5. Reinicie o backend

---

### ❌ Erro: "SMTPAuthenticationError"

**Causa:** Senha normal do Gmail ao invés de App Password

**Solução:**
- Use App Password, NÃO sua senha normal!
- Gere uma nova App Password seguindo os passos acima

---

### ❌ Email não chega

**Verificações:**
1. ✅ Cheque a pasta de **SPAM/Lixo eletrônico**
2. ✅ Verifique o email remetente (`EMAIL_FROM`) está correto
3. ✅ Veja os logs do backend:
   ```bash
   podman logs gym_backend | grep -i email
   ```
4. ✅ Teste com outro email (Gmail, Outlook, etc.)

---

### ❌ Erro: "Connection refused" ou "Connection timed out"

**Causa:** Firewall ou porta bloqueada

**Solução:**
1. Verifique se a porta 465 está aberta
2. Teste conexão:
   ```bash
   telnet smtp.gmail.com 465
   ```
3. Se estiver atrás de firewall corporativo, pode estar bloqueado

**Alternativa:** Use porta 587 (TLS):
```bash
SMTP_PORT=587
```

E mude o código em `email_service.py`:
```python
with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
    server.starttls()  # Adicione esta linha
    server.login(...)
```

---

## 📝 Notas Importantes

### Segurança:

1. ✅ **NUNCA** comite o arquivo `.env` no Git!
   - Já está no `.gitignore`
   - Contém senhas sensíveis

2. ✅ **App Password** é específica para este app
   - Não dá acesso completo à sua conta Gmail
   - Pode ser revogada a qualquer momento

3. ✅ Para **revogar** uma App Password:
   - Acesse: https://myaccount.google.com/apppasswords
   - Encontre "GymTracker"
   - Clique em "Revoke" ou "Remover"

### Produção:

- Em produção, use variáveis de ambiente do servidor
- Considere usar serviços dedicados (SendGrid, AWS SES)
- Rotacione as senhas periodicamente

---

## 📚 Links Úteis

- **Gerenciar App Passwords:** https://myaccount.google.com/apppasswords
- **Configurações de Segurança:** https://myaccount.google.com/security
- **Ajuda do Gmail:** https://support.google.com/accounts/answer/185833

---

## 🆘 Precisa de Ajuda?

Se ainda tiver problemas:

1. Verifique os logs do backend:
   ```bash
   podman logs -f gym_backend
   ```

2. Teste manualmente no Python:
   ```bash
   podman exec -it gym_backend python
   ```
   ```python
   from app.services.email_service import send_password_reset_email
   send_password_reset_email("seu-email@gmail.com", "test-token", "Seu Nome")
   ```

3. Verifique o arquivo `.env`:
   ```bash
   podman exec gym_backend cat /app/.env | grep EMAIL
   ```

Boa sorte! 🚀

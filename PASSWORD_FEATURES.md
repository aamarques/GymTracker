# Password Management Features

## ✅ Implemented Features

### 1. **Confirm Password on Registration**
- Users must enter password twice when registering
- Frontend validates passwords match before submitting
- Backend validates with Pydantic schema
- Clear error message if passwords don't match

### 2. **Change Password in Profile**
- New "Security" section in Profile tab
- "Change Password" button opens modal
- Requires current password for security
- New password must be different from current
- Validates password confirmation
- Password must be minimum 8 characters

### 3. **Forgot Password / Password Recovery**
- "Forgot Password?" link on login page
- User enters email or username
- System generates secure reset token (valid for 1 hour)
- Token expires after use or timeout
- In development mode: token shown in console and auto-filled
- In production: token would be sent via email

---

## 🗄️ Database Changes

### New Table: `password_reset_tokens`
```sql
CREATE TABLE password_reset_tokens (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🚀 How to Apply Changes

### Step 1: Run Database Migration

```bash
# Using Podman
podman exec gym_backend python backend/alembic/versions/002_add_password_reset_tokens.py

# Using Docker Compose
docker-compose exec backend python backend/alembic/versions/002_add_password_reset_tokens.py

# Or use Alembic (if configured)
podman exec gym_backend alembic upgrade head
```

### Step 2: Restart Backend Container

```bash
# Using Podman
podman restart gym_backend

# Using Docker Compose
docker-compose restart backend
```

### Step 3: Clear Browser Cache

Clear your browser cache or do a hard refresh (Ctrl+Shift+R / Cmd+Shift+R) to load the updated JavaScript and HTML.

---

## 📋 How to Use the Features

### For Users - Registration

1. Go to registration page
2. Enter username, email, and password
3. **NEW:** Re-enter password in "Confirm Password" field
4. If passwords don't match, you'll see an error
5. Complete registration

### For Users - Change Password

1. Login to your account
2. Go to **Profile** tab
3. Scroll to **Security** section
4. Click **Change Password** button
5. Enter:
   - Current password
   - New password
   - Confirm new password
6. Click **Change Password**
7. Success! You can now login with new password

### For Users - Forgot Password

1. On login page, click **"Forgot Password?"**
2. Enter your email or username
3. Click **Send Reset Link**
4. **Check your email! 📧**
   - Email will arrive from GymTracker
   - Subject: "GymTracker - Redefinir Senha / Reset Password"
   - Click the button or link in the email
5. **Reset Password Page Opens**
   - Token is auto-filled from URL
   - Enter new password twice
6. Click **Reset Password**
7. Login with new password

**Note:** Email link expires in 1 hour!

---

## 🔐 API Endpoints

### Change Password (Authenticated)
```http
POST /api/auth/change-password
Authorization: Bearer <token>

{
  "current_password": "oldpass123",
  "new_password": "newpass123",
  "confirm_new_password": "newpass123"
}
```

### Request Password Reset
```http
POST /api/auth/forgot-password

{
  "email": "user@example.com"  // or username
}
```

**Response (Development Mode):**
```json
{
  "message": "If an account with that email/username exists, a password reset link has been sent.",
  "reset_token": "abc123...xyz"  // Only in development
}
```

### Reset Password with Token
```http
POST /api/auth/reset-password

{
  "token": "abc123...xyz",
  "new_password": "newpass123",
  "confirm_new_password": "newpass123"
}
```

---

## 🛡️ Security Features

### Password Validation
- Minimum 8 characters required
- Password confirmation required
- Backend validates all inputs with Pydantic

### Reset Token Security
- Cryptographically secure random tokens (32 bytes)
- Tokens expire after 1 hour
- Tokens are single-use (marked as used after successful reset)
- Old tokens automatically invalidated when new one requested
- User enumeration prevention (same message for existing/non-existing users)

### Change Password Security
- Requires current password verification
- New password must differ from current password
- All password operations use bcrypt hashing
- Passwords never stored in plain text

---

## 🧪 Testing

### Test 1: Registration Password Confirmation
1. Try to register with non-matching passwords
2. Should see error: "Passwords do not match"
3. Register with matching passwords
4. Should succeed

### Test 2: Change Password
1. Login
2. Go to Profile > Security
3. Try wrong current password → Error
4. Try matching new password = current → Error
5. Use correct inputs → Success
6. Logout and login with new password → Success

### Test 3: Forgot Password
1. Click "Forgot Password?" on login
2. Enter email/username
3. Check console for reset token
4. Modal opens with token pre-filled
5. Enter new password twice
6. Reset → Success
7. Login with new password → Success

### Test 4: Password Reset Token Expiry
```bash
# Manually test by setting token expiry in past
podman exec -it gym_postgres psql -U gymuser -d gymtracker
UPDATE password_reset_tokens SET expires_at = NOW() - INTERVAL '2 hours' WHERE token = 'your_token';
```
Should get error: "Reset token has expired"

---

## 📝 Notes

### Email Configuration - Gmail SMTP

**✅ IMPLEMENTED!** Emails are now sent via Gmail SMTP.

**How it works:**
- User requests password reset
- Email sent to user's inbox with reset link
- Link contains token and redirects to reset page
- Token expires in 1 hour

**Setup Required:**
1. **Create Gmail App Password** (see `GMAIL_SETUP.md`)
2. **Configure `.env` file** with your Gmail credentials
3. **Restart backend** to apply changes

**Debug Mode:**
- When `DEBUG=True` in `.env`, token is ALSO returned in API response
- Useful for testing without checking email
- Remove `DEBUG=True` in production!

**Files Created:**
- `backend/app/services/email_service.py` - Email sending service
- `backend/.env.example` - Environment variables template
- `GMAIL_SETUP.md` - Complete setup instructions

---

## 🐛 Troubleshooting

### Error: "Passwords do not match"
- Check both password fields
- Ensure no extra spaces
- Password is case-sensitive

### Error: "Current password is incorrect"
- Verify you're entering the correct current password
- Password is case-sensitive

### Error: "Invalid or expired reset token"
- Token may have expired (1 hour limit)
- Request new reset token
- Token may have already been used

### Frontend not showing new features
- Clear browser cache
- Hard refresh (Ctrl+Shift+R)
- Check browser console for errors

### Migration failed
- Check if table already exists
- Verify database connection
- Check migration logs

---

## 📚 Files Modified

### Backend
- `backend/app/models/models.py` - Added PasswordResetToken model
- `backend/app/schemas/schemas.py` - Added password schemas
- `backend/app/api/auth.py` - Added password management endpoints
- `backend/alembic/versions/002_add_password_reset_tokens.py` - Migration file

### Frontend
- `frontend/index.html` - Added password modals and confirm fields
- `frontend/js/app.js` - Added password handling functions

---

## ✨ Future Enhancements

- [ ] Email integration for password resets
- [ ] Password strength meter on frontend
- [ ] Password history (prevent reusing recent passwords)
- [ ] Two-factor authentication (2FA)
- [ ] Account lockout after failed attempts
- [ ] Password complexity requirements (uppercase, numbers, special chars)
- [ ] Configurable token expiry time
- [ ] Admin dashboard for password resets

---

## 🆘 Support

If you encounter issues:
1. Check browser console for errors
2. Check backend logs: `podman logs gym_backend`
3. Verify database migration succeeded
4. Clear browser cache
5. Restart backend container

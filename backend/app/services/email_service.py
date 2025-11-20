"""
Email service for sending transactional emails
Uses Gmail SMTP for password resets and notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


def send_email(to_email: str, subject: str, html_content: str):
    """
    Send an email using Gmail SMTP

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
    """
    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"GymTracker <{settings.EMAIL_FROM}>"
    message["To"] = to_email

    # Add HTML content
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    try:
        # Connect to Gmail SMTP server
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            # Login
            server.login(settings.EMAIL_FROM, settings.EMAIL_PASSWORD)

            # Send email
            server.send_message(message)

        print(f"✅ Email sent successfully to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {str(e)}")
        raise Exception(f"Failed to send email: {str(e)}")


def send_password_reset_email(to_email: str, reset_token: str, user_name: str):
    """
    Send password reset email with token

    Args:
        to_email: User's email address
        reset_token: Password reset token
        user_name: User's name for personalization
    """
    # Build reset link
    reset_link = f"{settings.FRONTEND_URL}?reset_token={reset_token}"

    # Email subject
    subject = "GymTracker - Redefinir Senha / Reset Password"

    # HTML template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: white;
                border-radius: 10px;
                padding: 40px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                padding-bottom: 30px;
                border-bottom: 3px solid #667eea;
            }}
            .header h1 {{
                color: #667eea;
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 30px 0;
            }}
            .button {{
                display: inline-block;
                padding: 15px 40px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white !important;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 20px 0;
                text-align: center;
            }}
            .button:hover {{
                background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            }}
            .footer {{
                padding-top: 30px;
                border-top: 1px solid #eee;
                text-align: center;
                color: #666;
                font-size: 12px;
            }}
            .warning {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .info {{
                background: #d1ecf1;
                border-left: 4px solid #0c5460;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏋️ GymTracker</h1>
            </div>

            <div class="content">
                <h2>Olá {user_name}! / Hello {user_name}!</h2>

                <p><strong>Português:</strong></p>
                <p>Você solicitou redefinir sua senha do GymTracker.</p>
                <p>Clique no botão abaixo para criar uma nova senha:</p>

                <center>
                    <a href="{reset_link}" class="button">🔐 Redefinir Senha</a>
                </center>

                <div class="info">
                    ⏰ <strong>Este link expira em 1 hora.</strong>
                </div>

                <p>Se o botão não funcionar, copie e cole este link no navegador:</p>
                <p style="word-break: break-all; color: #667eea;">{reset_link}</p>

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">

                <p><strong>English:</strong></p>
                <p>You requested to reset your GymTracker password.</p>
                <p>Click the button above to create a new password.</p>

                <div class="warning">
                    ⚠️ Se você não solicitou isso, ignore este email. Sua senha permanecerá inalterada.<br>
                    ⚠️ If you didn't request this, ignore this email. Your password will remain unchanged.
                </div>
            </div>

            <div class="footer">
                <p>GymTracker © 2025</p>
                <p>Este é um email automático, por favor não responda.</p>
                <p>This is an automated email, please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_content)


def send_welcome_email(to_email: str, user_name: str):
    """
    Send welcome email to new users

    Args:
        to_email: User's email address
        user_name: User's name
    """
    subject = "Bem-vindo ao GymTracker! / Welcome to GymTracker!"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: white;
                border-radius: 10px;
                padding: 40px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                padding-bottom: 30px;
            }}
            .header h1 {{
                color: #667eea;
                margin: 0;
                font-size: 32px;
            }}
            .content {{
                padding: 20px 0;
            }}
            .button {{
                display: inline-block;
                padding: 15px 40px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white !important;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .footer {{
                padding-top: 30px;
                border-top: 1px solid #eee;
                text-align: center;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Bem-vindo! / Welcome!</h1>
            </div>

            <div class="content">
                <h2>Olá {user_name}!</h2>

                <p><strong>Português:</strong></p>
                <p>Sua conta no GymTracker foi criada com sucesso!</p>
                <p>Agora você pode começar a rastrear seus treinos, criar planos de exercícios e acompanhar seu progresso.</p>

                <center>
                    <a href="{settings.FRONTEND_URL}" class="button">Acessar GymTracker</a>
                </center>

                <hr style="margin: 30px 0;">

                <p><strong>English:</strong></p>
                <p>Your GymTracker account has been successfully created!</p>
                <p>You can now start tracking your workouts, creating exercise plans, and monitoring your progress.</p>
            </div>

            <div class="footer">
                <p>GymTracker © 2025</p>
                <p>Este é um email automático, por favor não responda.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_content)

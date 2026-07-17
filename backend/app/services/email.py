import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from app.config import Settings

logger = structlog.get_logger()


class EmailService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def send_password_reset_email(self, to_email: str, token: str) -> None:
        reset_url = f"{self.settings.password_reset_url}?token={token}"
        ttl = self.settings.password_reset_token_ttl_minutes

        # Professional branded HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    background-color: #0d0e12;
                    color: #e4e6eb;
                    margin: 0;
                    padding: 0;
                    -webkit-font-smoothing: antialiased;
                }}
                .email-container {{
                    max-width: 580px;
                    margin: 0 auto;
                    padding: 30px;
                    background-color: #121318;
                    border: 1px solid #22252e;
                    border-radius: 8px;
                    margin-top: 40px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    font-size: 24px;
                    font-weight: 700;
                    letter-spacing: 0.05em;
                    color: #ffffff;
                    margin: 0;
                }}
                .header span {{
                    color: #4f46e5;
                }}
                .content {{
                    line-height: 1.6;
                    font-size: 16px;
                }}
                .btn-container {{
                    text-align: center;
                    margin: 35px 0;
                }}
                .btn {{
                    display: inline-block;
                    padding: 14px 28px;
                    background-color: #4f46e5;
                    color: #ffffff !important;
                    text-decoration: none;
                    font-weight: bold;
                    border-radius: 6px;
                    font-size: 16px;
                    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
                }}
                .footer {{
                    margin-top: 40px;
                    font-size: 12px;
                    color: #6b7280;
                    text-align: center;
                    border-top: 1px solid #22252e;
                    padding-top: 20px;
                }}
                .plain-link {{
                    word-break: break-all;
                    color: #4f46e5;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>RAHFIT <span>AI</span></h1>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>We received a request to reset the password for your RAHFIT AI account.
                    Click the button below to set a new password:</p>
                    <div class="btn-container">
                        <a href="{reset_url}" class="btn">Reset Password</a>
                    </div>
                    <p>This reset link will expire in <strong>{ttl} minutes</strong>.</p>
                    <p>If you did not request a password reset, you can safely ignore this email.
                    Your password will remain unchanged.</p>
                    <p>If the button doesn't work, copy and paste this URL into your browser:</p>
                    <p class="plain-link">{reset_url}</p>
                </div>
                <div class="footer">
                    <p>&copy; 2026 RAHFIT AI. All rights reserved.</p>
                    <p>This is an automated security transmission.
                    Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = (
            f"RAHFIT AI - Password Reset\n\n"
            f"Hello,\n\n"
            f"We received a request to reset the password for your RAHFIT AI account. "
            f"Use the following link to set a new password:\n\n"
            f"{reset_url}\n\n"
            f"This link will expire in {ttl} minutes.\n\n"
            f"If you did not request this, please ignore this email.\n"
        )

        if self.settings.email_provider == "development":
            # Expose the URL to logs only in development/test environments
            logger.info("email_reset_password_logged", to=to_email, reset_url=reset_url)
            return

        # SMTP implementation
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Reset your RAHFIT AI password"
        msg["From"] = f"{self.settings.smtp_from_name} <{self.settings.smtp_from_email}>"
        msg["To"] = to_email

        msg.attach(MIMEText(plain_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        try:
            server: smtplib.SMTP
            if self.settings.smtp_port == 465:
                server = smtplib.SMTP_SSL(
                    self.settings.smtp_host, self.settings.smtp_port, timeout=10
                )
            else:
                server = smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=10)
                if self.settings.smtp_use_tls:
                    server.starttls()

            if self.settings.smtp_username and self.settings.smtp_password:
                server.login(
                    self.settings.smtp_username, self.settings.smtp_password.get_secret_value()
                )

            server.sendmail(self.settings.smtp_from_email, to_email, msg.as_string())
            server.quit()
            logger.info("email_reset_password_sent", to=to_email)
        except Exception as exc:
            logger.error("email_reset_password_failed", to=to_email, error=str(exc))
            raise

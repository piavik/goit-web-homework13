from pathlib import Path
from fastapi import FastAPI, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List

from src.config.settings import settings
from src.services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME   = settings.mail_username,
    MAIL_PASSWORD   = settings.mail_password,
    MAIL_FROM       = settings.mail_from,
    MAIL_PORT       = settings.mail_port,
    MAIL_SERVER     = settings.mail_server,
    MAIL_FROM_NAME  = settings.mail_from_name,
    MAIL_STARTTLS   = settings.mail_starttls,
    MAIL_SSL_TLS    = settings.mail_ssl_tls,
    USE_CREDENTIALS = settings.mail_use_credentials,
    VALIDATE_CERTS  = settings.mail_validate_certs,
    TEMPLATE_FOLDER = Path(__file__).parent / 'templates',
)

async def send_email(email: EmailStr, username: str, host: str) -> None:
    """
    Send email to the user.

    Args:
        email (EmailStr): User email.
        username (str): User name.
        host (str): Hostname for the URL that will be used in email for confirmation. (The on that FastAPI app is running on)
    """
    try:
        token_verification = await auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Please confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="confirmatilon_email_template.html")
    except ConnectionError as connErr:
        print(connErr)

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from app.core.config import settings
# --- FIX: Import the new centralized path ---
from app.core.paths import TEMPLATES_DIR

# This part remains the same
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    MAIL_DEBUG=True,
)

# --- FIX: Use the new, unambiguous path from our config file ---
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

async def send_email_notification(recipient_email: str, query: str, results_url: str):
    """Renders the email template manually and sends the email."""
    # We moved the try/except block to the scheduler for better logic control.
    template = env.get_template("email_template.html")
    html_content = template.render(query=query, results_url=results_url)

    message = MessageSchema(
        subject=f"Your Image Set for '{query}' is Ready!",
        recipients=[recipient_email],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    print(f"📧 Preparing to send email for query '{query}' to {recipient_email}...")
    await fm.send_message(message)


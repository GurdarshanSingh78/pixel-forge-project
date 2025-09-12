from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Manages application settings."""
    PROJECT_NAME: str = "Image Fetcher Project"
    CLIP_FILTER_THRESHOLD: float = 0.28
    PEXELS_API_KEY: str = "YOUR_DEFAULT_KEY_IF_NOT_IN_ENV"

    # Email Configuration
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.sendgrid.net"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True

    # --- THIS IS THE FIX ---
    # We are telling our email client not to perform the certificate verification that is failing.
    VALIDATE_CERTS: bool = False # Change from True to False

    MAIL_BACKEND: str = "smtp"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
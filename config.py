import os
from pathlib import Path

# =========================================================
# BASE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"

# Garante que a pasta instance exista
INSTANCE_DIR.mkdir(exist_ok=True)

# =========================================================
# CONFIG BASE
# =========================================================

class BaseConfig:
    """Configurações base compartilhadas"""

    # -----------------------------------------------------
    # Segurança
    # -----------------------------------------------------
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-this")

    # -----------------------------------------------------
    # Flask
    # -----------------------------------------------------
    DEBUG = False
    TESTING = False

    # -----------------------------------------------------
    # Banco de dados
    # -----------------------------------------------------
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------------------------------------------------
    # Sessão / Cookies
    # -----------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # -----------------------------------------------------
    # Uploads (LOGO DA BARBEARIA)
    # -----------------------------------------------------
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

    UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "uploads"
    UPLOAD_LOGOS_FOLDER = UPLOAD_FOLDER / "logos"

    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # Garante pastas de upload
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    UPLOAD_LOGOS_FOLDER.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------
    # Timezone
    # -----------------------------------------------------
    TIMEZONE = "America/Sao_Paulo"

    # -----------------------------------------------------
    # Branding / White-label
    # -----------------------------------------------------
    APP_NAME = "BarberSaaS"
    THEME = "dark"


# =========================================================
# DESENVOLVIMENTO
# =========================================================

class DevelopmentConfig(BaseConfig):
    DEBUG = True

    # SQLite para MVP
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'database.db'}"
    )


# =========================================================
# PRODUÇÃO
# =========================================================

class ProductionConfig(BaseConfig):
    DEBUG = False

    # Produção geralmente usa Postgres
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Cookies mais seguros
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


# =========================================================
# TESTES (opcional)
# =========================================================

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# =========================================================
# MAPA DE CONFIG
# =========================================================

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config():
    """Retorna config baseada na variável FLASK_ENV"""
    env = os.getenv("FLASK_ENV", "development")
    return config_by_name.get(env, DevelopmentConfig)

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# =========================================================
# EXTENSÕES CENTRALIZADAS
# =========================================================

# Banco de dados
db = SQLAlchemy()

# Login / Sessão
login_manager = LoginManager()

# Configurações padrão do login
login_manager.login_view = "auth.login"
login_manager.login_message = "Faça login para continuar."
login_manager.login_message_category = "warning"


# =========================================================
# CLOUDINARY - ARMAZENAMENTO DE IMAGENS
# =========================================================
try:
    import cloudinary

    CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

    if CLOUDINARY_URL:
        cloudinary.config(
            cloud_name=CLOUDINARY_URL.split("@")[1],
            api_key=CLOUDINARY_URL.split("//")[1].split(":")[0],
            api_secret=CLOUDINARY_URL.split(":")[2].split("@")[0],
            secure=True
        )
        print("Cloudinary configurado com sucesso")
    else:
        print("⚠️ CLOUDINARY_URL não configurado no ambiente")
except Exception as e:
    print(f"⚠️ Erro ao configurar Cloudinary: {e}")

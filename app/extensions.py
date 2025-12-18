from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

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

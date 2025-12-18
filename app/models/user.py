from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

# =========================================================
# MODEL: USER
# =========================================================

class User(UserMixin, db.Model):
    """
    Usuários do sistema:
    - ADMIN_GLOBAL (você)
    - TENANT_ADMIN (dono da barbearia)
    - BARBER (barbeiro)
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Identidade
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Autenticação
    senha = db.Column(db.String(255), nullable=False)

    # Papel no sistema
    role = db.Column(db.String(20), nullable=False)

    # Relacionamento com tenant
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=True)

    # Status
    ativo = db.Column(db.Boolean, default=True)

    # Auditoria
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # =====================================================
    # MÉTODOS DE AUTENTICAÇÃO
    # =====================================================

    def set_password(self, password: str):
        """Define a senha com hash seguro"""
        self.senha = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifica senha"""
        return check_password_hash(self.senha, password)

    # =====================================================
    # HELPERS DE ROLE
    # =====================================================

    def is_admin_global(self) -> bool:
        return self.role == "ADMIN_GLOBAL"

    def is_tenant_admin(self) -> bool:
        return self.role == "TENANT_ADMIN"

    def is_barber(self) -> bool:
        return self.role == "BARBER"

    # =====================================================
    # REPRESENTAÇÃO
    # =====================================================

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

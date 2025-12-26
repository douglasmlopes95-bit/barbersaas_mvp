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
    - ADMIN_GLOBAL (admin do SaaS)
    - TENANT_ADMIN (dono da barbearia)
    - BARBER (barbeiro)
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # =====================================================
    # IDENTIDADE
    # =====================================================
    nome = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    # =====================================================
    # AUTENTICAÇÃO
    # =====================================================
    senha = db.Column(
        db.String(255),
        nullable=False
    )

    # =====================================================
    # PAPEL / PERMISSÃO
    # =====================================================
    role = db.Column(
        db.String(20),
        nullable=False
    )

    # =====================================================
    # MULTI-TENANT
    # =====================================================
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=True,
        index=True
    )

    # =====================================================
    # STATUS / CONTROLE
    # =====================================================
    ativo = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    excluido = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # =====================================================
    # AUDITORIA
    # =====================================================
    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    atualizado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # =====================================================
    # MÉTODOS DE AUTENTICAÇÃO
    # =====================================================
    def set_password(self, password: str):
        self.senha = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
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
    # AÇÕES DE DOMÍNIO
    # =====================================================
    def desativar(self):
        self.ativo = False

    def ativar(self):
        self.ativo = True

    def soft_delete(self):
        self.excluido = True
        self.ativo = False

    # =====================================================
    # FLASK-LOGIN
    # =====================================================
    def get_id(self):
        return str(self.id)

    # =====================================================
    # REPRESENTAÇÃO
    # =====================================================
    def __repr__(self):
        status = "ativo" if self.ativo else "inativo"
        return f"<User id={self.id} email={self.email} role={self.role} status={status}>"

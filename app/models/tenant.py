from datetime import datetime
from app.extensions import db

# =========================================================
# MODEL: TENANT (BARBEARIA)
# =========================================================

class Tenant(db.Model):
    """
    Representa uma barbearia dentro do SaaS (tenant).
    Todos os dados do sistema se relacionam a um tenant.
    """

    __tablename__ = "tenants"

    id = db.Column(db.Integer, primary_key=True)

    # Identidade
    nome = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)

    # Status
    ativo = db.Column(db.Boolean, default=True)

    # Auditoria
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # =====================================================
    # RELACIONAMENTOS
    # =====================================================
    users = db.relationship(
        "User",
        backref="tenant",
        lazy=True,
        cascade="all, delete-orphan"
    )

    services = db.relationship(
        "Service",
        backref="tenant",
        lazy=True,
        cascade="all, delete-orphan"
    )

    appointments = db.relationship(
        "Appointment",
        backref="tenant",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # =====================================================
    # MÉTODOS
    # =====================================================
    def __repr__(self):
        return f"<Tenant {self.nome}>"

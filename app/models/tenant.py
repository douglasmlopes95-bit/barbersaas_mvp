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

    # =====================================================
    # IDENTIDADE
    # =====================================================
    nome = db.Column(
        db.String(120),
        nullable=False
    )

    slug = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    # =====================================================
    # BRANDING / INFORMAÇÕES PÚBLICAS
    # =====================================================
    logo = db.Column(
        db.String(255),
        nullable=True
    )  # nome do arquivo salvo em static/uploads/logos

    descricao = db.Column(
        db.String(255),
        nullable=True
    )

    whatsapp = db.Column(
        db.String(30),
        nullable=True
    )

    endereco = db.Column(
        db.String(255),
        nullable=True
    )

    horario_funcionamento = db.Column(
        db.String(255),
        nullable=True
    )

    # =====================================================
    # STATUS
    # =====================================================
    ativo = db.Column(
        db.Boolean,
        default=True,
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
    # RELACIONAMENTOS
    # =====================================================
    users = db.relationship(
        "User",
        backref="tenant",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    services = db.relationship(
        "Service",
        backref="tenant",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    appointments = db.relationship(
        "Appointment",
        backref="tenant",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # HELPERS
    # =====================================================
    @property
    def logo_url(self):
        """
        Retorna a URL pública da logo, se existir.
        """
        if self.logo:
            return f"/static/uploads/logos/{self.logo}"
        return None

    # =====================================================
    # REPRESENTAÇÃO
    # =====================================================
    def __repr__(self):
        return f"<Tenant id={self.id} nome={self.nome}>"

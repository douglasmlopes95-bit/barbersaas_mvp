from datetime import datetime
from app.extensions import db

# =========================================================
# MODEL: SERVICE
# =========================================================

class Service(db.Model):
    """
    Serviços oferecidos pela barbearia
    (ex: Corte, Barba, Corte + Barba)
    """

    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)

    # Identidade do serviço
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)

    # Valores
    preco = db.Column(db.Float, nullable=False)
    duracao_min = db.Column(db.Integer, default=30)

    # Relacionamento com tenant
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False
    )

    # Status
    ativo = db.Column(db.Boolean, default=True)

    # Auditoria
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # =====================================================
    # MÉTODOS
    # =====================================================

    def __repr__(self):
        return f"<Service {self.nome} - R$ {self.preco:.2f}>"

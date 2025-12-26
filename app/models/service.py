from datetime import datetime
from decimal import Decimal

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

    # =====================================================
    # IDENTIDADE
    # =====================================================
    nome = db.Column(
        db.String(120),
        nullable=False
    )

    descricao = db.Column(
        db.String(255),
        nullable=True
    )

    # =====================================================
    # VALORES
    # =====================================================
    preco = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    duracao_min = db.Column(
        db.Integer,
        default=30,
        nullable=False
    )

    # =====================================================
    # RELAÇÃO COM BARBEIRO (USER ROLE = BARBER)
    # =====================================================
    barber_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    barber = db.relationship(
        "User",
        foreign_keys=[barber_id],
        lazy="joined"
    )

    # =====================================================
    # MULTI-TENANT
    # =====================================================
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False,
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
    # HELPERS
    # =====================================================
    @property
    def preco_decimal(self) -> Decimal:
        return Decimal(self.preco)

    def pode_excluir(self) -> bool:
        """
        Serviço só pode ser excluído se não houver
        agendamentos vinculados.
        """
        from app.models.appointment import Appointment

        existe = Appointment.query.filter_by(
            service_id=self.id
        ).first()

        return not bool(existe)

    # =====================================================
    # AÇÕES DE DOMÍNIO
    # =====================================================
    def desativar(self):
        self.ativo = False

    def ativar(self):
        self.ativo = True

    def soft_delete(self):
        """
        Exclusão lógica para manter histórico
        """
        self.excluido = True
        self.ativo = False

    # =====================================================
    # REPRESENTAÇÃO
    # =====================================================
    def __repr__(self):
        status = "ativo" if self.ativo else "inativo"
        barber = self.barber.nome if self.barber else "Sem barbeiro"
        return f"<Service {self.nome} | {status} | {barber} | R$ {self.preco_decimal:.2f}>"

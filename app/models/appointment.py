from datetime import datetime
from app.extensions import db

# =========================================================
# MODEL: APPOINTMENT (AGENDAMENTO)
# =========================================================

class Appointment(db.Model):
    """
    Agendamentos realizados pelos clientes
    """

    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)

    # Relacionamento com tenant (barbearia)
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False
    )

    # Barbeiro responsável
    barber_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Serviço escolhido
    service_id = db.Column(
        db.Integer,
        db.ForeignKey("services.id"),
        nullable=False
    )

    # Dados do cliente (MVP não exige login)
    cliente_nome = db.Column(db.String(120), nullable=False)
    cliente_whatsapp = db.Column(db.String(30), nullable=False)

    # Data e hora do agendamento
    data_hora = db.Column(db.DateTime, nullable=False)

    # Status do agendamento
    status = db.Column(
        db.String(20),
        nullable=False,
        default="AGENDADO"
    )  # AGENDADO | CONCLUIDO | CANCELADO

    # Data de conclusão do serviço
    concluido_em = db.Column(
        db.DateTime,
        nullable=True
    )

    # Observações opcionais
    observacoes = db.Column(db.String(255), nullable=True)

    # Auditoria
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
    # MÉTODOS DE DOMÍNIO
    # =====================================================

    def concluir(self):
        """
        Marca o agendamento como concluído
        """
        if self.status != "AGENDADO":
            return False

        self.status = "CONCLUIDO"
        self.concluido_em = datetime.utcnow()
        return True

    def cancelar(self):
        """
        Cancela o agendamento
        """
        if self.status == "CONCLUIDO":
            return False

        self.status = "CANCELADO"
        return True

    # =====================================================
    # REPRESENTAÇÃO
    # =====================================================

    def __repr__(self):
        return (
            f"<Appointment {self.id} | "
            f"{self.data_hora.strftime('%d/%m/%Y %H:%M')} | "
            f"Status: {self.status}>"
        )

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
        default="AGENDADO"
    )  # AGENDADO | CONCLUIDO | CANCELADO

    # Observações opcionais
    observacoes = db.Column(db.String(255), nullable=True)

    # Auditoria
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # =====================================================
    # MÉTODOS
    # =====================================================

    def __repr__(self):
        return (
            f"<Appointment {self.id} | "
            f"{self.data_hora.strftime('%d/%m %H:%M')} | "
            f"Status: {self.status}>"
        )

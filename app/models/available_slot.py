from datetime import datetime
from app.extensions import db

# =========================================================
# MODEL: HORÁRIOS DISPONÍVEIS
# =========================================================
# Representa os horários que a barbearia libera
# para cada barbeiro em uma data específica.
#
# O cliente NÃO cria horário.
# O cliente apenas consome um slot disponível.
# =========================================================

class AvailableSlot(db.Model):
    __tablename__ = "available_slots"

    id = db.Column(db.Integer, primary_key=True)

    # =====================================================
    # MULTI-TENANT
    # =====================================================
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False,
        index=True
    )

    barber_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # DATA E HORA
    # =====================================================
    data = db.Column(
        db.Date,
        nullable=False,
        index=True
    )

    hora = db.Column(
        db.Time,
        nullable=False,
        index=True
    )

    # =====================================================
    # CONTROLE
    # =====================================================
    disponivel = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    bloqueado_manual = db.Column(
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
    # REGRAS DE DOMÍNIO
    # =====================================================
    def pode_excluir(self) -> bool:
        """
        Não permite exclusão se já existir agendamento
        vinculado a este horário.
        """
        from app.models.appointment import Appointment
        from datetime import datetime as dt

        data_hora = dt.combine(self.data, self.hora)

        existe = Appointment.query.filter_by(
            barber_id=self.barber_id,
            data_hora=data_hora
        ).first()

        return not bool(existe)

    def bloquear(self):
        self.disponivel = False
        self.bloqueado_manual = True

    def liberar(self):
        self.disponivel = True
        self.bloqueado_manual = False

    # =====================================================
    # HELPERS
    # =====================================================
    @property
    def status(self) -> str:
        if not self.disponivel and self.bloqueado_manual:
            return "BLOQUEADO"
        if not self.disponivel:
            return "OCUPADO"
        return "DISPONIVEL"

    # =====================================================
    # REPRESENTAÇÃO
    # =====================================================
    def __repr__(self):
        return (
            f"<AvailableSlot barber_id={self.barber_id} "
            f"data={self.data} hora={self.hora} "
            f"status={self.status}>"
        )

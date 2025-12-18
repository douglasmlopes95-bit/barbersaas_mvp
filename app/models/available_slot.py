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

    # Relacionamentos
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False
    )

    barber_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Data e hora do atendimento
    data = db.Column(
        db.Date,
        nullable=False
    )

    hora = db.Column(
        db.Time,
        nullable=False
    )

    # Controle de disponibilidade
    disponivel = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # =====================================================
    # MÉTODOS AUXILIARES
    # =====================================================

    def __repr__(self):
        return (
            f"<AvailableSlot barber_id={self.barber_id} "
            f"data={self.data} hora={self.hora} "
            f"disponivel={self.disponivel}>"
        )

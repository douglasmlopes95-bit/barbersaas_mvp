from datetime import datetime
from decimal import Decimal

from app.extensions import db


class Payment(db.Model):
    """
    Pagamentos / Faturamento da barbearia

    Usado para:
    - Relatórios financeiros
    - Gráficos de faturamento
    - Abertura e fechamento de caixa
    - Cálculo de lucro
    """

    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    # ==============================
    # MULTI-TENANT
    # ==============================
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False,
        index=True
    )

    # ==============================
    # RELACIONAMENTOS OPCIONAIS
    # ==============================
    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.id"),
        nullable=True
    )

    barber_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    # ==============================
    # DADOS FINANCEIROS
    # ==============================
    valor = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    metodo_pagamento = db.Column(
        db.String(20),
        nullable=False
    )
    # DINHEIRO | PIX | CARTAO | CREDITO | DEBITO

    status = db.Column(
        db.String(20),
        nullable=False,
        default="PAGO"
    )
    # PAGO | ESTORNADO | CANCELADO

    data = db.Column(
        db.Date,
        nullable=False,
        default=datetime.utcnow
    )

    criado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # ==============================
    # HELPERS
    # ==============================

    def __repr__(self):
        return f"<Payment {self.id} | R$ {self.valor} | {self.metodo_pagamento}>"

    @property
    def valor_decimal(self):
        return Decimal(self.valor)

    @property
    def valor_float(self):
        """Facilita uso em gráficos"""
        return float(self.valor)

    @property
    def esta_pago(self):
        return self.status == "PAGO"

    # ==============================
    # QUERIES PARA RELATÓRIOS
    # ==============================

    @staticmethod
    def total_por_periodo(tenant_id, data_inicio, data_fim):
        """Total faturado em um período"""
        return (
            db.session.query(db.func.coalesce(db.func.sum(Payment.valor), 0))
            .filter(
                Payment.tenant_id == tenant_id,
                Payment.status == "PAGO",
                Payment.data.between(data_inicio, data_fim)
            )
            .scalar()
        )

    @staticmethod
    def total_por_metodo(tenant_id, data_inicio, data_fim):
        """Agrupa faturamento por método de pagamento"""
        return (
            db.session.query(
                Payment.metodo_pagamento,
                db.func.sum(Payment.valor).label("total")
            )
            .filter(
                Payment.tenant_id == tenant_id,
                Payment.status == "PAGO",
                Payment.data.between(data_inicio, data_fim)
            )
            .group_by(Payment.metodo_pagamento)
            .all()
        )

    @staticmethod
    def total_por_barbeiro(tenant_id, data_inicio, data_fim):
        """Faturamento por barbeiro"""
        return (
            db.session.query(
                Payment.barber_id,
                db.func.sum(Payment.valor).label("total")
            )
            .filter(
                Payment.tenant_id == tenant_id,
                Payment.status == "PAGO",
                Payment.data.between(data_inicio, data_fim)
            )
            .group_by(Payment.barber_id)
            .all()
        )

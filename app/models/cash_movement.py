from datetime import datetime
from decimal import Decimal

from app.extensions import db


class CashMovement(db.Model):
    """
    Movimentações de Caixa

    Representa QUALQUER entrada ou saída financeira:
    - Serviços concluídos
    - Pagamentos de clientes
    - Despesas operacionais
    - Ajustes manuais
    - Sangria / Reforço de caixa

    Sempre vinculada a uma CashSession
    """

    __tablename__ = "cash_movements"

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

    cash_session_id = db.Column(
        db.Integer,
        db.ForeignKey("cash_sessions.id"),
        nullable=False,
        index=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # ==============================
    # TIPO DE MOVIMENTO
    # ==============================
    tipo = db.Column(
        db.String(20),
        nullable=False
    )
    # ENTRADA | SAIDA | AJUSTE | SANGRIA | REFORCO

    categoria = db.Column(
        db.String(50),
        nullable=True
    )

    descricao = db.Column(
        db.String(255),
        nullable=True
    )

    # ==============================
    # VALORES
    # ==============================
    valor = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    metodo_pagamento = db.Column(
        db.String(30),
        nullable=True
    )
    # DINHEIRO | PIX | CARTAO | TRANSFERENCIA

    # ==============================
    # VÍNCULOS OPCIONAIS
    # ==============================
    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.id"),
        nullable=True,
        index=True
    )

    payment_id = db.Column(
        db.Integer,
        db.ForeignKey("payments.id"),
        nullable=True
    )

    expense_id = db.Column(
        db.Integer,
        db.ForeignKey("expenses.id"),
        nullable=True
    )

    # ==============================
    # AUDITORIA
    # ==============================
    criado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    # ==============================
    # HELPERS
    # ==============================

    def __repr__(self):
        return f"<CashMovement {self.id} | {self.tipo} | R$ {self.valor}>"

    @property
    def valor_decimal(self):
        return Decimal(self.valor)

    @property
    def eh_entrada(self):
        return self.tipo == "ENTRADA"

    @property
    def eh_saida(self):
        return self.tipo == "SAIDA"

    # ==============================
    # MÉTODOS DE NEGÓCIO
    # ==============================

    @staticmethod
    def registrar_entrada(
        tenant_id,
        cash_session,
        usuario_id,
        valor,
        categoria=None,
        descricao=None,
        metodo_pagamento=None,
        appointment_id=None,
        payment_id=None
    ):
        """
        Registra entrada no caixa
        """
        valor = Decimal(valor)

        movimento = CashMovement(
            tenant_id=tenant_id,
            cash_session_id=cash_session.id,
            usuario_id=usuario_id,
            tipo="ENTRADA",
            valor=valor,
            categoria=categoria,
            descricao=descricao,
            metodo_pagamento=metodo_pagamento,
            appointment_id=appointment_id,
            payment_id=payment_id
        )

        db.session.add(movimento)
        cash_session.registrar_entrada(valor)
        db.session.commit()

        return movimento

    @staticmethod
    def registrar_saida(
        tenant_id,
        cash_session,
        usuario_id,
        valor,
        categoria=None,
        descricao=None,
        expense_id=None
    ):
        """
        Registra saída no caixa
        """
        valor = Decimal(valor)

        movimento = CashMovement(
            tenant_id=tenant_id,
            cash_session_id=cash_session.id,
            usuario_id=usuario_id,
            tipo="SAIDA",
            valor=valor,
            categoria=categoria,
            descricao=descricao,
            expense_id=expense_id
        )

        db.session.add(movimento)
        cash_session.registrar_saida(valor)
        db.session.commit()

        return movimento

    @staticmethod
    def registrar_ajuste(
        tenant_id,
        cash_session,
        usuario_id,
        valor,
        descricao=None
    ):
        """
        Ajuste manual de caixa (positivo ou negativo)
        """
        valor = Decimal(valor)
        tipo_movimento = "ENTRADA" if valor >= 0 else "SAIDA"
        valor_abs = abs(valor)

        movimento = CashMovement(
            tenant_id=tenant_id,
            cash_session_id=cash_session.id,
            usuario_id=usuario_id,
            tipo="AJUSTE",
            valor=valor_abs,
            descricao=descricao
        )

        db.session.add(movimento)

        if tipo_movimento == "ENTRADA":
            cash_session.registrar_entrada(valor_abs)
        else:
            cash_session.registrar_saida(valor_abs)

        db.session.commit()

        return movimento

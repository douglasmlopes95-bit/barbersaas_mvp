from datetime import datetime

from app.extensions import db


class Expense(db.Model):
    """
    Despesas da barbearia
    Usado para:
    - Relatórios financeiros
    - Cálculo de lucro
    - Gráficos (faturamento x despesas)
    """

    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)

    # Multi-tenant
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False,
        index=True
    )

    # Dados da despesa
    categoria = db.Column(
        db.String(50),
        nullable=False
    )

    descricao = db.Column(
        db.String(255),
        nullable=True
    )

    valor = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    metodo_pagamento = db.Column(
        db.String(20),
        nullable=True
    )
    # Ex: DINHEIRO, PIX, CARTAO, TRANSFERENCIA

    data = db.Column(
        db.Date,
        nullable=False,
        default=datetime.utcnow
    )

    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # =====================================================
    # HELPERS
    # =====================================================

    def __repr__(self):
        return f"<Expense {self.categoria} - R$ {self.valor}>"

    @property
    def valor_float(self):
        """Facilita uso em gráficos"""
        return float(self.valor)

    # =====================================================
    # QUERIES ÚTEIS (RELATÓRIOS)
    # =====================================================

    @staticmethod
    def total_por_periodo(tenant_id, data_inicio, data_fim):
        """Total de despesas em um período"""
        return (
            db.session.query(db.func.coalesce(db.func.sum(Expense.valor), 0))
            .filter(
                Expense.tenant_id == tenant_id,
                Expense.data >= data_inicio,
                Expense.data <= data_fim
            )
            .scalar()
        )

    @staticmethod
    def total_por_categoria(tenant_id, data_inicio, data_fim):
        """Agrupa despesas por categoria"""
        return (
            db.session.query(
                Expense.categoria,
                db.func.sum(Expense.valor).label("total")
            )
            .filter(
                Expense.tenant_id == tenant_id,
                Expense.data >= data_inicio,
                Expense.data <= data_fim
            )
            .group_by(Expense.categoria)
            .all()
        )

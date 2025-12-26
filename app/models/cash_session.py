from datetime import datetime
from decimal import Decimal

from app.extensions import db


class CashSession(db.Model):
    """
    Sessão de Caixa (Abertura / Fechamento)

    Usado para:
    - Controle diário de caixa
    - Abertura e fechamento
    - Auditoria financeira
    - Relatórios de faturamento vs despesas
    """

    __tablename__ = "cash_sessions"

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

    usuario_abertura_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    usuario_fechamento_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    # ==============================
    # DADOS DA SESSÃO
    # ==============================
    aberto_em = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    fechado_em = db.Column(
        db.DateTime,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ABERTO"
    )
    # ABERTO | FECHADO

    # ==============================
    # VALORES
    # ==============================
    valor_inicial = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    valor_final = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    total_entradas = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    total_saidas = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    observacoes = db.Column(
        db.Text,
        nullable=True
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
        return f"<CashSession {self.id} | {self.status}>"

    @property
    def saldo_calculado(self):
        return (
            Decimal(self.valor_inicial)
            + Decimal(self.total_entradas)
            - Decimal(self.total_saidas)
        )

    @property
    def esta_aberto(self):
        return self.status == "ABERTO"

    # ==============================
    # MÉTODOS UTILITÁRIOS
    # ==============================

    @staticmethod
    def caixa_aberto(tenant_id):
        return CashSession.query.filter_by(
            tenant_id=tenant_id,
            status="ABERTO"
        ).first()

    @classmethod
    def get_or_create_aberta(cls, tenant_id, usuario_id):
        """
        Compatível com o dashboard:
        - Retorna caixa aberto
        - Se não existir, abre automaticamente
        """
        caixa = cls.caixa_aberto(tenant_id)

        if caixa:
            return caixa

        novo = cls(
            tenant_id=tenant_id,
            usuario_abertura_id=usuario_id,
            status="ABERTO",
            valor_inicial=Decimal("0.00"),
            total_entradas=Decimal("0.00"),
            total_saidas=Decimal("0.00")
        )

        db.session.add(novo)
        db.session.commit()

        return novo

    # ==============================
    # OPERAÇÕES
    # ==============================

    @staticmethod
    def abrir_caixa(tenant_id, usuario_id, valor_inicial=0, observacoes=None):
        if CashSession.caixa_aberto(tenant_id):
            raise Exception("Já existe um caixa aberto para este tenant")

        caixa = CashSession(
            tenant_id=tenant_id,
            usuario_abertura_id=usuario_id,
            valor_inicial=Decimal(valor_inicial),
            observacoes=observacoes
        )

        db.session.add(caixa)
        db.session.commit()
        return caixa

    def registrar_entrada(self, valor):
        self.total_entradas = Decimal(self.total_entradas) + Decimal(valor)
        db.session.commit()

    def registrar_saida(self, valor):
        self.total_saidas = Decimal(self.total_saidas) + Decimal(valor)
        db.session.commit()

    def fechar_caixa(self, usuario_id, valor_final, observacoes=None):
        self.usuario_fechamento_id = usuario_id
        self.valor_final = Decimal(valor_final)
        self.fechado_em = datetime.utcnow()
        self.status = "FECHADO"

        if observacoes:
            self.observacoes = observacoes

        db.session.commit()

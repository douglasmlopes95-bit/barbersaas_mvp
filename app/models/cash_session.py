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
        """
        Saldo esperado no fechamento
        """
        return (
            Decimal(self.valor_inicial)
            + Decimal(self.total_entradas)
            - Decimal(self.total_saidas)
        )

    @property
    def esta_aberto(self):
        return self.status == "ABERTO"

    # ==============================
    # MÉTODOS DE NEGÓCIO
    # ==============================

    @staticmethod
    def caixa_aberto(tenant_id):
        """
        Retorna o caixa aberto atual (se existir)
        """
        return CashSession.query.filter_by(
            tenant_id=tenant_id,
            status="ABERTO"
        ).first()

    @staticmethod
    def abrir_caixa(
        tenant_id,
        usuario_id,
        valor_inicial=0,
        observacoes=None
    ):
        """
        Abre um novo caixa
        """
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
        """
        Registra entrada no caixa (pagamentos)
        """
        self.total_entradas = Decimal(self.total_entradas) + Decimal(valor)
        db.session.commit()

    def registrar_saida(self, valor):
        """
        Registra saída do caixa (despesas)
        """
        self.total_saidas = Decimal(self.total_saidas) + Decimal(valor)
        db.session.commit()

    def fechar_caixa(
        self,
        usuario_id,
        valor_final,
        observacoes=None
    ):
        """
        Fecha o caixa
        """
        self.usuario_fechamento_id = usuario_id
        self.valor_final = Decimal(valor_final)
        self.fechado_em = datetime.utcnow()
        self.status = "FECHADO"

        if observacoes:
            self.observacoes = observacoes

        db.session.commit()

from flask import (
    Blueprint, render_template,
    request, abort
)
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import date, datetime
from decimal import Decimal

from app.extensions import db
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.payment import Payment
from app.models.expense import Expense
from app.models.cash_session import CashSession
from app.models.cash_movement import CashMovement

# =========================================================
# BLUEPRINT
# =========================================================

tenant_reports_bp = Blueprint(
    "tenant_reports",
    __name__,
    url_prefix="/dashboard/reports"
)

# =========================================================
# RELATÓRIOS — VISÃO GERAL
# =========================================================

@tenant_reports_bp.route("/", methods=["GET"])
@login_required
def overview():

    if not current_user.is_tenant_admin():
        abort(403)

    tenant_id = current_user.tenant_id

    # -------------------------------------------------
    # FILTRO DE PERÍODO
    # -------------------------------------------------
    start = request.args.get("start")
    end = request.args.get("end")

    start_date = (
        datetime.strptime(start, "%Y-%m-%d").date()
        if start else date.today().replace(day=1)
    )

    end_date = (
        datetime.strptime(end, "%Y-%m-%d").date()
        if end else date.today()
    )

    # -------------------------------------------------
    # FATURAMENTO
    # -------------------------------------------------
    faturamento = db.session.query(
        func.coalesce(func.sum(Payment.valor), 0)
    ).filter(
        Payment.tenant_id == tenant_id,
        Payment.status == "PAGO",
        Payment.data.between(start_date, end_date)
    ).scalar()

    # -------------------------------------------------
    # DESPESAS
    # -------------------------------------------------
    despesas = db.session.query(
        func.coalesce(func.sum(Expense.valor), 0)
    ).filter(
        Expense.tenant_id == tenant_id,
        Expense.data.between(start_date, end_date)
    ).scalar()

    lucro = Decimal(faturamento) - Decimal(despesas)

    # -------------------------------------------------
    # AGENDAMENTOS / TICKET MÉDIO
    # -------------------------------------------------
    total_agendamentos = Appointment.query.filter(
        Appointment.tenant_id == tenant_id,
        Appointment.status == "CONCLUIDO",
        Appointment.data_hora.between(start_date, end_date)
    ).count()

    ticket_medio = (
        Decimal(faturamento) / total_agendamentos
        if total_agendamentos > 0 else Decimal("0.00")
    )

    # -------------------------------------------------
    # TOP SERVIÇOS
    # -------------------------------------------------
    top_services = db.session.query(
        Service.nome,
        func.count(Appointment.id)
    ).join(
        Appointment, Appointment.service_id == Service.id
    ).filter(
        Appointment.tenant_id == tenant_id,
        Appointment.status == "CONCLUIDO",
        Appointment.data_hora.between(start_date, end_date)
    ).group_by(
        Service.nome
    ).order_by(
        func.count(Appointment.id).desc()
    ).limit(5).all()

    # -------------------------------------------------
    # FLUXO DE CAIXA
    # -------------------------------------------------
    entradas = db.session.query(
        func.coalesce(func.sum(CashMovement.valor), 0)
    ).filter(
        CashMovement.tenant_id == tenant_id,
        CashMovement.tipo == "ENTRADA",
        CashMovement.criado_em.between(start_date, end_date)
    ).scalar()

    saidas = db.session.query(
        func.coalesce(func.sum(CashMovement.valor), 0)
    ).filter(
        CashMovement.tenant_id == tenant_id,
        CashMovement.tipo == "SAIDA",
        CashMovement.criado_em.between(start_date, end_date)
    ).scalar()

    saldo_caixa = Decimal(entradas) - Decimal(saidas)

    return render_template(
        "tenant_reports.html",
        start_date=start_date,
        end_date=end_date,
        faturamento=faturamento,
        despesas=despesas,
        lucro=lucro,
        ticket_medio=ticket_medio,
        total_agendamentos=total_agendamentos,
        top_services=top_services,
        entradas=entradas,
        saidas=saidas,
        saldo_caixa=saldo_caixa
    )

# =========================================================
# HISTÓRICO DE CAIXA
# =========================================================

@tenant_reports_bp.route("/cash", methods=["GET"])
@login_required
def cash_history():

    if not current_user.is_tenant_admin():
        abort(403)

    sessions = CashSession.query.filter_by(
        tenant_id=current_user.tenant_id
    ).order_by(
        CashSession.aberto_em.desc()
    ).all()

    return render_template(
        "reports/cash_history.html",
        sessions=sessions
    )

# =========================================================
# DETALHE DO CAIXA
# =========================================================

@tenant_reports_bp.route("/cash/<int:session_id>", methods=["GET"])
@login_required
def cash_detail(session_id):

    session = CashSession.query.get_or_404(session_id)

    if session.tenant_id != current_user.tenant_id:
        abort(403)

    movements = CashMovement.query.filter_by(
        cash_session_id=session.id
    ).order_by(
        CashMovement.criado_em.asc()
    ).all()

    return render_template(
        "reports/cash_detail.html",
        session=session,
        movements=movements
    )

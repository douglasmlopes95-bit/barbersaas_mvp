from sqlalchemy import func
from datetime import date

from app.extensions import db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.payment import Payment
from app.models.appointment import Appointment


# =========================================================
# TENANTS / BARBEARIAS
# =========================================================

def get_all_tenants():
    return Tenant.query.order_by(Tenant.criado_em.desc()).all()


def get_tenant_by_id(tenant_id: int):
    return Tenant.query.get_or_404(tenant_id)


def get_tenant_admin(tenant_id: int):
    return User.query.filter_by(
        tenant_id=tenant_id,
        role="TENANT_ADMIN",
        ativo=True
    ).first()


# =========================================================
# MÉTRICAS GERAIS (ADMIN)
# =========================================================

def get_global_kpis():
    """
    KPIs gerais da plataforma
    """
    total_tenants = Tenant.query.count()
    tenants_ativos = Tenant.query.filter_by(ativo=True).count()
    tenants_inativos = Tenant.query.filter_by(ativo=False).count()

    return {
        "total": total_tenants,
        "ativos": tenants_ativos,
        "inativos": tenants_inativos
    }


# =========================================================
# FATURAMENTO
# =========================================================

def get_tenant_faturamento_total(tenant_id: int):
    """
    Faturamento total da barbearia
    """
    valor = db.session.query(
        func.coalesce(func.sum(Payment.valor), 0)
    ).filter(
        Payment.tenant_id == tenant_id,
        Payment.status == "PAGO"
    ).scalar()

    return float(valor or 0)


def get_top_tenants_by_faturamento(limit=5):
    """
    Ranking das barbearias que mais faturam
    """
    results = db.session.query(
        Tenant,
        func.coalesce(func.sum(Payment.valor), 0).label("faturamento")
    ).join(
        Payment, Payment.tenant_id == Tenant.id
    ).filter(
        Payment.status == "PAGO"
    ).group_by(
        Tenant.id
    ).order_by(
        func.sum(Payment.valor).desc()
    ).limit(limit).all()

    return results


# =========================================================
# AGENDAMENTOS
# =========================================================

def get_tenant_total_appointments(tenant_id: int):
    return Appointment.query.filter_by(
        tenant_id=tenant_id
    ).count()


def get_tenant_completed_appointments(tenant_id: int):
    return Appointment.query.filter_by(
        tenant_id=tenant_id,
        status="CONCLUIDO"
    ).count()


def get_tenant_appointments_today(tenant_id: int):
    today = date.today()

    return Appointment.query.filter(
        Appointment.tenant_id == tenant_id,
        func.date(Appointment.data_hora) == today
    ).count()


# =========================================================
# DASHBOARD TENANT (VISÃO ADMIN)
# =========================================================

def get_tenant_admin_overview(tenant_id: int):
    """
    Resumo completo da barbearia (para ADMIN_GLOBAL)
    """
    return {
        "faturamento_total": get_tenant_faturamento_total(tenant_id),
        "total_agendamentos": get_tenant_total_appointments(tenant_id),
        "agendamentos_concluidos": get_tenant_completed_appointments(tenant_id),
        "agendamentos_hoje": get_tenant_appointments_today(tenant_id),
    }

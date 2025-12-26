from flask import (
    Blueprint, render_template,
    request, redirect, url_for,
    flash, abort, session
)
from flask_login import (
    login_required,
    current_user,
    login_user
)

from sqlalchemy import func
from datetime import datetime, timedelta

from app.extensions import db
from app.models.tenant import Tenant
from app.models.user import User


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# =========================================================
# DASHBOARD ADMIN GLOBAL
# =========================================================
@admin_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():

    if not current_user.is_admin_global():
        abort(403)

    tenants = Tenant.query.order_by(Tenant.criado_em.desc()).all()

    total_tenants = len(tenants)
    ativos = len([t for t in tenants if t.ativo])
    inativos = len([t for t in tenants if not t.ativo])

    period = request.args.get("period", "30")

    try:
        days = int(period)
    except:
        days = 30

    start_date = datetime.utcnow() - timedelta(days=days)

    total_faturamento = 0
    ranking = []
    faturamento_mensal = []

    try:
        from app.models.cash_movement import CashMovement

        total_faturamento = (
            db.session.query(func.sum(CashMovement.valor))
            .filter(CashMovement.tipo == "ENTRADA")
            .filter(CashMovement.criado_em >= start_date)
            .scalar()
        ) or 0

        ranking_query = (
            db.session.query(
                Tenant,
                func.coalesce(func.sum(CashMovement.valor), 0).label("faturamento")
            )
            .outerjoin(CashMovement, CashMovement.tenant_id == Tenant.id)
            .filter(
                (CashMovement.tipo == "ENTRADA") |
                (CashMovement.tipo.is_(None))
            )
            .filter(
                (CashMovement.criado_em >= start_date) |
                (CashMovement.criado_em.is_(None))
            )
            .group_by(Tenant.id)
            .order_by(func.sum(CashMovement.valor).desc())
            .all()
        )

        ranking = [
            {"tenant": r[0], "faturamento": float(r[1] or 0)}
            for r in ranking_query
        ]

        faturamento_raw = (
            db.session.query(
                func.strftime("%Y-%m", CashMovement.criado_em).label("mes"),
                func.sum(CashMovement.valor)
            )
            .filter(CashMovement.tipo == "ENTRADA")
            .filter(CashMovement.criado_em >= start_date)
            .group_by("mes")
            .order_by("mes")
            .all()
        )

        faturamento_mensal = [(m, float(v or 0)) for m, v in faturamento_raw]

    except Exception as e:
        print("Dashboard Financeiro não disponível:", e)

    return render_template(
        "admin/dashboard.html",
        tenants=tenants,
        total_tenants=total_tenants,
        ativos=ativos,
        inativos=inativos,
        period=str(period),
        total_faturamento=total_faturamento,
        ranking=ranking,
        faturamento_mensal=faturamento_mensal
    )



# =========================================================
# LISTAGEM DE BARBEARIAS
# =========================================================
@admin_bp.route("/tenants", methods=["GET", "POST"])
@login_required
def tenants_list():

    if not current_user.is_admin_global():
        abort(403)

    if request.method == "POST":
        nome = request.form.get("nome")
        slug = request.form.get("slug")
        email = request.form.get("email")
        senha = request.form.get("senha")

        if not all([nome, slug, email, senha]):
            flash("Preencha todos os campos", "danger")
            return redirect(url_for("admin.tenants_list"))

        slug = slug.strip().lower()

        if Tenant.query.filter_by(slug=slug).first():
            flash("Slug já existe", "danger")
            return redirect(url_for("admin.tenants_list"))

        if User.query.filter_by(email=email).first():
            flash("E-mail já cadastrado", "danger")
            return redirect(url_for("admin.tenants_list"))

        tenant = Tenant(nome=nome, slug=slug, ativo=True)
        db.session.add(tenant)
        db.session.commit()

        admin_tenant = User(
            nome=nome,
            email=email,
            role="TENANT_ADMIN",
            tenant_id=tenant.id,
            ativo=True
        )
        admin_tenant.set_password(senha)

        db.session.add(admin_tenant)
        db.session.commit()

        flash("Barbearia criada com sucesso", "success")
        return redirect(url_for("admin.tenants_list"))

    tenants = Tenant.query.order_by(Tenant.criado_em.desc()).all()

    return render_template(
        "admin/tenants_list.html",
        tenants=tenants
    )



# =========================================================
# DETALHE
# =========================================================
@admin_bp.route("/tenants/<int:tenant_id>", methods=["GET"])
@login_required
def tenant_detail(tenant_id):

    if not current_user.is_admin_global():
        abort(403)

    tenant = Tenant.query.get_or_404(tenant_id)

    admins = User.query.filter_by(
        tenant_id=tenant.id,
        role="TENANT_ADMIN"
    ).all()

    return render_template(
        "admin/tenant_detail.html",
        tenant=tenant,
        admins=admins
    )



# =========================================================
# IMPERSONAÇÃO (ENTRAR NO SALÃO)
# =========================================================
@admin_bp.route("/tenants/<int:tenant_id>/access", methods=["GET", "POST"])
@login_required
def access_tenant(tenant_id):

    if not current_user.is_admin_global():
        abort(403)

    tenant = Tenant.query.get_or_404(tenant_id)

    admin_tenant = User.query.filter_by(
        tenant_id=tenant.id,
        role="TENANT_ADMIN",
        ativo=True
    ).first()

    if not admin_tenant:
        flash("Nenhum administrador encontrado para esta barbearia", "danger")
        return redirect(url_for("admin.tenant_detail", tenant_id=tenant.id))

    # 🔥 salva quem era o admin global
    session["original_admin_id"] = current_user.id

    login_user(admin_tenant)
    flash(f"Acessando {tenant.nome}", "success")

    return redirect(url_for("tenant.dashboard"))



# =========================================================
# VOLTAR PARA ADMIN GLOBAL
# =========================================================
@admin_bp.route("/return", methods=["GET"])
@login_required
def return_admin():

    admin_id = session.get("original_admin_id")

    if not admin_id:
        flash("Sessão administrativa não encontrada", "danger")
        return redirect(url_for("tenant.dashboard"))

    admin = User.query.get(admin_id)

    if not admin or not admin.is_admin_global():
        flash("Acesso administrativo inválido", "danger")
        return redirect(url_for("tenant.dashboard"))

    login_user(admin)
    session.pop("original_admin_id", None)

    flash("Você voltou para o painel administrativo", "success")
    return redirect(url_for("admin.dashboard"))

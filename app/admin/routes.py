from flask import (
    Blueprint, render_template,
    request, redirect, url_for,
    flash, abort
)
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.tenant import Tenant
from app.models.user import User

# =========================================================
# BLUEPRINT
# =========================================================

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

# =========================================================
# DASHBOARD ADMIN GLOBAL
# =========================================================

@admin_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """
    Dashboard do ADMIN_GLOBAL:
    - Cria barbearias
    - Cria admin da barbearia
    - Lista barbearias
    """

    # Segurança: apenas ADMIN_GLOBAL
    if not current_user.is_admin_global():
        abort(403)

    # ---------------------------------
    # CRIAR BARBEARIA
    # ---------------------------------
    if request.method == "POST":
        nome = request.form.get("nome")
        slug = request.form.get("slug")
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Validações básicas
        if not all([nome, slug, email, senha]):
            flash("Preencha todos os campos", "danger")
            return redirect(url_for("admin.dashboard"))

        if Tenant.query.filter_by(slug=slug).first():
            flash("Slug já existe", "danger")
            return redirect(url_for("admin.dashboard"))

        if User.query.filter_by(email=email).first():
            flash("E-mail já cadastrado", "danger")
            return redirect(url_for("admin.dashboard"))

        # Cria tenant
        tenant = Tenant(
            nome=nome,
            slug=slug
        )
        db.session.add(tenant)
        db.session.commit()

        # Cria admin da barbearia
        tenant_admin = User(
            nome=nome,
            email=email,
            role="TENANT_ADMIN",
            tenant_id=tenant.id
        )
        tenant_admin.senha = generate_password_hash(senha)

        db.session.add(tenant_admin)
        db.session.commit()

        flash("Barbearia criada com sucesso", "success")
        return redirect(url_for("admin.dashboard"))

    # ---------------------------------
    # LISTAGEM
    # ---------------------------------
    tenants = Tenant.query.order_by(Tenant.criado_em.desc()).all()

    return render_template(
        "admin_dashboard.html",
        tenants=tenants
    )

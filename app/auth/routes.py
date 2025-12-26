from flask import (
    Blueprint, render_template,
    request, redirect, url_for,
    flash
)
from flask_login import (
    login_user, logout_user,
    login_required
)

from app.extensions import db
from app.models.user import User

# =========================================================
# BLUEPRINT
# =========================================================

auth_bp = Blueprint(
    "auth",
    __name__
)

# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Login do sistema:
    - ADMIN_GLOBAL
    - TENANT_ADMIN
    - BARBER
    """

    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        next_url = request.args.get("next")

        if not email or not senha:
            flash("Preencha todos os campos", "danger")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(
            email=email,
            ativo=True,
            excluido=False
        ).first()

        if not user or not user.check_password(senha):
            flash("E-mail ou senha inválidos", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)

        # ---------------------------------
        # REDIRECIONAMENTO
        # ---------------------------------
        if next_url:
            return redirect(next_url)

        if user.is_admin_global():
            return redirect(url_for("admin.dashboard"))

        return redirect(url_for("tenant.dashboard"))

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

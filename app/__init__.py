from flask import Flask, render_template
from dotenv import load_dotenv
from flask_migrate import Migrate
from datetime import datetime

from config import get_config
from app.extensions import db, login_manager


# =========================================================
# FACTORY
# =========================================================
def create_app():
    """
    Factory principal da aplicação.
    Permite múltiplos ambientes, testes e escala futura.
    """

    # Carrega variáveis do .env
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)

    # Carrega configuração baseada no ambiente
    app.config.from_object(get_config())

    # =====================================================
    # INICIALIZA EXTENSÕES
    # =====================================================
    db.init_app(app)
    login_manager.init_app(app)

    # =====================================================
    # MIGRAÇÕES (Flask-Migrate / Alembic)
    # =====================================================
    migrate = Migrate()
    migrate.init_app(app, db)

    # =====================================================
    # FIX — GARANTIR COLUNAS SOMENTE NO POSTGRES (Render)
    # =====================================================
    try:
        from sqlalchemy import text
        with app.app_context():

            engine_name = db.session.bind.dialect.name

            if engine_name == "postgresql":
                # -------- SERVICES.excluido ----------
                db.session.execute(text("""
                    ALTER TABLE services
                    ADD COLUMN IF NOT EXISTS excluido BOOLEAN DEFAULT FALSE;
                """))

                db.session.commit()
                print("✔ Patch aplicado no Postgres (services.excluido)")

            else:
                print("ℹ Patch ignorado (não é Postgres)")

    except Exception as e:
        print("⚠ Erro garantindo colunas no banco:", e)

    # =====================================================
    # REGISTRO DE BLUEPRINTS
    # =====================================================
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.tenant.routes import tenant_bp
    from app.tenant.cash_routes import cash_bp
    from app.tenant.reports_routes import tenant_reports_bp
    from app.booking.routes import booking_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(cash_bp)
    app.register_blueprint(tenant_reports_bp)
    app.register_blueprint(booking_bp)

    # =====================================================
    # HEALTHCHECK (Render exige rota válida)
    # =====================================================
    @app.route("/healthz")
    def health():
        return "OK", 200

    # =====================================================
    # ROTA RAIZ — LANDING PAGE
    # =====================================================
    @app.route("/")
    def landing():
        return render_template("landing.html")

    # =====================================================
    # CONTEXT PROCESSOR GLOBAL
    # =====================================================
    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow}

    return app


# =========================================================
# FLASK-LOGIN
# =========================================================
from app.models.user import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# =========================================================
# SEED ADMIN GLOBAL
# =========================================================
def seed_admin():
    """
    Cria o usuário ADMIN_GLOBAL inicial
    apenas se não existir.
    NÃO é chamado automaticamente.
    """
    from werkzeug.security import generate_password_hash
    import os

    admin_email = os.getenv("ADMIN_EMAIL", "admin@admin.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            nome="Administrador",
            email=admin_email,
            senha=generate_password_hash(admin_password),
            role="ADMIN_GLOBAL",
            ativo=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✔ Admin global criado com sucesso")
    else:
        print("✔ Admin global já existe")

from app import create_app, db
from flask_migrate import upgrade

app = create_app()

# ==============================
# AUTO MIGRATION NO RENDER
# ==============================
with app.app_context():
    try:
        upgrade()
        print("✔️ Migrations aplicadas automaticamente")
    except Exception as e:
        print("⚠️ Erro ao aplicar migrations:", e)


# ==============================
# ENTRYPOINT LOCAL
# ==============================
if __name__ == "__main__":
    app.run()

from app import create_app, db
from sqlalchemy import text

app = create_app()

# ==============================
# AUTO FIX PARA BANCO NO RENDER
# ==============================
with app.app_context():
    conn = db.engine.connect()

    try:
        # Garantir coluna concluido_em
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns
                    WHERE table_name='appointments' 
                    AND column_name='concluido_em'
                ) THEN
                    ALTER TABLE appointments 
                    ADD COLUMN concluido_em TIMESTAMP NULL;
                END IF;
            END$$;
        """))
        print("✔ Coluna 'concluido_em' garantida no banco de dados")

        # Garantir coluna atualizado_em
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns
                    WHERE table_name='appointments' 
                    AND column_name='atualizado_em'
                ) THEN
                    ALTER TABLE appointments 
                    ADD COLUMN atualizado_em TIMESTAMP NULL;
                END IF;
            END$$;
        """))
        print("✔ Coluna 'atualizado_em' garantida no banco de dados")

    except Exception as e:
        print("⚠️ Erro garantindo colunas:", e)



# ==============================
# ENTRYPOINT LOCAL
# ==============================
if __name__ == "__main__":
    app.run()

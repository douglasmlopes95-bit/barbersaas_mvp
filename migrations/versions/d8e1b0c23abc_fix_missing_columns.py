from alembic import op
import sqlalchemy as sa


revision = "d8e1b0c23abc"
down_revision = "c10b43fb79cc"
branch_labels = None
depends_on = None


def column_exists_pg(table, column):
    """
    Verifica coluna no Postgres
    """
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = :table
            AND column_name = :column
        """),
        {"table": table, "column": column}
    )
    return result.scalar() is not None


def column_exists_sqlite(table, column):
    """
    Verifica coluna no SQLite
    """
    conn = op.get_bind()
    result = conn.execute(sa.text(f"PRAGMA table_info({table});")).fetchall()
    cols = [r[1] for r in result]
    return column in cols


def smart_exists(table, column):
    """
    Decide automaticamente conforme o banco
    """
    conn = op.get_bind()
    if conn.dialect.name == "sqlite":
        return column_exists_sqlite(table, column)
    return column_exists_pg(table, column)


def upgrade():

    # ================= SERVICES =================
    if not smart_exists("services", "barber_id"):
        op.add_column(
            "services",
            sa.Column("barber_id", sa.Integer(), nullable=True)
        )

    if not smart_exists("services", "excluido"):
        op.add_column(
            "services",
            sa.Column("excluido", sa.Boolean(), server_default="false", nullable=False)
        )

    # ================= APPOINTMENTS =================
    if not smart_exists("appointments", "concluido_em"):
        op.add_column(
            "appointments",
            sa.Column("concluido_em", sa.DateTime(), nullable=True)
        )

    if not smart_exists("appointments", "atualizado_em"):
        op.add_column(
            "appointments",
            sa.Column("atualizado_em", sa.DateTime(), nullable=True)
        )


def downgrade():
    pass

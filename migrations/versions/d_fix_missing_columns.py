from alembic import op
import sqlalchemy as sa

# Revisão atual
revision = 'fix_missing_columns'
down_revision = 'c10b43fb79cc'   # <-- CONFIRME que é sua última migration
branch_labels = None
depends_on = None


def column_exists(table, column):
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT 1
            FROM information_schema.columns
            WHERE table_name=:table
            AND column_name=:column
        """),
        {"table": table, "column": column}
    )
    return result.scalar() is not None


def upgrade():

    # ================= SERVICES =================
    if not column_exists("services", "barber_id"):
        op.add_column(
            "services",
            sa.Column("barber_id", sa.Integer(), nullable=True)
        )

    if not column_exists("services", "excluido"):
        op.add_column(
            "services",
            sa.Column("excluido", sa.Boolean(), server_default="false")
        )

    # ================= APPOINTMENTS =================
    if not column_exists("appointments", "concluido_em"):
        op.add_column(
            "appointments",
            sa.Column("concluido_em", sa.DateTime(), nullable=True)
        )

    if not column_exists("appointments", "atualizado_em"):
        op.add_column(
            "appointments",
            sa.Column("atualizado_em", sa.DateTime(), nullable=True)
        )


def downgrade():
    pass

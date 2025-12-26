"""link service to barber user

Revision ID: c10b43fb79cc
Revises: 552f3e0ad575
Create Date: 2025-12-26 01:42:30.831567
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c10b43fb79cc'
down_revision = '552f3e0ad575'
branch_labels = None
depends_on = None


def upgrade():
    # SERVICES
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('barber_id', sa.Integer(), nullable=True)
        )

        batch_op.create_index(
            batch_op.f('ix_services_barber_id'),
            ['barber_id'],
            unique=False
        )

        batch_op.create_foreign_key(
            'fk_services_barber_id',     # NOME OBRIGATÓRIO
            'users',                     # TABELA ALVO
            ['barber_id'],               # COLUNA LOCAL
            ['id'],                      # COLUNA REMOTA
            ondelete="SET NULL"
        )

    # TENANTS
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.alter_column(
            'ativo',
            existing_type=sa.BOOLEAN(),
            nullable=False
        )

        batch_op.create_index(
            batch_op.f('ix_tenants_slug'),
            ['slug'],
            unique=True
        )


def downgrade():
    # TENANTS
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_tenants_slug'))
        batch_op.alter_column(
            'ativo',
            existing_type=sa.BOOLEAN(),
            nullable=True
        )

    # SERVICES
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.drop_constraint(
            'fk_services_barber_id',
            type_='foreignkey'
        )

        batch_op.drop_index(batch_op.f('ix_services_barber_id'))
        batch_op.drop_column('barber_id')

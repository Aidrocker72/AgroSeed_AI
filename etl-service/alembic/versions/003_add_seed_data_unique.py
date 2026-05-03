"""Add unique constraint on seed_data (territory_id, name, date)

Revision ID: 003_add_seed_data_unique
Revises: 002_add_etl_runs
Create Date: 2026-05-02 00:00:00.000000

"""
from alembic import op

revision = '003_add_seed_data_unique'
down_revision = '002_add_etl_runs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Удаляем дубли перед созданием constraint: оставляем запись с наименьшим id
    op.execute("""
        DELETE FROM seed_data a
        USING seed_data b
        WHERE a.id > b.id
          AND a.territory_id = b.territory_id
          AND a.name = b.name
          AND a.date = b.date
    """)

    op.execute("""
        ALTER TABLE seed_data
        ADD CONSTRAINT uq_seed_data_territory_crop_date
        UNIQUE (territory_id, name, date)
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE seed_data
        DROP CONSTRAINT IF EXISTS uq_seed_data_territory_crop_date
    """)

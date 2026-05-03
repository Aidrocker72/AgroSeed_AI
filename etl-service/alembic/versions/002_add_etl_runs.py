"""Add etl_runs table

Revision ID: 002_add_etl_runs
Revises: 001_initial_migration
Create Date: 2026-05-02 00:00:00.000000

"""
from alembic import op

revision = '002_add_etl_runs'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS etl_runs (
            id SERIAL PRIMARY KEY,
            started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            completed_at TIMESTAMPTZ,
            status VARCHAR NOT NULL DEFAULT 'running',
            seed_data_count INTEGER DEFAULT 0,
            news_count INTEGER DEFAULT 0,
            data_source VARCHAR,
            error TEXT
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_etl_runs_id ON etl_runs (id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS etl_runs")

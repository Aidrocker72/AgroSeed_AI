"""Add exchange_rates table

Revision ID: 004_add_exchange_rates
Revises: 003_add_seed_data_unique
Create Date: 2026-05-02 00:00:00.000000

"""
from alembic import op

revision = '004_add_exchange_rates'
down_revision = '003_add_seed_data_unique'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id SERIAL PRIMARY KEY,
            currency VARCHAR(3) NOT NULL,
            date TIMESTAMPTZ NOT NULL,
            rate NUMERIC(12, 4) NOT NULL,
            CONSTRAINT uq_exchange_rate_currency_date UNIQUE (currency, date)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_exchange_rates_id ON exchange_rates (id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS exchange_rates")

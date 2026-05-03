"""Initial migration

Revision ID: 001_initial_migration
Revises:
Create Date: 2025-11-30 17:00:00.000000

"""
from alembic import op

revision = '001_initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR NOT NULL UNIQUE,
            password_hash VARCHAR NOT NULL,
            created_at TIMESTAMPTZ
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_id ON users (id)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS territories (
            id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_territories_id ON territories (id)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS seed_data (
            id SERIAL PRIMARY KEY,
            territory_id INTEGER NOT NULL REFERENCES territories(id),
            name VARCHAR NOT NULL,
            price NUMERIC(12, 2) NOT NULL,
            date TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_seed_data_id ON seed_data (id)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id SERIAL PRIMARY KEY,
            territory_id INTEGER NOT NULL REFERENCES territories(id),
            title VARCHAR NOT NULL,
            content TEXT NOT NULL,
            date TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_news_id ON news (id)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            territory_id INTEGER NOT NULL REFERENCES territories(id),
            created_at TIMESTAMPTZ NOT NULL,
            raw_data JSON NOT NULL,
            ai_result JSON NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_forecasts_id ON forecasts (id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS forecasts")
    op.execute("DROP TABLE IF EXISTS news")
    op.execute("DROP TABLE IF EXISTS seed_data")
    op.execute("DROP TABLE IF EXISTS territories")
    op.execute("DROP TABLE IF EXISTS users")

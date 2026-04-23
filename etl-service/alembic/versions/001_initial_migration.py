"""Initial migration

Revision ID: 001_initial_migration
Revises: 
Create Date: 2025-11-30 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create territories table
    op.create_table('territories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create seed_data table
    op.create_table('seed_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('territory_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('price', sa.Numeric(12, 2), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['territory_id'], ['territories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create news table
    op.create_table('news',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('territory_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['territory_id'], ['territories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop news table
    op.drop_table('news')
    
    # Drop seed_data table
    op.drop_table('seed_data')
    
    # Drop territories table
    op.drop_table('territories')
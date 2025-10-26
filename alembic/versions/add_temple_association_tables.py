"""add temple association tables

Revision ID: add_temple_association_tables
Revises: 9f84a1b10055
Create Date: 2025-10-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_temple_association_tables'
down_revision = '9f84a1b10055'
branch_labels = None
depends_on = None


def upgrade():
    # Create temple table first so association tables can reference it
    op.create_table(
        'temple',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('slug', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create temple_recommended_pujas association table
    op.create_table(
        'temple_recommended_pujas',
        sa.Column('temple_id', sa.Integer(), nullable=False),
        sa.Column('puja_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['temple_id'], ['temple.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['puja_id'], ['pujas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('temple_id', 'puja_id')
    )

    # Create temple_chadawas association table
    op.create_table(
        'temple_chadawas',
        sa.Column('temple_id', sa.Integer(), nullable=False),
        sa.Column('chadawa_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['temple_id'], ['temple.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chadawa_id'], ['chadawas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('temple_id', 'chadawa_id')
    )


def downgrade():
    op.drop_table('temple_chadawas')
    op.drop_table('temple_recommended_pujas')

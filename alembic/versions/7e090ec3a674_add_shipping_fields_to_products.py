"""Add shipping fields to products

Revision ID: 7e090ec3a674
Revises: af96049e7c18
Create Date: 2025-12-01 23:28:56.658373

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e090ec3a674'
down_revision = 'af96049e7c18'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add shipping_charge column
    op.add_column('products', sa.Column('shipping_charge', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'))
    
    # Add free_shipping_above column
    op.add_column('products', sa.Column('free_shipping_above', sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade() -> None:
    # Remove columns
    op.drop_column('products', 'free_shipping_above')
    op.drop_column('products', 'shipping_charge')

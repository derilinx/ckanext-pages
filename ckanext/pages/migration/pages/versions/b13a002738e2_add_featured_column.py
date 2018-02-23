"""add featured column

Revision ID: b13a002738e2
Revises: 1725892d1d94
Create Date: 2025-06-25 09:21:01.621646

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b13a002738e2'
down_revision = '1725892d1d94'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ckanext_pages', sa.Column('featured', sa.Boolean, default=False))


def downgrade():
    pass

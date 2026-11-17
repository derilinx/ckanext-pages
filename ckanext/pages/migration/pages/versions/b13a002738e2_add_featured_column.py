"""add featured column

Revision ID: b13a002738e2
Revises: a756dbd73ead
Create Date: 2025-06-25 09:21:01.621646

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b13a002738e2'
down_revision = 'a756dbd73ead'
branch_labels = None
depends_on = None


def upgrade():
    # Databases created with the legacy init_db() already have this column
    inspector = sa.inspect(op.get_bind())
    columns = [c["name"] for c in inspector.get_columns("ckanext_pages")]
    if "featured" not in columns:
        op.add_column('ckanext_pages', sa.Column('featured', sa.Boolean, default=False))


def downgrade():
    pass

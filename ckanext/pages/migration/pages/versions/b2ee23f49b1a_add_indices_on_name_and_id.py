"""add indices on name and id

Revision ID: b2ee23f49b1a
Revises: b13a002738e2
Create Date: 2025-06-25 09:29:19.093806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2ee23f49b1a'
down_revision = 'b13a002738e2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ckanext_pages_id_idx", "ckanext_pages", ["id"])
    op.create_index("ckanext_pages_name_idx", "ckanext_pages", ["name"])


def downgrade():
    op.drop_index("ckanext_pages_id_idx")
    op.drop_index("ckanext_pages_name_idx")

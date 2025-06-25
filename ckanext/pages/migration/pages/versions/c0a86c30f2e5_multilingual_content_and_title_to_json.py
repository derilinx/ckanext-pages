"""multilingual: content and title to json

Revision ID: c0a86c30f2e5
Revises: b2ee23f49b1a
Create Date: 2025-06-25 09:52:22.753916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0a86c30f2e5'
down_revision = 'b2ee23f49b1a'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('ckanext_pages', 'title', type_=sa.JSON, postgresql_using="json_build_object(lang, title)")
    op.alter_column('ckanext_pages', 'content', type_=sa.JSON, postgresql_using='json_build_object(lang, content)')


def downgrade():
    pass

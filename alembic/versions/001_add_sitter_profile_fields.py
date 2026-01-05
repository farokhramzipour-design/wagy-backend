"""add sitter profile fields

Revision ID: 001
Revises: 
Create Date: 2023-10-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to sitter_profiles table
    op.add_column('sitter_profiles', sa.Column('government_id_number', sa.String(), nullable=True))
    op.add_column('sitter_profiles', sa.Column('government_id_image', sa.String(), nullable=True))
    op.add_column('sitter_profiles', sa.Column('address', sa.String(), nullable=True))
    op.add_column('sitter_profiles', sa.Column('postal_code', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove columns from sitter_profiles table
    op.drop_column('sitter_profiles', 'government_id_number')
    op.drop_column('sitter_profiles', 'government_id_image')
    op.drop_column('sitter_profiles', 'address')
    op.drop_column('sitter_profiles', 'postal_code')

"""safe add profile_complete and resume fields to users

Revision ID: e1f2c3d4b5a6
Revises: d9acb5449f25
Create Date: 2025-11-10 (patched)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e1f2c3d4b5a6'
down_revision: Union[str, Sequence[str], None] = 'd9acb5449f25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema safely: add columns only if they are missing."""
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing_cols = [c['name'] for c in insp.get_columns('users')]

    if 'profile_complete' not in existing_cols:
        op.add_column(
            'users',
            sa.Column('profile_complete', sa.Boolean(), nullable=False, server_default=sa.text('false'))
        )

    if 'parsed_resume_mongo_id' not in existing_cols:
        op.add_column(
            'users',
            sa.Column('parsed_resume_mongo_id', sa.String(length=255), nullable=True)
        )

    if 'parsed_resume_summary' not in existing_cols:
        op.add_column(
            'users',
            sa.Column('parsed_resume_summary', sa.Text(), nullable=True)
        )


def downgrade() -> None:
    """Revert the upgrade by dropping the added columns if they exist."""
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing_cols = [c['name'] for c in insp.get_columns('users')]

    if 'parsed_resume_summary' in existing_cols:
        op.drop_column('users', 'parsed_resume_summary')

    if 'parsed_resume_mongo_id' in existing_cols:
        op.drop_column('users', 'parsed_resume_mongo_id')

    if 'profile_complete' in existing_cols:
        op.drop_column('users', 'profile_complete')

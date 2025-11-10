"""few changes

Revision ID: d9acb5449f25
Revises: 7ac8b2338c6b
Create Date: 2025-11-10 18:54:53.748438
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9acb5449f25'
down_revision: Union[str, Sequence[str], None] = '7ac8b2338c6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # make domains.name nullable
    op.alter_column(
        'domains', 'name',
        existing_type=sa.VARCHAR(length=100),
        nullable=True
    )

    # drop unique constraint safely (if present)
    op.execute("ALTER TABLE IF EXISTS domains DROP CONSTRAINT IF EXISTS domains_name_key")

    # create indexes idempotently
    op.execute("CREATE INDEX IF NOT EXISTS ix_domains_id ON domains (id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_domains_name ON domains (name)")

    # add project columns (nullable to be safe)
    op.add_column('projects', sa.Column('team_pending', sa.Boolean(), nullable=True))
    op.add_column('projects', sa.Column('team_pending_until', sa.DateTime(timezone=True), nullable=True))
    op.add_column('projects', sa.Column('solo_assigned', sa.Boolean(), nullable=True))
    op.add_column('projects', sa.Column('status', sa.String(length=50), nullable=True))

    # alter resumes.parsed_mongo_id length
    op.alter_column(
        'resumes', 'parsed_mongo_id',
        existing_type=sa.VARCHAR(length=50),
        type_=sa.String(length=100),
        existing_nullable=True
    )

    # make roles.name nullable
    op.alter_column(
        'roles', 'name',
        existing_type=sa.VARCHAR(length=100),
        nullable=True
    )

    # create role indexes idempotently
    op.execute("CREATE INDEX IF NOT EXISTS ix_roles_id ON roles (id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_roles_name ON roles (name)")

    # add team_projects columns (nullable)
    op.add_column('team_projects', sa.Column('team_pending', sa.Boolean(), nullable=True))
    op.add_column('team_projects', sa.Column('team_pending_until', sa.DateTime(timezone=True), nullable=True))
    op.add_column('team_projects', sa.Column('solo_assigned', sa.Boolean(), nullable=True))

    # add user parsed resume / profile flags (nullable first)
    op.add_column('users', sa.Column('profile_complete', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('parsed_resume_mongo_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('parsed_resume_summary', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # remove columns we added (reverse order)
    op.drop_column('users', 'parsed_resume_summary')
    op.drop_column('users', 'parsed_resume_mongo_id')
    op.drop_column('users', 'profile_complete')

    op.drop_column('team_projects', 'solo_assigned')
    op.drop_column('team_projects', 'team_pending_until')
    op.drop_column('team_projects', 'team_pending')

    op.execute("DROP INDEX IF EXISTS ix_roles_name")
    op.execute("DROP INDEX IF EXISTS ix_roles_id")

    op.alter_column('roles', 'name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)

    op.alter_column('resumes', 'parsed_mongo_id',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)

    op.drop_column('projects', 'status')
    op.drop_column('projects', 'solo_assigned')
    op.drop_column('projects', 'team_pending_until')
    op.drop_column('projects', 'team_pending')

    op.execute("DROP INDEX IF EXISTS ix_domains_name")
    op.execute("DROP INDEX IF EXISTS ix_domains_id")
    op.execute("ALTER TABLE IF EXISTS domains ADD CONSTRAINT domains_name_key UNIQUE (name)")

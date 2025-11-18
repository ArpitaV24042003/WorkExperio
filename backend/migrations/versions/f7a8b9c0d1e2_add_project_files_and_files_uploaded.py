"""add project_files table and files_uploaded field

Revision ID: f7a8b9c0d1e2
Revises: e1f2c3d4b5a6
Create Date: 2025-01-XX
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f7a8b9c0d1e2'
down_revision: Union[str, Sequence[str], None] = 'e1f2c3d4b5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add project_files table and files_uploaded column."""
    conn = op.get_bind()
    insp = sa.inspect(conn)
    
    # Check if project_files table already exists
    existing_tables = insp.get_table_names()
    
    if 'project_files' not in existing_tables:
        # Create project_files table
        op.create_table(
            'project_files',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('project_id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('filename', sa.String(length=255), nullable=False),
            sa.Column('file_path', sa.String(length=500), nullable=False),
            sa.Column('file_size', sa.Integer(), nullable=False),
            sa.Column('file_type', sa.String(length=50), nullable=True),
            sa.Column('mime_type', sa.String(length=100), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('uploaded_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        # Create indexes
        op.create_index('ix_project_files_project_id', 'project_files', ['project_id'], unique=False)
        op.create_index('ix_project_files_user_id', 'project_files', ['user_id'], unique=False)
        print("✅ Created project_files table")
    else:
        print("⚠️  project_files table already exists, skipping creation")
    
    # Check if files_uploaded column exists in user_stats
    if 'user_stats' in existing_tables:
        existing_cols = [c['name'] for c in insp.get_columns('user_stats')]
        
        if 'files_uploaded' not in existing_cols:
            op.add_column(
                'user_stats',
                sa.Column('files_uploaded', sa.Integer(), nullable=False, server_default=sa.text('0'))
            )
            print("✅ Added files_uploaded column to user_stats")
        else:
            print("⚠️  files_uploaded column already exists in user_stats")
    else:
        print("⚠️  user_stats table does not exist, files_uploaded will be added when table is created")


def downgrade() -> None:
    """Revert the upgrade."""
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing_tables = insp.get_table_names()
    
    # Drop files_uploaded column if it exists
    if 'user_stats' in existing_tables:
        existing_cols = [c['name'] for c in insp.get_columns('user_stats')]
        if 'files_uploaded' in existing_cols:
            op.drop_column('user_stats', 'files_uploaded')
            print("✅ Dropped files_uploaded column from user_stats")
    
    # Drop project_files table if it exists
    if 'project_files' in existing_tables:
        try:
            op.drop_index('ix_project_files_user_id', table_name='project_files')
        except:
            pass
        try:
            op.drop_index('ix_project_files_project_id', table_name='project_files')
        except:
            pass
        op.drop_table('project_files')
        print("✅ Dropped project_files table")


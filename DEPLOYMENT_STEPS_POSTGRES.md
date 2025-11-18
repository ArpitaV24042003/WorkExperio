# PostgreSQL Deployment Steps for Render

This guide covers deploying the WorkExperio backend with PostgreSQL on Render, including the new features (file uploads, extended sessions, etc.).

## Prerequisites

1. PostgreSQL database on Render
2. Backend service on Render
3. Environment variables configured

## Step 1: Environment Variables

Ensure these are set in your Render backend service:

- `DATABASE_URL` - Your PostgreSQL connection string (automatically set by Render if using Render PostgreSQL)
- `SECRET_KEY` - A secure secret key for JWT tokens
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Optional (defaults to 43200 = 30 days)
- `ALLOW_ORIGINS` - Comma-separated list of allowed origins (e.g., your frontend URL)

## Step 2: Run Database Migrations

### Option A: Automatic Migration on Deploy (Recommended)

Add this to your Render build command or create a startup script:

```bash
# In your build command or startup script
cd backend && alembic upgrade head
```

Or modify your `Procfile` or startup command to include:

```bash
python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Option B: Manual Migration via Render Shell

1. Go to Render Dashboard > Your Backend Service > Shell
2. Run:

```bash
cd backend
alembic upgrade head
```

## Step 3: Verify Database Tables

After migration, verify the new tables exist:

```sql
-- Check if project_files table exists
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name = 'project_files';

-- Check if files_uploaded column exists in user_stats
SELECT column_name FROM information_schema.columns
WHERE table_name = 'user_stats' AND column_name = 'files_uploaded';
```

## Step 4: Create Upload Directory

The file upload functionality requires a directory for storing files. On Render, you may need to:

1. Use a persistent volume, OR
2. Store files in a cloud storage service (S3, etc.), OR
3. Use the temporary filesystem (files will be lost on restart)

For production, consider using cloud storage. For now, the code uses `backend/uploads/projects/` which will work but files won't persist across restarts.

## Step 5: Test the Deployment

1. **Test Authentication**: Sign up/login should work with 30-day token expiration
2. **Test File Upload**: Create a project, form a team, and try uploading a file
3. **Test Performance Report**: Check that file uploads appear in performance metrics
4. **Test Chat**: Verify the improved chat interface works
5. **Test AI Assistant**: Check that enhanced AI responses work

## Migration Details

The new migration (`f7a8b9c0d1e2_add_project_files_and_files_uploaded.py`) adds:

1. **project_files table**:

   - Stores uploaded files for projects
   - Links to projects and users
   - Tracks file metadata (size, type, mime type, etc.)

2. **files_uploaded column** in `user_stats`:
   - Tracks number of files uploaded per user
   - Used in performance evaluation

## Troubleshooting

### Migration Fails

If migration fails, check:

- Database connection string is correct
- Database user has CREATE TABLE permissions
- Previous migrations have been applied

### Tables Not Created

If tables aren't created:

1. Check application logs for errors
2. Run `alembic current` to see current migration version
3. Run `alembic history` to see all migrations
4. Run `alembic upgrade head` manually

### File Uploads Not Working

1. Check that `backend/uploads/projects/` directory exists and is writable
2. Check file size limits (currently 100MB max)
3. Check application logs for upload errors

## Rollback (if needed)

To rollback the migration:

```bash
alembic downgrade -1
```

This will:

- Remove `files_uploaded` column from `user_stats`
- Drop `project_files` table

## Notes

- Token expiration is now 30 days (43200 minutes) instead of 60 minutes
- File uploads contribute to performance scores
- All new features are backward compatible with existing data

# Database Persistence Fix - Critical Issue

## 🚨 Problem Identified

Your data is being lost because the application is likely using **SQLite** instead of **PostgreSQL** on Render.

**Why this happens:**

- If `DATABASE_URL` is not set in Render environment variables, the app falls back to SQLite
- SQLite on Render uses **ephemeral storage** (temporary filesystem)
- **ALL DATA IS LOST** when the service restarts or redeploys

## ✅ Solution: Set DATABASE_URL in Render

### Step 1: Get Your PostgreSQL Connection String

1. Go to **Render Dashboard**: https://dashboard.render.com
2. Find your **PostgreSQL database** service (not the backend)
3. Click on it
4. Go to **"Info"** tab
5. Find **"Internal Database URL"** or **"Connection String"**
6. Copy the entire connection string

It should look like:

```
postgresql://user:password@host:port/database?sslmode=require
```

### Step 2: Add DATABASE_URL to Backend Service

1. Go back to Render Dashboard
2. Select your **backend service** (workexperio-backend)
3. Click **"Environment"** tab
4. Look for `DATABASE_URL` in the list
5. If it's **NOT there** or **empty**:
   - Click **"Add Environment Variable"**
   - **Key:** `DATABASE_URL`
   - **Value:** Paste your PostgreSQL connection string
   - Click **"Save Changes"**
6. Render will automatically redeploy

### Step 3: Verify Configuration

After deployment, check the logs. You should see:

```
✅ Using PostgreSQL database - data will persist!
✅ Database tables initialized successfully
```

**NOT:**

```
⚠️ WARNING: Using SQLite database!
⚠️ SQLite on Render uses ephemeral storage - ALL DATA WILL BE LOST!
```

### Step 4: Test Database Persistence

1. Visit: `https://workexperio-backend.onrender.com/health`
2. Check the response - it should show:
   - `"database_type": "PostgreSQL (✅ Persistent)"`
   - `"warning": null`

Or visit: `https://workexperio-backend.onrender.com/diagnostics/database`

- Should show `"is_persistent": true`
- Should show `"database_type": "PostgreSQL"`

## 🔍 How to Check Current Status

### Option 1: Check Health Endpoint

Visit: `https://workexperio-backend.onrender.com/health`

Look for:

- `database_type`: Should be "PostgreSQL", NOT "SQLite"
- `warning`: Should be `null`, NOT a warning about SQLite

### Option 2: Check Diagnostics Endpoint

Visit: `https://workexperio-backend.onrender.com/diagnostics/database`

Look for:

- `is_persistent`: Should be `true`
- `database_type`: Should be "PostgreSQL"
- `warning`: Should be `null`

### Option 3: Check Render Logs

After restart, look for these messages:

- ✅ `"✅ Using PostgreSQL database - data will persist!"` = GOOD
- ❌ `"⚠️ WARNING: Using SQLite database!"` = BAD - needs fix

## 📋 Complete Checklist

- [ ] PostgreSQL database exists in Render
- [ ] `DATABASE_URL` is set in backend service environment variables
- [ ] `DATABASE_URL` points to PostgreSQL (starts with `postgresql://`)
- [ ] Backend service has been redeployed after setting `DATABASE_URL`
- [ ] Health endpoint shows PostgreSQL, not SQLite
- [ ] Test: Create user → Restart service → User still exists

## 🚨 If DATABASE_URL is Already Set

If `DATABASE_URL` is already set but data is still being lost:

1. **Verify the connection string is correct:**

   - Check it starts with `postgresql://` (not `postgres://`)
   - Check it includes `?sslmode=require` for Render
   - Test the connection string manually

2. **Check if it's pointing to the right database:**

   - Make sure it's your Render PostgreSQL, not a local one
   - Verify the database name matches

3. **Check Render logs for connection errors:**

   - Look for PostgreSQL connection errors
   - Check if tables are being created

4. **Run migrations:**
   ```bash
   # In Render Shell or locally with DATABASE_URL set
   alembic upgrade head
   ```

## 💡 Why This Happens

Render's filesystem is **ephemeral** - it gets wiped on each deploy/restart. Only:

- ✅ **PostgreSQL databases** (separate service) persist data
- ❌ **SQLite files** (in filesystem) are lost on restart

The app defaults to SQLite if `DATABASE_URL` is not set, which causes data loss.

## ✅ After Fixing

Once `DATABASE_URL` is properly set:

- ✅ All user data persists
- ✅ All projects persist
- ✅ All tasks persist
- ✅ Login works (no need to signup again)
- ✅ Data survives restarts and deploys

## 🔧 Quick Test

1. Set `DATABASE_URL` in Render
2. Wait for redeploy
3. Create a test user
4. Restart the service (or wait for auto-restart)
5. Try to login with the test user
6. If login works → ✅ Fixed!
7. If login fails → Check logs and verify `DATABASE_URL`

---

**This is a critical fix - without it, all data will be lost on every restart!**

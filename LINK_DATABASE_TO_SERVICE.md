# Link Database to Service in Render

## 🚨 The Issue

Render's `fromDatabase` in `render.yaml` **only works with Blueprint deployments**, not Git-based deployments. That's why `DATABASE_URL` is not being set automatically.

## ✅ Solution: Link Database in Render Dashboard

### Step 1: Link Database to Backend Service

1. **Render Dashboard** → **Backend service** (workexperio-backend)
2. **Look for "Connections" or "Linked Resources"** section
3. **Or go to "Settings" tab** → Look for database connection options
4. **Find "Link Database" or "Connect Database"** button
5. **Select** `workexperio-database` from the list
6. **Click "Link" or "Connect"**

This will automatically set `DATABASE_URL` environment variable!

### Step 2: Verify DATABASE_URL is Set

1. **Backend service** → **Environment tab**
2. **Look for `DATABASE_URL`** - it should now be there automatically
3. **Check its value** - should have the complete connection string

### Step 3: Redeploy (if needed)

After linking, Render should automatically redeploy, or you can manually trigger a redeploy.

## 🎯 Alternative: Set DATABASE_URL Manually (If Linking Doesn't Work)

If you can't find the "Link Database" option:

1. **PostgreSQL service** → **Info tab** → **Copy "Internal Database URL"**
2. **Backend service** → **Environment tab**
3. **Add `DATABASE_URL`** with the copied connection string
4. **Make sure it ends with `?sslmode=require`**
5. **Save and redeploy**

## ✅ After Linking

Check logs. You should see:
```
✅ Using PostgreSQL database - data will persist!
✅ Database tables initialized successfully
```

---

**Link the database to your backend service in Render Dashboard - this will automatically set DATABASE_URL!**


# Automatically Link Database to Service

## 🎯 The Solution: Link Database in Render Dashboard

Render's `fromDatabase` in `render.yaml` **only works with Blueprint deployments**. For Git-based deployments, you need to **link the database manually** in Render Dashboard, which will **automatically set DATABASE_URL**.

## ✅ Step-by-Step: Link Database

### Option 1: Link from Backend Service (Recommended)

1. **Render Dashboard** → **Backend service** (workexperio-backend)
2. **Look for "Connections" or "Linked Resources"** section (usually in Settings or Info tab)
3. **Click "Link Database" or "Connect Database"** button
4. **Select** `workexperio-database` from the dropdown
5. **Click "Link" or "Connect"**
6. **Render will automatically:**
   - Set `DATABASE_URL` environment variable
   - Use the correct, current password
   - Link the database to your service

### Option 2: Link from Database Service

1. **Render Dashboard** → **PostgreSQL service** (workexperio-database)
2. **Look for "Connected Services" or "Links"** section
3. **Click "Link Service" or "Connect Service"**
4. **Select** `workexperio-backend` from the list
5. **Click "Link"**

### Option 3: Manual DATABASE_URL (If Linking Doesn't Work)

If you can't find the link option:

1. **PostgreSQL service** → **Info tab** → **Copy "Internal Database URL"**
2. **Backend service** → **Environment tab**
3. **Add `DATABASE_URL`** with the copied connection string
4. **Save and redeploy**

## ✅ After Linking

1. **Check Environment tab** - `DATABASE_URL` should be there automatically
2. **Check logs** after redeploy - should see:
   ```
   ✅ Using PostgreSQL database - data will persist!
   ✅ Database tables initialized successfully
   ```

## 🎯 Benefits of Linking

- ✅ **Automatic DATABASE_URL** - Set by Render
- ✅ **Current password** - Always up-to-date
- ✅ **Data persists** - PostgreSQL is separate service
- ✅ **Works after restart** - Database persists independently
- ✅ **No manual management** - Render handles it

---

**Link the database in Render Dashboard - this will automatically set DATABASE_URL and solve the password issue!**


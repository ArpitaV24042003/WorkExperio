# Automatic Database Setup via render.yaml

## ✅ Solution: Use render.yaml for Automatic Database Connection

Instead of manually setting `DATABASE_URL` in environment variables, we can configure `render.yaml` to **automatically** get the connection string from the PostgreSQL database service.

## 🎯 How It Works

The `render.yaml` file now has:
```yaml
- key: DATABASE_URL
  fromDatabase:
    name: workexperio-database
    property: connectionString
```

This tells Render to:
1. **Automatically find** the `workexperio-database` service
2. **Get the connection string** from it
3. **Set DATABASE_URL** automatically with the **correct, current password**

## ✅ Steps to Use This

### Step 1: Remove Manual DATABASE_URL

1. **Render Dashboard** → **Backend service** → **Environment tab**
2. **Find `DATABASE_URL`** (if it exists)
3. **DELETE it completely**
4. **Save Changes**

Render will now use the automatic connection from `render.yaml`!

### Step 2: Verify Database Name in render.yaml

Make sure the database name in `render.yaml` matches your PostgreSQL service name:
- **Service name in Render:** `workexperio-database`
- **In render.yaml:** `name: workexperio-database` ✅

### Step 3: Redeploy

After removing manual DATABASE_URL:
1. **Render will automatically redeploy**
2. **It will set DATABASE_URL automatically** from the database
3. **This connection string will have the CORRECT password!**

## ✅ Benefits

- ✅ **No manual password management** - Render handles it
- ✅ **Always uses current password** - Automatically updated
- ✅ **Data persists** - PostgreSQL persists data permanently
- ✅ **Works after restart** - Database is separate service
- ✅ **No environment variable needed** - Set automatically

## 🔍 Verify It's Working

After redeploy, check logs. You should see:
```
✅ Using PostgreSQL database - data will persist!
✅ Database tables initialized successfully
```

Or visit: `https://workexperio-backend.onrender.com/diagnostics/database`
- Should show: `"connection_test": "✅ Connected"`
- Should show: `"is_persistent": true`

## 📋 What Happens

1. **Render reads `render.yaml`**
2. **Finds `workexperio-database` service**
3. **Gets the connection string** (with current password)
4. **Sets `DATABASE_URL` automatically**
5. **Your app connects** with the correct credentials

---

**Remove DATABASE_URL from environment variables and let render.yaml handle it automatically!**


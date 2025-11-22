# Exact DATABASE_URL Configuration

## From Your Render Dashboard

Based on your Render dashboard, here's the exact connection string you need:

### Internal Database URL (from Render):
```
postgresql://workexperio_sopi_user:iF5kjz3zyGYDqj8f1Cxer4Bsa4ciJZaK@dpg-d4ddu96mcj7s73dvtml0-a/workexperio_sopi
```

### Complete Connection String (with SSL):
The Internal Database URL from Render might be missing the full hostname and SSL mode. Use this complete version:

```
postgresql://workexperio_sopi_user:iF5kjz3zyGYDqj8f1Cxer4Bsa4ciJZaK@dpg-d4ddu96mcj7s73dvtml0-a.oregon-postgres.render.com:5432/workexperio_sopi?sslmode=require
```

## ✅ Steps to Fix

### Option 1: Use Render's Internal Database URL Directly (Recommended)

1. **Render Dashboard** → **PostgreSQL service (workexperio_db)** → **Info tab**
2. **Click the COPY button** next to "Internal Database URL"
3. **Go to Backend service** → **Environment tab**
4. **Edit `DATABASE_URL`** → **Paste the copied URL**
5. **If it doesn't end with `?sslmode=require`, add it:**
   - If the URL ends with `/workexperio_sopi`, change it to `/workexperio_sopi?sslmode=require`
6. **Save and wait for redeploy**

### Option 2: Use Complete Connection String

If the Internal Database URL from Render doesn't work, use this complete version:

```
postgresql://workexperio_sopi_user:iF5kjz3zyGYDqj8f1Cxer4Bsa4ciJZaK@dpg-d4ddu96mcj7s73dvtml0-a.oregon-postgres.render.com:5432/workexperio_sopi?sslmode=require
```

**Steps:**
1. **Render Dashboard** → **Backend service** → **Environment tab**
2. **Edit `DATABASE_URL`**
3. **Paste the complete connection string above**
4. **Save and wait for redeploy**

## 🔍 Database Details from Your Dashboard

- **Database Service Name:** `workexperio_db`
- **Port:** `5432`
- **Database Name:** `workexperio_sopi`
- **Username:** `workexperio_sopi_user`
- **Password:** `iF5kjz3zyGYDqj8f1Cxer4Bsa4ciJZaK`
- **Host:** `dpg-d4ddu96mcj7s73dvtml0-a.oregon-postgres.render.com`

## ✅ After Updating

Check Render logs. You should see:
```
✅ Database connection successful
✅ Tables created successfully
✅ Using PostgreSQL database - data will persist!
```

## 🎯 Quick Test

1. Update DATABASE_URL in Render
2. Wait for redeploy
3. Visit: `https://workexperio-backend.onrender.com/diagnostics/database`
4. Should show: `"connection_test": "✅ Connected"`

---

**Important:** I've updated `render.yaml` to use the correct database name (`workexperio_db`). But you still need to update `DATABASE_URL` in Render Dashboard environment variables!


# New Database Setup - Complete Connection String

## ✅ New Database Details

- **Database Name:** `workexperiodb`
- **Username:** `workexperiodb_user`
- **Password:** `q9fWCuAxAdHrrWFNJzAqpsWotLgq8048`
- **Service ID:** `dpg-d4gqmp75r7bs73bem4u0-a`

## 🔗 Complete Connection String

The Internal Database URL you provided is missing the full hostname, port, and SSL mode. Use this **complete** connection string:

```
postgresql://workexperiodb_user:q9fWCuAxAdHrrWFNJzAqpsWotLgq8048@dpg-d4gqmp75r7bs73bem4u0-a.oregon-postgres.render.com:5432/workexperiodb?sslmode=require
```

## 📋 Step-by-Step Setup

### Step 1: Update DATABASE_URL in Render Dashboard

1. **Render Dashboard** → **Backend service** (workexperio-backend)
2. **Environment tab**
3. **Find `DATABASE_URL`** (or add it if it doesn't exist)
4. **Edit it** and paste this complete connection string:
   ```
   postgresql://workexperiodb_user:q9fWCuAxAdHrrWFNJzAqpsWotLgq8048@dpg-d4gqmp75r7bs73bem4u0-a.oregon-postgres.render.com:5432/workexperiodb?sslmode=require
   ```
5. **Verify it ends with `?sslmode=require`**
6. **Save Changes**
7. **Wait for redeploy** (2-3 minutes)

### Step 2: Verify render.yaml is Updated

I've updated `render.yaml` to use the new database:
- Database name: `workexperio-database`
- This will work for future deployments

### Step 3: Verify Connection

After redeploy, check logs. You should see:
```
✅ Using PostgreSQL database - data will persist!
✅ Database tables initialized successfully
```

Or visit: `https://workexperio-backend.onrender.com/diagnostics/database`
- Should show: `"connection_test": "✅ Connected"`
- Should show: `"is_persistent": true`

## ✅ After Setup

1. **Test connection** - Should work now!
2. **Create a test user** - Verify data persistence
3. **Restart service** - Data should still be there
4. **Login with test user** - Should work after restart

---

**Use the complete connection string above - it has everything needed (hostname, port, SSL mode)!**


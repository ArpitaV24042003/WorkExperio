# Use Render's Automatic Database Connection

## 🎯 The Real Solution: Let Render Set DATABASE_URL Automatically

Your `render.yaml` is configured to automatically get the connection string from the database. But if you have a **manual DATABASE_URL** in environment variables, it's overriding the automatic one!

## ✅ Step 1: Remove Manual DATABASE_URL

1. **Render Dashboard** → **Backend service** (workexperio-backend)
2. **Environment tab**
3. **Find `DATABASE_URL`** in the list
4. **DELETE it completely** (click delete/remove button)
5. **Save Changes**

This will let Render's `fromDatabase` in `render.yaml` automatically set the correct connection string!

## ✅ Step 2: Verify render.yaml Configuration

Your `render.yaml` has:
```yaml
- key: DATABASE_URL
  fromDatabase:
    name: workexperio_db
    property: connectionString
```

This tells Render to **automatically** get the connection string from the `workexperio_db` database.

## ✅ Step 3: Redeploy

After removing the manual DATABASE_URL:
1. **Render will automatically redeploy**
2. **It will set DATABASE_URL automatically** from the database
3. **This connection string will have the CORRECT password!**

## 🔍 Why This Works

- Render's `fromDatabase` gets the connection string **directly from the database service**
- It uses the **current, correct password** that Render knows
- No manual copying needed - Render handles it automatically!

## ✅ After Removing Manual DATABASE_URL

Check logs. You should see:
```
✅ Using PostgreSQL database - data will persist!
✅ Database tables initialized successfully
```

## 🎯 Alternative: Check What Render Actually Sets

After removing manual DATABASE_URL and redeploying:

1. **Backend service** → **Environment tab**
2. **Look for `DATABASE_URL`** - it should be there automatically
3. **Check its value** - this is what Render automatically set
4. **If it's still wrong**, there might be an issue with the database itself

## 📋 Quick Checklist

- [ ] Removed manual DATABASE_URL from backend environment variables
- [ ] Saved changes (Render will redeploy)
- [ ] Waited for redeploy (2-3 minutes)
- [ ] Checked logs for success message
- [ ] Verified DATABASE_URL is set automatically by Render
- [ ] Tested: Create user → Restart → Login works

---

**Remove the manual DATABASE_URL and let Render set it automatically - this will use the correct password!**


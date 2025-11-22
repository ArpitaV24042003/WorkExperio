# Troubleshoot Database Connection - Step by Step

## 🔍 Step 1: Check What DATABASE_URL is Actually Being Used

After your next deploy, visit:

```
https://workexperio-backend.onrender.com/diagnostics/database
```

This will show you:

- What database type is being used
- If DATABASE_URL is set
- Connection test results
- Specific error messages

## 🚨 Common Issues and Fixes

### Issue 1: Password Authentication Failed

**Error:** `password authentication failed for user "workexperio_sopi_user"`

**Cause:** The password in `DATABASE_URL` is outdated or incorrect.

**Fix:**

1. **Go to Render Dashboard** → Your **PostgreSQL database service**
2. Click **"Info"** tab
3. Find **"Internal Database URL"** (NOT External Database URL)
4. Click the **copy icon** next to it
5. **Go to Backend service** → **Environment** tab
6. **Delete the entire old DATABASE_URL value**
7. **Paste the NEW Internal Database URL**
8. **Verify it ends with `?sslmode=require`**
9. **Save** and wait for redeploy

**Important:** Use "Internal Database URL", not "External Database URL"!

### Issue 2: DATABASE_URL Not Being Read

**Symptoms:** Still using SQLite even after setting DATABASE_URL

**Fix:**

1. In Render → Backend service → Environment tab
2. Check if `DATABASE_URL` exists
3. If it doesn't exist, **add it** (don't just edit)
4. Make sure there are **no spaces** before/after the value
5. Make sure it's exactly: `DATABASE_URL` (case-sensitive)
6. Save and redeploy

### Issue 3: Special Characters in Password

**Symptoms:** Connection fails even with correct password

**Fix:**
If your PostgreSQL password has special characters (like `@`, `#`, `%`, etc.):

1. The password in the connection string needs to be **URL-encoded**
2. Or better: **Reset the PostgreSQL password** in Render
3. Then use the new connection string Render provides

### Issue 4: Connection String Format Wrong

**Correct format:**

```
postgresql://username:password@host:port/database?sslmode=require
```

**Check:**

- Starts with `postgresql://` (not `postgres://`)
- Has `?sslmode=require` at the end
- No extra spaces or line breaks
- Password doesn't have unencoded special characters

## 🔧 Step-by-Step Diagnostic Process

### Step 1: Check Current Status

Visit: `https://workexperio-backend.onrender.com/diagnostics/database`

Look for:

- `database_type`: Should be "PostgreSQL"
- `connection_test`: Should be "✅ Connected"
- `is_persistent`: Should be `true`

### Step 2: Check Render Environment Variables

1. Render Dashboard → Backend service → Environment tab
2. Find `DATABASE_URL`
3. Check if it exists and has a value
4. Verify it starts with `postgresql://`

### Step 3: Get Fresh Connection String

1. Render Dashboard → PostgreSQL service → Info tab
2. Copy "Internal Database URL"
3. This is the **CURRENT, CORRECT** connection string

### Step 4: Update and Test

1. Paste into Backend service → Environment → DATABASE_URL
2. Save
3. Wait for redeploy (2-3 minutes)
4. Check logs for: `✅ Using PostgreSQL database - data will persist!`
5. Visit diagnostics endpoint again to verify

## 🎯 Quick Test After Fix

1. Create a test user
2. Create a test project
3. **Manually restart** the backend service in Render
4. Try to login with test user
5. Check if test project still exists

If both work → ✅ **FIXED!**

## 📋 Checklist

- [ ] DATABASE_URL exists in Render backend environment variables
- [ ] DATABASE_URL uses "Internal Database URL" from PostgreSQL service
- [ ] DATABASE_URL starts with `postgresql://`
- [ ] DATABASE_URL ends with `?sslmode=require`
- [ ] No extra spaces in the connection string
- [ ] Backend service has been redeployed after setting DATABASE_URL
- [ ] Logs show "✅ Using PostgreSQL database"
- [ ] Diagnostics endpoint shows "✅ Connected"
- [ ] Test: Create user → Restart → Login works

## 🆘 Still Not Working?

If you've tried everything and still get password errors:

1. **Reset PostgreSQL Password:**

   - Render Dashboard → PostgreSQL service
   - Go to "Settings" or "Info" tab
   - Look for "Reset Password" or "Change Password"
   - Generate a new password
   - Get the new "Internal Database URL"
   - Update DATABASE_URL in backend

2. **Check PostgreSQL Service Status:**

   - Make sure PostgreSQL service is running (not paused)
   - Check if it's a free tier (might have limitations)

3. **Verify Network Access:**

   - Use "Internal Database URL" (works within Render network)
   - Don't use "External Database URL" (requires IP whitelisting)

4. **Check for Multiple DATABASE_URL:**
   - Make sure there's only ONE DATABASE_URL in environment variables
   - Remove any duplicates

---

**The most common issue is using an OLD connection string. Always get a fresh one from Render PostgreSQL service!**

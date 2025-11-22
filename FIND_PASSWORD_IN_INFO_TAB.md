# Find Password in Info Tab (No Settings Tab)

## ✅ The Password is in the "Info" Tab!

Since you don't see a "Settings" tab, the password and connection string are in the **"Info" tab** where you are now.

## 📋 Step-by-Step: Get Connection String from Info Tab

### Step 1: Find "Internal Database URL" in Info Tab

1. **You're already on the "Info" tab** (it's highlighted in purple)
2. **Scroll down** in the Info tab
3. **Look for these fields:**
   - **Port:** `5432`
   - **Database:** `workexperio_sopi`
   - **Username:** `workexperio_sopi_user`
   - **Password:** (with an eye icon 👁️ to show/hide it)
   - **Internal Database URL:** (with a copy icon 📋)

### Step 2: Copy Internal Database URL

1. **Find "Internal Database URL"** field
2. **Click the COPY icon** (📋) next to it
3. **This is your COMPLETE connection string with the CORRECT password!**

### Step 3: Update Backend DATABASE_URL

1. **Go to Backend service** (workexperio-backend) in Render
2. **Environment tab** → **Edit `DATABASE_URL`**
3. **DELETE old value**
4. **PASTE the Internal Database URL** you just copied
5. **Make sure it ends with `?sslmode=require`**
   - If it doesn't, add `?sslmode=require` at the end
6. **Save Changes**
7. **Wait for redeploy**

## 🔍 Alternative: Check "Connect" Dropdown

If you don't see the password fields:

1. **Look at the top right** of the Info tab
2. **Find the "Connect" dropdown button**
3. **Click it** - it might show connection options
4. **Look for "Internal Database URL"** or connection string there

## 🎯 What to Look For

In the Info tab, you should see something like:

```
Port: 5432
Database: workexperio_sopi
Username: workexperio_sopi_user
Password: [eye icon] [copy icon]
Internal Database URL: postgresql://... [copy icon]
External Database URL: ... [copy icon]
```

**Use the "Internal Database URL"** - it has everything correct!

## ✅ After Copying Internal Database URL

1. **Paste it into `DATABASE_URL`** in backend service
2. **Verify it ends with `?sslmode=require`**
3. **Save and redeploy**
4. **Check logs** - should see `✅ Database connection successful`

---

**The password and connection string are in the Info tab - scroll down to find "Internal Database URL" and copy it!**


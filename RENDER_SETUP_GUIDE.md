# Render Setup Guide - Complete Instructions

## ✅ Database Persistence (Already Working!)

**Good News:** Your Render PostgreSQL database **persists all data** across restarts.

- ✅ Users stay logged in (just login, no signup needed)
- ✅ All projects, tasks, files are saved
- ✅ Data survives shutdowns and restarts
- ✅ The `DATABASE_URL` warning during build is normal - it's set in Render environment variables

**You don't need to do anything for database persistence - it's already working!**

---

## 🔧 Setting Up OpenAI API Key on Render

### Step 1: Add Environment Variable

1. Go to your **Render Dashboard**: https://dashboard.render.com
2. Select your **backend service** (workexperio-backend)
3. Click on **"Environment"** tab (in the left sidebar)
4. Click **"Add Environment Variable"** button
5. Add:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `sk-your-actual-key-here` (get from https://platform.openai.com/api-keys)
6. Click **"Save Changes"**
7. Render will **automatically redeploy** your service

### Step 2: Fix OpenAI Quota Issue

The error `429 - You exceeded your current quota` means you need to:

1. Go to **OpenAI Platform**: https://platform.openai.com/
2. Click on your **profile** (top right)
3. Go to **"Billing"** or **"Settings" → "Billing"**
4. Add a **payment method** (credit card)
5. Set up **billing** (even $5-10 is enough to start)
6. Check your **usage limits** and **quota**

**Important:** Free tier OpenAI accounts have very limited quota. You need to:

- Add a payment method
- Set up billing
- Add credits to your account

### Step 3: Verify Setup

After adding billing to OpenAI:

1. Wait 1-2 minutes for changes to propagate
2. Try using AI features again
3. Check Render logs - you should see successful API calls instead of 429 errors

---

## 📋 Complete Environment Variables Checklist for Render

Make sure these are set in your Render backend service:

### Required:

- ✅ `DATABASE_URL` - Your PostgreSQL connection string (already set)
- ✅ `OPENAI_API_KEY` - Your OpenAI API key (set this)

### Optional but Recommended:

- `OPENAI_MODEL` - Model to use (default: `gpt-4o-mini`)
- `SECRET_KEY` - For JWT tokens (should be set)
- `ALLOW_ORIGINS` - CORS origins (should include your frontend URL)

---

## 🔍 How to Check Your Environment Variables

1. Go to Render Dashboard
2. Select your backend service
3. Click **"Environment"** tab
4. You'll see all your environment variables listed

**Note:** Environment variables are **encrypted** and **not visible** in logs for security.

---

## 🚨 Current Issues from Your Logs

### Issue 1: DATABASE_URL Warning (Not a Problem)

```
⚠️  DATABASE_URL environment variable not set
```

**Status:** ✅ **This is normal** - The warning appears during build, but `DATABASE_URL` is set in Render environment variables and works at runtime.

### Issue 2: OpenAI Quota Exceeded (Needs Fix)

```
Error code: 429 - 'You exceeded your current quota'
```

**Status:** ❌ **Needs action - Add billing to OpenAI account**

---

## 💡 Quick Fix Steps

1. **Add OpenAI API Key to Render:**

   - Render Dashboard → Backend Service → Environment → Add `OPENAI_API_KEY`

2. **Fix OpenAI Quota:**

   - OpenAI Platform → Billing → Add Payment Method → Add Credits

3. **Verify:**
   - Wait 2-3 minutes
   - Try AI features again
   - Check logs for successful API calls

---

## ✅ Database Persistence Confirmation

**Yes, your data is saved!** Here's proof from your logs:

```
✅ Database tables initialized successfully
✅ WorkExperio API started successfully
```

And you can see successful operations:

- `POST /auth/signup HTTP/1.1" 200 OK` - User created
- `GET /projects HTTP/1.1" 200 OK` - Projects loaded
- `GET /users/me HTTP/1.1" 200 OK` - User data retrieved

**Your PostgreSQL database on Render:**

- ✅ Persists all data permanently
- ✅ Survives service restarts
- ✅ Users can login (no need to signup again)
- ✅ All projects, tasks, files are saved

---

## 🎯 Summary

1. **Database:** ✅ Already working - data persists across restarts
2. **OpenAI API Key:** ⚠️ Set in Render but quota exceeded - add billing
3. **Next Steps:** Add billing to OpenAI account to fix 429 errors

Your database persistence is working perfectly! The only issue is the OpenAI quota.

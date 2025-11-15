# 🤖 Automated Deployment Steps

## ✅ What Has Been Automated

### 1. Code Preparation ✅
- ✅ All code committed and pushed to GitHub
- ✅ All deployment configs created
- ✅ Database initialization scripts ready
- ✅ Docker files created
- ✅ Documentation complete

### 2. Deployment Readiness Check ✅
Run this to verify everything is ready:
```powershell
python deployment_automation_check.py
```

### 3. Environment Variable Templates ✅
Run this to generate env var templates:
```powershell
python create_render_env_template.py
```

This creates:
- `render_backend_env.txt` - Backend environment variables
- `render_frontend_env.txt` - Frontend environment variables

---

## 📋 What YOU Need to Do (Manual Steps)

### Step 1: Verify Readiness (Automated Check)
```powershell
python deployment_automation_check.py
```
**Expected**: All checks should pass ✅

### Step 2: Generate Environment Variables
```powershell
python create_render_env_template.py
```
**This creates**: `render_backend_env.txt` and `render_frontend_env.txt`

### Step 3: Create Render Account
1. Go to https://render.com
2. Sign up (free tier available)
3. Verify your email

### Step 4: Create PostgreSQL Database
1. In Render dashboard: **New +** → **PostgreSQL**
2. Name: `workexperio-db`
3. Database: `workexperio`
4. Region: Choose closest
5. Plan: Free (or Starter for production)
6. Click **Create Database**
7. **Copy the "Internal Database URL"** (you'll need this!)

### Step 5: Deploy Backend Service
1. **New +** → **Web Service**
2. Connect your GitHub repository: `ArpitaV24042003/WorkExperio`
3. Configure:
   - **Name**: `workexperio-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Add Environment Variables** (from `render_backend_env.txt`):
   - Copy each line from the file
   - Replace `<FROM_POSTGRES_DATABASE_INTERNAL_URL>` with actual database URL
   - Replace `<OPTIONAL_...>` placeholders or leave empty
5. Click **Create Web Service**
6. Wait for deployment (3-5 minutes)

### Step 6: Initialize Database
1. Go to backend service → **Shell** tab
2. Run:
   ```bash
   python init_db_production.py
   ```
3. Verify output shows all tables created ✅

### Step 7: Deploy Frontend Service
1. **New +** → **Static Site**
2. Connect your GitHub repository: `ArpitaV24042003/WorkExperio`
3. Configure:
   - **Name**: `workexperio-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. **Add Environment Variables** (from `render_frontend_env.txt`):
   - Copy each line
   - Update URLs with your actual backend URL
5. Click **Create Static Site**
6. Wait for deployment (2-3 minutes)
7. **Copy your frontend URL** (e.g., `https://workexperio-frontend.onrender.com`)

### Step 8: Update CORS
1. Go back to **Backend service**
2. **Environment** tab
3. Update `ALLOW_ORIGINS` with your frontend URL:
   ```
   ALLOW_ORIGINS=https://workexperio-frontend.onrender.com
   ```
4. Click **Save Changes** (triggers redeploy)

### Step 9: Update Frontend URLs
1. Go to **Frontend service**
2. **Environment** tab
3. Update:
   ```
   VITE_API_URL=https://workexperio-backend.onrender.com
   VITE_WS_URL=wss://workexperio-backend.onrender.com
   ```
4. Click **Save Changes** (triggers rebuild)

### Step 10: Test Your Deployment
1. Visit your frontend URL
2. Test:
   - ✅ Sign up
   - ✅ Login
   - ✅ Create profile
   - ✅ Create project
   - ✅ Test all features

---

## 🎯 Quick Reference

### Your URLs (after deployment):
- **Frontend**: `https://workexperio-frontend.onrender.com`
- **Backend API**: `https://workexperio-backend.onrender.com`
- **API Docs**: `https://workexperio-backend.onrender.com/docs`

### Important Notes:
- Use **Internal Database URL** (not external) for `DATABASE_URL`
- Use `wss://` (not `ws://`) for WebSocket URLs
- Update CORS after frontend is deployed
- Database initialization is required after first deployment

---

## ✅ Checklist

- [ ] Run `deployment_automation_check.py` - all checks pass
- [ ] Run `create_render_env_template.py` - env files created
- [ ] Render account created
- [ ] PostgreSQL database created
- [ ] Backend service deployed
- [ ] Database initialized (`init_db_production.py`)
- [ ] Frontend service deployed
- [ ] CORS updated
- [ ] Frontend URLs updated
- [ ] All features tested in production

---

**Ready to deploy!** Follow the steps above. 🚀


# 🚀 Render Deployment Guide - Step by Step

Complete step-by-step guide to deploy WorkExperio to Render.

---

## 📋 Prerequisites

1. **GitHub Account** - Your code should be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com) (free tier available)
3. **PostgreSQL Database** - Will be created on Render

---

## 🎯 Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Verify these files exist**:
   - `backend/requirements.txt`
   - `backend/app/main.py`
   - `backend/init_db_production.py`
   - `render.yaml` (optional, for auto-deployment)

---

## 🗄️ Step 2: Create PostgreSQL Database

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"PostgreSQL"**
3. **Configure**:
   - **Name**: `workexperio-db`
   - **Database**: `workexperio`
   - **User**: `workexperio_user` (auto-generated)
   - **Region**: Choose closest to you
   - **Plan**: Free (for testing) or Starter ($7/month)
4. **Click "Create Database"**
5. **Wait for database to be ready** (1-2 minutes)
6. **Copy the "Internal Database URL"** - You'll need this!

---

## 🔧 Step 3: Deploy Backend

1. **Click "New +"** → **"Web Service"**
2. **Connect your GitHub repository**
3. **Configure the service**:
   - **Name**: `workexperio-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Click "Advanced"** and add **Environment Variables**:
   ```
   SECRET_KEY=<click "Generate" or use: openssl rand -hex 32>
   DATABASE_URL=<paste Internal Database URL from Step 2>
   ALLOW_ORIGINS=https://workexperio-frontend.onrender.com
   ENV=production
   LOG_LEVEL=INFO
   ```
   **Note**: We'll update `ALLOW_ORIGINS` after frontend is deployed.
5. **Click "Create Web Service"**
6. **Wait for deployment** (3-5 minutes)

---

## 🎨 Step 4: Deploy Frontend

1. **Click "New +"** → **"Static Site"**
2. **Connect your GitHub repository**
3. **Configure**:
   - **Name**: `workexperio-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. **Add Environment Variables**:
   ```
   VITE_API_URL=https://workexperio-backend.onrender.com
   VITE_WS_URL=wss://workexperio-backend.onrender.com
   ```
   **Note**: Replace with your actual backend URL after deployment.
5. **Click "Create Static Site"**
6. **Wait for deployment** (2-3 minutes)
7. **Copy your frontend URL** (e.g., `https://workexperio-frontend.onrender.com`)

---

## 🔄 Step 5: Update CORS and Environment Variables

1. **Go back to Backend service**
2. **Update Environment Variables**:
   - Update `ALLOW_ORIGINS` with your frontend URL:
     ```
     ALLOW_ORIGINS=https://workexperio-frontend.onrender.com
     ```
3. **Click "Save Changes"** - This will trigger a redeploy

---

## 🗃️ Step 6: Initialize Database

1. **Go to Backend service** → **"Shell"** tab
2. **Run**:
   ```bash
   python init_db_production.py
   ```
3. **Verify output** shows all tables created successfully

---

## ✅ Step 7: Test Your Deployment

1. **Visit your frontend URL**: `https://workexperio-frontend.onrender.com`
2. **Test these features**:
   - ✅ Sign up for a new account
   - ✅ Login
   - ✅ Complete profile setup
   - ✅ Create a project
   - ✅ Test chat (if implemented)

---

## 🔍 Troubleshooting

### Backend won't start:
- Check **Logs** tab in Render dashboard
- Verify `DATABASE_URL` is correct
- Ensure `SECRET_KEY` is set
- Check build logs for Python errors

### Database connection errors:
- Verify `DATABASE_URL` uses the **Internal Database URL** (not external)
- Check database is running (green status)
- Ensure database user has proper permissions

### CORS errors:
- Verify `ALLOW_ORIGINS` includes your frontend URL exactly
- No trailing slashes
- Use `https://` not `http://`

### Frontend can't connect to backend:
- Verify `VITE_API_URL` matches your backend URL
- Use `wss://` for WebSocket (not `ws://`)
- Rebuild frontend after changing env vars

---

## 📊 Your URLs

After deployment, you'll have:
- **Frontend**: `https://workexperio-frontend.onrender.com`
- **Backend API**: `https://workexperio-backend.onrender.com`
- **API Docs**: `https://workexperio-backend.onrender.com/docs`
- **Database**: Managed by Render (internal access only)

---

## 🎉 Success!

Your WorkExperio application is now live on Render!

**Next Steps**:
- Set up custom domain (optional)
- Configure GitHub OAuth (optional)
- Set up MongoDB Atlas for resume parsing (optional)
- Monitor logs and performance

---

## 💡 Pro Tips

1. **Free Tier Limits**: 
   - Services spin down after 15 min of inactivity
   - First request after spin-down takes ~30 seconds
   - Consider upgrading to Starter plan for always-on

2. **Database Backups**: 
   - Free tier: Manual backups only
   - Starter plan: Daily automatic backups

3. **Environment Variables**: 
   - Use Render's "Generate" for `SECRET_KEY`
   - Never commit secrets to GitHub

4. **Monitoring**: 
   - Check Render dashboard regularly
   - Set up email alerts for service failures

---

**Need Help?** Check Render docs: https://render.com/docs


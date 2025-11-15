# ⚡ Quick Deployment Guide

## 🚀 Fastest Way: Render (5 minutes)

### Step 1: Backend on Render

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:

   - **Name**: `workexperio-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. Add PostgreSQL Database:

   - Click "New +" → "PostgreSQL"
   - Copy the "Internal Database URL"

6. Add Environment Variables:

   ```
   SECRET_KEY=<click "Generate" or use a strong random string>
   DATABASE_URL=<paste PostgreSQL Internal Database URL>
   ALLOW_ORIGINS=https://workexperio-frontend.onrender.com
   ENV=production
   ```

7. Click "Create Web Service"
8. After deployment, go to Shell and run:
   ```bash
   python init_db.py
   ```

### Step 2: Frontend on Render

1. Click "New +" → "Static Site"
2. Connect your GitHub repository
3. Configure:

   - **Name**: `workexperio-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. Add Environment Variables:

   ```
   VITE_API_URL=https://workexperio-backend.onrender.com
   VITE_WS_URL=wss://workexperio-backend.onrender.com
   ```

5. Click "Create Static Site"

### Step 3: Update Backend CORS

1. Go back to backend service
2. Update `ALLOW_ORIGINS` to your frontend URL:
   ```
   ALLOW_ORIGINS=https://workexperio-frontend.onrender.com
   ```
3. Redeploy

**Done!** Your app is live! 🎉

---

## 🐳 Alternative: Docker Compose (Local/Server)

```bash
# 1. Update environment variables in docker-compose.yml
# 2. Run:
docker-compose up -d

# Access:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
```

---

## 📝 Important Notes

1. **SECRET_KEY**: Must be a strong random string (32+ characters)
2. **Database**: Use PostgreSQL in production (not SQLite)
3. **CORS**: Update `ALLOW_ORIGINS` with your frontend URL
4. **WebSocket**: Use `wss://` (not `ws://`) for HTTPS

---

## 🔗 Your URLs

After deployment:

- **Frontend**: `https://workexperio-frontend.onrender.com`
- **Backend**: `https://workexperio-backend.onrender.com`
- **API Docs**: `https://workexperio-backend.onrender.com/docs`

---

## ✅ Test Your Deployment

1. Visit your frontend URL
2. Sign up for a new account
3. Complete profile setup
4. Create a project
5. Test all features

**That's it!** 🚀

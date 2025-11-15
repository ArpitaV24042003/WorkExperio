# ✅ Deployment Checklist

Use this checklist to ensure a smooth deployment.

## 📋 Pre-Deployment

- [ ] **Code is tested locally**
- [ ] **All environment variables documented**
- [ ] **Database schema is ready**
- [ ] **Secrets are generated (SECRET_KEY, etc.)**
- [ ] **CORS origins updated for production**

## 🔧 Backend Setup

- [ ] **Platform selected** (Render/Railway/Heroku/etc.)
- [ ] **PostgreSQL database created**
- [ ] **Environment variables configured**:
  - [ ] `SECRET_KEY` (strong random string)
  - [ ] `DATABASE_URL` (PostgreSQL connection string)
  - [ ] `ALLOW_ORIGINS` (frontend URL)
  - [ ] `ENV=production`
  - [ ] `MONGO_URL` (optional)
  - [ ] `GITHUB_CLIENT_ID` (optional)
  - [ ] `GITHUB_CLIENT_SECRET` (optional)
- [ ] **Database initialized** (`python init_db.py`)
- [ ] **Backend is accessible** (test API endpoint)

## 🎨 Frontend Setup

- [ ] **Platform selected** (Vercel/Render Static/etc.)
- [ ] **Environment variables configured**:
  - [ ] `VITE_API_URL` (backend URL)
  - [ ] `VITE_WS_URL` (backend WebSocket URL with wss://)
- [ ] **Build successful** (`npm run build`)
- [ ] **Frontend is accessible**

## 🔗 Integration

- [ ] **CORS configured correctly**
- [ ] **WebSocket uses wss:// (not ws://)**
- [ ] **API calls work from frontend**
- [ ] **Authentication works**
- [ ] **File uploads work** (if applicable)

## 🧪 Testing

- [ ] **User signup works**
- [ ] **User login works**
- [ ] **Profile creation works**
- [ ] **Project creation works**
- [ ] **Team formation works**
- [ ] **Chat works (WebSocket)**
- [ ] **AI features work**

## 🔐 Security

- [ ] **HTTPS enabled** (both frontend and backend)
- [ ] **SECRET_KEY is strong and unique**
- [ ] **Database credentials are secure**
- [ ] **CORS origins are specific (no wildcards)**
- [ ] **Environment variables not in code**

## 📊 Monitoring

- [ ] **Error logging set up**
- [ ] **Application monitoring configured**
- [ ] **Database backups enabled**
- [ ] **Uptime monitoring set up**

## ✅ Post-Deployment

- [ ] **All features tested in production**
- [ ] **Performance is acceptable**
- [ ] **Error handling works**
- [ ] **Documentation updated with production URLs**

---

## 🚨 Common Issues

### Backend won't start:

- Check `DATABASE_URL` format
- Verify all required env vars are set
- Check build logs for errors

### Frontend can't connect to backend:

- Verify `VITE_API_URL` is correct
- Check CORS configuration
- Ensure backend is running

### WebSocket not working:

- Use `wss://` for HTTPS
- Check platform WebSocket support
- Verify backend WebSocket endpoint

### Database errors:

- Run `python init_db.py` after deployment
- Check database connection string
- Verify database is accessible

---

**Ready to deploy!** Follow the steps in `DEPLOYMENT_GUIDE.md` 🚀

# 🚀 WorkExperio - Deployment Guide

Complete guide to deploy WorkExperio to various platforms.

---

## 📋 Pre-Deployment Checklist

- [ ] Update `SECRET_KEY` in backend `.env` (use a strong random string)
- [ ] Set up PostgreSQL database (for production)
- [ ] Configure MongoDB (optional, for resume parsing)
- [ ] Set up GitHub OAuth (optional)
- [ ] Update CORS origins with production URLs
- [ ] Test locally before deploying

---

## 🌐 Deployment Options

### Option 1: Render (Recommended - Easy)

Render supports both backend and frontend with PostgreSQL.

#### Backend Deployment on Render:

1. **Create a new Web Service**:

   - Connect your GitHub repository
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Add Environment Variables**:

   ```
   SECRET_KEY=<generate-a-strong-secret-key>
   DATABASE_URL=<from-postgres-database>
   ALLOW_ORIGINS=https://your-frontend-url.onrender.com
   ENV=production
   MONGO_URL=<your-mongodb-url> (optional)
   GITHUB_CLIENT_ID=<your-github-client-id> (optional)
   GITHUB_CLIENT_SECRET=<your-github-client-secret> (optional)
   ```

3. **Create PostgreSQL Database**:

   - Add a PostgreSQL database in Render
   - Copy the connection string to `DATABASE_URL`

4. **Initialize Database**:
   - After first deployment, run: `python init_db.py` via Render shell

#### Frontend Deployment on Render:

1. **Create a new Static Site**:

   - Connect your GitHub repository
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`

2. **Add Environment Variables**:
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   VITE_WS_URL=wss://your-backend-url.onrender.com
   ```

**OR use `render.yaml`** (already created):

- Push `render.yaml` to your repo
- Render will auto-detect and deploy both services

---

### Option 2: Railway (Easy + Fast)

Railway auto-detects Python/Node and deploys automatically.

#### Steps:

1. **Connect Repository**:

   - Go to [railway.app](https://railway.app)
   - New Project → Deploy from GitHub
   - Select your repository

2. **Backend Service**:

   - Railway will auto-detect Python
   - Root Directory: `backend`
   - Add environment variables (same as Render)
   - Add PostgreSQL database

3. **Frontend Service**:

   - Add another service
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npx serve dist -p $PORT`
   - Add environment variables

4. **Database Migration**:
   - Use Railway shell: `cd backend && python init_db.py`

---

### Option 3: Docker (Any Platform)

Deploy using Docker containers.

#### Build and Run:

**Backend:**

```bash
cd backend
docker build -t workexperio-backend .
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql://... \
  workexperio-backend
```

**Frontend:**

```bash
cd frontend
docker build -t workexperio-frontend .
docker run -p 80:80 workexperio-frontend
```

#### Docker Compose (Full Stack):

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/workexperio
      - ALLOW_ORIGINS=http://localhost:3000
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_WS_URL=ws://localhost:8000

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=workexperio
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run: `docker-compose up -d`

---

### Option 4: Vercel (Frontend) + Render/Railway (Backend)

Best for frontend performance.

#### Frontend on Vercel:

1. **Deploy to Vercel**:

   ```bash
   cd frontend
   npm install -g vercel
   vercel
   ```

2. **Configure**:

   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Environment Variables:
     ```
     VITE_API_URL=https://your-backend-url
     VITE_WS_URL=wss://your-backend-url
     ```

3. **Backend**: Deploy to Render/Railway (see above)

---

## 🔧 Environment Variables

### Backend Production `.env`:

```env
SECRET_KEY=<generate-strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ENV=production
ALLOW_ORIGINS=https://your-frontend-domain.com
LOG_LEVEL=INFO
MONGO_URL=mongodb://host:27017 (optional)
MONGO_DB_NAME=workexperio_db
GITHUB_CLIENT_ID=your-client-id (optional)
GITHUB_CLIENT_SECRET=your-client-secret (optional)
BACKEND_BASE_URL=https://your-backend-domain.com
FRONTEND_URL=https://your-frontend-domain.com
```

### Frontend Production `.env`:

```env
VITE_API_URL=https://your-backend-domain.com
VITE_WS_URL=wss://your-backend-domain.com
```

---

## 🔐 Security Checklist

- [ ] Use strong `SECRET_KEY` (32+ random characters)
- [ ] Enable HTTPS for all services
- [ ] Use PostgreSQL in production (not SQLite)
- [ ] Set proper CORS origins (no wildcards)
- [ ] Use environment variables (never commit secrets)
- [ ] Enable database backups
- [ ] Set up monitoring/logging
- [ ] Use rate limiting (consider Cloudflare)

---

## 📊 Database Setup

### PostgreSQL (Production):

1. **Create Database**:

   ```sql
   CREATE DATABASE workexperio;
   CREATE USER workexperio_user WITH PASSWORD 'strong_password';
   GRANT ALL PRIVILEGES ON DATABASE workexperio TO workexperio_user;
   ```

2. **Update DATABASE_URL**:

   ```
   postgresql+psycopg://workexperio_user:strong_password@host:5432/workexperio
   ```

3. **Run Migrations**:
   ```bash
   cd backend
   python init_db.py
   ```

---

## 🚀 Quick Deploy Commands

### Render (using render.yaml):

```bash
# Just push to GitHub, Render auto-deploys
git add render.yaml
git commit -m "Add Render deployment config"
git push
```

### Railway:

```bash
railway login
railway init
railway up
```

### Vercel (Frontend):

```bash
cd frontend
vercel --prod
```

---

## 🐛 Troubleshooting

### Backend Issues:

1. **Database Connection Error**:

   - Check `DATABASE_URL` format
   - Ensure database is accessible
   - Check firewall rules

2. **CORS Errors**:

   - Verify `ALLOW_ORIGINS` includes frontend URL
   - Check for trailing slashes

3. **WebSocket Not Working**:
   - Ensure WebSocket is enabled on platform
   - Use `wss://` for HTTPS
   - Check proxy settings

### Frontend Issues:

1. **API Not Found**:

   - Check `VITE_API_URL` environment variable
   - Rebuild after changing env vars

2. **WebSocket Connection Failed**:
   - Verify `VITE_WS_URL` uses `wss://` for HTTPS
   - Check backend WebSocket endpoint

---

## 📝 Post-Deployment

1. **Test All Features**:

   - Sign up/login
   - Upload resume
   - Create project
   - Team formation
   - Chat functionality

2. **Monitor**:

   - Check application logs
   - Monitor database connections
   - Set up error tracking (Sentry, etc.)

3. **Optimize**:
   - Enable CDN for frontend
   - Set up database indexes
   - Configure caching

---

## 🎯 Recommended Setup

**For Production:**

- **Backend**: Render or Railway (with PostgreSQL)
- **Frontend**: Vercel or Render Static Site
- **Database**: PostgreSQL (managed by platform)
- **MongoDB**: MongoDB Atlas (optional, for resume parsing)

**For Quick Testing:**

- Use `render.yaml` - push to GitHub and Render auto-deploys everything!

---

## 📚 Additional Resources

- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Vercel Docs](https://vercel.com/docs)
- [Docker Docs](https://docs.docker.com)

---

## ✅ Deployment Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Database connected and migrated
- [ ] Environment variables configured
- [ ] CORS configured correctly
- [ ] WebSocket working (wss://)
- [ ] All features tested
- [ ] Monitoring set up
- [ ] Backups configured

---

**Ready to deploy!** Choose your platform and follow the steps above. 🚀


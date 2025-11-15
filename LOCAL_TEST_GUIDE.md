# 🧪 Local Testing Guide

## ✅ Git Operations Complete!

**Status**: All code has been committed and pushed to GitHub
- **Commit**: `9902cb1` - "Ready for deployment - Added deployment configs, E2E tests, and database verification scripts"
- **Repository**: https://github.com/ArpitaV24042003/WorkExperio.git
- **Branch**: `main`

---

## 🧪 Testing Locally

### Step 1: Start Backend Server

Open a **new terminal** and run:

```powershell
cd "S:\6-7 Main Project\WorkExpirio_Backend\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Or use the batch file**:
```powershell
cd "S:\6-7 Main Project\WorkExpirio_Backend"
.\start_backend.bat
```

Wait for: `Application startup complete.`

---

### Step 2: Verify Database Tables

In a **new terminal** (while backend is running):

```powershell
cd "S:\6-7 Main Project\WorkExpirio_Backend\backend"
python verify_db.py
```

**Expected output**: All 12 tables should be verified ✅

---

### Step 3: Run End-to-End Tests

In the **same terminal** (backend still running):

```powershell
cd "S:\6-7 Main Project\WorkExpirio_Backend\backend"
python run_e2e_tests.py
```

**Expected output**: All tests should pass ✅

---

### Step 4: Manual Testing (Optional)

1. **Start Frontend** (in another terminal):
   ```powershell
   cd "S:\6-7 Main Project\WorkExpirio_Backend\frontend"
   npm run dev
   ```

2. **Open Browser**: http://localhost:5173

3. **Test Features**:
   - ✅ Sign up
   - ✅ Login
   - ✅ Complete profile
   - ✅ Create project
   - ✅ Test chat

---

## 📊 Test Results

After running tests, you should see:

```
✅ Test 1: Backend server is accessible
✅ Test 2: User signed up successfully
✅ Test 3: User logged in successfully
✅ Test 4: Retrieved user profile
✅ Test 5: Created education entry
✅ Test 6: Created skill
✅ Test 7: Created project
✅ Test 8: Listed projects

Total: 8/8 tests passed
```

---

## 🚀 Next: Deploy to Render

Once local tests pass, follow `RENDER_DEPLOY.md`:

1. ✅ **Step 1**: Git operations (DONE!)
2. **Step 2**: Create PostgreSQL database on Render
3. **Step 3**: Deploy backend service
4. **Step 4**: Deploy frontend static site
5. **Step 5**: Initialize database
6. **Step 6**: Test in production

---

## 🔍 Troubleshooting

### Backend won't start:
- Check if port 8000 is available
- Verify Python dependencies: `pip install -r requirements.txt`
- Check for errors in terminal

### Database errors:
- Run `python init_db.py` first
- Check `DATABASE_URL` in `.env`

### Tests fail:
- Ensure backend is running on port 8000
- Check backend logs for errors
- Verify database is initialized

---

**Ready to test!** Start the backend server and run the tests. 🧪


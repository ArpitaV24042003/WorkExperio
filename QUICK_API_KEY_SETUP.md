# Quick OpenAI API Key Setup

## 🚨 Current Issue
Your AI features are showing errors because the OpenAI API key is not configured. Here's how to fix it:

## ✅ Quick Fix (3 Steps)

### Step 1: Get Your API Key
1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click **"Create new secret key"**
4. Copy the key (it starts with `sk-`)

### Step 2: Create .env File
1. Navigate to: `S:\6-7 Main Project\WorkExpirio_Backend\backend\`
2. Create a new file named `.env` (not `.env.txt`, just `.env`)
3. Add this line (replace with your actual key):
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

### Step 3: Restart Backend
1. Stop your backend server (Ctrl+C in the terminal)
2. Start it again:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

## 🎯 For Render Deployment

If you're deploying to Render:

1. Go to your Render dashboard
2. Select your backend service
3. Go to **Environment** tab
4. Click **"Add Environment Variable"**
5. Add:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `sk-your-actual-key-here`
6. Click **"Save Changes"**
7. Render will automatically redeploy

## ✅ Verify It's Working

After setting up:
1. Go to AI Assistant
2. Ask: "Can you suggest me codes?"
3. You should get a proper AI response (not an error)

Or:
1. Upload a code file
2. Click "Analyze code"
3. You should see detailed AI analysis (not just "Unable to perform detailed analysis")

## 🔍 Troubleshooting

**Still seeing errors?**
- Check the `.env` file is in `backend/` folder (not root)
- Verify the key starts with `sk-`
- Make sure there are no spaces: `OPENAI_API_KEY=sk-...` (not `OPENAI_API_KEY = sk-...`)
- Restart the backend server after creating `.env`
- Check backend logs for error messages

**File location:**
```
WorkExpirio_Backend/
  backend/
    .env          ← Create this file here
    app/
      main.py
```

## 💡 Cost Note

OpenAI API is pay-as-you-go:
- ~$0.01-0.05 per AI chat message
- ~$0.02-0.10 per code analysis
- Very affordable for development/testing

Set spending limits in OpenAI dashboard if concerned.


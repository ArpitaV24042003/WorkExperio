# OpenAI API Key Setup Guide

This guide explains how to set up the `OPENAI_API_KEY` environment variable for the WorkExperio backend to enable AI features.

## Why You Need This

The following features require an OpenAI API key:

- ✅ **AI Task Generation** - Automatically break down projects into tasks
- ✅ **AI Code Analysis** - Comprehensive code quality, accuracy, and performance analysis
- ✅ **AI Task Validation** - Validate task completion automatically
- ✅ **AI Assistant Chat** - Multi-turn dialogue with project context
- ✅ **AI Task Assignment** - Intelligent task assignment to team members

**Note:** All features have fallback implementations that work without an API key, but they provide basic functionality only.

## Step 1: Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section: https://platform.openai.com/api-keys
4. Click **"Create new secret key"**
5. Give it a name (e.g., "WorkExperio Backend")
6. **Copy the key immediately** - you won't be able to see it again!

## Step 2: Set Up Environment Variable

### Option A: Local Development (Windows)

1. Create or edit `.env` file in the `backend` folder:

   ```
   backend/.env
   ```

2. Add your API key:

   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   # OR use the alternative name:
   OPENAI_API_KEY_WORKEXPERIO=sk-your-actual-api-key-here
   ```

3. **Important:** Make sure `.env` is in `.gitignore` (it should be already)

### Option B: Local Development (Linux/Mac)

1. Create or edit `.env` file in the `backend` folder:

   ```bash
   cd backend
   nano .env
   ```

2. Add your API key:

   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. Or export it in your shell:
   ```bash
   export OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

### Option C: Render (Production Deployment)

1. Go to your Render dashboard
2. Select your backend service
3. Go to **Environment** tab
4. Click **"Add Environment Variable"**
5. Add:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `sk-your-actual-api-key-here`
6. Click **"Save Changes"**
7. Render will automatically redeploy your service

### Option D: Other Deployment Platforms

#### Railway

1. Go to your Railway project
2. Select your service
3. Go to **Variables** tab
4. Add `OPENAI_API_KEY` with your key value

#### Heroku

```bash
heroku config:set OPENAI_API_KEY=sk-your-actual-api-key-here -a your-app-name
```

#### Docker

Add to your `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - OPENAI_API_KEY=sk-your-actual-api-key-here
```

Or use `.env` file:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Step 3: Verify Setup

### Check if Environment Variable is Loaded

1. **Backend Logs:**

   - Start your backend server
   - Check logs for any OpenAI-related errors
   - If you see "LLM not configured" messages, the key isn't being read

2. **Test Endpoint:**

   ```bash
   # Test AI task generation
   curl -X POST http://localhost:8000/projects/{project_id}/ai-generate-tasks \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **Check Environment:**
   ```python
   # In Python shell or add to a test endpoint
   import os
   print(os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_WORKEXPERIO"))
   ```

## Step 4: Optional Configuration

### Set Custom Model (Optional)

You can specify which OpenAI model to use:

```env
OPENAI_MODEL=gpt-4o-mini  # Default
# OR
OPENAI_MODEL=gpt-4
# OR
OPENAI_MODEL=gpt-3.5-turbo
```

**Note:** `gpt-4o-mini` is recommended for cost-effectiveness. `gpt-4` provides better quality but costs more.

## Security Best Practices

1. ✅ **Never commit API keys to Git**

   - Ensure `.env` is in `.gitignore`
   - Never hardcode keys in source code

2. ✅ **Use Environment Variables**

   - Always use environment variables, never hardcode

3. ✅ **Rotate Keys Regularly**

   - Regenerate keys periodically for security
   - Revoke old keys if compromised

4. ✅ **Set Usage Limits**

   - In OpenAI dashboard, set monthly spending limits
   - Monitor usage regularly

5. ✅ **Use Different Keys for Dev/Prod**
   - Use separate API keys for development and production
   - This helps track usage and isolate issues

## Troubleshooting

### Issue: "LLM not configured" messages

**Solution:**

- Check that `.env` file exists in `backend` folder
- Verify the variable name is exactly `OPENAI_API_KEY` or `OPENAI_API_KEY_WORKEXPERIO`
- Restart your backend server after adding the key
- Check for typos in the key value

### Issue: "Invalid API key" errors

**Solution:**

- Verify the key starts with `sk-`
- Check for extra spaces or newlines
- Regenerate the key in OpenAI dashboard
- Ensure you're using the correct key (not a test key)

### Issue: API calls failing

**Solution:**

- Check your OpenAI account has credits/billing set up
- Verify API rate limits haven't been exceeded
- Check network connectivity
- Review OpenAI dashboard for error messages

### Issue: Environment variable not loading

**Solution:**

- Make sure `.env` file is in the correct location (`backend/.env`)
- Restart the server after adding the variable
- Check if your framework requires specific loading (e.g., `python-dotenv`)
- Verify the variable name matches exactly (case-sensitive)

## Cost Considerations

OpenAI API pricing (as of 2024):

- **gpt-4o-mini**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **gpt-4**: ~$5 per 1M input tokens, ~$15 per 1M output tokens

**Estimated costs for WorkExperio:**

- Task generation: ~$0.01-0.05 per project
- Code analysis: ~$0.02-0.10 per analysis
- Task validation: ~$0.01-0.03 per validation
- Chat messages: ~$0.01-0.05 per conversation

**Tips to reduce costs:**

- Use `gpt-4o-mini` instead of `gpt-4`
- Set spending limits in OpenAI dashboard
- Monitor usage regularly
- Cache responses when possible

## Alternative: Use Without API Key

If you don't want to use OpenAI API, the system will:

- Use basic fallback task generation (5 generic tasks)
- Provide simple code analysis (line count based)
- Skip AI task validation (basic file check only)
- Use simple rule-based chat responses

The system is fully functional without the API key, just with reduced AI capabilities.

## Support

If you encounter issues:

1. Check OpenAI status: https://status.openai.com/
2. Review OpenAI documentation: https://platform.openai.com/docs
3. Check backend logs for detailed error messages
4. Verify your account has active billing/credits

---

**Ready to go!** Once you've set up the API key, restart your backend server and the AI features will be enabled automatically.

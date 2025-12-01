# Backend Deployment Guide - Railway.app

## Prerequisites
- GitHub account
- Railway.app account (free tier available)
- Python backend code pushed to GitHub

## Step 1: Prepare Your Repository

Ensure these files exist in your `backend/` folder:
- `requirements.txt`
- `railway.json`
- `nixpacks.toml`
- `Procfile`
- `.gitignore`

## Step 2: Deploy to Railway

1. Go to [Railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select your `smartdoc-ai` repository
6. Railway will automatically detect Python and start building

## Step 3: Configure Environment Variables

In Railway Dashboard:

1. Click on your project
2. Go to **"Variables"** tab
3. Add these environment variables:
```
OPENAI_API_KEY=your-openai-key
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
SECRET_KEY=your-secret-key
ENVIRONMENT=production
APP_NAME=SmartDoc AI
APP_VERSION=1.0.0
```

## Step 4: Set Root Directory (Important!)

1. Go to **"Settings"** tab
2. Find **"Root Directory"**
3. Set it to: `backend`
4. Click **"Save"**

## Step 5: Deploy

1. Railway will automatically deploy
2. Wait 2-3 minutes for build to complete
3. You'll get a URL like: `https://smartdoc-ai-production.up.railway.app`

## Step 6: Test Your API

Visit:
- `https://your-app.up.railway.app/` - Root endpoint
- `https://your-app.up.railway.app/docs` - Interactive API docs
- `https://your-app.up.railway.app/api/v1/health` - Health check

## Step 7: Custom Domain (Optional)

1. In Railway, go to **"Settings"**
2. Click **"Generate Domain"** or add custom domain
3. Update your frontend `NEXT_PUBLIC_API_URL` to new domain

## Troubleshooting

### Build fails
- Check logs in Railway dashboard
- Ensure `requirements.txt` is correct
- Verify Python version compatibility

### App crashes on start
- Check environment variables are set
- Review application logs
- Ensure `PORT` variable is used correctly

### CORS errors
- Add your frontend URL to `CORS_ORIGINS` in config
- Redeploy after changes

## Monitoring

Railway provides:
- Real-time logs
- Resource usage metrics
- Deployment history
- Automatic SSL certificates

## Costs

Railway free tier includes:
- $5 credit per month
- Sufficient for development/portfolio
- Upgrade to hobby plan ($5/month) for production
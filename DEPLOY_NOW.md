# 🚀 Deploy TradingAgents Web Interface in 5 Minutes

## Option 1: Railway (Recommended - Easiest)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose this repository
5. Add environment variable:
   - `OPENAI_API_KEY` = `sk-your-openai-key`

### Step 3: Done! 🎉
Your app will be live at: `https://your-app.railway.app`

**Cost**: ~$5/month (includes $5 free credit)

---

## Option 2: Render (Free Tier Available)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy
1. Go to [render.com](https://render.com)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml`
5. Add your `OPENAI_API_KEY` in the dashboard

### Step 3: Done! 🎉
Your app will be live at: `https://your-app.onrender.com`

**Cost**: Free tier available, paid starts at $7/month

---

## Option 3: Fly.io (Free Tier)

### Step 1: Install Fly CLI
```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Deploy
```bash
fly auth login
fly launch --now
fly secrets set OPENAI_API_KEY=sk-your-key
```

### Step 3: Done! 🎉
Your app will be live at: `https://your-app.fly.dev`

**Cost**: Free tier includes 3 small VMs

---

## What You Need

✅ GitHub account (to push your code)
✅ OpenAI API key ([get one here](https://platform.openai.com/api-keys))
✅ 5 minutes of your time

---

## After Deployment

Your users can access the web interface at the provided URL and:
1. Select an AI model
2. Enter a stock ticker
3. Choose analysts
4. Get comprehensive trading analysis

---

## Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key

Optional:
- `ALPHA_VANTAGE_API_KEY` - For additional financial data

---

## Troubleshooting

### "Build failed"
- Make sure all files are committed and pushed
- Check that `requirements.txt` includes all dependencies

### "App crashes on startup"
- Verify `OPENAI_API_KEY` is set correctly
- Check platform logs for error messages

### "Can't access the app"
- Wait 2-3 minutes for initial deployment
- Check if the app is running in platform dashboard

---

## Next Steps

1. **Custom Domain**: Add your own domain in platform settings
2. **Monitoring**: Set up uptime monitoring
3. **Scaling**: Adjust instance size based on usage
4. **Authentication**: Add user auth for production use

---

## Need Help?

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions for each platform.

---

**Recommended**: Start with Railway for the fastest deployment! 🚂

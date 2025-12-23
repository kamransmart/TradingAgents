# Deploy to Railway (Easiest Cloud Deployment!)

Railway is the **easiest cloud platform** to deploy to - much simpler than AWS App Runner.

## Why Railway?

- ✅ No complex configuration needed
- ✅ Auto-detects Dockerfile
- ✅ One-click deployment from GitHub
- ✅ Automatic HTTPS
- ✅ Easy environment variables
- ✅ $5 free credit to start
- ✅ ~$5-10/month after that

## 🚀 Deploy in 3 Minutes

### Step 1: Push to GitHub (if not already)

```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin feature/custom-with-web
```

### Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Click **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select repository: **TradingAgents**
6. Select branch: **feature/custom-with-web**
7. Railway will auto-detect your Dockerfile ✅

### Step 3: Add Environment Variables

In the Railway dashboard:
1. Click on your project
2. Click **"Variables"** tab
3. Click **"New Variable"**
4. Add:
   - `OPENAI_API_KEY` = `your-key-here`
   - `ALPHA_VANTAGE_API_KEY` = `your-key-here` (optional)

### Step 4: Deploy!

1. Railway automatically starts building
2. Wait 3-5 minutes for deployment
3. Click **"Settings"** → **"Generate Domain"**
4. Get your URL: `https://your-app.up.railway.app`

### Step 5: Done! 🎉

Open your URL and start using your TradingAgents web interface!

---

## 💰 Cost

- **First $5**: Free credit (enough for ~1 month)
- **After that**: ~$5-10/month
- **No surprise bills**: Clear, predictable pricing

---

## 🔄 Updates

Every time you push to GitHub:
```bash
git push origin feature/custom-with-web
```

Railway automatically redeploys! ✨

---

## 📊 Monitor

- **Logs**: Real-time in Railway dashboard
- **Metrics**: CPU, Memory, Network usage
- **Deployments**: See history and rollback if needed

---

## Alternative: Use Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Add environment variables
railway variables set OPENAI_API_KEY=sk-your-key

# Deploy
railway up
```

---

## ⚡ Why Railway is Better than App Runner for This

| Feature | Railway | AWS App Runner |
|---------|---------|----------------|
| Setup | 3 minutes | 15+ minutes |
| Config needed | None (auto) | Complex JSON |
| Environment vars | Easy UI | CLI only |
| Logs | Real-time | Delayed |
| Price | $5-10/mo | $25+/mo |
| Free credit | $5 | None |
| Debugging | Easy | Hard |

---

## 🆘 Troubleshooting

### Build fails
- Check logs in Railway dashboard
- Usually very clear error messages

### App doesn't start
- Verify environment variables are set
- Check logs for errors

### Can't access URL
- Make sure you generated a domain in Settings
- Wait 3-5 minutes for first deployment

---

## 🌐 Custom Domain

1. Railway dashboard → Your project
2. Settings → Domains
3. Add your custom domain
4. Update DNS records
5. SSL automatically configured

---

## 💡 Pro Tips

- Railway has **excellent logs** - use them!
- Can deploy multiple services (database, etc.)
- Free SSL certificates included
- Can scale up/down easily
- Great for startups and side projects

---

**Railway is honestly the easiest way to deploy this app. Highly recommended!** 🚀

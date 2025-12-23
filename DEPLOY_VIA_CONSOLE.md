# Deploy to AWS App Runner via Console (No Docker/CLI needed!)

Since you have permission issues resolved, the **easiest way** is to deploy directly from GitHub using AWS Console.

## 🚀 Quick Deploy Steps (5 minutes)

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Ready for AWS deployment"
git push origin main
```

### Step 2: Go to App Runner Console

Open: https://console.aws.amazon.com/apprunner/home?region=us-east-1

### Step 3: Create Service

1. Click **"Create service"**

2. **Source and deployment**:
   - Repository type: **Source code repository**
   - Source: **Connect to GitHub**
   - Click **"Add new"** to connect GitHub
   - Select your repository: `TradingAgents`
   - Branch: `main`
   - Deployment trigger: **Automatic** (deploys on git push)
   - Click **Next**

3. **Build settings**:
   - Configuration file: **Use a configuration file**
   - Configuration file: `aws-apprunner.yaml` ✅ (already in your repo)
   - Or manually configure:
     - Build command: `pip install -r requirements.txt`
     - Start command: `chainlit run chainlit_app_interactive.py --host 0.0.0.0 --port 8000`
     - Port: `8000`
   - Click **Next**

4. **Service settings**:
   - Service name: `tradingagents-web`
   - CPU: **1 vCPU**
   - Memory: **2 GB**
   - Environment variables - Click **"Add environment variable"**:
     - Name: `OPENAI_API_KEY`
     - Value: `sk-your-openai-api-key-here`
     - (Optional) Name: `ALPHA_VANTAGE_API_KEY`, Value: `your-key`
   - Click **Next**

5. **Review and create**:
   - Review all settings
   - Click **"Create & deploy"**

### Step 4: Wait for Deployment (5-10 minutes)

- App Runner will:
  1. Clone your GitHub repo
  2. Build the Docker container
  3. Deploy the container
  4. Provide you with a URL

### Step 5: Get Your URL

Once deployed (status shows "Running"):
- Copy the **Default domain** URL
- Example: `https://abc123xyz.us-east-1.awsapprunner.com`
- Open it in your browser!

## ✅ Done!

Your TradingAgents web interface is now live on AWS! 🎉

---

## 💰 Cost

- **~$25/month** for 1 vCPU, 2 GB RAM running 24/7
- Scales automatically based on traffic
- HTTPS included for free

---

## 🔄 Updates

Every time you push to GitHub:
```bash
git add .
git commit -m "Update app"
git push origin main
```

App Runner will automatically rebuild and redeploy! ✨

---

## 📊 Monitor Your App

### View Logs:
1. Go to App Runner Console
2. Click your service
3. Click **"Logs"** tab
4. See real-time logs

### Metrics:
- CPU usage
- Memory usage
- Request count
- Response times

---

## 🌐 Custom Domain (Optional)

1. In App Runner Console → Your service
2. Click **"Custom domains"** tab
3. Click **"Link domain"**
4. Enter your domain (e.g., `trade.yourdomain.com`)
5. Add DNS records shown by AWS
6. SSL certificate is automatically provisioned

---

## 🛑 Pause/Stop Service

To save costs when not in use:
1. Go to App Runner Console
2. Click your service
3. Click **"Actions"** → **"Pause service"**
4. Resume anytime with **"Resume service"**

---

## ❌ Delete Service

If you want to remove it:
1. App Runner Console → Your service
2. **"Actions"** → **"Delete service"**
3. This stops all charges

---

## 🔐 Security Best Practices

1. **Don't commit API keys** - Always use environment variables
2. **Use Secrets Manager** (optional, more secure):
   - Store secrets in AWS Secrets Manager
   - Reference them in App Runner configuration
3. **Enable WAF** (optional, for production):
   - Add Web Application Firewall rules

---

## 📝 Your Service Details

Once deployed, save these:
- **Service URL**: (from App Runner console)
- **Service Name**: `tradingagents-web`
- **Region**: `us-east-1`
- **Account**: `185327115759`

---

## 💡 Tips

- **First deployment takes 5-10 minutes** (building container)
- **Subsequent deployments are faster** (3-5 minutes)
- **Logs are your friend** - check them if something goes wrong
- **Environment variables can be updated** without redeploying

---

## 🆘 Troubleshooting

### Build fails
- Check logs in App Runner console
- Verify `requirements.txt` has all dependencies
- Make sure `chainlit_app_interactive.py` exists

### App doesn't start
- Verify `OPENAI_API_KEY` environment variable is set
- Check logs for error messages
- Ensure port 8000 is configured

### Can't access URL
- Wait 10 minutes for first deployment
- Check service status is "Running"
- Try in incognito/private browser window

---

## 📚 Resources

- App Runner Console: https://console.aws.amazon.com/apprunner
- Documentation: https://docs.aws.amazon.com/apprunner/
- Pricing: https://aws.amazon.com/apprunner/pricing/

---

**This is the easiest deployment method - no Docker or CLI commands needed!** 🚀

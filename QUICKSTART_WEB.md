# 🚀 Quick Start - TradingAgents Web Interface

Get your TradingAgents web interface running in 5 minutes!

## Option 1: Local Testing (Fastest) ⚡

### Prerequisites
- Python 3.11+ installed
- At least one LLM API key (OpenAI, Anthropic, Google, etc.)

### Steps

1. **Clone and navigate to the project** (if not already there):
```bash
cd /Users/akamran/Development/TradingAgents
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API keys (at least one LLM provider required)
nano .env  # or use your favorite editor
```

Your `.env` should look like:
```bash
# At least ONE of these is required
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-key-here
OPENROUTER_API_KEY=sk-or-your-key-here

# Optional (but recommended for better data)
ALPHA_VANTAGE_API_KEY=your-key-here

# Optional (for social sentiment)
REDDIT_CLIENT_ID=your-id-here
REDDIT_CLIENT_SECRET=your-secret-here
```

4. **Run the web app**:
```bash
# Using the convenience script
./start_web.sh

# OR manually
chainlit run chainlit_app.py
```

5. **Open your browser**:
   - Navigate to: **http://localhost:8000**
   - You should see the TradingAgents web interface!

6. **Start analyzing**:
   - Follow the on-screen prompts
   - Type a stock ticker (e.g., "AAPL")
   - Configure your analysis settings
   - Watch the agents work!

---

## Option 2: Docker (Containerized) 🐳

### Prerequisites
- Docker and Docker Compose installed
- API keys ready

### Steps

1. **Navigate to project**:
```bash
cd /Users/akamran/Development/TradingAgents
```

2. **Set up environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Build and run with Docker Compose**:
```bash
docker-compose up --build
```

4. **Access the app**:
   - Open: **http://localhost:8000**

5. **Stop the app**:
```bash
docker-compose down
```

---

## Option 3: Deploy to Cloud (Railway) ☁️

Railway is the easiest cloud deployment option!

### Prerequisites
- Railway account (free tier available)
- GitHub account

### Steps

1. **Push your code to GitHub** (if not already there)

2. **Go to [Railway.app](https://railway.app)** and sign up

3. **Create a new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your TradingAgents repository

4. **Add environment variables**:
   - In Railway dashboard, go to Variables
   - Add your API keys:
     - `OPENAI_API_KEY`
     - `ALPHA_VANTAGE_API_KEY`
     - etc.

5. **Deploy**:
   - Railway auto-detects the Dockerfile
   - Deployment happens automatically!
   - You'll get a public URL like: `https://tradingagents-production.up.railway.app`

6. **Share and use**:
   - Share the URL with anyone
   - They can analyze stocks without any setup!

**Cost**: ~$5-10/month on Railway's paid tier (free tier available with limits)

---

## Testing Your Installation

Once the app is running, try this test:

1. **Open the web interface**
2. **Type**: "AAPL" or "analyze Apple"
3. **Configure settings**:
   - Date: Today (press Enter)
   - Analysts: All (press Enter)
   - Position: None (press Enter)
   - Debate rounds: 1 (press Enter)
   - Predictions: No (press Enter)
   - LLM: OpenAI (press Enter or select your provider)

4. **Wait for analysis** (2-5 minutes)

5. **Check results**:
   - You should see agent updates in real-time
   - Final recommendation with prices
   - Downloadable reports

---

## Troubleshooting

### "Module not found: chainlit"
```bash
pip install chainlit
```

### "API key not found"
- Make sure your `.env` file exists and has the correct keys
- Check that you've set at least one LLM provider key

### "Port 8000 already in use"
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# OR use a different port
chainlit run chainlit_app.py --port 8001
```

### "Cannot connect to Docker daemon"
```bash
# Make sure Docker Desktop is running
open -a Docker

# Wait for Docker to start, then try again
docker-compose up
```

### Analysis takes too long
- Reduce the number of analysts (try just "market,news")
- Keep debate rounds at 1
- Disable predictions
- Use faster models (gpt-4o-mini instead of o4-mini)

### Out of memory errors
- Close other applications
- If using Docker, increase memory limit in Docker Desktop settings
- If on cloud, upgrade to a plan with more RAM (2GB minimum)

---

## What's Next?

### For Development
- Customize the UI by editing `chainlit_app.py`
- Modify agent behavior in `tradingagents/agents/`
- Add new features or data sources

### For Production
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guides
- Set up monitoring and logging
- Configure auto-scaling
- Add authentication if needed

### For Users
- Just share the URL!
- No installation needed on their end
- Works on any device with a browser

---

## File Structure

After running, you'll see:

```
TradingAgents/
├── chainlit_app.py          # Main web app
├── .chainlit                # Chainlit config
├── README_CHAINLIT.md       # User guide (shows on web)
├── results/                 # Analysis results
│   └── {TICKER}/
│       └── {DATE}/
│           └── reports/     # Markdown reports
├── dataflows/
│   └── data_cache/         # Cached API responses
└── .env                    # Your API keys (don't commit!)
```

---

## Configuration Options

### Change Port
```bash
chainlit run chainlit_app.py --port 8001
```

### Enable Debug Mode
```bash
chainlit run chainlit_app.py --debug
```

### Run in Background
```bash
nohup chainlit run chainlit_app.py > chainlit.log 2>&1 &
```

### Change LLM Provider
Edit the configuration when starting an analysis, or modify defaults in `tradingagents/default_config.py`

---

## Tips for Best Experience

1. **Use good API keys**:
   - OpenAI or Anthropic for best results
   - Alpha Vantage for comprehensive data

2. **Start simple**:
   - Test with just 2 analysts first
   - Use 1 debate round
   - Disable predictions initially

3. **Monitor costs**:
   - Each analysis makes multiple LLM calls
   - o4-mini is more expensive than gpt-4o-mini
   - Enable caching to reduce API calls

4. **Share thoughtfully**:
   - Set up authentication for public deployments
   - Monitor usage to avoid unexpected costs
   - Consider rate limiting if sharing widely

---

## Getting API Keys

### OpenAI (Recommended)
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up and add payment method
3. Go to API keys section
4. Create new key
5. Cost: ~$0.10-1.00 per analysis (depending on models)

### Anthropic (Claude)
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up
3. Create API key
4. Cost: ~$0.15-0.50 per analysis

### Alpha Vantage (Data)
1. Go to [alphavantage.co](https://www.alphavantage.co)
2. Get free API key
3. Free tier: 25 calls/day
4. Premium: $49.99/month for unlimited

### Google (Gemini)
1. Go to [ai.google.dev](https://ai.google.dev)
2. Get API key
3. Free tier available!

---

## Support

- **Issues**: Open an issue on GitHub
- **Questions**: Check [DEPLOYMENT.md](DEPLOYMENT.md)
- **Updates**: Pull the latest code with `git pull`

---

**Ready to start?** Run `./start_web.sh` and open http://localhost:8000! 🚀

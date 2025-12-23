# 🤖 TradingAgents Web Interface

Welcome! This is a conversational interface for the TradingAgents multi-agent trading analysis system.

## What is TradingAgents?

TradingAgents uses specialized AI agents that collaborate to analyze stocks from multiple perspectives:

### 📊 Analyst Teams
- **Market Analyst** - Technical indicators (MACD, RSI, Bollinger Bands)
- **Social Analyst** - Reddit sentiment and community discussions
- **News Analyst** - Breaking news, insider transactions, global events
- **Fundamentals Analyst** - Financial statements and company metrics

### 🎯 Research & Decision Teams
- **Bull & Bear Researchers** - Debate the investment thesis
- **Research Manager** - Synthesizes the debate
- **Trader** - Creates executable trading plans
- **Risk Management Team** - Evaluates risk from multiple perspectives
- **Portfolio Manager** - Makes final position-aware recommendations

### 🔮 Prediction Team (Optional)
- **Price Forecasts** - 14-day, 30-day, and 90-day predictions with probabilities

## How to Use

1. **Start a conversation** - The system will guide you through configuration
2. **Choose your settings**:
   - Stock ticker (e.g., AAPL, TSLA, MSFT)
   - Analysis date
   - Which analysts to include
   - Your current position (optional)
   - Research depth (debate rounds)
   - Enable/disable predictions
   - LLM provider (OpenAI, Anthropic, Google, etc.)

3. **Watch the agents work** - See real-time updates as each agent completes their analysis

4. **Get comprehensive reports** - Download detailed markdown reports with:
   - Technical analysis
   - Sentiment analysis
   - News summaries
   - Investment recommendations with exact entry/exit prices
   - Risk assessment
   - Price predictions (if enabled)

## Example Analysis

```
User: "Analyze TSLA"

System will ask:
- Analysis date? [Today]
- Which analysts? [All]
- Current position? [None]
- Debate rounds? [1]
- Enable predictions? [No]
- LLM provider? [OpenAI]

Then run the full analysis pipeline and provide:
✅ Market technical analysis
✅ Social sentiment from Reddit
✅ Recent news and events
✅ Fundamental metrics
✅ Bull vs Bear debate
✅ Trading plan with specific prices
✅ Risk assessment
✅ Final recommendation
```

## Supported LLM Providers

- **OpenAI** - GPT-4, o4-mini, gpt-4o-mini
- **Anthropic** - Claude Sonnet 4, Claude Haiku
- **Google** - Gemini 2.0 Flash
- **OpenRouter** - DeepSeek R1, Gemini Free
- **Ollama** - Local models (llama3.1, qwen2.5)

## Required API Keys

Make sure you have the necessary API keys in your `.env` file:

```bash
# LLM Provider (at least one required)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here

# Data Providers (optional but recommended)
ALPHA_VANTAGE_API_KEY=your_key_here

# Social Media (optional)
REDDIT_CLIENT_ID=your_id_here
REDDIT_CLIENT_SECRET=your_secret_here
```

## Tips for Best Results

1. **Use multiple analysts** - Each provides unique insights
2. **Enable predictions** - Get probabilistic price forecasts
3. **Specify your position** - Get personalized recommendations
4. **Increase debate rounds** - More thorough analysis (but slower)
5. **Try different LLM providers** - Each has unique reasoning styles

## Getting Started

Simply type a message to begin! Try:
- "Analyze AAPL"
- "What do you think about Tesla?"
- "I want to analyze Microsoft"

The system will guide you through the rest! 🚀

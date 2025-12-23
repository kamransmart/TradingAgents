"""
Chainlit Web Interface for TradingAgents - Simplified Version

This app provides a web-based chat interface for the TradingAgents multi-agent system.
"""

import os
import chainlit as cl
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Load environment variables
load_dotenv()

# LLM provider configurations
LLM_PROVIDERS = {
    "OpenAI": {
        "provider": "openai",
        "deep_model": "o4-mini",
        "quick_model": "gpt-4o-mini",
        "url": "https://api.openai.com/v1"
    },
    "Anthropic": {
        "provider": "anthropic",
        "deep_model": "claude-sonnet-4",
        "quick_model": "claude-3-5-haiku-20241022",
        "url": "https://api.anthropic.com/v1/messages"
    },
}


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    await cl.Message(
        content="""# 🤖 TradingAgents Web Interface

Welcome! I'll help you analyze stocks using AI agents.

**To start**, simply type a stock ticker (e.g., "AAPL", "TSLA", "MSFT")
"""
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""

    ticker = message.content.strip().upper()

    # Simple validation
    if len(ticker) > 5 or not ticker.isalpha():
        await cl.Message(
            content="Please provide a valid stock ticker (e.g., AAPL, TSLA, MSFT)"
        ).send()
        return

    await cl.Message(content=f"🔄 Starting analysis for **{ticker}**...").send()

    try:
        # Use default configuration
        config = DEFAULT_CONFIG.copy()

        # Create the graph (automatically builds internally)
        await cl.Message(content="🔧 Initializing trading agents...").send()

        graph = TradingAgentsGraph(
            selected_analysts=["market", "news"],  # Use fewer analysts for faster results
            debug=False,
            config=config
        )

        # Create initial state
        await cl.Message(content="📊 Preparing analysis...").send()

        init_state = graph.propagator.create_initial_state(
            ticker,
            datetime.now().strftime('%Y-%m-%d')
        )
        args = graph.propagator.get_graph_args()

        # Run the analysis
        await cl.Message(content="🚀 Running analysis (this may take 2-5 minutes)...").send()

        # Use invoke instead of stream for simplicity
        final_state = graph.graph.invoke(init_state, **args)

        # Extract final decision
        final_decision = final_state.get("final_trade_decision", "No decision available")

        # Send result
        await cl.Message(
            content=f"""# 📊 Analysis Complete for {ticker}

## Final Trading Decision

{final_decision}

---

*Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        ).send()

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()

        await cl.Message(
            content=f"""❌ **Error during analysis**

{str(e)}

**Debug info:**
```
{error_details[-800:]}
```

Please check:
- Your API keys are set in `.env`
- You have a valid OpenAI API key
- The ticker symbol is correct
"""
        ).send()


if __name__ == "__main__":
    pass

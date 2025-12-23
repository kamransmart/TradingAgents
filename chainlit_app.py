"""
Chainlit Web Interface for TradingAgents

This app provides a web-based chat interface for the TradingAgents multi-agent system.
Users can trigger analysis through a conversational interface and see real-time agent outputs.
"""

import os
import chainlit as cl
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Load environment variables
load_dotenv()


# Configuration options for the UI
ANALYST_OPTIONS = {
    "Market Analysis": "market",
    "Social Sentiment": "social",
    "News Analysis": "news",
    "Fundamentals Analysis": "fundamentals"
}

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
    "Google": {
        "provider": "google",
        "deep_model": "gemini-2.0-flash-exp",
        "quick_model": "gemini-2.0-flash-exp",
        "url": None
    },
    "OpenRouter": {
        "provider": "openrouter",
        "deep_model": "deepseek/deepseek-r1",
        "quick_model": "google/gemini-2.0-flash-exp:free",
        "url": "https://openrouter.ai/api/v1"
    },
    "Ollama (Local)": {
        "provider": "ollama",
        "deep_model": "qwen2.5:7b",
        "quick_model": "qwen2.5:7b",
        "url": "http://localhost:11434/v1"
    }
}


@cl.on_chat_start
async def start():
    """Initialize the chat session with welcome message and settings form."""

    # Welcome message
    welcome_msg = """# 🤖 TradingAgents Web Interface

Welcome to the TradingAgents multi-agent trading analysis system!

This system uses specialized AI agents to analyze stocks from multiple perspectives:
- 📊 **Market Analyst**: Technical indicators, price patterns
- 💬 **Social Analyst**: Reddit sentiment, community discussions
- 📰 **News Analyst**: Breaking news, insider transactions, global events
- 📈 **Fundamentals Analyst**: Financial statements, company metrics

The agents will debate and collaborate to provide you with comprehensive investment recommendations.

**To get started**, please configure your analysis settings below.
"""

    await cl.Message(content=welcome_msg).send()

    # Create settings form
    settings = await cl.AskUserMessage(
        content="Let's configure your analysis. Please provide the following:",
        timeout=300,
    ).send()

    # Store in user session
    cl.user_session.set("initialized", True)


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages and trigger analysis."""

    # Check if this is the first message after settings
    if not cl.user_session.get("config_set"):
        await configure_analysis(message.content)
        return

    # Otherwise, process as a new analysis request
    await handle_analysis_request(message.content)


async def configure_analysis(user_input: str):
    """Configure analysis parameters through interactive forms."""

    # Ask for ticker symbol
    ticker_response = await cl.AskUserMessage(
        content="📊 Which stock ticker would you like to analyze? (e.g., AAPL, TSLA, MSFT)",
        timeout=60
    ).send()
    ticker = ticker_response['output'].strip().upper()

    # Ask for analysis date
    date_response = await cl.AskUserMessage(
        content=f"📅 Analysis date? (Press Enter for today: {datetime.now().strftime('%Y-%m-%d')})",
        timeout=60
    ).send()
    analysis_date = date_response['output'].strip() or datetime.now().strftime('%Y-%m-%d')

    # Ask for analyst selection
    analyst_msg = """🔍 Select which analysts to include (comma-separated):

1. **market** - Technical analysis (MACD, RSI, price patterns)
2. **social** - Reddit sentiment analysis
3. **news** - News events & insider transactions
4. **fundamentals** - Financial statements & metrics

Example: market,news,fundamentals
(Press Enter for all analysts)"""

    analyst_response = await cl.AskUserMessage(
        content=analyst_msg,
        timeout=90
    ).send()

    analyst_input = analyst_response['output'].strip().lower()
    if analyst_input:
        selected_analysts = [a.strip() for a in analyst_input.split(',') if a.strip()]
        # Validate analyst names
        valid_analysts = ["market", "social", "news", "fundamentals"]
        selected_analysts = [a for a in selected_analysts if a in valid_analysts]
        if not selected_analysts:
            await cl.Message(content="⚠️ No valid analysts selected, using all analysts.").send()
            selected_analysts = ["market", "social", "news", "fundamentals"]
    else:
        selected_analysts = ["market", "social", "news", "fundamentals"]

    # Ask for portfolio position (optional)
    position_msg = """💼 Do you currently own shares of this stock?

If yes, provide: <shares>,<purchase_price>
Example: 100,150.50

Press Enter to skip."""

    position_response = await cl.AskUserMessage(
        content=position_msg,
        timeout=60
    ).send()

    shares_owned = 0
    purchase_price = 0
    position_input = position_response['output'].strip()
    if position_input:
        try:
            parts = position_input.split(',')
            shares_owned = float(parts[0].strip())
            purchase_price = float(parts[1].strip())
        except:
            await cl.Message(content="⚠️ Invalid format, proceeding without position data.").send()

    # Ask for debate rounds
    rounds_response = await cl.AskUserMessage(
        content="🔄 Research depth (1-5 debate rounds)? Press Enter for 1:",
        timeout=30
    ).send()

    try:
        debate_rounds = int(rounds_response['output'].strip() or "1")
        debate_rounds = max(1, min(5, debate_rounds))
    except:
        debate_rounds = 1

    # Ask for prediction team
    prediction_response = await cl.AskUserMessage(
        content="🔮 Include price predictions (14/30/90 day forecasts)? (yes/no, default: no)",
        timeout=30
    ).send()

    enable_predictions = prediction_response['output'].strip().lower() in ['yes', 'y']

    # Ask for LLM provider
    provider_msg = f"""🤖 Select LLM provider (enter number):

1. OpenAI (GPT-4, o4-mini)
2. Anthropic (Claude Sonnet, Haiku)
3. Google (Gemini 2.0)
4. OpenRouter (DeepSeek R1, Gemini)
5. Ollama (Local models)

Press Enter for OpenAI:"""

    provider_response = await cl.AskUserMessage(
        content=provider_msg,
        timeout=60
    ).send()

    provider_choice = provider_response['output'].strip() or "1"
    provider_map = {
        "1": "OpenAI",
        "2": "Anthropic",
        "3": "Google",
        "4": "OpenRouter",
        "5": "Ollama (Local)"
    }
    provider_name = provider_map.get(provider_choice, "OpenAI")
    provider_config = LLM_PROVIDERS[provider_name]

    # Build configuration
    config = DEFAULT_CONFIG.copy()
    config.update({
        "llm_provider": provider_config["provider"],
        "deep_think_llm": provider_config["deep_model"],
        "quick_think_llm": provider_config["quick_model"],
        "backend_url": provider_config["url"],
        "max_debate_rounds": debate_rounds,
        "max_risk_discuss_rounds": 1,
        "max_prediction_rounds": 1,
    })

    # Store in session
    cl.user_session.set("config", config)
    cl.user_session.set("ticker", ticker)
    cl.user_session.set("analysis_date", analysis_date)
    cl.user_session.set("selected_analysts", selected_analysts)
    cl.user_session.set("shares_owned", shares_owned)
    cl.user_session.set("purchase_price", purchase_price)
    cl.user_session.set("enable_predictions", enable_predictions)
    cl.user_session.set("config_set", True)

    # Confirmation message
    confirmation = f"""✅ Configuration Complete!

**Ticker**: {ticker}
**Date**: {analysis_date}
**Analysts**: {', '.join(selected_analysts)}
**Position**: {f'{shares_owned} shares @ ${purchase_price}' if shares_owned > 0 else 'None'}
**Debate Rounds**: {debate_rounds}
**Predictions**: {'Enabled' if enable_predictions else 'Disabled'}
**LLM Provider**: {provider_name}

Starting analysis now... This may take 2-5 minutes depending on the number of analysts and debate rounds.
"""

    await cl.Message(content=confirmation).send()

    # Trigger the analysis
    await run_trading_analysis()


async def run_trading_analysis():
    """Execute the trading agents graph and stream results."""

    # Get configuration from session
    config = cl.user_session.get("config")
    ticker = cl.user_session.get("ticker")
    analysis_date = cl.user_session.get("analysis_date")
    selected_analysts = cl.user_session.get("selected_analysts")
    shares_owned = cl.user_session.get("shares_owned")
    purchase_price = cl.user_session.get("purchase_price")
    enable_predictions = cl.user_session.get("enable_predictions")

    # Send progress messages
    await cl.Message(content="🔄 Initializing agents...").send()

    try:
        # Initialize the graph
        graph = TradingAgentsGraph(
            selected_analysts=selected_analysts,
            debug=False,
            config=config
        )

        await cl.Message(content="🔄 Building analysis graph...").send()

        # Build the graph
        compiled_graph = graph.build_graph(enable_predictions=enable_predictions)

        await cl.Message(content=f"🔄 Running analysis for {ticker}...").send()

        # Run the graph
        result = await run_graph_with_streaming(
            compiled_graph,
            ticker,
            analysis_date,
            shares_owned,
            purchase_price
        )

        # Send final results
        await send_final_results(result, ticker, analysis_date)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"❌ **Error during analysis**: {str(e)}\n\nPlease check your API keys and configuration.\n\n**Details**:\n```\n{error_details[-500:]}\n```"
        await cl.Message(content=error_msg).send()

        # Reset config to allow retry
        cl.user_session.set("config_set", False)


async def run_graph_with_streaming(graph, ticker, analysis_date, shares_owned, purchase_price):
    """Run the graph and stream agent outputs to the chat."""

    # Initial inputs
    inputs = {
        "company_of_interest": ticker,
        "trade_date": analysis_date,
        "shares_owned": shares_owned,
        "purchase_price": purchase_price,
        "messages": []
    }

    # Track agent progress
    agent_tracker = {
        "current_agent": None,
        "current_step": 0,
        "total_steps": 0
    }

    result = None

    # Stream the graph execution
    async for event in graph.astream(inputs):
        for node_name, node_output in event.items():

            # Update progress based on node
            agent_name = format_agent_name(node_name)
            agent_tracker["current_agent"] = agent_name
            agent_tracker["current_step"] += 1

            # Send progress update
            await cl.Message(
                content=f"🤖 **{agent_name}** working... (Step {agent_tracker['current_step']})"
            ).send()

            # Check if there are messages to display
            if isinstance(node_output, dict) and "messages" in node_output:
                messages = node_output["messages"]
                if messages and len(messages) > 0:
                    last_msg = messages[-1]
                    if hasattr(last_msg, 'content') and last_msg.content:
                        # Send agent message to chat
                        content_preview = last_msg.content[:300] if len(last_msg.content) > 300 else last_msg.content
                        await cl.Message(
                            content=f"**{agent_name}**: {content_preview}...",
                            author=agent_name
                        ).send()

        result = node_output

    return result


async def send_final_results(result, ticker, analysis_date):
    """Send the final analysis results and downloadable reports."""

    # Extract final decision
    final_decision = result.get("final_trade_decision", "No decision available")
    final_predictions = result.get("final_predictions", "")

    # Send final decision
    decision_msg = f"""# 📊 Final Trading Decision for {ticker}

{final_decision}
"""
    await cl.Message(content=decision_msg).send()

    # Send predictions if available
    if final_predictions:
        predictions_msg = f"""# 🔮 Price Predictions

{final_predictions}
"""
        await cl.Message(content=predictions_msg).send()

    # Check for report files
    results_dir = Path(f"./results/{ticker}/{analysis_date}")

    if results_dir.exists():
        reports_dir = results_dir / "reports"
        if reports_dir.exists():
            # Send report files
            report_files = list(reports_dir.glob("*.md"))

            if report_files:
                await cl.Message(content="📄 **Analysis Reports:**").send()

                for report_file in report_files:
                    # Read and send report content
                    with open(report_file, 'r') as f:
                        report_content = f.read()

                    # Create downloadable file
                    file_element = cl.File(
                        name=report_file.name,
                        path=str(report_file),
                        display="inline"
                    )

                    report_name = report_file.stem.replace('_', ' ').title()
                    await cl.Message(
                        content=f"**{report_name}**",
                        elements=[file_element]
                    ).send()

    # Offer to run another analysis
    await cl.Message(
        content="\n\n---\n\n✨ Analysis complete! To analyze another stock, simply type 'analyze' or the ticker symbol."
    ).send()

    # Reset for next analysis
    cl.user_session.set("config_set", False)


async def handle_analysis_request(user_message: str):
    """Handle a new analysis request from the user."""

    message_lower = user_message.lower().strip()

    if message_lower in ['analyze', 'new', 'start', 'run'] or len(message_lower) <= 5:
        # Trigger new configuration
        await configure_analysis(user_message)
    else:
        await cl.Message(
            content="To start a new analysis, type 'analyze' or provide a stock ticker symbol."
        ).send()


def format_agent_name(node_name: str) -> str:
    """Format node names to readable agent names."""

    name_map = {
        "market_analyst": "📊 Market Analyst",
        "social_analyst": "💬 Social Analyst",
        "news_analyst": "📰 News Analyst",
        "fundamentals_analyst": "📈 Fundamentals Analyst",
        "bull_researcher": "🐂 Bull Researcher",
        "bear_researcher": "🐻 Bear Researcher",
        "research_manager": "🎯 Research Manager",
        "trader": "💼 Trader",
        "risky_analyst": "🔥 Risky Analyst",
        "neutral_analyst": "⚖️ Neutral Analyst",
        "safe_analyst": "🛡️ Safe Analyst",
        "risk_manager": "⚠️ Risk Manager",
        "portfolio_manager": "💰 Portfolio Manager",
        "short_term_predictor": "📅 Short-Term Predictor",
        "medium_term_predictor": "📆 Medium-Term Predictor",
        "long_term_predictor": "🗓️ Long-Term Predictor",
        "prediction_manager": "🔮 Prediction Manager"
    }

    return name_map.get(node_name, node_name.replace('_', ' ').title())


if __name__ == "__main__":
    # This allows running the app directly with: chainlit run chainlit_app.py
    pass

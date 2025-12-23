"""
Chainlit Web Interface for TradingAgents - Interactive Version

Collects user preferences through conversational flow.
"""

import os
import chainlit as cl
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

load_dotenv()

# Configuration state
class ConfigState:
    MODEL = "model"
    TICKER = "ticker"
    ANALYSTS = "analysts"
    POSITION = "position"
    PREDICTIONS = "predictions"
    READY = "ready"


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    cl.user_session.set("state", ConfigState.MODEL)

    await cl.Message(
        content="""# 🤖 TradingAgents - AI Stock Analysis

Welcome! I'll guide you through analyzing a stock with AI agents.

**Step 1/5: Select AI Model**

Which OpenAI model would you like to use?

1. **o4-mini** - Latest reasoning model (recommended, slower but more thoughtful)
2. **gpt-4o** - GPT-4 Optimized (balanced speed and quality)
3. **gpt-4o-mini** - Fast and cost-effective
4. **o1-mini** - Previous generation reasoning model
5. **gpt-4-turbo** - GPT-4 Turbo

Type the number (1-5) or model name directly."""
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle conversational flow."""

    state = cl.user_session.get("state")
    user_input = message.content.strip()

    if state == ConfigState.MODEL:
        await handle_model(user_input)

    elif state == ConfigState.TICKER:
        await handle_ticker(user_input)

    elif state == ConfigState.ANALYSTS:
        await handle_analysts(user_input)

    elif state == ConfigState.POSITION:
        await handle_position(user_input)

    elif state == ConfigState.PREDICTIONS:
        await handle_predictions(user_input)

    elif state == ConfigState.READY:
        await cl.Message(content="Analysis is running. Please wait for results...").send()


async def handle_model(selection: str):
    """Handle model selection."""
    selection = selection.lower().strip()

    model_map = {
        "1": "o4-mini",
        "2": "gpt-4o",
        "3": "gpt-4o-mini",
        "4": "o1-mini",
        "5": "gpt-4-turbo",
        "o4-mini": "o4-mini",
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini",
        "o1-mini": "o1-mini",
        "gpt-4-turbo": "gpt-4-turbo"
    }

    model = model_map.get(selection)

    if not model:
        await cl.Message(
            content="❌ Invalid selection. Please type a number (1-5) or model name (e.g., 'gpt-4o')"
        ).send()
        return

    cl.user_session.set("model", model)
    cl.user_session.set("state", ConfigState.TICKER)

    await cl.Message(
        content=f"""✅ Using model: **{model}**

**Step 2/5: Stock Ticker**

Which stock would you like to analyze?

Examples: AAPL, TSLA, MSFT, NVDA, GOOGL"""
    ).send()


async def handle_ticker(ticker: str):
    """Handle ticker input."""
    ticker = ticker.upper().strip()

    # Validation
    if len(ticker) > 5 or not ticker.isalpha():
        await cl.Message(
            content="❌ Please enter a valid stock ticker (e.g., AAPL, TSLA, MSFT)"
        ).send()
        return

    cl.user_session.set("ticker", ticker)
    cl.user_session.set("state", ConfigState.ANALYSTS)

    await cl.Message(
        content=f"""✅ Analyzing **{ticker}**

**Step 3/5: Select Analysts**

Which analysts should I use? Type the numbers separated by commas, or type 'all':

1. **Market** - Technical analysis (MACD, RSI, price patterns)
2. **Social** - Reddit sentiment analysis
3. **News** - News events & insider transactions
4. **Fundamentals** - Financial statements & metrics

Examples:
- Type: `all` (use all analysts - recommended)
- Type: `1,3,4` (market, news, fundamentals)
- Type: `1,2` (market and social)"""
    ).send()


async def handle_analysts(selection: str):
    """Handle analyst selection."""
    selection = selection.lower().strip()

    analyst_map = {
        "1": "market",
        "2": "social",
        "3": "news",
        "4": "fundamentals"
    }

    if selection == "all":
        selected = ["market", "social", "news", "fundamentals"]
    else:
        nums = [n.strip() for n in selection.replace(',', ' ').split()]
        selected = [analyst_map.get(n) for n in nums if n in analyst_map]

    if not selected:
        await cl.Message(
            content="❌ Invalid selection. Please try again (e.g., 'all' or '1,3,4')"
        ).send()
        return

    cl.user_session.set("analysts", selected)
    cl.user_session.set("state", ConfigState.POSITION)

    analyst_names = ", ".join(selected)
    await cl.Message(
        content=f"""✅ Using analysts: **{analyst_names}**

**Step 4/5: Portfolio Position (Optional)**

Do you currently own shares of this stock?

- If **YES**: Type shares and price (e.g., `100 150.50` or `100,150.50`)
- If **NO**: Type `no` or `skip`

Example: If you own 100 shares bought at $150.50, type: `100 150.50`"""
    ).send()


async def handle_position(position_input: str):
    """Handle position input."""
    position_input = position_input.lower().strip()

    shares_owned = 0
    purchase_price = 0

    if position_input not in ["no", "skip", "none", ""]:
        try:
            # Try parsing: "100 150.50" or "100,150.50"
            parts = position_input.replace(',', ' ').split()
            if len(parts) >= 2:
                shares_owned = float(parts[0])
                purchase_price = float(parts[1])
        except:
            await cl.Message(
                content="❌ Invalid format. Please type like: `100 150.50` or type `skip`"
            ).send()
            return

    cl.user_session.set("shares_owned", shares_owned)
    cl.user_session.set("purchase_price", purchase_price)
    cl.user_session.set("state", ConfigState.PREDICTIONS)

    if shares_owned > 0:
        await cl.Message(
            content=f"""✅ Position: **{shares_owned} shares @ ${purchase_price}**

**Step 5/5: Price Predictions**

Should I include price predictions (14/30/90 day forecasts)?

- Type `yes` to enable predictions (takes longer)
- Type `no` to skip predictions (faster)"""
        ).send()
    else:
        await cl.Message(
            content="""✅ No position data

**Step 5/5: Price Predictions**

Should I include price predictions (14/30/90 day forecasts)?

- Type `yes` to enable predictions (takes longer)
- Type `no` to skip predictions (faster)"""
        ).send()


async def handle_predictions(choice: str):
    """Handle prediction choice and start analysis."""
    choice = choice.lower().strip()

    enable_predictions = choice in ["yes", "y", "true", "1"]

    cl.user_session.set("enable_predictions", enable_predictions)
    cl.user_session.set("state", ConfigState.READY)

    # Get all config
    model = cl.user_session.get("model")
    ticker = cl.user_session.get("ticker")
    analysts = cl.user_session.get("analysts")
    shares = cl.user_session.get("shares_owned", 0)
    price = cl.user_session.get("purchase_price", 0)

    # Build summary
    summary = f"""✅ Configuration Complete!

**Model**: {model}
**Stock**: {ticker}
**Analysts**: {', '.join(analysts)}
**Position**: {f'{shares} shares @ ${price}' if shares > 0 else 'None'}
**Predictions**: {'Enabled' if enable_predictions else 'Disabled'}

🚀 **Starting analysis...** (this will take 2-5 minutes)

I'll update you as each agent completes their work."""

    await cl.Message(content=summary).send()

    # Run analysis
    await run_analysis()


async def run_analysis():
    """Execute the trading analysis."""

    try:
        # Get configuration
        model = cl.user_session.get("model", "gpt-4o-mini")
        ticker = cl.user_session.get("ticker")
        analysts = cl.user_session.get("analysts")
        shares = cl.user_session.get("shares_owned", 0)
        price = cl.user_session.get("purchase_price", 0)
        enable_predictions = cl.user_session.get("enable_predictions", False)

        # Setup config
        config = DEFAULT_CONFIG.copy()
        config["enable_prediction_team"] = enable_predictions
        config["deep_think_llm"] = model
        config["quick_think_llm"] = model

        # Create graph
        await cl.Message(content="🔧 Initializing AI agents...").send()

        graph = TradingAgentsGraph(
            selected_analysts=analysts,
            debug=False,
            config=config
        )

        # Create initial state
        await cl.Message(content="📊 Setting up analysis...").send()

        init_state = graph.propagator.create_initial_state(
            ticker,
            datetime.now().strftime('%Y-%m-%d')
        )

        # Add position data if provided
        if shares > 0:
            init_state["shares_owned"] = shares
            init_state["purchase_price"] = price

        args = graph.propagator.get_graph_args()

        # Stream the analysis with updates
        await cl.Message(content=f"🤖 Running {len(analysts)} agents for {ticker}...").send()

        step_count = 0
        # Track each report type separately to prevent duplicates
        shown_reports = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "judge_decision": None,
            "trader_investment_plan": None,
            "risk_decision": None,
            "final_trade_decision": None
        }

        async for chunk in graph.graph.astream(init_state, **args):
            step_count += 1

            # Check for analyst reports (show with 3000 char preview)
            if "market_report" in chunk and chunk["market_report"] and chunk["market_report"] != shown_reports["market_report"]:
                report = chunk["market_report"]
                preview = report[:3000] + "\n\n*[Report continues...]*" if len(report) > 3000 else report
                await cl.Message(content=f"📊 **Market Analyst** completed\n\n{preview}").send()
                shown_reports["market_report"] = report

            if "sentiment_report" in chunk and chunk["sentiment_report"] and chunk["sentiment_report"] != shown_reports["sentiment_report"]:
                report = chunk["sentiment_report"]
                preview = report[:3000] + "\n\n*[Report continues...]*" if len(report) > 3000 else report
                await cl.Message(content=f"💬 **Social Analyst** completed\n\n{preview}").send()
                shown_reports["sentiment_report"] = report

            if "news_report" in chunk and chunk["news_report"] and chunk["news_report"] != shown_reports["news_report"]:
                report = chunk["news_report"]
                preview = report[:3000] + "\n\n*[Report continues...]*" if len(report) > 3000 else report
                await cl.Message(content=f"📰 **News Analyst** completed\n\n{preview}").send()
                shown_reports["news_report"] = report

            if "fundamentals_report" in chunk and chunk["fundamentals_report"] and chunk["fundamentals_report"] != shown_reports["fundamentals_report"]:
                report = chunk["fundamentals_report"]
                preview = report[:3000] + "\n\n*[Report continues...]*" if len(report) > 3000 else report
                await cl.Message(content=f"📈 **Fundamentals Analyst** completed\n\n{preview}").send()
                shown_reports["fundamentals_report"] = report

            # Check for debate states (show with 3000 char preview)
            if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
                debate = chunk["investment_debate_state"]
                if "judge_decision" in debate and debate["judge_decision"] and debate["judge_decision"] != shown_reports["judge_decision"]:
                    decision = debate["judge_decision"]
                    preview = decision[:3000] + "\n\n*[Report continues...]*" if len(decision) > 3000 else decision
                    await cl.Message(content=f"🎯 **Research Manager** completed\n\n{preview}").send()
                    shown_reports["judge_decision"] = decision

            if "trader_investment_plan" in chunk and chunk["trader_investment_plan"] and chunk["trader_investment_plan"] != shown_reports["trader_investment_plan"]:
                plan = chunk["trader_investment_plan"]
                preview = plan[:3000] + "\n\n*[Report continues...]*" if len(plan) > 3000 else plan
                await cl.Message(content=f"💼 **Trader** created plan\n\n{preview}").send()
                shown_reports["trader_investment_plan"] = plan

            if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
                risk = chunk["risk_debate_state"]
                if "judge_decision" in risk and risk["judge_decision"] and risk["judge_decision"] != shown_reports["risk_decision"]:
                    decision = risk["judge_decision"]
                    preview = decision[:3000] + "\n\n*[Report continues...]*" if len(decision) > 3000 else decision
                    await cl.Message(content=f"⚠️ **Risk Manager** completed\n\n{preview}").send()
                    shown_reports["risk_decision"] = decision

            if "final_trade_decision" in chunk and chunk["final_trade_decision"] and chunk["final_trade_decision"] != shown_reports["final_trade_decision"]:
                decision = chunk["final_trade_decision"]
                # Don't show preview here since we'll show the full decision at the end
                await cl.Message(content="💰 **Portfolio Manager** made final decision").send()
                shown_reports["final_trade_decision"] = decision

            # Show periodic progress
            if step_count % 10 == 0:
                await cl.Message(content=f"⏳ Processing... (step {step_count})").send()

        # Get final state
        final_state = chunk

        # Extract results
        final_decision = final_state.get("final_trade_decision", "No decision available")
        final_predictions = final_state.get("final_predictions", "")

        # Save results to file
        analysis_date = datetime.now().strftime('%Y-%m-%d')
        results_dir = Path("results") / ticker / analysis_date
        reports_dir = results_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Save individual reports
        if shown_reports["market_report"]:
            with open(reports_dir / "market_report.md", "w") as f:
                f.write(shown_reports["market_report"])

        if shown_reports["sentiment_report"]:
            with open(reports_dir / "sentiment_report.md", "w") as f:
                f.write(shown_reports["sentiment_report"])

        if shown_reports["news_report"]:
            with open(reports_dir / "news_report.md", "w") as f:
                f.write(shown_reports["news_report"])

        if shown_reports["fundamentals_report"]:
            with open(reports_dir / "fundamentals_report.md", "w") as f:
                f.write(shown_reports["fundamentals_report"])

        if shown_reports["judge_decision"]:
            with open(reports_dir / "investment_plan.md", "w") as f:
                f.write(shown_reports["judge_decision"])

        if shown_reports["trader_investment_plan"]:
            with open(reports_dir / "trader_investment_plan.md", "w") as f:
                f.write(shown_reports["trader_investment_plan"])

        if shown_reports["risk_decision"]:
            with open(reports_dir / "risk_analysis.md", "w") as f:
                f.write(shown_reports["risk_decision"])

        # Save final decision
        with open(results_dir / f"{ticker}_final_decision.txt", "w") as f:
            f.write(final_decision)

        if final_predictions:
            with open(reports_dir / "predictions.md", "w") as f:
                f.write(final_predictions)

        # Send results
        await cl.Message(
            content=f"""# 📊 Analysis Complete for {ticker}

## Final Trading Decision

{final_decision}

---

*Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Results saved to: `{results_dir}`*"""
        ).send()

        if final_predictions:
            await cl.Message(
                content=f"""## 🔮 Price Predictions

{final_predictions}"""
            ).send()

        # Offer to analyze another
        await cl.Message(
            content="""---

✨ **Analysis complete!**

Want to analyze another stock? Just type a new ticker symbol to start over."""
        ).send()

        # Reset state for new analysis
        cl.user_session.set("state", ConfigState.MODEL)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()

        await cl.Message(
            content=f"""❌ **Error during analysis**

{str(e)}

**Debug info:**
```
{error_details[-600:]}
```

Please check:
- Your API keys are set in `.env`
- The ticker symbol is correct
- You have sufficient API credits

Type a new ticker to try again."""
        ).send()

        # Reset state
        cl.user_session.set("state", ConfigState.MODEL)


if __name__ == "__main__":
    pass

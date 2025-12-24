"""
Chainlit Web Interface for TradingAgents with Results Viewer

This app provides a web-based chat interface for the TradingAgents multi-agent system
with an integrated results viewer to browse and explore previous analyses.
"""

import os
import chainlit as cl
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional
import boto3
from botocore.exceptions import ClientError

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from results_viewer import ResultsManager, format_results_list, format_report_content

# Load environment variables
load_dotenv()

# S3 Configuration
S3_BUCKET = os.getenv("S3_RESULTS_BUCKET", "tradingagents-results-185327115759")
USE_S3 = os.getenv("USE_S3", "true").lower() == "true"

def save_to_s3(content: str, s3_key: str) -> bool:
    """Save content to S3 bucket."""
    if not USE_S3:
        return False

    try:
        s3_client = boto3.client('s3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=content.encode('utf-8'),
            ContentType='text/plain'
        )
        return True
    except ClientError as e:
        print(f"Error saving to S3: {e}")
        return False

# Initialize Results Manager
results_manager = ResultsManager()

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
    """Initialize the chat session with welcome message and options."""

    # Welcome message with results viewer option
    welcome_msg = """# 🤖 TradingAgents Web Interface

Welcome to the TradingAgents multi-agent trading analysis system!

## What would you like to do?

**Option 1: Run New Analysis**
Analyze stocks using specialized AI agents:
- 📊 **Market Analyst**: Technical indicators, price patterns
- 💬 **Social Analyst**: Reddit sentiment, community discussions
- 📰 **News Analyst**: Breaking news, insider transactions, global events
- 📈 **Fundamentals Analyst**: Financial statements, company metrics

**Option 2: Browse Previous Results**
View and explore previously generated analysis reports.

---

**Commands:**
- Type `analyze` or `new` to start a new analysis
- Type `results` or `browse` to view previous results
- Type `help` for more commands

**Quick Start:** Just type a command or stock ticker to begin!
"""

    await cl.Message(content=welcome_msg).send()

    # Initialize user session
    cl.user_session.set("initialized", True)
    cl.user_session.set("mode", "menu")  # menu, analysis, results_viewer


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages and route to appropriate handler."""

    message_lower = message.content.lower().strip()
    current_mode = cl.user_session.get("mode", "menu")

    # Help command
    if message_lower in ["help", "?", "/help"]:
        await show_help()
        return

    # Results viewer commands
    if message_lower in ["results", "browse", "view", "history", "past"]:
        cl.user_session.set("mode", "results_viewer")
        await show_results_browser()
        return

    # Analysis commands
    if message_lower in ["analyze", "new", "start", "run", "analysis"]:
        cl.user_session.set("mode", "analysis")
        cl.user_session.set("config_set", False)
        await configure_analysis(message.content)
        return

    # Main menu command
    if message_lower in ["menu", "main", "home", "back"]:
        cl.user_session.set("mode", "menu")
        await start()
        return

    # Mode-specific handling
    if current_mode == "results_viewer":
        await handle_results_viewer_input(message.content)
    elif current_mode == "analysis":
        if not cl.user_session.get("config_set"):
            await configure_analysis(message.content)
        else:
            await handle_analysis_request(message.content)
    else:
        # Try to interpret as ticker or command
        if len(message_lower) <= 5 and message_lower.isalpha():
            # Likely a ticker symbol
            cl.user_session.set("mode", "analysis")
            cl.user_session.set("config_set", False)
            await configure_analysis(message.content)
        else:
            await cl.Message(
                content="I didn't understand that. Type `help` for available commands, `analyze` to start a new analysis, or `results` to browse previous results."
            ).send()


async def show_help():
    """Display help information."""
    help_msg = """# 📚 TradingAgents Help

## Available Commands

### Main Commands
- `analyze`, `new`, `start` - Start a new stock analysis
- `results`, `browse`, `history` - View previous analysis results
- `menu`, `home`, `back` - Return to main menu
- `help` - Show this help message

### In Results Viewer
- `list` - Show all available results
- `recent [N]` - Show N most recent results (default: 10)
- `ticker AAPL` - Show all results for a specific ticker
- `view N` - View full details for result number N
- `report N [report_name]` - View specific report from result N
- `stats` - Show summary statistics

### In Analysis Mode
- Type a ticker symbol (e.g., `AAPL`) to start analysis
- Follow the prompts to configure your analysis

### Examples
```
analyze          # Start new analysis
results          # Browse all results
recent 5         # Show 5 most recent
ticker TSLA      # Show TSLA results
view 1           # View first result
stats            # Show statistics
```
"""
    await cl.Message(content=help_msg).send()


async def show_results_browser():
    """Display the main results browser interface."""

    # Get summary stats
    stats = results_manager.get_summary_stats()

    # Get recent results
    recent_results = results_manager.get_recent_results(limit=10)

    stats_msg = f"""# 📊 Results Browser

## Summary Statistics
- **Total Analyses**: {stats['total_analyses']}
- **Unique Tickers**: {stats['unique_tickers']}
- **Date Range**: {stats['date_range'] if stats['date_range'] else 'N/A'}
- **Most Analyzed**: {stats['most_analyzed_ticker'] if stats['most_analyzed_ticker'] else 'N/A'}

## Recent Analyses (Last 10)
{format_results_list(recent_results)}

---

## Available Commands
- `list` - Show all results
- `recent [N]` - Show N most recent results
- `ticker SYMBOL` - Filter by ticker (e.g., `ticker AAPL`)
- `view N` - View detailed reports for result number N
- `stats` - Show detailed statistics
- `menu` - Return to main menu

**Type a command to continue...**
"""

    await cl.Message(content=stats_msg).send()

    # Store recent results for reference
    cl.user_session.set("current_results_list", recent_results)


async def handle_results_viewer_input(user_input: str):
    """Handle commands in results viewer mode."""

    parts = user_input.lower().strip().split()
    if not parts:
        return

    command = parts[0]

    try:
        # List all results
        if command == "list":
            all_results = results_manager.get_all_results()
            msg = f"# 📋 All Results ({len(all_results)} total)\n\n"
            msg += format_results_list(all_results, show_details=True)
            await cl.Message(content=msg).send()
            cl.user_session.set("current_results_list", all_results)

        # Show recent N results
        elif command == "recent":
            limit = int(parts[1]) if len(parts) > 1 else 10
            recent = results_manager.get_recent_results(limit=limit)
            msg = f"# 🕐 Recent Results (Last {limit})\n\n"
            msg += format_results_list(recent, show_details=True)
            await cl.Message(content=msg).send()
            cl.user_session.set("current_results_list", recent)

        # Filter by ticker
        elif command == "ticker":
            if len(parts) < 2:
                await cl.Message(content="Please specify a ticker symbol. Example: `ticker AAPL`").send()
                return

            ticker = parts[1].upper()
            ticker_results = results_manager.get_results_by_ticker(ticker)

            if not ticker_results:
                await cl.Message(content=f"No results found for ticker **{ticker}**.").send()
                return

            msg = f"# 📈 Results for {ticker} ({len(ticker_results)} analyses)\n\n"
            msg += format_results_list(ticker_results, show_details=True)
            await cl.Message(content=msg).send()
            cl.user_session.set("current_results_list", ticker_results)

        # View specific result
        elif command == "view":
            if len(parts) < 2:
                await cl.Message(content="Please specify a result number. Example: `view 1`").send()
                return

            result_num = int(parts[1]) - 1
            current_list = cl.user_session.get("current_results_list", [])

            if result_num < 0 or result_num >= len(current_list):
                await cl.Message(content=f"Invalid result number. Please choose between 1 and {len(current_list)}.").send()
                return

            result = current_list[result_num]
            await show_result_details(result)

        # Show stats
        elif command == "stats":
            stats = results_manager.get_summary_stats()

            msg = f"""# 📊 Detailed Statistics

**Total Analyses**: {stats['total_analyses']}
**Unique Tickers**: {stats['unique_tickers']}
**Date Range**: {stats['date_range'] if stats['date_range'] else 'N/A'}

## Analysis Count by Ticker
"""
            if stats.get('ticker_counts'):
                for ticker, count in sorted(stats['ticker_counts'].items(), key=lambda x: x[1], reverse=True):
                    msg += f"- **{ticker}**: {count} analyses\n"

            await cl.Message(content=msg).send()

        # Report viewing
        elif command == "report":
            if len(parts) < 2:
                await cl.Message(content="Please specify a result number. Example: `report 1` or `report 1 final_trade_decision.md`").send()
                return

            result_num = int(parts[1]) - 1
            current_list = cl.user_session.get("current_results_list", [])

            if result_num < 0 or result_num >= len(current_list):
                await cl.Message(content=f"Invalid result number. Please choose between 1 and {len(current_list)}.").send()
                return

            result = current_list[result_num]

            # If specific report name provided
            if len(parts) > 2:
                report_name = parts[2]
                await show_specific_report(result, report_name)
            else:
                # Show all reports
                await show_result_details(result)

        else:
            await cl.Message(
                content=f"Unknown command: `{command}`. Type `help` for available commands."
            ).send()

    except ValueError as e:
        await cl.Message(content=f"Invalid input. Please check your command syntax. Error: {str(e)}").send()
    except Exception as e:
        await cl.Message(content=f"Error processing command: {str(e)}").send()


async def show_result_details(result: dict):
    """Display detailed information for a specific result."""

    ticker = result['ticker']
    date = result['date']

    # Get all reports
    reports = results_manager.get_all_reports_for_analysis(ticker, date)

    header = f"""# 📊 Analysis Details: {ticker} ({date})

**Reports Available**: {result['report_count']}
**Created**: {result['created_time'].strftime('%Y-%m-%d %I:%M %p') if result['created_time'] else 'Unknown'}

---
"""

    await cl.Message(content=header).send()

    # Send each report as a separate message with file attachment
    report_priority = [
        'final_trade_decision.md',
        'trader_investment_plan.md',
        'market_report.md',
        'fundamentals_report.md',
        'news_report.md',
        'sentiment_report.md'
    ]

    # Send priority reports first
    for report_name in report_priority:
        if report_name in reports:
            await send_report_message(ticker, date, report_name, reports[report_name])

    # Send remaining reports
    for report_name, content in reports.items():
        if report_name not in report_priority:
            await send_report_message(ticker, date, report_name, content)


async def send_report_message(ticker: str, date: str, report_name: str, content: str):
    """Send a single report as a message with file attachment."""

    formatted_name, preview = format_report_content(report_name, content, max_preview_length=None)

    # Create file element
    report_path = Path(f"./results/{ticker}/{date}/reports/{report_name}")

    if report_path.exists():
        file_element = cl.File(
            name=report_name,
            path=str(report_path),
            display="inline"
        )

        await cl.Message(
            content=f"## {formatted_name}\n\n{preview}",
            elements=[file_element]
        ).send()
    else:
        await cl.Message(
            content=f"## {formatted_name}\n\n{preview}"
        ).send()


async def show_specific_report(result: dict, report_name: str):
    """Show a specific report from a result."""

    ticker = result['ticker']
    date = result['date']

    # Ensure .md extension
    if not report_name.endswith('.md'):
        report_name += '.md'

    content = results_manager.read_report(ticker, date, report_name)

    if content is None:
        await cl.Message(content=f"Report `{report_name}` not found for {ticker} ({date}).").send()
        return

    await send_report_message(ticker, date, report_name, content)


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
        "enable_prediction_team": enable_predictions,
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
        # Clear any existing ChromaDB collections to avoid conflicts
        import chromadb
        from chromadb.config import Settings
        try:
            chroma_client = chromadb.Client(Settings(allow_reset=True))
            chroma_client.reset()
        except:
            pass  # Continue even if reset fails

        # Initialize the graph (builds automatically)
        graph = TradingAgentsGraph(
            selected_analysts=selected_analysts,
            debug=False,
            config=config
        )

        await cl.Message(content=f"🔄 Running analysis for {ticker}...").send()

        # Create initial state
        inputs = graph.propagator.create_initial_state(
            company_name=ticker,
            trade_date=analysis_date,
            shares_owned=shares_owned,
            purchase_price=purchase_price
        )

        # Run the graph
        result = await run_graph_with_streaming(
            graph,
            inputs
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


async def run_graph_with_streaming(graph, inputs):
    """Run the graph and stream agent outputs to the chat."""

    # Track agent progress
    agent_tracker = {
        "current_agent": None,
        "current_step": 0,
        "total_steps": 0
    }

    result = None

    # Stream the graph execution using graph.graph.astream with increased recursion limit
    config = {"recursion_limit": 100}
    async for event in graph.graph.astream(inputs, config=config):
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
                        # Send agent message to chat (full content, no truncation)
                        await cl.Message(
                            content=f"**{agent_name}**: {last_msg.content}",
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

    # Get the actual trade date from result (in case "today" was passed)
    actual_date = result.get("trade_date", analysis_date)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    s3_base = f"results/{ticker}/{actual_date}_{timestamp}"

    # Extract reports directly from result state
    reports = {
        "market_report.md": result.get("market_report"),
        "sentiment_report.md": result.get("sentiment_report"),
        "news_report.md": result.get("news_report"),
        "fundamentals_report.md": result.get("fundamentals_report"),
    }

    # Save all reports to S3 (works on Railway without local disk)
    if USE_S3:
        for report_name, report_content in reports.items():
            if report_content:
                save_to_s3(report_content, f"{s3_base}/reports/{report_name}")

        # Save final decision and predictions
        save_to_s3(final_decision, f"{s3_base}/{ticker}_final_decision.txt")
        if final_predictions:
            save_to_s3(final_predictions, f"{s3_base}/reports/predictions.md")

    # Display reports in UI
    await cl.Message(content="📄 **Analysis Reports:**").send()

    for report_name, report_content in reports.items():
        if report_content:
            formatted_name = report_name.replace('_', ' ').replace('.md', '').title()
            await cl.Message(
                content=f"**{formatted_name}**\n\n{report_content}"
            ).send()

    # Also try to attach local files if they exist (for local dev)
    results_dir = Path(f"./results/{ticker}/{actual_date}")
    if results_dir.exists():
        reports_dir = results_dir / "reports"
        if reports_dir.exists():
            report_files = list(reports_dir.glob("*.md"))
            for report_file in report_files:
                try:
                    file_element = cl.File(
                        name=report_file.name,
                        path=str(report_file),
                        display="inline"
                    )
                    await cl.Message(content=f"Download: {report_file.name}", elements=[file_element]).send()
                except:
                    pass  # Skip if file attachment fails

    # Show storage location and offer next actions
    storage_info = f"S3: `s3://{S3_BUCKET}/{s3_base}/`" if USE_S3 else f"Local: `{results_dir}`"
    await cl.Message(
        content=f"""\n\n---

✨ **Analysis complete!**

*Results saved to: {storage_info}*

**What's next?**
- Type `analyze` to analyze another stock
- Type `results` to browse all results
- Type `menu` to return to main menu"""
    ).send()

    # Return to menu mode
    cl.user_session.set("mode", "menu")
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
    # This allows running the app directly with: chainlit run chainlit_app_with_viewer.py
    pass

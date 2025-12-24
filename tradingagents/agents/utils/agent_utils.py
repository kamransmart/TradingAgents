from langchain_core.messages import HumanMessage, RemoveMessage

# Import tools from separate utility files
from tradingagents.agents.utils.core_stock_tools import (
    get_stock_data
)
from tradingagents.agents.utils.technical_indicators_tools import (
    get_indicators
)
from tradingagents.agents.utils.fundamental_data_tools import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement
)
from tradingagents.agents.utils.news_data_tools import (
    get_news,
    get_insider_sentiment,
    get_insider_transactions,
    get_global_news
)

def create_msg_delete():
    def delete_messages(state):
        """Clear messages, extract current price from tool results, and add placeholder for Anthropic compatibility"""
        messages = state["messages"]
        current_price = state.get("current_price")  # Check if already set

        # If current_price not yet set, try to extract from tool messages
        if current_price is None:
            import re
            import pandas as pd
            from langchain_core.messages import ToolMessage

            # Look for tool messages containing stock data
            for msg in reversed(messages):  # Start from most recent
                if isinstance(msg, ToolMessage):
                    content = str(msg.content)

                    # Try to parse as DataFrame string representation
                    try:
                        # Strategy: Find lines with date patterns, extract Close value from those lines
                        # This avoids grabbing numbers from other columns like "Stock Splits"

                        # Pattern: Date line with OHLCV data
                        # Format: YYYY-MM-DD,Open,High,Low,Close,Volume,Dividends,Stock Splits
                        # We want the 5th field (Close) from lines starting with a date
                        date_pattern = r'(\d{4}-\d{2}-\d{2}),([^,]+),([^,]+),([^,]+),([^,]+),'
                        matches = re.findall(date_pattern, content)

                        if matches:
                            # Get the Close price from the last (most recent) date
                            # matches[-1][4] is the Close field from the last date line
                            try:
                                current_price = float(matches[-1][4].strip())
                                break
                            except (ValueError, IndexError):
                                pass

                        # Fallback: Try DataFrame table format (less reliable)
                        # Look for Close column values that are reasonable stock prices (> $1, < $10000)
                        if not current_price:
                            close_pattern = r'Close[,\s]+(\d+\.?\d*)'
                            close_matches = re.findall(close_pattern, content, re.IGNORECASE)
                            # Filter to reasonable stock price range and take the last one
                            valid_prices = [float(p) for p in close_matches if 1.0 < float(p) < 10000.0]
                            if valid_prices:
                                current_price = valid_prices[-1]
                                break

                    except (ValueError, IndexError):
                        continue

        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]

        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")

        result = {"messages": removal_operations + [placeholder]}

        # Add current_price if we found one
        if current_price is not None:
            result["current_price"] = current_price

        return result

    return delete_messages


        
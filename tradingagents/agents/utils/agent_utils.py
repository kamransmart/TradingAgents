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
                        # Look for the last Close price in the message
                        # Multiple patterns to handle different DataFrame formats
                        patterns = [
                            # Pattern 1: Table format with column header "Close" and values
                            r'(?:Close[\s\|]+)([\d.]+)',
                            # Pattern 2: Last row format "2024-XX-XX ... Close_Value ..."
                            r'Close\s+(\d+\.?\d+)',
                            # Pattern 3: Direct number after "Close"
                            r'Close[:\s]+(\d+\.?\d+)',
                        ]

                        for pattern in patterns:
                            close_matches = re.findall(pattern, content, re.IGNORECASE)
                            if close_matches:
                                # Get the last (most recent) close price
                                try:
                                    current_price = float(close_matches[-1])
                                    break
                                except ValueError:
                                    continue

                        if current_price:
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


        
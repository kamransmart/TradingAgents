import functools
import time
import json


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        shares_owned = state.get("shares_owned", 0)
        purchase_price = state.get("purchase_price", 0)

        # Extract current price from market report
        import re
        current_price = None
        price_patterns = [
            r'Close Price[:\s]+\$?(\d+\.?\d*)',
            r'price at the close[^$]*?was\s+\$?(\d+\.?\d*)',
            r'close on[^$]*?was\s+\$?(\d+\.?\d*)',
            r'current price[^$]*?\$?(\d+\.?\d*)',
            r'\|\s*Close\s*\|\s*(\d+\.?\d+)',
        ]
        for pattern in price_patterns:
            match = re.search(pattern, market_research_report, re.IGNORECASE)
            if match:
                try:
                    current_price = float(match.group(1))
                    break
                except (ValueError, IndexError):
                    continue

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        # Build portfolio position context with current price
        position_context = ""
        if shares_owned > 0:
            total_cost = shares_owned * purchase_price
            current_value = shares_owned * current_price if current_price else total_cost
            unrealized_pnl = current_value - total_cost if current_price else 0
            pnl_pct = (unrealized_pnl / total_cost * 100) if total_cost > 0 and current_price else 0

            price_info = f"**CURRENT MARKET PRICE: ${current_price:.2f}**\n- " if current_price else ""
            position_context = f"\n\n{price_info}**CURRENT PORTFOLIO POSITION:**\n- Shares Owned: {shares_owned}\n- Purchase Price: ${purchase_price:.2f} per share\n- Total Investment: ${total_cost:.2f}"

            if current_price:
                position_context += f"\n- Current Market Price: ${current_price:.2f}\n- Current Value: ${current_value:.2f}\n- Unrealized P/L: ${unrealized_pnl:+.2f} ({pnl_pct:+.1f}%)"

            position_context += "\n\n**CRITICAL**: The current market price is ${:.2f}. All your price targets must be relative to THIS price, not the purchase price.\n\nYou must provide:\n1. Specific PRICE TARGETS relative to current ${:.2f} market price (e.g., 'Buy at $X-Y' or 'Sell at $X-Y')\n2. Percentage of position to trade\n3. Timeframe for execution".format(current_price if current_price else purchase_price, current_price if current_price else purchase_price)
        else:
            price_info = f"**CURRENT MARKET PRICE: ${current_price:.2f}**\n\n" if current_price else ""
            position_context = f"\n\n{price_info}**CURRENT PORTFOLIO POSITION:** No current position in {company_name}.\n\n"
            if current_price:
                position_context += f"**CRITICAL**: The current market price is ${current_price:.2f}. All your price targets must be relative to THIS price.\n\n"
            position_context += "You must provide:\n1. Specific PRICE TARGET relative to current market price (e.g., 'Buy at $X-Y' or 'Wait for pullback to $X')\n2. Percentage of planned position to establish\n3. Timeframe for execution"

        context = {
            "role": "user",
            "content": f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}{position_context}\n\nLeverage these insights to make an informed and strategic decision.",
        }

        messages = [
            {
                "role": "system",
                "content": f"""You are a trading agent analyzing market data to make investment decisions. Based on your analysis, provide a specific recommendation to buy, sell, or hold.

Your recommendation MUST include ALL of the following:

1. **Action**: BUY, SELL, or HOLD

2. **Price Targets** (REQUIRED - Be specific):
   - For BUY: Specific price or price range to enter (e.g., "Buy at $18.50-$19.00" or "Enter if price drops to $17")
   - For SELL: Specific price or price range to exit (e.g., "Sell at $25-$26" or "Take profit above $30")
   - For HOLD: Price levels that would trigger action (e.g., "Hold unless drops below $22 or rises above $28")
   - Include both entry/exit prices AND stop-loss levels

3. **Quantity**: Express as a percentage (e.g., "Buy to increase position by 25%" or "Sell 50% of current position")

4. **Timeframe**: General timeframe for execution (e.g., "within 1-2 weeks", "over the next month", "wait 3-6 months")

5. **Reasoning**: Brief justification for the price targets and recommendation based on technical levels, support/resistance, or catalysts

**CRITICAL**: You MUST provide specific price targets. Do not give vague guidance like "on pullbacks" without stating the actual price level.

Format your recommendation clearly with these components, and always conclude with 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your recommendation.

Do not forget to utilize lessons from past decisions to learn from your mistakes. Here is some reflections from similar situations you traded in and the lessons learned: {past_memory_str}""",
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")

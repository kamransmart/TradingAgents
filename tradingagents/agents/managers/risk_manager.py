import time
import json


def create_risk_manager(llm, memory):
    def risk_manager_node(state) -> dict:

        company_name = state["company_of_interest"]

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["news_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]
        shares_owned = state.get("shares_owned", 0)
        purchase_price = state.get("purchase_price", 0)

        # Get current price from state (set by market analyst)
        current_price = state.get("current_price")

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # Build portfolio position context with current price
        position_context = ""
        if shares_owned > 0:
            total_cost = shares_owned * purchase_price
            current_value = shares_owned * current_price if current_price else total_cost
            unrealized_pnl = current_value - total_cost if current_price else 0
            pnl_pct = (unrealized_pnl / total_cost * 100) if total_cost > 0 and current_price else 0

            position_context = f"""

**CURRENT MARKET PRICE: ${current_price:.2f}**

**CURRENT PORTFOLIO POSITION:**
- Company: {company_name}
- Shares Owned: {shares_owned}
- Purchase Price: ${purchase_price:.2f} per share
- Total Investment: ${total_cost:.2f}
""" if current_price else f"""

**CURRENT PORTFOLIO POSITION:**
- Company: {company_name}
- Shares Owned: {shares_owned}
- Purchase Price: ${purchase_price:.2f} per share
- Total Investment: ${total_cost:.2f}
"""

            if current_price:
                position_context += f"""- Current Market Price: ${current_price:.2f}
- Current Value: ${current_value:.2f}
- Unrealized P/L: ${unrealized_pnl:+.2f} ({pnl_pct:+.1f}%)

**CRITICAL**: The current market price is ${current_price:.2f}. All your price targets must be relative to THIS CURRENT PRICE (${current_price:.2f}), NOT the purchase price (${purchase_price:.2f}).
"""

            position_context += f"""
Your final recommendation MUST include:
1. **Specific PRICE TARGETS relative to current ${current_price if current_price else purchase_price:.2f} market price**:
   - If SELL: At what price to exit (e.g., "Sell at $X-Y" where X > current ${current_price if current_price else purchase_price:.2f})
   - If BUY: At what price to add (e.g., "Add more at $X-Y" relative to ${current_price if current_price else purchase_price:.2f})
   - If HOLD: Price levels that trigger action (e.g., "Hold unless drops below $X or exceeds $Y")
   - Stop-loss price level

2. **Position Sizing**: What percentage of the {shares_owned} shares to trade

3. **Timeframe**: When to execute (e.g., "within 1-2 weeks", "after earnings on Jan 7")
"""
        else:
            position_context = f"""

**CURRENT MARKET PRICE: ${current_price:.2f}**

**CURRENT PORTFOLIO POSITION:** No current position in {company_name}

**CRITICAL**: The current market price is ${current_price:.2f}. All your price targets must be relative to THIS CURRENT PRICE.

Your final recommendation MUST include:
1. **Specific PRICE TARGET relative to current ${current_price:.2f} market price**: At what price to enter (e.g., "Buy at $X-Y" relative to current ${current_price:.2f})

2. **Position Sizing**: What percentage of intended position to establish initially

3. **Timeframe**: When to execute or reassess
""" if current_price else f"""

**CURRENT PORTFOLIO POSITION:** No current position in {company_name}

Your final recommendation MUST include:
1. **Specific PRICE TARGET**: At what price to enter (e.g., "Buy at $X-Y")

2. **Position Sizing**: What percentage of intended position to establish initially

3. **Timeframe**: When to execute or reassess
"""

        prompt = f"""As the Risk Management Judge and Debate Facilitator, your goal is to evaluate the debate between three risk analysts—Risky, Neutral, and Safe/Conservative—and determine the best course of action for the trader. Your decision must result in a clear recommendation: Buy, Sell, or Hold. Choose Hold only if strongly justified by specific arguments, not as a fallback when all sides seem valid. Strive for clarity and decisiveness.

Guidelines for Decision-Making:
1. **Summarize Key Arguments**: Extract the strongest points from each analyst, focusing on relevance to the context.
2. **Provide Rationale**: Support your recommendation with direct quotes and counterarguments from the debate.
3. **Refine the Trader's Plan**: Start with the trader's original plan, **{trader_plan}**, and adjust it based on the analysts' insights.
4. **Learn from Past Mistakes**: Use lessons from **{past_memory_str}** to address prior misjudgments and improve the decision you are making now to make sure you don't make a wrong BUY/SELL/HOLD call that loses money.

{position_context}

Deliverables (ALL REQUIRED):
1. **Clear Action**: Buy, Sell, or Hold

2. **SPECIFIC PRICE TARGETS** (CRITICAL - Must include):
   - Entry price or price range for BUY recommendations (e.g., "Buy at $18-19")
   - Exit price or price range for SELL recommendations (e.g., "Sell at $25-26")
   - Trigger prices for HOLD recommendations (e.g., "Hold unless drops below $22")
   - Stop-loss price level in all cases
   - Use technical analysis, support/resistance levels, or recent price action to justify the specific prices

3. **Position Sizing**: Specific percentages for buying or selling (e.g., "Sell 25%", "Add 15% to position")

4. **Timeframe**: General timeframe for execution (e.g., "within 1-2 weeks", "after earnings call on Jan 7", "over the next month")

5. **Detailed Reasoning**: Explain WHY those specific price levels, anchored in debate and past reflections

**IMPORTANT**: Do NOT provide vague guidance like "on pullbacks" or "technical rebounds" without stating the EXACT PRICE LEVELS. The trader needs specific numbers to set limit orders and alerts.

---

**Analysts Debate History:**
{history}

---

Focus on actionable insights with SPECIFIC PRICE TARGETS. Build on past lessons, critically evaluate all perspectives, and ensure each decision advances better outcomes with precise execution guidance."""

        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node

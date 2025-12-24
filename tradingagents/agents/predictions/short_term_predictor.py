"""Short-term (14-day) price prediction agent."""


def create_short_term_predictor(llm, memory=None):
    """Create a short-term (14-day) price prediction agent.

    This agent analyzes all previous team outputs to predict stock prices
    over the next 14 days with bear/base/bull scenarios and probabilities.
    """

    def short_term_predictor_node(state) -> dict:
        prediction_debate_state = state.get("prediction_debate_state", {})
        history = prediction_debate_state.get("history", "")
        short_term_history = prediction_debate_state.get("short_term_history", "")

        current_medium_term_response = prediction_debate_state.get("current_medium_term_response", "")
        current_long_term_response = prediction_debate_state.get("current_long_term_response", "")

        # Get all previous analysis
        company = state["company_of_interest"]
        trade_date = state["trade_date"]
        current_price = state.get("current_price")
        market_report = state.get("market_report", "")
        sentiment_report = state.get("sentiment_report", "")
        news_report = state.get("news_report", "")
        fundamentals_report = state.get("fundamentals_report", "")

        investment_debate_state = state.get("investment_debate_state", {})
        bull_analysis = investment_debate_state.get("bull_history", "")
        bear_analysis = investment_debate_state.get("bear_history", "")
        research_decision = investment_debate_state.get("judge_decision", "")

        trader_plan = state.get("trader_investment_plan", "")

        risk_debate_state = state.get("risk_debate_state", {})
        final_decision = state.get("final_trade_decision", "")

        # Retrieve memory if available
        memory_context = ""
        if memory:
            try:
                past_experiences = memory.get_memories(
                    f"Short-term prediction for {company}", n_matches=3
                )
                if past_experiences:
                    memory_text = "\n".join([
                        f"- Previous: {exp['matched_situation']}\n  Outcome: {exp['recommendation']}"
                        for exp in past_experiences
                    ])
                    memory_context = f"\n\nPast Prediction Performance:\n{memory_text}\n"
            except Exception:
                memory_context = ""

        # Format current price for display
        price_context = f"\n**CURRENT MARKET PRICE: ${current_price:.2f}**\n" if current_price else ""

        prompt = f"""You are the Short-Term Price Predictor (14-day horizon). Your role is to analyze all available data and provide a detailed 14-day price forecast for {company} as of {trade_date}.
{price_context}
COMPREHENSIVE ANALYSIS AVAILABLE:

Market Analysis:
{market_report}

Sentiment Analysis:
{sentiment_report}

News Analysis:
{news_report}

Fundamentals:
{fundamentals_report}

Bull Case:
{bull_analysis}

Bear Case:
{bear_analysis}

Research Team Decision:
{research_decision}

Trader's Plan:
{trader_plan}

Risk Analysis & Final Decision:
{final_decision}
{memory_context}

OTHER PREDICTOR VIEWS:
Medium-Term (30-day) Predictor: {current_medium_term_response if current_medium_term_response else "Not yet available"}
Long-Term (90-day) Predictor: {current_long_term_response if current_long_term_response else "Not yet available"}

DEBATE HISTORY:
{history if history else "First round of predictions"}

YOUR TASK:
Provide a comprehensive SHORT-TERM (14-day) price prediction with the following structure:

1. **Current Price**: The current market price is ${current_price:.2f if current_price else 'XX.XX'} (from market data above).

2. **14-Day Price Predictions**: Provide three scenarios with EXACT dollar values and probabilities:
   - **Bear Case** (worst-case scenario): Price target and probability (%)
   - **Base Case** (most likely scenario): Price target and probability (%)
   - **Bull Case** (best-case scenario): Price target and probability (%)

   CRITICAL: Your probabilities MUST sum to exactly 100%

3. **Key Short-Term Catalysts**: List 3-5 specific factors that will drive price movement in the next 14 days (earnings, technical levels, news events, etc.)

4. **Technical Considerations**: Mention key support/resistance levels, momentum indicators, and short-term chart patterns relevant to 14 days.

5. **Confidence Level**: State your confidence (High/Medium/Low) and explain why.

6. **Response to Other Predictions**: If medium-term or long-term predictors have shared their views, comment on alignment or divergence and explain your reasoning.

OUTPUT FORMAT:
Start your response with "Short-Term Predictor (14-day):" and present your analysis in a conversational yet structured manner. Be specific with numbers and reasoning. Challenge other predictors' views if you disagree, using data to support your position.

Remember: Focus on SHORT-TERM catalysts and price movements that will materialize within 14 days. Be realistic about probability distributions."""

        response = llm.invoke(prompt)

        argument = f"Short-Term Predictor (14-day): {response.content}"

        new_prediction_debate_state = {
            "history": history + "\n\n" + argument,
            "short_term_history": short_term_history + "\n\n" + argument,
            "medium_term_history": prediction_debate_state.get("medium_term_history", ""),
            "long_term_history": prediction_debate_state.get("long_term_history", ""),
            "latest_speaker": "Short-Term",
            "current_short_term_response": argument,
            "current_medium_term_response": prediction_debate_state.get("current_medium_term_response", ""),
            "current_long_term_response": prediction_debate_state.get("current_long_term_response", ""),
            "final_predictions": prediction_debate_state.get("final_predictions", ""),
            "count": prediction_debate_state.get("count", 0) + 1,
        }

        return {"prediction_debate_state": new_prediction_debate_state}

    return short_term_predictor_node

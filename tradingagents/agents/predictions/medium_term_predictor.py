"""Medium-term (30-day) price prediction agent."""


def create_medium_term_predictor(llm, memory=None):
    """Create a medium-term (30-day) price prediction agent.

    This agent analyzes all previous team outputs to predict stock prices
    over the next 30 days with bear/base/bull scenarios and probabilities.
    """

    def medium_term_predictor_node(state) -> dict:
        prediction_debate_state = state.get("prediction_debate_state", {})
        history = prediction_debate_state.get("history", "")
        medium_term_history = prediction_debate_state.get("medium_term_history", "")

        current_short_term_response = prediction_debate_state.get("current_short_term_response", "")
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
                    f"Medium-term prediction for {company}", n_matches=3
                )
                if past_experiences:
                    memory_text = "\n".join([
                        f"- Previous: {exp['matched_situation']}\n  Outcome: {exp['recommendation']}"
                        for exp in past_experiences
                    ])
                    memory_context = f"\n\nPast Prediction Performance:\n{memory_text}\n"
            except Exception:
                memory_context = ""

        price_context = f"\n**CURRENT MARKET PRICE: ${current_price:.2f}**\n" if current_price else ""
        prompt = f"""You are the Medium-Term Price Predictor (30-day horizon). Your role is to analyze all available data and provide a detailed 30-day price forecast for {company} as of {trade_date}.
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
Short-Term (14-day) Predictor: {current_short_term_response if current_short_term_response else "Not yet available"}
Long-Term (90-day) Predictor: {current_long_term_response if current_long_term_response else "Not yet available"}

DEBATE HISTORY:
{history if history else "First round of predictions"}

YOUR TASK:
Provide a comprehensive MEDIUM-TERM (30-day) price prediction with the following structure:

1. **Current Price**: The current market price is ${current_price:.2f if current_price else 'XX.XX'} (from market data above).

2. **30-Day Price Predictions**: Provide three scenarios with EXACT dollar values and probabilities:
   - **Bear Case** (worst-case scenario): Price target and probability (%)
   - **Base Case** (most likely scenario): Price target and probability (%)
   - **Bull Case** (best-case scenario): Price target and probability (%)

   CRITICAL: Your probabilities MUST sum to exactly 100%

3. **Key Medium-Term Catalysts**: List 3-5 specific factors that will drive price movement over the next 30 days (upcoming earnings, product launches, macro trends, sector rotation, etc.)

4. **Trend Analysis**: Discuss prevailing trends (technical, fundamental, sentiment) that are likely to persist or reverse over the 30-day period.

5. **Confidence Level**: State your confidence (High/Medium/Low) and explain why.

6. **Response to Other Predictions**: If short-term or long-term predictors have shared their views, comment on the progression from 14-day to 30-day to 90-day forecasts. Explain any differences in trajectory.

OUTPUT FORMAT:
Start your response with "Medium-Term Predictor (30-day):" and present your analysis in a conversational yet structured manner. Be specific with numbers and reasoning. Challenge other predictors' views if you disagree, using data to support your position.

Remember: Focus on MEDIUM-TERM catalysts and trends that will materialize within 30 days. Balance short-term volatility with emerging medium-term trends."""

        response = llm.invoke(prompt)

        argument = f"Medium-Term Predictor (30-day): {response.content}"

        new_prediction_debate_state = {
            "history": history + "\n\n" + argument,
            "short_term_history": prediction_debate_state.get("short_term_history", ""),
            "medium_term_history": medium_term_history + "\n\n" + argument,
            "long_term_history": prediction_debate_state.get("long_term_history", ""),
            "latest_speaker": "Medium-Term",
            "current_short_term_response": prediction_debate_state.get("current_short_term_response", ""),
            "current_medium_term_response": argument,
            "current_long_term_response": prediction_debate_state.get("current_long_term_response", ""),
            "final_predictions": prediction_debate_state.get("final_predictions", ""),
            "count": prediction_debate_state.get("count", 0) + 1,
        }

        return {"prediction_debate_state": new_prediction_debate_state}

    return medium_term_predictor_node

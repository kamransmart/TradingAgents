"""Prediction Manager - consolidates all price predictions."""

import re


def create_prediction_manager(llm, memory=None):
    """Create a prediction manager that consolidates all timeframe predictions.

    This agent synthesizes short, medium, and long-term predictions into a
    final cohesive forecast with validation of probabilities.
    """

    def prediction_manager_node(state) -> dict:
        prediction_debate_state = state.get("prediction_debate_state", {})

        short_term_response = prediction_debate_state.get("current_short_term_response", "")
        medium_term_response = prediction_debate_state.get("current_medium_term_response", "")
        long_term_response = prediction_debate_state.get("current_long_term_response", "")

        company = state["company_of_interest"]
        trade_date = state["trade_date"]

        # Retrieve memory if available
        memory_context = ""
        if memory:
            try:
                past_experiences = memory.get_memories(
                    f"Prediction management for {company}", n_matches=3
                )
                if past_experiences:
                    memory_text = "\n".join([
                        f"- Previous: {exp['matched_situation']}\n  Outcome: {exp['recommendation']}"
                        for exp in past_experiences
                    ])
                    memory_context = f"\n\nPast Prediction Consolidation Performance:\n{memory_text}\n"
            except Exception:
                memory_context = ""

        prompt = f"""You are the Prediction Manager. Your role is to synthesize and consolidate the price predictions from all three timeframe predictors into a final, cohesive forecast for {company} as of {trade_date}.

SHORT-TERM (14-DAY) PREDICTION:
{short_term_response}

MEDIUM-TERM (30-DAY) PREDICTION:
{medium_term_response}

LONG-TERM (90-DAY) PREDICTION:
{long_term_response}
{memory_context}

YOUR TASK:
Create a consolidated prediction summary that:

1. **Extracts and Validates Predictions**: Parse out the specific price targets and probabilities from each predictor for each scenario (bear/base/bull).

2. **Validates Probability Distributions**: Ensure each predictor's probabilities sum to 100%. If not, flag the discrepancy and provide adjusted probabilities.

3. **Identifies Consensus and Divergence**: Highlight where predictors agree and where they diverge. Explain the reasoning behind any major differences.

4. **Creates Final Prediction Table**: Present a clean, formatted table with all predictions.

5. **Provides Strategic Recommendation**: Based on the collective predictions, provide a clear investment recommendation (Conservative Hold, Moderate Buy, Aggressive Buy, Reduce Position, etc.)

OUTPUT FORMAT:
Present your analysis in a structured format with the following sections:

**PREDICTION VALIDATION**
[Note any probability issues or concerns]

**CONSENSUS ANALYSIS**
[Discuss agreement/disagreement between predictors]

**FINAL PREDICTION SUMMARY TABLE**

```
===================================================================================
TIMEFRAME    | BEAR CASE      | BASE CASE      | BULL CASE      | CONFIDENCE
===================================================================================
14-Day       | $XX.XX (XX%)   | $XX.XX (XX%)   | $XX.XX (XX%)   | High/Med/Low
30-Day       | $XX.XX (XX%)   | $XX.XX (XX%)   | $XX.XX (XX%)   | High/Med/Low
90-Day       | $XX.XX (XX%)   | $XX.XX (XX%)   | $XX.XX (XX%)   | High/Med/Low
===================================================================================
Current Price: $XX.XX (from market data)
```

**STRATEGIC RECOMMENDATION**
[Clear recommendation with reasoning]

**KEY FACTORS TO MONITOR**
[3-5 critical factors investors should watch]

Be precise with numbers extracted from the predictor responses. If probabilities don't sum to 100%, normalize them and note the adjustment."""

        response = llm.invoke(prompt)

        final_predictions_content = response.content

        # Update state with final predictions
        new_prediction_debate_state = {
            "history": prediction_debate_state.get("history", ""),
            "short_term_history": prediction_debate_state.get("short_term_history", ""),
            "medium_term_history": prediction_debate_state.get("medium_term_history", ""),
            "long_term_history": prediction_debate_state.get("long_term_history", ""),
            "latest_speaker": "Prediction Manager",
            "current_short_term_response": short_term_response,
            "current_medium_term_response": medium_term_response,
            "current_long_term_response": long_term_response,
            "final_predictions": final_predictions_content,
            "count": prediction_debate_state.get("count", 0) + 1,
        }

        return {
            "prediction_debate_state": new_prediction_debate_state,
            "final_predictions": final_predictions_content,
        }

    return prediction_manager_node

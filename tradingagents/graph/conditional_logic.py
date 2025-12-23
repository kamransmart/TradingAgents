# TradingAgents/graph/conditional_logic.py

from tradingagents.agents.utils.agent_states import AgentState


class ConditionalLogic:
    """Handles conditional logic for determining graph flow."""

    def __init__(self, config=None):
        """Initialize with configuration parameters."""
        if config is None:
            config = {}
        self.max_debate_rounds = config.get("max_debate_rounds", 1)
        self.max_risk_discuss_rounds = config.get("max_risk_discuss_rounds", 1)
        self.max_prediction_rounds = config.get("max_prediction_rounds", 1)

    def should_continue_market(self, state: AgentState):
        """Determine if market analysis should continue."""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools_market"
        return "Msg Clear Market"

    def should_continue_social(self, state: AgentState):
        """Determine if social media analysis should continue."""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools_social"
        return "Msg Clear Social"

    def should_continue_news(self, state: AgentState):
        """Determine if news analysis should continue."""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools_news"
        return "Msg Clear News"

    def should_continue_fundamentals(self, state: AgentState):
        """Determine if fundamentals analysis should continue."""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools_fundamentals"
        return "Msg Clear Fundamentals"

    def should_continue_debate(self, state: AgentState) -> str:
        """Determine if debate should continue."""

        if (
            state["investment_debate_state"]["count"] >= 2 * self.max_debate_rounds
        ):  # 3 rounds of back-and-forth between 2 agents
            return "Research Manager"
        if state["investment_debate_state"]["current_response"].startswith("Bull"):
            return "Bear Researcher"
        return "Bull Researcher"

    def should_continue_risk_analysis(self, state: AgentState) -> str:
        """Determine if risk analysis should continue."""
        if (
            state["risk_debate_state"]["count"] >= 3 * self.max_risk_discuss_rounds
        ):  # 3 rounds of back-and-forth between 3 agents
            return "Risk Judge"
        if state["risk_debate_state"]["latest_speaker"].startswith("Risky"):
            return "Safe Analyst"
        if state["risk_debate_state"]["latest_speaker"].startswith("Safe"):
            return "Neutral Analyst"
        return "Risky Analyst"

    def should_continue_prediction(self, state: AgentState) -> str:
        """Determine if prediction debate should continue."""
        prediction_state = state.get("prediction_debate_state", {})
        count = prediction_state.get("count", 0)

        # After 3 * max_prediction_rounds, go to manager
        # (3 agents * rounds = total interactions)
        if count >= 3 * self.max_prediction_rounds:
            return "Prediction Manager"

        # Round-robin between predictors
        latest_speaker = prediction_state.get("latest_speaker", "")
        if latest_speaker == "Short-Term":
            return "Medium-Term Predictor"
        elif latest_speaker == "Medium-Term":
            return "Long-Term Predictor"
        else:  # Long-Term or initial state
            return "Short-Term Predictor" if count > 0 else "Medium-Term Predictor"

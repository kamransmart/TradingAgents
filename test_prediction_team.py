#!/usr/bin/env python3
"""
Test script for isolated Prediction Team testing.
This allows you to test the prediction agents without running the full analysis.
"""

import sys
from datetime import datetime
from tradingagents.graph.trading_graph import TradingAgentsGraph

def test_prediction_team(ticker="AAPL", date=None, enable_predictions=True):
    """
    Test the Prediction Team in isolation.

    Args:
        ticker: Stock ticker symbol
        date: Analysis date (YYYY-MM-DD format), defaults to today
        enable_predictions: Whether to enable the prediction team
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    print(f"\n{'='*80}")
    print(f"TESTING PREDICTION TEAM")
    print(f"{'='*80}")
    print(f"Ticker: {ticker}")
    print(f"Date: {date}")
    print(f"Prediction Team: {'Enabled' if enable_predictions else 'Disabled'}")
    print(f"{'='*80}\n")

    # Create config with prediction team setting
    config = {
        "enable_prediction_team": enable_predictions,
        "max_debate_rounds": 1,  # Keep debates short for testing
        "max_risk_discuss_rounds": 1,
        "max_prediction_rounds": 1,  # Single round of predictions
    }

    try:
        # Initialize the graph with only market analyst for faster testing
        print("Initializing TradingAgents graph...")
        graph = TradingAgentsGraph(
            selected_analysts=["market"],  # Only use market analyst for speed
            config=config,
            debug=True
        )

        print(f"Running analysis for {ticker} on {date}...\n")

        # Run the analysis
        final_state, decision = graph.propagate(ticker, date)

        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*80}\n")

        # Display results
        if enable_predictions and final_state.get("final_predictions"):
            print("PREDICTION TEAM OUTPUT:")
            print("-" * 80)
            print(final_state["final_predictions"])
            print("-" * 80)

            # Display prediction debate state for debugging
            pred_state = final_state.get("prediction_debate_state", {})
            print(f"\nPrediction rounds completed: {pred_state.get('count', 0)}")
            print(f"Latest speaker: {pred_state.get('latest_speaker', 'N/A')}")

            # Show each predictor's response
            if pred_state.get("current_short_term_response"):
                print("\n" + "="*80)
                print("SHORT-TERM PREDICTOR (14-day)")
                print("="*80)
                print(pred_state["current_short_term_response"][:500] + "...")

            if pred_state.get("current_medium_term_response"):
                print("\n" + "="*80)
                print("MEDIUM-TERM PREDICTOR (30-day)")
                print("="*80)
                print(pred_state["current_medium_term_response"][:500] + "...")

            if pred_state.get("current_long_term_response"):
                print("\n" + "="*80)
                print("LONG-TERM PREDICTOR (90-day)")
                print("="*80)
                print(pred_state["current_long_term_response"][:500] + "...")
        else:
            print("Prediction Team was disabled or did not generate output.")

        print(f"\n{'='*80}")
        print("FINAL TRADE DECISION:")
        print("-" * 80)
        print(final_state.get("final_trade_decision", "No decision available"))
        print(f"{'='*80}\n")

        return final_state, decision

    except Exception as e:
        print(f"\n{'='*80}")
        print(f"ERROR: {str(e)}")
        print(f"{'='*80}\n")
        import traceback
        traceback.print_exc()
        return None, None


def test_prediction_workflow():
    """Test the prediction workflow logic."""
    print("\n" + "="*80)
    print("TESTING PREDICTION WORKFLOW LOGIC")
    print("="*80 + "\n")

    from tradingagents.graph.conditional_logic import ConditionalLogic
    from tradingagents.agents.utils.agent_states import PredictionDebateState

    # Create mock state
    config = {"max_prediction_rounds": 1}
    logic = ConditionalLogic(config)

    # Test round-robin routing
    test_cases = [
        ({"count": 0, "latest_speaker": ""}, "Expected: Medium-Term Predictor"),
        ({"count": 1, "latest_speaker": "Short-Term"}, "Expected: Medium-Term Predictor"),
        ({"count": 2, "latest_speaker": "Medium-Term"}, "Expected: Long-Term Predictor"),
        ({"count": 3, "latest_speaker": "Long-Term"}, "Expected: Prediction Manager"),
    ]

    for state_data, expected in test_cases:
        mock_state = {"prediction_debate_state": state_data}
        result = logic.should_continue_prediction(mock_state)
        status = "✓" if result in expected else "✗"
        print(f"{status} Count={state_data['count']}, Speaker={state_data['latest_speaker']!r} → {result}")
        print(f"   {expected}")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Test the Prediction Team in isolation")
    parser.add_argument("--ticker", "-t", default="AAPL", help="Stock ticker symbol (default: AAPL)")
    parser.add_argument("--date", "-d", default=None, help="Analysis date YYYY-MM-DD (default: today)")
    parser.add_argument("--disable", action="store_true", help="Disable prediction team to test workflow without it")
    parser.add_argument("--test-logic", action="store_true", help="Test prediction workflow logic only")

    args = parser.parse_args()

    if args.test_logic:
        # Just test the logic
        test_prediction_workflow()
    else:
        # Run full test
        test_prediction_team(
            ticker=args.ticker,
            date=args.date,
            enable_predictions=not args.disable
        )

    print("\nTest complete!")

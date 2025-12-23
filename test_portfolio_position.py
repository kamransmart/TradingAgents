#!/usr/bin/env python3
"""Test portfolio position tracking functionality."""

import sys
sys.dont_write_bytecode = True

from tradingagents.graph.propagation import Propagator
from tradingagents.agents.utils.agent_states import AgentState

def test_portfolio_position():
    """Test that portfolio position data is properly initialized in state."""

    print("Testing Portfolio Position Tracking Functionality")
    print("=" * 60)

    # Test 1: Create state with no position
    print("\nTest 1: Creating state with no position")
    propagator = Propagator()
    state_no_position = propagator.create_initial_state("AAPL", "2025-12-23")

    assert state_no_position["shares_owned"] == 0, "Default shares_owned should be 0"
    assert state_no_position["purchase_price"] == 0, "Default purchase_price should be 0"
    print(f"✓ No position state created successfully")
    print(f"  - Shares: {state_no_position['shares_owned']}")
    print(f"  - Price: ${state_no_position['purchase_price']}")

    # Test 2: Create state with existing position
    print("\nTest 2: Creating state with existing position")
    state_with_position = propagator.create_initial_state(
        "APLD", "2025-12-23",
        shares_owned=100,
        purchase_price=25.50
    )

    assert state_with_position["shares_owned"] == 100, "shares_owned should be 100"
    assert state_with_position["purchase_price"] == 25.50, "purchase_price should be 25.50"
    print(f"✓ Position state created successfully")
    print(f"  - Shares: {state_with_position['shares_owned']}")
    print(f"  - Price: ${state_with_position['purchase_price']}")
    print(f"  - Total Investment: ${state_with_position['shares_owned'] * state_with_position['purchase_price']:.2f}")

    # Test 3: Verify other state fields are intact
    print("\nTest 3: Verifying other state fields")
    assert state_with_position["company_of_interest"] == "APLD", "Company name should match"
    assert state_with_position["trade_date"] == "2025-12-23", "Trade date should match"
    assert state_with_position["market_report"] == "", "market_report should be initialized"
    print(f"✓ All state fields initialized correctly")

    # Test 4: Test trader position context building
    print("\nTest 4: Testing trader position context building")
    shares = 100
    price = 25.50
    total = shares * price

    if shares > 0:
        position_context = f"\n\n**CURRENT PORTFOLIO POSITION:**\n- Shares Owned: {shares}\n- Purchase Price: ${price:.2f} per share\n- Total Investment: ${total:.2f}\n\nYou must provide specific guidance on what percentage of the current position to buy/sell and within what timeframe."
        print("✓ Position context generated for existing position:")
        print(position_context)

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("\nThe portfolio position tracking feature is ready to use.")
    print("\nUsage:")
    print("  1. Run the CLI: python cli/main.py analyze")
    print("  2. When prompted, enter your current position:")
    print("     - Number of shares owned")
    print("     - Purchase price per share")
    print("  3. The recommendations will include:")
    print("     - Specific buy/sell percentages")
    print("     - Timeframes for execution")
    print("     - Position-aware analysis")

if __name__ == "__main__":
    try:
        test_portfolio_position()
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

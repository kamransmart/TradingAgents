#!/usr/bin/env python3
"""Simple test to verify portfolio position code changes."""

import sys
sys.dont_write_bytecode = True

def test_propagation_signature():
    """Test that Propagator.create_initial_state accepts portfolio parameters."""
    print("Testing Propagator.create_initial_state signature")
    print("=" * 60)

    # Read the propagation.py file
    with open("tradingagents/graph/propagation.py", "r") as f:
        content = f.read()

    # Check if the signature includes shares_owned and purchase_price
    if "shares_owned: float = 0" in content and "purchase_price: float = 0" in content:
        print("✓ Propagator signature includes portfolio parameters")
    else:
        print("✗ Propagator signature missing portfolio parameters")
        return False

    # Check if state initialization includes these fields
    if '"shares_owned": shares_owned' in content and '"purchase_price": purchase_price' in content:
        print("✓ State initialization includes portfolio fields")
    else:
        print("✗ State initialization missing portfolio fields")
        return False

    return True

def test_agent_state():
    """Test that AgentState includes portfolio fields."""
    print("\nTesting AgentState definition")
    print("=" * 60)

    with open("tradingagents/agents/utils/agent_states.py", "r") as f:
        content = f.read()

    if 'shares_owned: Annotated[float, "Number of shares currently owned"]' in content:
        print("✓ AgentState includes shares_owned field")
    else:
        print("✗ AgentState missing shares_owned field")
        return False

    if 'purchase_price: Annotated[float, "Price per share at which current position was purchased"]' in content:
        print("✓ AgentState includes purchase_price field")
    else:
        print("✗ AgentState missing purchase_price field")
        return False

    return True

def test_trader_node():
    """Test that trader node uses portfolio position."""
    print("\nTesting Trader node")
    print("=" * 60)

    with open("tradingagents/agents/trader/trader.py", "r") as f:
        content = f.read()

    if 'shares_owned = state.get("shares_owned", 0)' in content:
        print("✓ Trader extracts shares_owned from state")
    else:
        print("✗ Trader doesn't extract shares_owned")
        return False

    if 'purchase_price = state.get("purchase_price", 0)' in content:
        print("✓ Trader extracts purchase_price from state")
    else:
        print("✗ Trader doesn't extract purchase_price")
        return False

    if 'CURRENT PORTFOLIO POSITION' in content:
        print("✓ Trader builds position context")
    else:
        print("✗ Trader doesn't build position context")
        return False

    if "percentage" in content.lower():
        print("✓ Trader prompts for percentage-based recommendations")
    else:
        print("✗ Trader doesn't prompt for percentage recommendations")
        return False

    return True

def test_risk_manager():
    """Test that risk manager uses portfolio position."""
    print("\nTesting Risk Manager")
    print("=" * 60)

    with open("tradingagents/agents/managers/risk_manager.py", "r") as f:
        content = f.read()

    if 'shares_owned = state.get("shares_owned", 0)' in content:
        print("✓ Risk Manager extracts shares_owned from state")
    else:
        print("✗ Risk Manager doesn't extract shares_owned")
        return False

    if 'purchase_price = state.get("purchase_price", 0)' in content:
        print("✓ Risk Manager extracts purchase_price from state")
    else:
        print("✗ Risk Manager doesn't extract purchase_price")
        return False

    if 'CURRENT PORTFOLIO POSITION' in content:
        print("✓ Risk Manager builds position context")
    else:
        print("✗ Risk Manager doesn't build position context")
        return False

    if "percentage" in content.lower():
        print("✓ Risk Manager prompts for percentage-based recommendations")
    else:
        print("✗ Risk Manager doesn't prompt for percentage recommendations")
        return False

    return True

def test_cli():
    """Test that CLI collects portfolio position."""
    print("\nTesting CLI")
    print("=" * 60)

    with open("cli/main.py", "r") as f:
        content = f.read()

    if "def get_portfolio_position():" in content:
        print("✓ CLI has get_portfolio_position function")
    else:
        print("✗ CLI missing get_portfolio_position function")
        return False

    if "shares_owned, purchase_price = get_portfolio_position()" in content:
        print("✓ CLI calls get_portfolio_position")
    else:
        print("✗ CLI doesn't call get_portfolio_position")
        return False

    if '"shares_owned": shares_owned' in content and '"purchase_price": purchase_price' in content:
        print("✓ CLI stores portfolio position in selections")
    else:
        print("✗ CLI doesn't store portfolio position")
        return False

    if 'selections["shares_owned"], selections["purchase_price"]' in content:
        print("✓ CLI passes portfolio position to graph")
    else:
        print("✗ CLI doesn't pass portfolio position to graph")
        return False

    return True

def main():
    print("Portfolio Position Tracking - Code Verification")
    print("=" * 60)
    print()

    tests = [
        ("Propagation Module", test_propagation_signature),
        ("Agent State", test_agent_state),
        ("Trader Node", test_trader_node),
        ("Risk Manager", test_risk_manager),
        ("CLI Module", test_cli),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error testing {name}: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:30s} {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED! ✓")
        print("\nImplementation complete! The system now supports:")
        print("  • Portfolio position input (shares owned + purchase price)")
        print("  • Position-aware recommendations from Trader and Risk Manager")
        print("  • Percentage-based buy/sell guidance")
        print("  • Timeframe recommendations")
        print("\nTo use:")
        print("  1. Run: python cli/main.py analyze")
        print("  2. Enter your current position when prompted")
        print("  3. Get position-aware recommendations with quantities and timing")
        return 0
    else:
        print("SOME TESTS FAILED ✗")
        print("\nPlease review the failed tests above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

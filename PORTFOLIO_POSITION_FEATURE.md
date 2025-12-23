# Portfolio Position Tracking Feature

## Overview
This enhancement extends the TradingAgents system to accept current portfolio position information (shares owned and purchase price) and provide position-aware recommendations with specific buy/sell quantities and timeframes.

## What's New

### 1. Portfolio Position Input
The CLI now prompts users to input their current position:
- **Number of shares owned**: How many shares you currently hold
- **Purchase price per share**: The average price at which you bought them

This information is optional - if you don't own any shares, just enter 0 or leave blank.

### 2. Position-Aware Recommendations
Both the Trader and Portfolio Manager (Risk Manager) agents now:
- Consider your current position when making recommendations
- Calculate your total investment and potential gains/losses
- Provide context-specific advice based on whether you already own shares

### 3. Quantity Guidance
Recommendations now include specific percentages:
- **For SELL**: "Sell 25% of your position" or "Sell 50% of your 100 shares"
- **For BUY**: "Buy to increase position by 30%" or "Establish a 20% initial position"
- **For HOLD**: "Maintain current position" with conditions to reassess

### 4. Timeframe Recommendations
Each recommendation includes general timeframes for execution:
- "within 1-2 weeks" - for urgent actions
- "over the next month" - for moderate timing
- "wait 3-6 months" - for longer-term holds
- Event-driven: "after next earnings report" or "if price drops below $25"

## Files Modified

### Core State Management
1. **[tradingagents/agents/utils/agent_states.py](tradingagents/agents/utils/agent_states.py:79-80)**
   - Added `shares_owned` and `purchase_price` fields to `AgentState`

2. **[tradingagents/graph/propagation.py](tradingagents/graph/propagation.py:19-27)**
   - Updated `create_initial_state()` to accept portfolio position parameters
   - Initialize state with position data

### Agent Logic
3. **[tradingagents/agents/trader/trader.py](tradingagents/agents/trader/trader.py:14-33)**
   - Extract portfolio position from state
   - Build position-aware context for recommendations
   - Updated system prompt to require percentage and timeframe guidance

4. **[tradingagents/agents/managers/risk_manager.py](tradingagents/agents/managers/risk_manager.py:17-78)**
   - Extract portfolio position from state
   - Build detailed position context with investment totals
   - Updated prompt to require specific execution guidance

### User Interface
5. **[cli/main.py](cli/main.py)**
   - Added `get_portfolio_position()` function (lines 562-589)
   - Added Step 5 for portfolio position input (lines 481-493)
   - Updated selections dictionary to include position data (lines 528-529)
   - Pass position data to graph initialization (lines 1048-1051)

## Usage Example

### Starting the Analysis
```bash
python cli/main.py analyze
```

### Input Flow
```
Step 1: Ticker Symbol
> APLD

Step 2: Analysis Date
> 2025-12-23

Step 3: Analysts Team
[Select your analysts...]

Step 4: Research Depth
> 1

Step 5: Portfolio Position (Optional)
Enter your current position in this stock
Leave blank if you don't currently own this stock

Number of shares owned: 100
Purchase price per share: 25.50

Current Position: 100 shares @ $25.50

[Continue with remaining steps...]
```

### Sample Output

#### Without Current Position
```
FINAL TRANSACTION PROPOSAL: **BUY**

Recommendation: Establish an initial 20% position within the next 2-3 weeks.

Reasoning: Strong AI infrastructure demand and recent $100M funding provide
solid growth potential. Start with a small position to manage risk given
the company's negative cash flow.

Timeframe: Within 2-3 weeks, or after monitoring post-earnings volatility
```

#### With Current Position (100 shares @ $25.50)
```
FINAL TRANSACTION PROPOSAL: **HOLD**

Current Position: 100 shares @ $25.50 ($2,550 total investment)

Recommendation: Hold current position. Consider selling 25% (25 shares) if
price rises above $30 within the next month.

Reasoning: Current price of $26.43 shows modest gains. The upcoming earnings
call on January 7 could be a catalyst. Hold through earnings, but take
partial profits if significant upside materializes.

Timeframe:
- Hold for next 3-4 weeks until earnings
- Reassess after January 7 earnings call
- Consider partial exit if price exceeds $30

Stop Loss: Set at 15% below current price (~$22.50)
```

## Technical Details

### State Schema
```python
{
    "company_of_interest": str,     # Ticker symbol
    "trade_date": str,              # Analysis date
    "shares_owned": float,          # Number of shares (default: 0)
    "purchase_price": float,        # Purchase price per share (default: 0)
    # ... other fields
}
```

### Position Context Generation
The agents calculate:
- Total investment: `shares_owned * purchase_price`
- Current value: `shares_owned * current_price` (from market data)
- Unrealized gain/loss: `current_value - total_investment`
- Position percentage changes for recommendations

### Validation
- Shares cannot be negative (validated in CLI)
- Price cannot be negative (validated in CLI)
- Default values (0) allow system to work without position data
- Backward compatible - existing workflows continue to work

## Testing

Run the verification test:
```bash
python3 test_portfolio_simple.py
```

This validates:
- ✓ State includes portfolio fields
- ✓ Propagator accepts position parameters
- ✓ CLI collects and passes position data
- ✓ Trader uses position in recommendations
- ✓ Risk Manager uses position in recommendations
- ✓ Recommendations include percentages and timeframes

## Benefits

1. **Personalized Recommendations**: Advice tailored to your specific position
2. **Risk Management**: Better understand position sizing relative to your holdings
3. **Actionable Guidance**: Clear quantities and timeframes remove ambiguity
4. **Profit/Loss Awareness**: Agents consider your cost basis in their analysis
5. **Flexible Input**: Works both with and without existing positions

## Future Enhancements

Potential additions:
- Multiple positions across different purchases (cost basis tracking)
- Portfolio-level analysis across multiple stocks
- Tax implications for selling decisions
- Position sizing based on total portfolio value
- Risk/reward ratios based on current position

## Compatibility

- **Backward Compatible**: Works with existing configurations
- **Optional Feature**: Can skip position input by entering 0
- **No Breaking Changes**: All existing functionality preserved
- **Python 3.8+**: Compatible with existing requirements

## Support

For issues or questions:
1. Check that shares_owned and purchase_price are properly passed to the graph
2. Verify the CLI prompts are appearing in Step 5
3. Review agent outputs to ensure position context is included
4. Run `python3 test_portfolio_simple.py` to verify installation

---

**Implementation Date**: December 23, 2025
**Version**: 1.0
**Status**: ✓ Complete and Tested

# Quick Start Guide - Enhanced TradingAgents

## TL;DR
The system now requires:
1. **Your current position** (shares owned + purchase price)
2. **Specific price targets** in all recommendations (entry, exit, stop-loss)

You get actionable trades with exact prices, quantities, and timeframes.

---

## Run Analysis in 5 Steps

### 1. Start the CLI
```bash
cd /Users/akamran/Development/TradingAgents
python cli/main.py analyze
```

### 2. Enter Stock Details
```
Ticker: APLD
Analysis Date: 2025-12-23
```

### 3. Select Analysts
```
✓ Market Analyst
✓ Social Analyst
✓ News Analyst
✓ Fundamentals Analyst
```

### 4. **NEW: Enter Your Position**
```
Number of shares owned: 100
Purchase price per share: 25.50
```
*Leave blank or enter 0 if you don't own any*

### 5. Complete Setup
- Research Depth: 1 (or 2-3 for deeper analysis)
- Enable Prediction Team: Yes
- Select LLM provider
- Select thinking models

---

## What You'll Get

### Old Output (Generic)
```
Hold APLD. Monitor reports closely and consider adding on pullbacks.
```

### New Output (Actionable)
```
HOLD with Position Management

Current Position:
- 100 shares @ $25.50
- Current: $26.43
- Gain: +$93 (+3.6%)

Price Targets:
✓ Sell 40% at $29.50-$30.50 (40 shares)
✓ Stop-loss at $24.50 on remaining 60 shares
✓ Target $32-$33 for rest

Execute:
1. Set limit sell: 40 shares @ $29.75
2. Set stop: 60 shares @ $24.50
3. Set alert: Price hits $32

Timeframe: Next 2-4 weeks
```

---

## Example Scenarios

### Scenario A: You Own Stock at a Loss

**Input:**
- Stock: INTC
- Position: 100 shares @ $38
- Current Price: $20.50

**Output:**
```
BUY to Average Down

Loss: -$1,750 (-46%)

Price Targets:
- Add at $18.50-$19.50 (10-15 shares)
- Stop all shares at $16.50
- Target $24-$28 for exits

New average: $38 → $33
Risk: Additional $350 to stop
Reward: $500-$1,200 to targets
```

### Scenario B: You Own Stock at Profit

**Input:**
- Stock: APLD
- Position: 100 shares @ $25.50
- Current Price: $30

**Output:**
```
SELL Partial Position

Gain: +$450 (+17.6%)

Price Targets:
- Sell 40 shares now at $29.50-$30.50
- Sell 30 shares at $32-$33
- Trail stop 30 shares at $27

Locks in: ~$180-$400 profit
Keeps upside: 30 shares to run
Protects gains: Stop at $27
```

### Scenario C: No Position Yet

**Input:**
- Stock: TSLA
- Position: 0 shares
- Current Price: $245

**Output:**
```
BUY New Position on Pullback

Don't chase at $245

Price Targets:
- Wait for $225-$230 (buy 10 shares)
- Or $210-$215 (buy 10 more)
- Stop at $195
- Targets: $275, $300, $350

Strategy: Scale in at better prices
Timeframe: 3-4 weeks
```

---

## How to Execute Recommendations

### Step 1: Open Your Brokerage
- Login to your trading platform
- Navigate to stock ticker

### Step 2: Set Limit Orders
Based on recommendation:
```
"Sell 40 shares at $29.50-$30.50"
```

Enter order:
- Action: SELL
- Quantity: 40
- Order Type: LIMIT
- Limit Price: $29.75 (midpoint)
- Time in Force: GTC (Good Till Canceled)

### Step 3: Set Stop-Loss
Based on recommendation:
```
"Stop-loss at $24.50 on remaining 60 shares"
```

Enter order:
- Action: SELL
- Quantity: 60
- Order Type: STOP
- Stop Price: $24.50
- Time in Force: GTC

### Step 4: Set Price Alerts
- Alert when price hits $32
- Alert when price drops to $25
- Get notified, then reassess

---

## Reading the Output

### Position Summary
```
Current Position: 100 shares @ $25.50
Current Price: $26.43
Unrealized Gain: +$93 (+3.6%)
```
→ Shows YOUR specific position and P&L

### Price Targets Section
```
1. Entry: $18.50-$19.50
2. Exit: $29.50-$30.50
3. Stop-Loss: $24.50
4. Target: $32-$33
```
→ Exact prices for orders

### Position Sizing
```
Sell 40% (40 shares)
```
→ How much to trade

### Timeframe
```
Within 1-2 weeks
After earnings on Jan 7
```
→ When to act

### Reasoning
```
$29.50-$30.50 is resistance from December highs.
Volume declining suggests exhaustion.
```
→ Why those prices

---

## Tips for Best Results

### 1. Be Honest About Your Position
- Enter exact shares you own
- Use actual average purchase price
- Don't round or estimate

### 2. Use Limit Orders
- Don't use market orders
- Set limits at recommended prices
- Be patient for fills

### 3. Set Stop-Losses
- Always protect downside
- Use recommended stop prices
- Don't move stops lower

### 4. Scale In/Out
- Don't buy/sell all at once
- Follow percentage guidance
- Average better prices

### 5. Monitor Catalysts
- Watch for earnings dates
- Track news mentioned in reasoning
- Reassess when events occur

---

## Common Questions

**Q: What if I don't own the stock?**
A: Enter 0 shares. You'll get recommendations for new position entry with specific prices.

**Q: What if I own multiple lots at different prices?**
A: Use your average purchase price across all lots.

**Q: Should I follow recommendations exactly?**
A: Use them as guidance. Adjust based on your risk tolerance and situation.

**Q: What if price never reaches the target?**
A: Set GTC limit orders and be patient. Reassess after timeframe expires.

**Q: Can I change quantities?**
A: Yes, scale up/down based on your portfolio size and risk tolerance.

**Q: What if recommendation conflicts with my view?**
A: System provides data-driven analysis. You make final decision.

---

## Files to Reference

- **Full Feature Docs**: [PORTFOLIO_POSITION_FEATURE.md](PORTFOLIO_POSITION_FEATURE.md)
- **Price Targets**: [PRICE_TARGETS_ENHANCEMENT.md](PRICE_TARGETS_ENHANCEMENT.md)
- **Examples**: [RECOMMENDATION_COMPARISON.md](RECOMMENDATION_COMPARISON.md)
- **Complete Summary**: [ENHANCEMENT_SUMMARY.md](ENHANCEMENT_SUMMARY.md)

---

## Test Your Setup

Run verification:
```bash
python3 test_portfolio_simple.py
```

Should see:
```
✓ All tests passed!
✓ Implementation complete!
```

---

## Example Full Session

```bash
$ python cli/main.py analyze

Step 1: Ticker
> INTC

Step 2: Date
> 2025-12-23

Step 3: Analysts
[Select all 4]

Step 4: Research Depth
> 1

Step 5: Portfolio Position
Shares owned: 100
Purchase price: 38

✓ Position: 100 shares @ $38.00

[Continue through setup...]

[Wait for analysis... ~2-5 minutes]

Final Output:

════════════════════════════════════════
PORTFOLIO MANAGEMENT DECISION
════════════════════════════════════════

Current Position: 100 shares @ $38.00
Current Price: $20.50
Loss: -$1,750 (-46%)

RECOMMENDATION: BUY (Add to Position)

Price Targets:
• Primary Entry: $18.50-$19.50
  - 20-day MA support
  - Previous resistance

• Secondary Entry: $17-$17.50
  - 52-week lows
  - Deeper value

• Stop-Loss: $16.50
  - Below October lows
  - Limits downside

• Exit Targets:
  - $24-$25: Sell 25%
  - $28-$30: Sell 25%
  - $35+: Trail remainder

Position Sizing:
• Add 10-15 shares at $18.50-$19.50
• New average: $38 → $32-$33
• Total position: 110-115 shares

Timeframe:
• Next 2-4 weeks
• Before Q1 earnings
• Set limit orders now

Action Items:
1. Set limit buy: 8 shares @ $19.50
2. Set limit buy: 7 shares @ $18.50
3. Set stop: All shares @ $16.50
4. Monitor for fills

════════════════════════════════════════

✓ Report saved to: results/INTC/2025-12-23/
```

---

**Ready to Trade with Confidence** 📈

Now you have:
- ✅ Specific prices to act on
- ✅ Exact quantities to trade
- ✅ Clear timeframes
- ✅ Risk management built-in
- ✅ Position-aware strategy

**Start your analysis now!**

```bash
python cli/main.py analyze
```

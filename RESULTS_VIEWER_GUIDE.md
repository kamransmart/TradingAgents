# Results Viewer Guide

## Overview

The Results Viewer is a new feature integrated into the TradingAgents web interface that allows you to browse, search, and view previously generated trading analysis results. This eliminates the need to manually navigate the file system to find past analyses.

## Features

### 1. **Browse All Results**
- View a comprehensive list of all historical analyses
- See analysis metadata including date, ticker, report count
- Quick identification of completed analyses with status indicators

### 2. **Filter and Search**
- **By Ticker**: View all analyses for a specific stock symbol
- **By Date**: Show recent analyses (customizable count)
- **Quick Stats**: See summary statistics across all analyses

### 3. **Detailed Report Viewing**
- View complete analysis reports directly in the chat interface
- Download reports as markdown files
- Navigate between multiple reports for the same analysis

### 4. **Interactive Commands**
- Simple, intuitive command-based interface
- Context-aware help system
- Seamless switching between analysis and browsing modes

## Getting Started

### Running the Enhanced App

To use the Results Viewer, run the enhanced Chainlit app:

```bash
chainlit run chainlit_app_with_viewer.py
```

### Main Menu

When you first open the app, you'll see the main menu with two options:

1. **Run New Analysis** - Start a fresh stock analysis
2. **Browse Previous Results** - View historical analyses

## Commands Reference

### Main Commands

| Command | Description |
|---------|-------------|
| `results`, `browse`, `history` | Enter results viewer mode |
| `analyze`, `new`, `start` | Start a new analysis |
| `help` | Show help information |
| `menu`, `home`, `back` | Return to main menu |

### Results Viewer Commands

Once in results viewer mode, use these commands:

| Command | Description | Example |
|---------|-------------|---------|
| `list` | Show all available results | `list` |
| `recent [N]` | Show N most recent results (default: 10) | `recent 5` |
| `ticker SYMBOL` | Filter results by ticker symbol | `ticker AAPL` |
| `view N` | View detailed reports for result number N | `view 1` |
| `report N [name]` | View specific report from result N | `report 1 final_trade_decision.md` |
| `stats` | Show summary statistics | `stats` |

## Usage Examples

### Example 1: Browse Recent Analyses

```
User: results
Bot: [Shows summary statistics and 10 most recent analyses]

User: recent 20
Bot: [Shows last 20 analyses with details]
```

### Example 2: View Ticker-Specific Results

```
User: results
Bot: [Shows main results browser]

User: ticker TSLA
Bot: [Shows all TSLA analyses]
     1. TSLA (2025-12-23) - 7 reports ✅
     2. TSLA (2025-12-20) - 7 reports ✅
     3. TSLA (2025-12-15) - 6 reports ✅

User: view 1
Bot: [Shows all reports for TSLA analysis from 2025-12-23]
```

### Example 3: Check Statistics

```
User: results
Bot: [Shows main results browser]

User: stats
Bot:
# Detailed Statistics

**Total Analyses**: 47
**Unique Tickers**: 12
**Date Range**: 2025-11-15 to 2025-12-23

## Analysis Count by Ticker
- AAPL: 8 analyses
- TSLA: 7 analyses
- MSFT: 6 analyses
...
```

### Example 4: View Specific Report

```
User: ticker AAPL
Bot: [Shows AAPL results]

User: view 1
Bot: [Shows all reports for first AAPL result]

User: report 1 market_report.md
Bot: [Shows only the market analysis report]
```

## Understanding Result Indicators

When viewing results lists, you'll see indicators:

- ✅ **Green Check** - Analysis has final trading decision
- ⚠️ **Warning** - Analysis incomplete or missing final decision

## Results Structure

Each analysis result contains:

- **Ticker Symbol** - Stock that was analyzed
- **Analysis Date** - Date the analysis was performed
- **Creation Time** - When the analysis was run
- **Report Count** - Number of generated reports
- **Available Reports** - List of report files

### Common Report Types

1. **final_trade_decision.md** - Final trading recommendation
2. **trader_investment_plan.md** - Detailed investment strategy
3. **market_report.md** - Technical analysis
4. **fundamentals_report.md** - Fundamental analysis
5. **news_report.md** - News and events analysis
6. **sentiment_report.md** - Social sentiment analysis

## File Storage

Results are stored in the following structure:

```
results/
├── AAPL/
│   ├── 2025-12-23/
│   │   └── reports/
│   │       ├── final_trade_decision.md
│   │       ├── market_report.md
│   │       └── ...
│   └── 2025-12-22/
│       └── reports/
├── TSLA/
│   └── 2025-12-23/
│       └── reports/
└── ...
```

## Tips and Best Practices

1. **Start with `stats`** - Get an overview of your available data
2. **Use `recent`** - Quickly access your latest analyses
3. **Filter by ticker** - Focus on specific stocks you're tracking
4. **Download reports** - Click on attached files to download for offline viewing
5. **Use `menu`** - Easily switch between analysis and browsing modes

## Integration with Analysis Mode

The Results Viewer seamlessly integrates with the analysis workflow:

1. Run a new analysis using `analyze`
2. After completion, view results immediately or later
3. Use `results` command anytime to browse historical data
4. Compare multiple analyses for the same ticker over time

## Troubleshooting

### No Results Showing

- Ensure you've run at least one analysis
- Check that the `results/` directory exists
- Verify analyses completed successfully

### Reports Not Loading

- Confirm the report files exist in `results/TICKER/DATE/reports/`
- Check file permissions

### Commands Not Working

- Type `help` to see available commands
- Ensure you're in the correct mode (results viewer vs analysis)
- Check for typos in command syntax

## API Reference (For Developers)

### ResultsManager Class

The `ResultsManager` class provides programmatic access to results:

```python
from results_viewer import ResultsManager

# Initialize
manager = ResultsManager(results_base_dir="./results")

# Get all results
all_results = manager.get_all_results()

# Get results for specific ticker
aapl_results = manager.get_results_by_ticker("AAPL")

# Get recent results
recent = manager.get_recent_results(limit=10)

# Read specific report
report = manager.read_report("AAPL", "2025-12-23", "final_trade_decision.md")

# Get statistics
stats = manager.get_summary_stats()
```

### Key Methods

- `get_all_results()` - Returns all analyses with metadata
- `get_results_by_ticker(ticker)` - Filter by ticker symbol
- `get_results_by_date_range(start, end)` - Filter by date range
- `get_recent_results(limit)` - Get N most recent analyses
- `read_report(ticker, date, report_name)` - Read specific report file
- `get_all_reports_for_analysis(ticker, date)` - Get all reports for an analysis
- `get_available_tickers()` - List all analyzed tickers
- `get_summary_stats()` - Get aggregate statistics

## Future Enhancements

Potential improvements for future versions:

- Search by keywords within reports
- Date range filtering
- Export results to CSV/JSON
- Comparison view for multiple analyses
- Performance charts and visualizations
- Tagging and categorization
- Notes and annotations

## Support

For issues or questions:
- Check the main README
- Review the help command: `help`
- Open an issue on GitHub

---

**Version**: 1.0
**Last Updated**: 2025-12-23

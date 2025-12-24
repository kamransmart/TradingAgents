"""
Test script for Results Viewer functionality

This script tests the ResultsManager class to ensure it correctly
reads and processes analysis results from the results directory.
"""

from results_viewer import ResultsManager, format_results_list
from pathlib import Path


def test_results_manager():
    """Test the ResultsManager functionality."""

    print("=" * 80)
    print("Testing Results Viewer")
    print("=" * 80)

    # Initialize manager
    manager = ResultsManager(results_base_dir="./results")

    # Test 1: Get all results
    print("\n1. Testing get_all_results()...")
    all_results = manager.get_all_results()
    print(f"   Found {len(all_results)} total analyses")

    if all_results:
        print(f"   Sample result: {all_results[0]['ticker']} ({all_results[0]['date']})")
    else:
        print("   No results found. Run some analyses first!")

    # Test 2: Get available tickers
    print("\n2. Testing get_available_tickers()...")
    tickers = manager.get_available_tickers()
    print(f"   Available tickers: {', '.join(tickers) if tickers else 'None'}")

    # Test 3: Get summary stats
    print("\n3. Testing get_summary_stats()...")
    stats = manager.get_summary_stats()
    print(f"   Total analyses: {stats['total_analyses']}")
    print(f"   Unique tickers: {stats['unique_tickers']}")
    print(f"   Date range: {stats['date_range']}")
    print(f"   Most analyzed: {stats['most_analyzed_ticker']}")

    # Test 4: Get recent results
    print("\n4. Testing get_recent_results()...")
    recent = manager.get_recent_results(limit=5)
    print(f"   Recent results (last 5):")
    for i, result in enumerate(recent, 1):
        print(f"     {i}. {result['ticker']} ({result['date']}) - {result['report_count']} reports")

    # Test 5: Get results by ticker
    if tickers:
        test_ticker = tickers[0]
        print(f"\n5. Testing get_results_by_ticker('{test_ticker}')...")
        ticker_results = manager.get_results_by_ticker(test_ticker)
        print(f"   Found {len(ticker_results)} analyses for {test_ticker}")

        # Test 6: Read a report
        if ticker_results:
            print(f"\n6. Testing read_report()...")
            result = ticker_results[0]
            ticker = result['ticker']
            date = result['date']

            # Try to read final trade decision
            report_content = manager.read_report(ticker, date, "final_trade_decision.md")

            if report_content:
                print(f"   Successfully read final_trade_decision.md for {ticker} ({date})")
                print(f"   Content length: {len(report_content)} characters")
                print(f"   Preview: {report_content[:200]}...")
            else:
                print(f"   Report not found or error reading")

            # Test 7: Get all reports for analysis
            print(f"\n7. Testing get_all_reports_for_analysis()...")
            all_reports = manager.get_all_reports_for_analysis(ticker, date)
            print(f"   Found {len(all_reports)} reports:")
            for report_name in all_reports.keys():
                print(f"     - {report_name}")

    # Test 8: Format results list
    print("\n8. Testing format_results_list()...")
    if all_results:
        formatted = format_results_list(all_results[:3], show_details=True)
        print("   Formatted output:")
        print(formatted)

    print("\n" + "=" * 80)
    print("Testing Complete!")
    print("=" * 80)


if __name__ == "__main__":
    test_results_manager()

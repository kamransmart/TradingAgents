"""
Results Viewer Module for TradingAgents

This module provides functionality to browse, filter, and view previously generated
trading analysis results from the results directory.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json


class ResultsManager:
    """Manages access to stored trading analysis results."""

    def __init__(self, results_base_dir: str = "./results"):
        self.results_base_dir = Path(results_base_dir)

    def get_all_results(self) -> List[Dict[str, any]]:
        """
        Scan the results directory and return a list of all available analyses.

        Returns:
            List of dictionaries containing metadata for each analysis:
            - ticker: Stock ticker symbol
            - date: Analysis date
            - path: Full path to results directory
            - report_count: Number of report files
            - has_final_decision: Whether final decision exists
            - created_time: Directory creation timestamp
        """
        results = []

        if not self.results_base_dir.exists():
            return results

        # Iterate through ticker directories
        for ticker_dir in self.results_base_dir.iterdir():
            if not ticker_dir.is_dir():
                continue

            ticker = ticker_dir.name

            # Iterate through date directories
            for date_dir in ticker_dir.iterdir():
                if not date_dir.is_dir():
                    continue

                date = date_dir.name
                reports_dir = date_dir / "reports"

                if not reports_dir.exists():
                    continue

                # Count reports
                report_files = list(reports_dir.glob("*.md"))
                report_count = len(report_files)

                # Check for final decision
                has_final_decision = (reports_dir / "final_trade_decision.md").exists()

                # Get creation time
                try:
                    created_time = datetime.fromtimestamp(date_dir.stat().st_ctime)
                except:
                    created_time = None

                results.append({
                    "ticker": ticker,
                    "date": date,
                    "path": str(date_dir),
                    "reports_path": str(reports_dir),
                    "report_count": report_count,
                    "has_final_decision": has_final_decision,
                    "created_time": created_time,
                    "report_files": [f.name for f in report_files]
                })

        # Sort by creation time (newest first)
        results.sort(key=lambda x: x["created_time"] if x["created_time"] else datetime.min, reverse=True)

        return results

    def get_results_by_ticker(self, ticker: str) -> List[Dict[str, any]]:
        """Get all results for a specific ticker."""
        all_results = self.get_all_results()
        return [r for r in all_results if r["ticker"].upper() == ticker.upper()]

    def get_results_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, any]]:
        """Get results within a date range (YYYY-MM-DD format)."""
        all_results = self.get_all_results()
        return [
            r for r in all_results
            if start_date <= r["date"] <= end_date
        ]

    def get_recent_results(self, limit: int = 10) -> List[Dict[str, any]]:
        """Get the most recent N results."""
        all_results = self.get_all_results()
        return all_results[:limit]

    def read_report(self, ticker: str, date: str, report_name: str) -> Optional[str]:
        """
        Read a specific report file.

        Args:
            ticker: Stock ticker symbol
            date: Analysis date (YYYY-MM-DD)
            report_name: Name of the report file (e.g., 'final_trade_decision.md')

        Returns:
            Report content as string, or None if not found
        """
        report_path = self.results_base_dir / ticker / date / "reports" / report_name

        if not report_path.exists():
            return None

        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading report: {str(e)}"

    def get_all_reports_for_analysis(self, ticker: str, date: str) -> Dict[str, str]:
        """
        Get all reports for a specific analysis.

        Returns:
            Dictionary mapping report names to their content
        """
        reports_dir = self.results_base_dir / ticker / date / "reports"

        if not reports_dir.exists():
            return {}

        reports = {}
        for report_file in reports_dir.glob("*.md"):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    reports[report_file.name] = f.read()
            except Exception as e:
                reports[report_file.name] = f"Error reading report: {str(e)}"

        return reports

    def get_available_tickers(self) -> List[str]:
        """Get list of all tickers with analysis results."""
        if not self.results_base_dir.exists():
            return []

        tickers = []
        for ticker_dir in self.results_base_dir.iterdir():
            if ticker_dir.is_dir():
                tickers.append(ticker_dir.name)

        return sorted(tickers)

    def get_summary_stats(self) -> Dict[str, any]:
        """Get summary statistics about stored results."""
        all_results = self.get_all_results()

        if not all_results:
            return {
                "total_analyses": 0,
                "unique_tickers": 0,
                "date_range": None,
                "most_analyzed_ticker": None
            }

        tickers = [r["ticker"] for r in all_results]
        ticker_counts = {}
        for ticker in tickers:
            ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

        dates = [r["date"] for r in all_results]

        return {
            "total_analyses": len(all_results),
            "unique_tickers": len(set(tickers)),
            "date_range": f"{min(dates)} to {max(dates)}",
            "most_analyzed_ticker": max(ticker_counts, key=ticker_counts.get) if ticker_counts else None,
            "ticker_counts": ticker_counts
        }


def format_results_list(results: List[Dict[str, any]], show_details: bool = False) -> str:
    """
    Format results list for display in chat interface.

    Args:
        results: List of result dictionaries
        show_details: Whether to show detailed information

    Returns:
        Formatted markdown string
    """
    if not results:
        return "No results found."

    output = []

    for idx, result in enumerate(results, 1):
        ticker = result["ticker"]
        date = result["date"]
        report_count = result["report_count"]
        decision_icon = "✅" if result["has_final_decision"] else "⚠️"

        # Format creation time
        if result["created_time"]:
            created_str = result["created_time"].strftime("%Y-%m-%d %I:%M %p")
        else:
            created_str = "Unknown"

        if show_details:
            output.append(f"""
**{idx}. {ticker}** - {date} {decision_icon}
  - Created: {created_str}
  - Reports: {report_count}
  - Available reports: {', '.join(result['report_files'][:3])}{'...' if len(result['report_files']) > 3 else ''}
""")
        else:
            output.append(f"{idx}. **{ticker}** ({date}) - {report_count} reports {decision_icon}")

    return "\n".join(output)


def format_report_content(report_name: str, content: str, max_preview_length: int = None) -> Tuple[str, str]:
    """
    Format a report for display.

    Returns:
        Tuple of (formatted_name, full_or_preview_content)
    """
    # Format report name
    formatted_name = report_name.replace('_', ' ').replace('.md', '').title()

    # Create preview or return full content
    if max_preview_length and len(content) > max_preview_length:
        preview = content[:max_preview_length] + "\n\n... (truncated)"
    else:
        preview = content

    return formatted_name, preview

"""
Results Viewer Module for TradingAgents

This module provides functionality to browse, filter, and view previously generated
trading analysis results from the results directory and S3.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
import re


class ResultsManager:
    """Manages access to stored trading analysis results from local filesystem and S3."""

    def __init__(self, results_base_dir: str = "./results", s3_client=None, s3_bucket: str = None):
        self.results_base_dir = Path(results_base_dir)
        self.s3_client = s3_client
        self.s3_bucket = s3_bucket

    def get_s3_results(self) -> List[Dict[str, any]]:
        """Get all results from S3."""
        if not self.s3_client or not self.s3_bucket:
            return []

        results = []
        try:
            # List all objects in results/ prefix
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.s3_bucket, Prefix='results/')

            # Parse S3 keys to extract ticker/date info
            seen = set()
            for page in pages:
                if 'Contents' not in page:
                    continue

                for obj in page['Contents']:
                    key = obj['Key']
                    # Parse: results/TICKER/DATE_TIMESTAMP/...
                    # Match both formats: YYYY-MM-DD_TIMESTAMP and today_TIMESTAMP
                    match = re.match(r'results/([^/]+)/([^/]+)_(\d+)/', key)
                    if match:
                        ticker = match.group(1)
                        date_or_today = match.group(2)
                        timestamp = match.group(3)
                        result_id = f"{ticker}_{date_or_today}_{timestamp}"

                        if result_id not in seen:
                            seen.add(result_id)
                            # Convert 'today' to actual date for display
                            display_date = date_or_today
                            if date_or_today == 'today':
                                # Use the last modified date
                                display_date = obj['LastModified'].strftime('%Y-%m-%d')

                            results.append({
                                "ticker": ticker,
                                "date": display_date,
                                "timestamp": timestamp,
                                "path": f"s3://{self.s3_bucket}/results/{ticker}/{date_or_today}_{timestamp}",
                                "s3_prefix": f"results/{ticker}/{date_or_today}_{timestamp}",
                                "created_time": obj['LastModified'],
                                "source": "s3"
                            })

            # Sort by creation time (newest first)
            results.sort(key=lambda x: x["created_time"], reverse=True)
        except Exception as e:
            print(f"Error fetching S3 results: {e}")

        return results

    def get_all_results(self) -> List[Dict[str, any]]:
        """
        Scan both local and S3 for all available analyses.

        Returns:
            List of dictionaries containing metadata for each analysis
        """
        results = []

        # Get local results
        if self.results_base_dir.exists():
            for ticker_dir in self.results_base_dir.iterdir():
                if not ticker_dir.is_dir():
                    continue

                ticker = ticker_dir.name

                for date_dir in ticker_dir.iterdir():
                    if not date_dir.is_dir():
                        continue

                    date = date_dir.name
                    reports_dir = date_dir / "reports"

                    if not reports_dir.exists():
                        continue

                    report_files = list(reports_dir.glob("*.md"))
                    report_count = len(report_files)
                    has_final_decision = (reports_dir / "final_trade_decision.md").exists()

                    try:
                        created_time = datetime.fromtimestamp(date_dir.stat().st_ctime)
                    except Exception:
                        created_time = None

                    results.append({
                        "ticker": ticker,
                        "date": date,
                        "path": str(date_dir),
                        "reports_path": str(reports_dir),
                        "report_count": report_count,
                        "has_final_decision": has_final_decision,
                        "created_time": created_time,
                        "report_files": [f.name for f in report_files],
                        "source": "local"
                    })

        # Get S3 results
        s3_results = self.get_s3_results()
        results.extend(s3_results)

        # Sort by creation time (newest first)
        results.sort(key=lambda x: x["created_time"] if x.get("created_time") else datetime.min, reverse=True)

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

    def read_s3_report(self, s3_prefix: str, report_name: str) -> Optional[str]:
        """Read a report from S3."""
        if not self.s3_client or not self.s3_bucket:
            return None

        try:
            s3_key = f"{s3_prefix}/reports/{report_name}"
            response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=s3_key)
            return response['Body'].read().decode('utf-8')
        except Exception as e:
            # Try without /reports/ subdirectory (for final_decision.txt)
            try:
                s3_key = f"{s3_prefix}/{report_name}"
                response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=s3_key)
                return response['Body'].read().decode('utf-8')
            except Exception:
                return None

    def get_all_reports_for_analysis(self, ticker: str, date: str, s3_prefix: str = None) -> Dict[str, str]:
        """
        Get all reports for a specific analysis from local or S3.

        Returns:
            Dictionary mapping report names to their content
        """
        reports = {}

        # Try S3 first if s3_prefix is provided
        if s3_prefix and self.s3_client:
            try:
                # List all objects under this prefix
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix=f"{s3_prefix}/reports/"
                )

                if 'Contents' in response:
                    for obj in response['Contents']:
                        key = obj['Key']
                        filename = key.split('/')[-1]
                        if filename.endswith('.md') or filename.endswith('.txt'):
                            content = self.read_s3_report(s3_prefix, filename)
                            if content:
                                reports[filename] = content

                # Also get final_decision.txt if it exists
                final_decision = self.read_s3_report(s3_prefix, f"{ticker}_final_decision.txt")
                if final_decision:
                    reports[f"{ticker}_final_decision.txt"] = final_decision

            except Exception as e:
                print(f"Error reading S3 reports: {e}")

        # Fall back to local if no S3 reports found
        if not reports:
            reports_dir = self.results_base_dir / ticker / date / "reports"

            if reports_dir.exists():
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
        report_count = result.get("report_count", 0)
        has_final_decision = result.get("has_final_decision", False)
        decision_icon = "✅" if has_final_decision else "⚠️"
        source = result.get("source", "local")
        source_icon = "📁" if source == "local" else "☁️"

        # Format creation time
        if result.get("created_time"):
            created_str = result["created_time"].strftime("%Y-%m-%d %I:%M %p")
        else:
            created_str = "Unknown"

        if show_details:
            report_files = result.get('report_files', [])
            reports_str = ', '.join(report_files[:3]) + ('...' if len(report_files) > 3 else '') if report_files else 'Check details for report list'
            output.append(f"""
**{idx}. {ticker}** - {date} {decision_icon} {source_icon}
  - Created: {created_str}
  - Source: {source.upper()}
  - Reports: {report_count if report_count else 'Multiple'}
  - {reports_str}
""")
        else:
            output.append(f"{idx}. **{ticker}** ({date}) {source_icon} - {report_count if report_count else 'Multiple'} reports {decision_icon}")

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

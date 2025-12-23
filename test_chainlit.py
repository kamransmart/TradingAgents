#!/usr/bin/env python3
"""
Quick test script to verify all dependencies are installed correctly.
"""

import sys

def test_imports():
    """Test that all required modules can be imported."""

    tests = {
        "Chainlit": "chainlit",
        "TradingAgents": "tradingagents.graph.trading_graph",
        "LangChain OpenAI": "langchain_openai",
        "LangGraph": "langgraph",
        "Pandas": "pandas",
        "YFinance": "yfinance",
        "ChromaDB": "chromadb",
    }

    print("🧪 Testing imports...\n")

    all_passed = True
    for name, module in tests.items():
        try:
            __import__(module)
            print(f"✅ {name:<20} OK")
        except ImportError as e:
            print(f"❌ {name:<20} FAILED: {e}")
            all_passed = False

    print()

    if all_passed:
        print("🎉 All imports successful! You're ready to run the web interface.")
        print("\nTo start the app:")
        print("  ./start_web.sh")
        print("\nOr manually:")
        print("  source venv/bin/activate")
        print("  chainlit run chainlit_app.py")
        return 0
    else:
        print("⚠️  Some imports failed. Please run:")
        print("  source venv/bin/activate")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(test_imports())

#!/usr/bin/env python3
"""Quick test to verify agent initialization."""

import sys
sys.dont_write_bytecode = True

from cli.main import MessageBuffer

# Create message buffer
mb = MessageBuffer()

print(f"Total agents in agent_status: {len(mb.agent_status)}")
print("\nAll agents:")
for i, (agent, status) in enumerate(mb.agent_status.items(), 1):
    print(f"{i:2d}. {agent:30s} -> {status}")

print("\n\nTeams dictionary:")
teams = {
    "Analyst Team": [
        "Market Analyst",
        "Social Analyst",
        "News Analyst",
        "Fundamentals Analyst",
    ],
    "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
    "Trading Team": ["Trader"],
    "Risk Management": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
    "Portfolio Management": ["Portfolio Manager"],
    "Prediction Team": [
        "Short-Term Predictor",
        "Medium-Term Predictor",
        "Long-Term Predictor",
        "Prediction Manager",
    ],
}

for team, agents in teams.items():
    print(f"\n{team}:")
    for agent in agents:
        exists = agent in mb.agent_status
        print(f"  - {agent:30s} exists={exists}")

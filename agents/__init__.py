"""
This module contains the AI agents for the application.
"""

from agents.reddit_scout.agent import agent as reddit_scout_agent
from agents.reddit_scout_mcp.agent import agent as reddit_scout_mcp_agent

# Export both agents
agent = reddit_scout_mcp_agent  # Default to MCP version

# This makes the agent available at the root level as required by ADK

__all__ = ['reddit_scout_agent']


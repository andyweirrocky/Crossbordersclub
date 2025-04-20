"""
Reddit Scout agent module.
"""

# This file makes 'reddit_scout' a Python package.
# It should import the agent instance to make it discoverable.

# Import the agent instance (using conventional 'root_agent' name)
from agents.reddit_scout.agent import agent

__all__ = ['agent'] 
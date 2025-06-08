"""Prompts module for Alpaca MCP Server - Guided trading workflows."""

# Import all prompt modules
from .list_trading_capabilities import list_trading_capabilities
from .account_analysis_prompt import account_analysis
from .position_management_prompt import position_management
from .market_analysis_prompt import market_analysis

__all__ = [
    "list_trading_capabilities",
    "account_analysis",
    "position_management",
    "market_analysis",
]

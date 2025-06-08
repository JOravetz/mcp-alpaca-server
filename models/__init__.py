"""
Trading models and schemas for Alpaca MCP Server.

This package provides comprehensive data models for trading operations,
portfolio analysis, risk management, and market condition tracking.
"""

from .schemas import (
    # Enums
    MarketStatus,
    AssetClass,
    OrderSide,
    OrderType,
    RiskLevel,
    TradingStrategy,
    VolatilityLevel,
    
    # Core Data Models
    Money,
    PriceData,
    AccountSummary,
    PositionAnalysis,
    MarketConditions,
    TradingOpportunity,
    RiskMetrics,
    
    # State Management
    StateManager,
    MarketConditionsManager,
    StreamingSessionManager,
    AnalysisResultsManager,
    
    # Utility Functions
    calculate_position_size,
    calculate_portfolio_metrics,
    assess_market_risk,
    create_sample_data,
    
    # Global State Managers
    market_conditions_manager,
    streaming_session_manager,
    analysis_results_manager,
    get_global_state,
)

__all__ = [
    # Enums
    "MarketStatus",
    "AssetClass", 
    "OrderSide",
    "OrderType",
    "RiskLevel",
    "TradingStrategy",
    "VolatilityLevel",
    
    # Core Data Models
    "Money",
    "PriceData",
    "AccountSummary",
    "PositionAnalysis", 
    "MarketConditions",
    "TradingOpportunity",
    "RiskMetrics",
    
    # State Management
    "StateManager",
    "MarketConditionsManager",
    "StreamingSessionManager", 
    "AnalysisResultsManager",
    
    # Utility Functions
    "calculate_position_size",
    "calculate_portfolio_metrics",
    "assess_market_risk",
    "create_sample_data",
    
    # Global State Managers
    "market_conditions_manager",
    "streaming_session_manager",
    "analysis_results_manager",
    "get_global_state",
]

# Version info
__version__ = "1.0.0"
__author__ = "Alpaca MCP Server"
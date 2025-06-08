"""
Configuration package for Alpaca MCP Server.
"""

from .settings import (
    # Settings
    settings,
    Settings,
    
    # Client factory functions
    get_trading_client,
    get_stock_historical_client,
    get_stock_stream_client,
    get_option_historical_client,
    
    # Global streaming state (exposed for backward compatibility)
    _global_stock_stream,
    _stock_stream_thread,
    _stock_stream_active,
    _stock_stream_subscriptions,
    _stock_data_buffers,
    _stock_stream_stats,
    _stock_stream_start_time,
    _stock_stream_end_time,
    _stock_stream_config,
    
    # Helper classes and functions
    ConfigurableStockDataBuffer,
    get_or_create_stock_buffer,
    check_stock_stream_duration_limit,
)

__all__ = [
    # Settings
    'settings',
    'Settings',
    
    # Client factory functions
    'get_trading_client',
    'get_stock_historical_client',
    'get_stock_stream_client',
    'get_option_historical_client',
    
    # Global streaming state
    '_global_stock_stream',
    '_stock_stream_thread',
    '_stock_stream_active',
    '_stock_stream_subscriptions',
    '_stock_data_buffers',
    '_stock_stream_stats',
    '_stock_stream_start_time',
    '_stock_stream_end_time',
    '_stock_stream_config',
    
    # Helper classes and functions
    'ConfigurableStockDataBuffer',
    'get_or_create_stock_buffer',
    'check_stock_stream_duration_limit',
]
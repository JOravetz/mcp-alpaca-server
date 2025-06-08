"""
Configuration and settings management for Alpaca MCP Server.

This module handles all environment variable loading, client initialization,
and global state management for the Alpaca MCP Server.
"""

import os
from typing import Optional, Dict, Set, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv
from collections import defaultdict, deque
import threading
import time

from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.live.stock import StockDataStream


# Load environment variables
load_dotenv()


@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    
    # API Credentials
    api_key: str
    api_secret: str
    
    # Trading Mode
    paper: bool = True
    
    # API URLs (optional overrides)
    trade_api_url: Optional[str] = None
    trade_api_wss: Optional[str] = None
    data_api_url: Optional[str] = None
    stream_data_wss: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Create Settings instance from environment variables."""
        # Support both naming conventions for API keys
        api_key = os.getenv("APCA_API_KEY_ID") or os.getenv("ALPACA_API_KEY")
        api_secret = os.getenv("APCA_API_SECRET_KEY") or os.getenv("ALPACA_SECRET_KEY")
        
        if not api_key or not api_secret:
            raise ValueError(
                "Alpaca API credentials not found in environment variables. "
                "Please set APCA_API_KEY_ID and APCA_API_SECRET_KEY "
                "(or ALPACA_API_KEY and ALPACA_SECRET_KEY)"
            )
        
        return cls(
            api_key=api_key,
            api_secret=api_secret,
            paper=os.getenv("PAPER", "true").lower() in ["true", "1", "yes"],
            trade_api_url=os.getenv("trade_api_url"),
            trade_api_wss=os.getenv("trade_api_wss"),
            data_api_url=os.getenv("data_api_url"),
            stream_data_wss=os.getenv("stream_data_wss")
        )


# ============================================================================
# Global Stock Streaming State (Alpaca allows only ONE stream connection)
# ============================================================================

_global_stock_stream = None
_stock_stream_thread = None
_stock_stream_active = False
_stock_stream_subscriptions = {
    'trades': set(),
    'quotes': set(),
    'bars': set(),
    'updated_bars': set(),
    'daily_bars': set(),
    'statuses': set()
}

# Configurable stock data buffers - no artificial limits for active stocks
_stock_data_buffers = {}
_stock_stream_stats = defaultdict(int)
_stock_stream_start_time = None
_stock_stream_end_time = None
_stock_stream_config = {
    'feed': 'sip',
    'buffer_size': None,  # Unlimited by default
    'duration_seconds': None  # No time limit by default
}


# ============================================================================
# Stock Streaming Helper Classes
# ============================================================================

class ConfigurableStockDataBuffer:
    """Thread-safe buffer with configurable size limits for stock market data"""
    
    def __init__(self, max_size: Optional[int] = None):
        """
        Initialize buffer with optional size limit.
        
        Args:
            max_size: Maximum number of items to store. None = unlimited.
                     For active stocks, consider 10000+ or unlimited.
        """
        if max_size is None:
            self.data = deque()  # Unlimited
        else:
            self.data = deque(maxlen=max_size)  # Limited
        
        self.lock = threading.Lock()
        self.last_update = time.time()
        self.max_size = max_size
        self.total_items_added = 0  # Track total even if some are dropped
    
    def add(self, item):
        with self.lock:
            self.data.append(item)
            self.last_update = time.time()
            self.total_items_added += 1
    
    def get_recent(self, seconds: int = 60):
        with self.lock:
            cutoff = time.time() - seconds
            return [item for item in self.data if item.get('timestamp', 0) > cutoff]
    
    def get_all(self):
        with self.lock:
            return list(self.data)
    
    def get_stats(self):
        with self.lock:
            return {
                'current_size': len(self.data),
                'max_size': self.max_size,
                'total_added': self.total_items_added,
                'last_update': self.last_update,
                'is_unlimited': self.max_size is None
            }
    
    def clear(self):
        with self.lock:
            self.data.clear()
            self.total_items_added = 0


# ============================================================================
# Client Initialization
# ============================================================================

# Create settings instance
settings = Settings.from_env()

# Initialize clients as module-level singletons
_trading_client = None
_stock_historical_client = None
_stock_stream_client = None
_option_historical_client = None


def get_trading_client() -> TradingClient:
    """Get or create the trading client."""
    global _trading_client
    if _trading_client is None:
        _trading_client = TradingClient(
            settings.api_key, 
            settings.api_secret, 
            paper=settings.paper,
            url_override=settings.trade_api_url
        )
    return _trading_client


def get_stock_historical_client() -> StockHistoricalDataClient:
    """Get or create the stock historical data client."""
    global _stock_historical_client
    if _stock_historical_client is None:
        _stock_historical_client = StockHistoricalDataClient(
            settings.api_key,
            settings.api_secret,
            url_override=settings.data_api_url
        )
    return _stock_historical_client


def get_stock_stream_client() -> StockDataStream:
    """Get or create the stock data stream client."""
    global _stock_stream_client
    if _stock_stream_client is None:
        _stock_stream_client = StockDataStream(
            settings.api_key,
            settings.api_secret,
            url_override=settings.stream_data_wss
        )
    return _stock_stream_client


def get_option_historical_client() -> OptionHistoricalDataClient:
    """Get or create the option historical data client."""
    global _option_historical_client
    if _option_historical_client is None:
        _option_historical_client = OptionHistoricalDataClient(
            api_key=settings.api_key,
            secret_key=settings.api_secret,
            url_override=settings.data_api_url
        )
    return _option_historical_client


# ============================================================================
# Utility Functions for Stream Management
# ============================================================================

def get_or_create_stock_buffer(symbol: str, data_type: str, buffer_size: Optional[int] = None) -> ConfigurableStockDataBuffer:
    """Get or create a buffer for a stock symbol/data_type combination"""
    buffer_key = f"{symbol}_{data_type}"
    if buffer_key not in _stock_data_buffers:
        effective_size = buffer_size if buffer_size is not None else _stock_stream_config.get('buffer_size')
        _stock_data_buffers[buffer_key] = ConfigurableStockDataBuffer(effective_size)
    return _stock_data_buffers[buffer_key]


def check_stock_stream_duration_limit() -> bool:
    """Check if stock stream should stop due to duration limit"""
    if _stock_stream_config['duration_seconds'] and _stock_stream_start_time:
        elapsed = time.time() - _stock_stream_start_time
        if elapsed >= _stock_stream_config['duration_seconds']:
            return True
    return False


# ============================================================================
# Export all necessary components
# ============================================================================

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
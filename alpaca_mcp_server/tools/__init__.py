"""Tools module for Alpaca MCP Server - Individual trading actions."""

# Import all tool modules
from . import account_tools
from . import position_tools
from . import order_tools
from . import market_data_tools

# Import specific functions for easy access
from .account_tools import get_account_info, get_positions, get_open_position

from .position_tools import close_position, close_all_positions

from .order_tools import (
    get_orders,
    place_stock_order,
    cancel_all_orders,
    cancel_order_by_id,
    place_option_market_order,
)

from .market_data_tools import (
    get_stock_quote,
    get_stock_bars,
    get_stock_bars_intraday,
    get_stock_snapshots,
    get_stock_trades,
    get_stock_latest_trade,
    get_stock_latest_bar,
)

__all__ = [
    # Module references
    "account_tools",
    "position_tools",
    "order_tools",
    "market_data_tools",
    # Account functions
    "get_account_info",
    "get_positions",
    "get_open_position",
    # Position functions
    "close_position",
    "close_all_positions",
    # Order functions
    "get_orders",
    "place_stock_order",
    "cancel_all_orders",
    "cancel_order_by_id",
    "place_option_market_order",
    # Market data functions
    "get_stock_quote",
    "get_stock_bars",
    "get_stock_bars_intraday",
    "get_stock_snapshots",
    "get_stock_trades",
    "get_stock_latest_trade",
    "get_stock_latest_bar",
]

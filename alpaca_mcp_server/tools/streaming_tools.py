"""Real-time streaming tools for day trading."""

import time
import threading
import asyncio
from datetime import datetime
from typing import List, Optional, Dict
from collections import deque, defaultdict
from alpaca.data.live import StockDataStream
from alpaca.data.enums import DataFeed
from ..config.settings import settings

# Global streaming state
_global_stock_stream = None
_stock_stream_thread = None
_stock_stream_active = False
_stock_stream_subscriptions = {
    "trades": set(),
    "quotes": set(),
    "bars": set(),
    "updated_bars": set(),
    "daily_bars": set(),
    "statuses": set(),
}

# Streaming data buffers
_stock_data_buffers = {}
_stock_stream_stats = defaultdict(int)
_stock_stream_start_time = None
_stock_stream_end_time = None
_stock_stream_config = {
    "feed": "sip",
    "buffer_size": None,  # Unlimited by default
    "duration_seconds": None,  # No time limit by default
}


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
            # Add timestamp if not present
            if isinstance(item, dict) and "received_at" not in item:
                item["received_at"] = time.time()

            self.data.append(item)
            self.total_items_added += 1
            self.last_update = time.time()

    def get_recent(self, seconds: int) -> List:
        """Get items from the last N seconds"""
        with self.lock:
            cutoff_time = time.time() - seconds
            recent_items = []

            for item in reversed(self.data):
                if isinstance(item, dict) and "received_at" in item:
                    if item["received_at"] >= cutoff_time:
                        recent_items.append(item)
                    else:
                        break
                else:
                    # Fallback for items without timestamp
                    recent_items.append(item)
                    if len(recent_items) >= 100:  # Limit for safety
                        break

            return list(reversed(recent_items))

    def get_all(self) -> List:
        """Get all buffered items"""
        with self.lock:
            return list(self.data)

    def get_stats(self) -> Dict:
        """Get buffer statistics"""
        with self.lock:
            return {
                "current_size": len(self.data),
                "max_size": self.max_size or "Unlimited",
                "total_added": self.total_items_added,
                "last_update": self.last_update,
                "utilization": (
                    f"{len(self.data)}/{self.max_size}"
                    if self.max_size
                    else f"{len(self.data)}/∞"
                ),
            }

    def clear(self):
        """Clear all data from buffer"""
        with self.lock:
            self.data.clear()


def _get_or_create_stock_buffer(
    symbol: str, data_type: str, buffer_size: Optional[int] = None
):
    """Get or create a stock data buffer for symbol/data_type"""
    buffer_key = f"{symbol}_{data_type}"
    if buffer_key not in _stock_data_buffers:
        _stock_data_buffers[buffer_key] = ConfigurableStockDataBuffer(buffer_size)
    return _stock_data_buffers[buffer_key]


# Event handlers for streaming data
def handle_stock_trade(trade):
    """Handle incoming stock trade data"""
    global _stock_stream_stats
    try:
        symbol = trade.symbol
        buffer = _get_or_create_stock_buffer(
            symbol, "trades", _stock_stream_config["buffer_size"]
        )

        trade_data = {
            "symbol": symbol,
            "price": float(trade.price),
            "size": int(trade.size),
            "timestamp": (
                trade.timestamp.isoformat()
                if hasattr(trade.timestamp, "isoformat")
                else str(trade.timestamp)
            ),
            "conditions": getattr(trade, "conditions", []),
            "exchange": getattr(trade, "exchange", "Unknown"),
        }

        buffer.add(trade_data)
        _stock_stream_stats["trades"] += 1

    except Exception as e:
        print(f"Error handling stock trade: {e}")


def handle_stock_quote(quote):
    """Handle incoming stock quote data"""
    global _stock_stream_stats
    try:
        symbol = quote.symbol
        buffer = _get_or_create_stock_buffer(
            symbol, "quotes", _stock_stream_config["buffer_size"]
        )

        quote_data = {
            "symbol": symbol,
            "bid": float(quote.bid_price) if quote.bid_price else None,
            "ask": float(quote.ask_price) if quote.ask_price else None,
            "bid_size": int(quote.bid_size) if quote.bid_size else None,
            "ask_size": int(quote.ask_size) if quote.ask_size else None,
            "timestamp": (
                quote.timestamp.isoformat()
                if hasattr(quote.timestamp, "isoformat")
                else str(quote.timestamp)
            ),
            "bid_exchange": getattr(quote, "bid_exchange", "Unknown"),
            "ask_exchange": getattr(quote, "ask_exchange", "Unknown"),
        }

        buffer.add(quote_data)
        _stock_stream_stats["quotes"] += 1

    except Exception as e:
        print(f"Error handling stock quote: {e}")


def handle_stock_bar(bar):
    """Handle incoming stock bar data"""
    global _stock_stream_stats
    try:
        symbol = bar.symbol
        buffer = _get_or_create_stock_buffer(
            symbol, "bars", _stock_stream_config["buffer_size"]
        )

        bar_data = {
            "symbol": symbol,
            "open": float(bar.open),
            "high": float(bar.high),
            "low": float(bar.low),
            "close": float(bar.close),
            "volume": int(bar.volume),
            "timestamp": (
                bar.timestamp.isoformat()
                if hasattr(bar.timestamp, "isoformat")
                else str(bar.timestamp)
            ),
            "trade_count": getattr(bar, "trade_count", None),
            "vwap": getattr(bar, "vwap", None),
        }

        buffer.add(bar_data)
        _stock_stream_stats["bars"] += 1

    except Exception as e:
        print(f"Error handling stock bar: {e}")


def handle_stock_status(status):
    """Handle incoming stock status data"""
    global _stock_stream_stats
    try:
        symbol = status.symbol
        buffer = _get_or_create_stock_buffer(
            symbol, "statuses", _stock_stream_config["buffer_size"]
        )

        status_data = {
            "symbol": symbol,
            "status": str(status.status),
            "timestamp": (
                status.timestamp.isoformat()
                if hasattr(status.timestamp, "isoformat")
                else str(status.timestamp)
            ),
            "tape": getattr(status, "tape", "Unknown"),
        }

        buffer.add(status_data)
        _stock_stream_stats["statuses"] += 1

    except Exception as e:
        print(f"Error handling stock status: {e}")


async def start_global_stock_stream(
    symbols: List[str],
    data_types: List[str] = ["trades", "quotes"],
    feed: str = "sip",
    duration_seconds: Optional[int] = None,
    buffer_size_per_symbol: Optional[int] = None,
    replace_existing: bool = False,
) -> str:
    """
    Start the global real-time stock market data stream (Alpaca allows only one stream connection).

    Args:
        symbols (List[str]): List of stock symbols to stream (e.g., ['AAPL', 'MSFT', 'NVDA'])
        data_types (List[str]): Types of stock data to stream. Options:
            - "trades": Real-time stock trade executions
            - "quotes": Stock bid/ask prices and sizes
            - "bars": 1-minute OHLCV stock bars
            - "updated_bars": Corrections to stock minute bars
            - "daily_bars": Daily OHLCV stock bars
            - "statuses": Stock trading halt/resume notifications
        feed (str): Stock data feed source ("sip" for all exchanges, "iex" for IEX only)
        duration_seconds (Optional[int]): How long to run the stock stream in seconds. None = run indefinitely
        buffer_size_per_symbol (Optional[int]): Max items per stock symbol/data_type buffer.
                                               None = unlimited (recommended for active stocks)
                                               High-velocity stocks may need 10000+ or unlimited
        replace_existing (bool): If True, stop existing stock stream and start new one

    Returns:
        str: Confirmation with stock stream details and data access instructions
    """
    global _global_stock_stream, _stock_stream_thread, _stock_stream_active, _stock_stream_start_time, _stock_stream_end_time

    try:
        # Check if stock stream already exists
        if _stock_stream_active and not replace_existing:
            current_symbols = set()
            for data_type, symbol_set in _stock_stream_subscriptions.items():
                current_symbols.update(symbol_set)

            return f"""
❌ Global stock stream already active!

Current Stock Stream:
└── Symbols: {', '.join(sorted(current_symbols)) if current_symbols else 'None'}
└── Data Types: {[dt for dt, symbols in _stock_stream_subscriptions.items() if symbols]}
└── Feed: {_stock_stream_config['feed'].upper()}
└── Runtime: {(time.time() - _stock_stream_start_time)/60:.1f} minutes

Options:
└── Use add_symbols_to_stock_stream() to add more symbols
└── Use stop_global_stock_stream() to stop current stream
└── Use replace_existing=True to replace current stream
            """

        # Stop existing stock stream if replacing
        if _stock_stream_active and replace_existing:
            await stop_global_stock_stream()
            await asyncio.sleep(2)  # Give time for cleanup

        # Validate parameters
        valid_data_types = [
            "trades",
            "quotes",
            "bars",
            "updated_bars",
            "daily_bars",
            "statuses",
        ]
        invalid_types = [dt for dt in data_types if dt not in valid_data_types]
        if invalid_types:
            return f"Invalid data types: {invalid_types}. Valid options: {valid_data_types}"

        if feed.lower() not in ["sip", "iex"]:
            return "Feed must be 'sip' or 'iex'"

        # Convert symbols to uppercase
        symbols = [s.upper() for s in symbols]

        # Update global stock stream config
        _stock_stream_config.update(
            {
                "feed": feed,
                "buffer_size": buffer_size_per_symbol,
                "duration_seconds": duration_seconds,
            }
        )

        # Create data feed enum
        feed_enum = DataFeed.SIP if feed.lower() == "sip" else DataFeed.IEX

        # Create the single global stock stream
        _global_stock_stream = StockDataStream(
            api_key=settings.alpaca_api_key,
            secret_key=settings.alpaca_secret_key,
            feed=feed_enum,
            raw_data=False,
        )

        # Subscribe to requested stock data types
        if "trades" in data_types:
            _global_stock_stream.subscribe_trades(handle_stock_trade, *symbols)
            _stock_stream_subscriptions["trades"].update(symbols)

        if "quotes" in data_types:
            _global_stock_stream.subscribe_quotes(handle_stock_quote, *symbols)
            _stock_stream_subscriptions["quotes"].update(symbols)

        if "bars" in data_types:
            _global_stock_stream.subscribe_bars(handle_stock_bar, *symbols)
            _stock_stream_subscriptions["bars"].update(symbols)

        if "updated_bars" in data_types:
            _global_stock_stream.subscribe_updated_bars(handle_stock_bar, *symbols)
            _stock_stream_subscriptions["updated_bars"].update(symbols)

        if "daily_bars" in data_types:
            _global_stock_stream.subscribe_daily_bars(handle_stock_bar, *symbols)
            _stock_stream_subscriptions["daily_bars"].update(symbols)

        if "statuses" in data_types:
            _global_stock_stream.subscribe_trading_statuses(
                handle_stock_status, *symbols
            )
            _stock_stream_subscriptions["statuses"].update(symbols)

        # Function to run the stock stream with duration monitoring
        def run_stock_stream():
            global _stock_stream_active, _stock_stream_start_time, _stock_stream_end_time

            try:
                _stock_stream_active = True
                _stock_stream_start_time = time.time()
                _stock_stream_end_time = (
                    _stock_stream_start_time + duration_seconds
                    if duration_seconds
                    else None
                )

                print(f"Starting Alpaca stock stream for {len(symbols)} symbols...")

                # Start the stock stream
                _global_stock_stream.run()

            except Exception as e:
                print(f"Stock stream error: {e}")
            finally:
                _stock_stream_active = False
                print("Stock stream stopped")

        # Start the stock stream in a background thread
        _stock_stream_thread = threading.Thread(target=run_stock_stream, daemon=True)
        _stock_stream_thread.start()

        # Wait a moment for connection
        await asyncio.sleep(2)

        # Format response
        buffer_info = (
            "Unlimited"
            if buffer_size_per_symbol is None
            else f"{buffer_size_per_symbol:,} items"
        )
        duration_info = (
            f"{duration_seconds:,} seconds" if duration_seconds else "Indefinite"
        )

        return f"""
🚀 GLOBAL STOCK STREAM STARTED SUCCESSFULLY!

📊 Stock Stream Configuration:
└── Symbols: {', '.join(symbols)} ({len(symbols)} stock symbols)
└── Data Types: {', '.join(data_types)}
└── Feed: {feed.upper()}
└── Duration: {duration_info}
└── Buffer Size per Symbol: {buffer_info}
└── Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💾 Stock Data Access:
└── get_stock_stream_data("AAPL", "trades") - Recent stock trades
└── get_stock_stream_buffer_stats() - Buffer statistics  
└── list_active_stock_streams() - Current stream status
└── get_stock_stream_analysis("NVDA", "momentum") - Real-time analysis

⚡ Stock Stream Management:
└── add_symbols_to_stock_stream(["TSLA", "META"]) - Add more stocks
└── stop_global_stock_stream() - Stop streaming

🔥 Pro Tips for Stock Trading:
└── For active stocks like NVDA, TSLA: unlimited buffers recommended
└── Use get_stock_stream_data() with time filters for analysis
└── Combine with stock snapshots for comprehensive market view
└── Stock stream data persists until manually cleared
        """

    except Exception as e:
        return f"Error starting global stock stream: {str(e)}"


async def stop_global_stock_stream() -> str:
    """
    Stop the global stock streaming session and provide final statistics.

    Returns:
        str: Final statistics and confirmation message
    """
    global _global_stock_stream, _stock_stream_thread, _stock_stream_active, _stock_stream_subscriptions

    try:
        if not _stock_stream_active:
            return "No active stock stream to stop."

        # Calculate final statistics
        runtime_minutes = (
            (time.time() - _stock_stream_start_time) / 60
            if _stock_stream_start_time
            else 0
        )
        total_events = sum(_stock_stream_stats.values())

        # Stop the stream
        _stock_stream_active = False

        if _global_stock_stream:
            try:
                _global_stock_stream.stop()
            except Exception:
                pass  # Stream might already be stopped

        # Get final buffer statistics
        total_buffered_items = sum(
            len(buffer.get_all()) for buffer in _stock_data_buffers.values()
        )

        # Clear subscriptions
        for data_type in _stock_stream_subscriptions:
            _stock_stream_subscriptions[data_type].clear()

        result = "🛑 GLOBAL STOCK STREAM STOPPED\n"
        result += "=" * 40 + "\n\n"

        result += "📊 Final Stock Statistics:\n"
        result += f"  Runtime: {runtime_minutes:.1f} minutes\n"
        result += f"  Total Events Processed: {total_events:,}\n"
        result += f"  Items in Buffers: {total_buffered_items:,}\n"

        if runtime_minutes > 0:
            result += f"  Average Rate: {total_events/runtime_minutes:.1f} events/min\n"

        # Breakdown by data type
        result += "\n📈 Event Breakdown:\n"
        for data_type, count in _stock_stream_stats.items():
            if count > 0:
                percentage = (count / total_events * 100) if total_events > 0 else 0
                result += f"  {data_type.title()}: {count:,} ({percentage:.1f}%)\n"

        # Buffer retention info
        result += "\n💾 Data Retention:\n"
        result += f"  Buffers: {len(_stock_data_buffers)} remain in memory\n"
        result += "  Access: Use get_stock_stream_data() for historical analysis\n"
        result += "  Cleanup: Use clear_stock_stream_buffers() to free memory\n"

        result += "\n🔄 Restart Options:\n"
        result += "  start_global_stock_stream() - Start fresh stream\n"
        result += "  clear_stock_stream_buffers() - Free memory first\n"

        return result

    except Exception as e:
        return f"Error stopping stock stream: {str(e)}"


async def add_symbols_to_stock_stream(
    symbols: List[str], data_types: Optional[List[str]] = None
) -> str:
    """
    Add stock symbols to the existing global stock stream (if active).

    Args:
        symbols (List[str]): List of stock symbols to add
        data_types (Optional[List[str]]): Stock data types to subscribe for new symbols.
                                         If None, uses same types as existing subscriptions.

    Returns:
        str: Confirmation message with updated stock subscription details
    """
    global _global_stock_stream, _stock_stream_subscriptions

    try:
        if not _stock_stream_active or not _global_stock_stream:
            return (
                "No active global stock stream. Use start_global_stock_stream() first."
            )

        symbols = [s.upper() for s in symbols]

        # Determine data types to subscribe
        if data_types is None:
            # Use existing subscription types
            data_types = [
                dt
                for dt, symbol_set in _stock_stream_subscriptions.items()
                if symbol_set
            ]
            if not data_types:
                return "No existing stock subscriptions found. Specify data_types parameter."

        # Add stock subscriptions
        added_subscriptions = []

        if "trades" in data_types and "trades" in [
            dt for dt, s in _stock_stream_subscriptions.items() if s
        ]:
            _global_stock_stream.subscribe_trades(handle_stock_trade, *symbols)
            _stock_stream_subscriptions["trades"].update(symbols)
            added_subscriptions.append("trades")

        if "quotes" in data_types and "quotes" in [
            dt for dt, s in _stock_stream_subscriptions.items() if s
        ]:
            _global_stock_stream.subscribe_quotes(handle_stock_quote, *symbols)
            _stock_stream_subscriptions["quotes"].update(symbols)
            added_subscriptions.append("quotes")

        if "bars" in data_types and "bars" in [
            dt for dt, s in _stock_stream_subscriptions.items() if s
        ]:
            _global_stock_stream.subscribe_bars(handle_stock_bar, *symbols)
            _stock_stream_subscriptions["bars"].update(symbols)
            added_subscriptions.append("bars")

        # Create buffers for new stock symbols
        for symbol in symbols:
            for data_type in data_types:
                _get_or_create_stock_buffer(
                    symbol, data_type, _stock_stream_config["buffer_size"]
                )

        # Get current total stock symbols
        all_symbols = set()
        for symbol_set in _stock_stream_subscriptions.values():
            all_symbols.update(symbol_set)

        return f"""
✅ SYMBOLS ADDED TO STOCK STREAM

📈 Added: {', '.join(symbols)}
📊 Data Types: {', '.join(added_subscriptions)}
🔢 Total Stock Symbols: {len(all_symbols)}
💾 Buffers Created: {len(symbols) * len(data_types)}

Current Stock Stream:
└── All Symbols: {', '.join(sorted(all_symbols))}
└── Runtime: {(time.time() - _stock_stream_start_time)/60:.1f} minutes
└── Total Events: {sum(_stock_stream_stats.values()):,}
        """

    except Exception as e:
        return f"Error adding symbols to stock stream: {str(e)}"


async def get_stock_stream_data(
    symbol: str,
    data_type: str,
    recent_seconds: Optional[int] = None,
    limit: Optional[int] = None,
) -> str:
    """
    Retrieve streaming stock market data for a symbol with flexible filtering.

    Args:
        symbol (str): Stock symbol
        data_type (str): Type of stock data ("trades", "quotes", "bars", etc.)
        recent_seconds (Optional[int]): Get stock data from last N seconds. None = all data
        limit (Optional[int]): Maximum number of items to return. None = no limit

    Returns:
        str: Formatted streaming stock data with statistics
    """
    try:
        if not _stock_stream_active:
            return "No active stock stream. Use start_global_stock_stream() to begin streaming."

        symbol = symbol.upper()
        buffer_key = f"{symbol}_{data_type}"

        if buffer_key not in _stock_data_buffers:
            return f"No stock data buffer found for {symbol} {data_type}. Check if stock symbol is subscribed."

        buffer = _stock_data_buffers[buffer_key]

        # Get data based on filters
        if recent_seconds is not None:
            data = buffer.get_recent(recent_seconds)
            time_filter = f"last {recent_seconds}s"
        else:
            data = buffer.get_all()
            time_filter = "all time"

        # Apply limit if specified
        if limit is not None and len(data) > limit:
            data = data[-limit:]  # Get most recent items
            limit_info = f", limited to {limit} items"
        else:
            limit_info = ""

        if not data:
            return f"No {data_type} data found for {symbol} ({time_filter})"

        # Get buffer statistics
        buffer_stats = buffer.get_stats()

        # Format the response
        result = f"📊 STOCK STREAM DATA: {symbol} - {data_type.upper()}\n"
        result += "=" * 60 + "\n\n"

        result += f"🔍 Filter: {time_filter}{limit_info}\n"
        result += f"📈 Results: {len(data)} items\n"
        result += f"💾 Buffer: {buffer_stats['current_size']} total items (utilization: {buffer_stats['utilization']})\n\n"

        # Show recent data samples
        if data_type == "trades":
            result += "Recent Trades:\n"
            for i, trade in enumerate(data[-10:], 1):  # Last 10 trades
                result += f"  {i:2d}. ${trade['price']:8.4f} x {trade['size']:,} @ {trade['timestamp'][-8:]}\n"

        elif data_type == "quotes":
            result += "Recent Quotes:\n"
            for i, quote in enumerate(data[-10:], 1):  # Last 10 quotes
                bid = f"${quote['bid']:.4f}" if quote["bid"] else "N/A"
                ask = f"${quote['ask']:.4f}" if quote["ask"] else "N/A"
                result += f"  {i:2d}. {bid} x {ask} @ {quote['timestamp'][-8:]}\n"

        elif data_type == "bars":
            result += "Recent Bars:\n"
            for i, bar in enumerate(data[-5:], 1):  # Last 5 bars
                result += f"  {i}. O:${bar['open']:.4f} H:${bar['high']:.4f} L:${bar['low']:.4f} C:${bar['close']:.4f} V:{bar['volume']:,}\n"

        # Add analysis summary for trades
        if data_type == "trades" and len(data) > 1:
            prices = [t["price"] for t in data]
            volumes = [t["size"] for t in data]

            result += "\n📊 Quick Analysis:\n"
            result += f"  Price Range: ${min(prices):.4f} - ${max(prices):.4f}\n"
            result += f"  Last Price: ${prices[-1]:.4f}\n"
            result += f"  Total Volume: {sum(volumes):,} shares\n"
            result += f"  Avg Trade Size: {sum(volumes)/len(volumes):.0f} shares\n"

        return result

    except Exception as e:
        return f"Error retrieving stock stream data: {str(e)}"


async def list_active_stock_streams() -> str:
    """
    List all active stock streaming subscriptions and their status.

    Returns:
        str: Detailed information about active stock streams
    """
    try:
        if not _stock_stream_active:
            return "No active stock stream. Use start_global_stock_stream() to begin streaming."

        runtime_minutes = (
            (time.time() - _stock_stream_start_time) / 60
            if _stock_stream_start_time
            else 0
        )

        result = "📡 ACTIVE STOCK STREAMING STATUS\n"
        result += "=" * 50 + "\n\n"

        # Stream configuration
        result += "🔧 Stream Configuration:\n"
        result += f"  Feed: {_stock_stream_config['feed'].upper()}\n"
        result += f"  Runtime: {runtime_minutes:.1f} minutes\n"
        buffer_size_info = (
            "Unlimited"
            if _stock_stream_config["buffer_size"] is None
            else f"{_stock_stream_config['buffer_size']:,} per buffer"
        )
        result += f"  Buffer Size: {buffer_size_info}\n"

        if _stock_stream_config["duration_seconds"]:
            remaining = (
                _stock_stream_config["duration_seconds"]
                - (time.time() - _stock_stream_start_time)
            ) / 60
            result += f"  Duration: {_stock_stream_config['duration_seconds']/60:.1f} min ({remaining:.1f} min remaining)\n"
        else:
            result += "  Duration: Indefinite\n"

        # Active subscriptions
        result += "\n📊 Active Stock Subscriptions:\n"
        total_symbols = set()

        for data_type, symbol_set in _stock_stream_subscriptions.items():
            if symbol_set:
                result += f"  {data_type.upper()}: {', '.join(sorted(symbol_set))} ({len(symbol_set)} symbols)\n"
                total_symbols.update(symbol_set)

        result += f"\nTotal Unique Symbols: {len(total_symbols)}\n"

        # Statistics
        total_events = sum(_stock_stream_stats.values())
        result += "\n📈 Streaming Statistics:\n"
        result += f"  Total Events: {total_events:,}\n"
        if runtime_minutes > 0:
            result += f"  Rate: {total_events/runtime_minutes:.1f} events/min\n"

        for data_type, count in _stock_stream_stats.items():
            if count > 0:
                result += f"  {data_type.title()}: {count:,}\n"

        # Buffer status
        result += "\n💾 Buffer Status:\n"
        result += f"  Total Buffers: {len(_stock_data_buffers)}\n"
        total_buffered = sum(
            len(buffer.get_all()) for buffer in _stock_data_buffers.values()
        )
        result += f"  Total Items Buffered: {total_buffered:,}\n"

        # Quick access commands
        result += "\n🔧 Management Commands:\n"
        result += '  get_stock_stream_data("AAPL", "trades") - View recent trades\n'
        result += "  get_stock_stream_buffer_stats() - Detailed buffer stats\n"
        result += '  add_symbols_to_stock_stream(["TSLA"]) - Add more symbols\n'
        result += "  stop_global_stock_stream() - Stop streaming\n"

        return result

    except Exception as e:
        return f"Error listing active stock streams: {str(e)}"


async def get_stock_stream_buffer_stats() -> str:
    """
    Get detailed statistics about all streaming data buffers.

    Returns:
        str: Comprehensive buffer statistics
    """
    try:
        if not _stock_data_buffers:
            return "No stock stream buffers exist. Start streaming first with start_global_stock_stream()."

        result = "💾 STOCK STREAM BUFFER STATISTICS\n"
        result += "=" * 60 + "\n\n"

        total_items = 0
        total_buffers = len(_stock_data_buffers)

        # Group by symbol
        symbol_stats = defaultdict(
            lambda: {"buffers": 0, "total_items": 0, "data_types": []}
        )

        for buffer_key, buffer in _stock_data_buffers.items():
            symbol, data_type = buffer_key.rsplit("_", 1)
            stats = buffer.get_stats()

            symbol_stats[symbol]["buffers"] += 1
            symbol_stats[symbol]["total_items"] += stats["current_size"]
            symbol_stats[symbol]["data_types"].append(data_type)
            total_items += stats["current_size"]

        # Summary stats
        result += "📊 Summary:\n"
        result += f"  Total Buffers: {total_buffers}\n"
        result += f"  Total Items: {total_items:,}\n"
        result += f"  Unique Symbols: {len(symbol_stats)}\n"
        result += f"  Avg Items per Buffer: {total_items/total_buffers:.1f}\n\n"

        # Per-symbol breakdown
        result += "📈 Per-Symbol Breakdown:\n"
        for symbol, stats in sorted(symbol_stats.items()):
            result += f"  {symbol}:\n"
            result += (
                f"    Buffers: {stats['buffers']} ({', '.join(stats['data_types'])})\n"
            )
            result += f"    Items: {stats['total_items']:,}\n"
            result += (
                f"    Avg per Buffer: {stats['total_items']/stats['buffers']:.1f}\n"
            )

        # Detailed buffer info
        result += "\n🔍 Detailed Buffer Information:\n"
        for buffer_key, buffer in sorted(_stock_data_buffers.items()):
            stats = buffer.get_stats()
            last_update = (
                datetime.fromtimestamp(stats["last_update"]).strftime("%H:%M:%S")
                if stats["last_update"]
                else "Never"
            )
            result += f"  {buffer_key}:\n"
            result += f"    Size: {stats['utilization']}\n"
            result += f"    Total Added: {stats['total_added']:,}\n"
            result += f"    Last Update: {last_update}\n"

        # Memory usage estimate
        avg_item_size = 200  # Rough estimate in bytes
        estimated_memory_mb = (total_items * avg_item_size) / (1024 * 1024)
        result += f"\n🖥️  Estimated Memory Usage: {estimated_memory_mb:.1f} MB\n"

        # Cleanup options
        result += "\n🧹 Cleanup Options:\n"
        result += "  clear_stock_stream_buffers() - Clear all buffers\n"
        result += "  Individual buffer access via get_stock_stream_data()\n"

        return result

    except Exception as e:
        return f"Error getting buffer statistics: {str(e)}"


async def clear_stock_stream_buffers() -> str:
    """
    Clear all streaming data buffers to free memory.

    Returns:
        str: Confirmation message with cleared buffer count
    """
    global _stock_data_buffers

    try:
        buffer_count = len(_stock_data_buffers)
        total_items = sum(
            len(buffer.get_all()) for buffer in _stock_data_buffers.values()
        )

        # Clear all buffers
        for buffer in _stock_data_buffers.values():
            buffer.clear()

        return f"""
🧹 STOCK STREAM BUFFERS CLEARED

📊 Cleanup Summary:
  Buffers Cleared: {buffer_count}
  Items Removed: {total_items:,}
  Memory Freed: ~{(total_items * 200) / (1024 * 1024):.1f} MB

💾 Status:
  Buffers remain allocated but empty
  Streaming continues if active
  Use get_stock_stream_data() to verify clearing
        """

    except Exception as e:
        return f"Error clearing stock buffers: {str(e)}"

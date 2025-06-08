"""Main MCP server implementation with prompt-driven architecture."""

from mcp.server.fastmcp import FastMCP
from .config.settings import settings

# Import all tool modules
from .tools import (
    account_tools,
    position_tools,
    order_tools,
    market_data_tools,
    market_info_tools,
    options_tools,
    watchlist_tools,
    asset_tools,
    corporate_action_tools,
    streaming_tools,
)

# Import all prompt modules
from .prompts import (
    list_trading_capabilities as ltc_module,
    account_analysis_prompt,
    position_management_prompt,
    market_analysis_prompt,
)

# Import resource modules
from .resources import (
    account_resources,
    market_resources,
    position_resources,
    portfolio_resources,
    streaming_resources,
    market_momentum,
    intraday_pnl,
    data_quality,
    server_health,
    session_status,
    api_monitor,
)

# Create the FastMCP server instance
mcp = FastMCP(
    name=settings.server_name,
    version=settings.version,
    dependencies=["alpaca-py>=0.40.1", "python-dotenv>=1.1.0"],
)

# ============================================================================
# PROMPTS - Guided Trading Workflows (Highest Leverage)
# ============================================================================


@mcp.prompt()
async def list_trading_capabilities() -> str:
    """List all Alpaca trading capabilities with guided workflows."""
    return await ltc_module.list_trading_capabilities()


@mcp.prompt()
async def account_analysis() -> str:
    """Complete portfolio health check with actionable insights."""
    return await account_analysis_prompt.account_analysis()


@mcp.prompt()
async def position_management(symbol: str = None) -> str:
    """Strategic position review and optimization."""
    return await position_management_prompt.position_management(symbol)


@mcp.prompt()
async def market_analysis(
    symbols: list = None, timeframe: str = "1Day", analysis_type: str = "comprehensive"
) -> str:
    """Real-time market analysis with trading opportunities."""
    return await market_analysis_prompt.market_analysis(
        symbols, timeframe, analysis_type
    )


# ============================================================================
# TOOLS - Individual Trading Actions (Composed by Prompts)
# ============================================================================


# Account & Position Management Tools
@mcp.tool()
async def get_account_info() -> str:
    """Get current account information including balances and status."""
    return await account_tools.get_account_info()


@mcp.tool()
async def get_positions() -> str:
    """Get all current positions in the portfolio."""
    return await account_tools.get_positions()


@mcp.tool()
async def get_open_position(symbol: str) -> str:
    """Get details for a specific open position."""
    return await account_tools.get_open_position(symbol)


@mcp.tool()
async def close_position(symbol: str, qty: str = None, percentage: str = None) -> str:
    """Close a specific position."""
    return await position_tools.close_position(symbol, qty, percentage)


@mcp.tool()
async def close_all_positions(cancel_orders: bool = False) -> str:
    """Close all open positions."""
    return await position_tools.close_all_positions(cancel_orders)


# Market Data Tools
@mcp.tool()
async def get_stock_quote(symbol: str) -> str:
    """Get latest quote for a stock."""
    return await market_data_tools.get_stock_quote(symbol)


@mcp.tool()
async def get_stock_snapshots(symbols: str) -> str:
    """Get comprehensive market snapshots."""
    return await market_data_tools.get_stock_snapshots(symbols)


@mcp.tool()
async def get_stock_bars(symbol: str, days: int = 5) -> str:
    """Get historical price bars."""
    return await market_data_tools.get_stock_bars(symbol, days)


@mcp.tool()
async def get_stock_bars_intraday(
    symbol: str,
    timeframe: str = "1Min",
    start_date: str = None,
    end_date: str = None,
    limit: int = 10000,
) -> str:
    """Get intraday historical bars with analysis."""
    return await market_data_tools.get_stock_bars_intraday(
        symbol, timeframe, start_date, end_date, limit
    )


@mcp.tool()
async def get_stock_trades(symbol: str, days: int = 5, limit: int = None) -> str:
    """Get recent trades for a stock."""
    return await market_data_tools.get_stock_trades(symbol, days, limit)


@mcp.tool()
async def get_stock_latest_trade(symbol: str) -> str:
    """Get the latest trade for a stock."""
    return await market_data_tools.get_stock_latest_trade(symbol)


@mcp.tool()
async def get_stock_latest_bar(symbol: str) -> str:
    """Get the latest minute bar for a stock."""
    return await market_data_tools.get_stock_latest_bar(symbol)


# Market Info Tools
@mcp.tool()
async def get_market_clock() -> str:
    """Get current market status and next open/close times."""
    return await market_info_tools.get_market_clock()


@mcp.tool()
async def get_market_calendar(start_date: str, end_date: str) -> str:
    """Get market calendar for specified date range."""
    return await market_info_tools.get_market_calendar(start_date, end_date)


# Options Tools
@mcp.tool()
async def get_option_contracts(
    underlying_symbol: str,
    expiration_date: str = None,
    strike_price_gte: str = None,
    strike_price_lte: str = None,
    type: str = None,
    limit: int = None,
) -> str:
    """Get option contracts for underlying symbol."""
    return await options_tools.get_option_contracts(
        underlying_symbol,
        expiration_date,
        strike_price_gte,
        strike_price_lte,
        type,
        None,
        None,
        limit,
    )


@mcp.tool()
async def get_option_latest_quote(symbol: str) -> str:
    """Get latest quote for an option contract."""
    return await options_tools.get_option_latest_quote(symbol)


@mcp.tool()
async def get_option_snapshot(symbol: str) -> str:
    """Get comprehensive option snapshot with Greeks."""
    return await options_tools.get_option_snapshot(symbol)


# Watchlist Tools
@mcp.tool()
async def create_watchlist(name: str, symbols: list) -> str:
    """Create a new watchlist with specified symbols."""
    return await watchlist_tools.create_watchlist(name, symbols)


@mcp.tool()
async def get_watchlists() -> str:
    """Get all watchlists for the account."""
    return await watchlist_tools.get_watchlists()


@mcp.tool()
async def update_watchlist(
    watchlist_id: str, name: str = None, symbols: list = None
) -> str:
    """Update an existing watchlist."""
    return await watchlist_tools.update_watchlist(watchlist_id, name, symbols)


# Asset Tools
@mcp.tool()
async def get_all_assets(
    status: str = None,
    asset_class: str = None,
    exchange: str = None,
    attributes: str = None,
) -> str:
    """Get all available assets with optional filtering."""
    return await asset_tools.get_all_assets(status, asset_class, exchange, attributes)


@mcp.tool()
async def get_asset_info(symbol: str) -> str:
    """Get detailed information about a specific asset."""
    return await asset_tools.get_asset_info(symbol)


# Corporate Actions Tools
@mcp.tool()
async def get_corporate_announcements(
    ca_types: list,
    since: str,
    until: str,
    symbol: str = None,
    cusip: str = None,
    date_type: str = None,
) -> str:
    """Get corporate action announcements for specified criteria."""
    return await corporate_action_tools.get_corporate_announcements(
        ca_types, since, until, symbol, cusip, date_type
    )


# Real-time Streaming Tools (Critical for Day Trading)
@mcp.tool()
async def start_global_stock_stream(
    symbols: list,
    data_types: list = ["trades", "quotes"],
    feed: str = "sip",
    duration_seconds: int = None,
    buffer_size_per_symbol: int = None,
    replace_existing: bool = False,
) -> str:
    """Start global real-time stock data stream for day trading."""
    return await streaming_tools.start_global_stock_stream(
        symbols,
        data_types,
        feed,
        duration_seconds,
        buffer_size_per_symbol,
        replace_existing,
    )


@mcp.tool()
async def stop_global_stock_stream() -> str:
    """Stop the global stock streaming session."""
    return await streaming_tools.stop_global_stock_stream()


@mcp.tool()
async def add_symbols_to_stock_stream(symbols: list, data_types: list = None) -> str:
    """Add symbols to existing stock stream."""
    return await streaming_tools.add_symbols_to_stock_stream(symbols, data_types)


@mcp.tool()
async def get_stock_stream_data(
    symbol: str, data_type: str, recent_seconds: int = None, limit: int = None
) -> str:
    """Get streaming data for analysis."""
    return await streaming_tools.get_stock_stream_data(
        symbol, data_type, recent_seconds, limit
    )


@mcp.tool()
async def list_active_stock_streams() -> str:
    """List all active streaming subscriptions."""
    return await streaming_tools.list_active_stock_streams()


@mcp.tool()
async def get_stock_stream_buffer_stats() -> str:
    """Get detailed streaming buffer statistics."""
    return await streaming_tools.get_stock_stream_buffer_stats()


@mcp.tool()
async def clear_stock_stream_buffers() -> str:
    """Clear streaming buffers to free memory."""
    return await streaming_tools.clear_stock_stream_buffers()


# Order Management Tools
@mcp.tool()
async def place_stock_order(
    symbol: str,
    side: str,
    quantity: float,
    order_type: str = "market",
    time_in_force: str = "day",
    limit_price: float = None,
    stop_price: float = None,
    trail_price: float = None,
    trail_percent: float = None,
    extended_hours: bool = False,
    client_order_id: str = None,
) -> str:
    """Place a stock order of any type."""
    return await order_tools.place_stock_order(
        symbol,
        side,
        quantity,
        order_type,
        time_in_force,
        limit_price,
        stop_price,
        trail_price,
        trail_percent,
        extended_hours,
        client_order_id,
    )


@mcp.tool()
async def get_orders(status: str = "all", limit: int = 10) -> str:
    """Get orders with specified status."""
    return await order_tools.get_orders(status, limit)


@mcp.tool()
async def cancel_order_by_id(order_id: str) -> str:
    """Cancel a specific order by ID."""
    return await order_tools.cancel_order_by_id(order_id)


@mcp.tool()
async def cancel_all_orders() -> str:
    """Cancel all open orders."""
    return await order_tools.cancel_all_orders()


@mcp.tool()
async def place_option_market_order(
    legs: list, order_class: str = None, quantity: int = 1
) -> str:
    """Place single or multi-leg options market order."""
    return await order_tools.place_option_market_order(legs, order_class, quantity)


# ============================================================================
# RESOURCES - Dynamic Trading Context
# ============================================================================


@mcp.resource("account://status")
async def get_account_status() -> dict:
    """Real-time account health and trading capacity."""
    return await account_resources.get_account_status()


@mcp.resource("positions://current")
async def get_current_positions() -> dict:
    """Live position data with P&L updates."""
    return await position_resources.get_current_positions()


@mcp.resource("market://conditions")
async def get_market_conditions() -> dict:
    """Current market status and conditions."""
    return await market_resources.get_market_conditions()


@mcp.resource("portfolio://performance")
async def get_portfolio_performance() -> dict:
    """Real-time portfolio performance metrics and P&L analysis."""
    return await portfolio_resources.get_portfolio_performance()


@mcp.resource("portfolio://allocation")
async def get_portfolio_allocation() -> dict:
    """Asset allocation breakdown with winners/losers analysis."""
    return await portfolio_resources.get_portfolio_allocation()


@mcp.resource("portfolio://risk")
async def get_portfolio_risk() -> dict:
    """Portfolio risk metrics and exposure analysis."""
    return await portfolio_resources.get_portfolio_risk()


@mcp.resource("streams://status")
async def get_stream_status() -> dict:
    """Real-time streaming status and buffer statistics."""
    return await streaming_resources.get_stream_status()


@mcp.resource("streams://performance")
async def get_stream_performance() -> dict:
    """Streaming performance metrics and health indicators."""
    return await streaming_resources.get_stream_performance()


@mcp.resource("market://momentum")
async def get_market_momentum_resource() -> dict:
    """Real-time market momentum for SPY with default parameters."""
    return await market_momentum.get_market_momentum()


@mcp.resource("positions://intraday_pnl")
async def get_intraday_pnl_resource() -> dict:
    """Track today's intraday P&L with default parameters."""
    return await intraday_pnl.get_intraday_pnl()


@mcp.resource("data://quality")
async def get_data_quality_resource() -> dict:
    """Monitor data feed quality with default parameters."""
    return await data_quality.get_data_quality()


@mcp.resource("server://health")
async def get_server_health_resource() -> dict:
    """Comprehensive server health monitoring."""
    return await server_health.get_server_health()


@mcp.resource("server://session")
async def get_session_status_resource() -> dict:
    """Trading session and market status."""
    return await session_status.get_session_status()


@mcp.resource("server://apis")
async def get_api_status_resource() -> dict:
    """Monitor API connections and performance."""
    return await api_monitor.get_api_status()


# ============================================================================
# RESOURCE MIRROR TOOLS - For Claude Code Compatibility
# ============================================================================


@mcp.tool()
async def resource_account_status() -> dict:
    """Tool mirror of account://status resource."""
    return await account_resources.get_account_status()


@mcp.tool()
async def resource_current_positions() -> dict:
    """Tool mirror of positions://current resource."""
    return await position_resources.get_current_positions()


@mcp.tool()
async def resource_market_conditions() -> dict:
    """Tool mirror of market://conditions resource."""
    return await market_resources.get_market_conditions()


@mcp.tool()
async def resource_market_momentum(
    symbol: str = "SPY",
    timeframe_minutes: int = 1,
    analysis_hours: int = 2,
    sma_short: int = 5,
    sma_long: int = 20,
) -> dict:
    """Tool mirror of market://momentum resource."""
    return await market_momentum.get_market_momentum(
        symbol=symbol,
        timeframe_minutes=timeframe_minutes,
        analysis_hours=analysis_hours,
        sma_short=sma_short,
        sma_long=sma_long,
    )


@mcp.tool()
async def resource_intraday_pnl(
    days_back: int = 0,
    include_open_positions: bool = True,
    min_trade_value: float = 0.0,
    symbol_filter: str = None,
) -> dict:
    """Tool mirror of positions://intraday_pnl resource."""
    return await intraday_pnl.get_intraday_pnl(
        days_back=days_back,
        include_open_positions=include_open_positions,
        min_trade_value=min_trade_value,
        symbol_filter=symbol_filter,
    )


@mcp.tool()
async def resource_data_quality(
    test_symbols: list = None,
    latency_threshold_ms: float = 500.0,
    quote_age_threshold_seconds: float = 60.0,
    spread_threshold_pct: float = 1.0,
) -> dict:
    """Tool mirror of data://quality resource."""
    return await data_quality.get_data_quality(
        test_symbols=test_symbols,
        latency_threshold_ms=latency_threshold_ms,
        quote_age_threshold_seconds=quote_age_threshold_seconds,
        spread_threshold_pct=spread_threshold_pct,
    )


@mcp.tool()
async def resource_server_health() -> dict:
    """Tool mirror of server://health resource."""
    return await server_health.get_server_health()


@mcp.tool()
async def resource_session_status() -> dict:
    """Tool mirror of server://session resource."""
    return await session_status.get_session_status()


@mcp.tool()
async def resource_api_status() -> dict:
    """Tool mirror of server://apis resource."""
    return await api_monitor.get_api_status()


@mcp.tool()
async def health_check() -> str:
    """Quick server health and status check."""
    try:
        health = await server_health.get_server_health()
        session = await session_status.get_session_status()

        status_emoji = (
            "🟢"
            if health.get("server_status") == "healthy"
            else "🟡" if health.get("server_status") == "degraded" else "🔴"
        )
        market_emoji = "🔔" if session.get("alpaca_market_open") else "🔕"

        return f"""
{status_emoji} Server Status: {health.get("server_status", "unknown").upper()}
{market_emoji} Market: {session.get("session_description", "unknown")}

Quick Stats:
• Memory: {health.get("process_metrics", {}).get("memory_usage_mb", 0):.1f} MB
• CPU: {health.get("process_metrics", {}).get("cpu_usage_percent", 0):.1f}%
• Uptime: {health.get("uptime_formatted", "unknown")}
• APIs: {health.get("connection_health", {}).get("healthy_connections", 0)}/{health.get("connection_health", {}).get("total_connections", 0)}

Market Session:
• Phase: {session.get("session_phase", "unknown")}
• Extended Hours: {session.get("is_extended_hours", False)}
• Next: {session.get("next_event", "unknown")} in {session.get("time_to_next_formatted", "unknown")}

Capabilities: {health.get("capabilities", {}).get("tools", 0)} tools, {health.get("capabilities", {}).get("resources", 0)} resources
        """

    except Exception as e:
        return f"❌ Health check failed: {str(e)}"


@mcp.tool()
async def get_extended_market_clock() -> str:
    """Enhanced market clock with pre/post market sessions."""
    from .tools.enhanced_market_clock import get_extended_market_clock

    return await get_extended_market_clock()


@mcp.tool()
async def validate_extended_hours_order(
    symbol: str, order_type: str, extended_hours: bool = None
) -> dict:
    """Validate if order can be placed in current market session."""
    from .tools.extended_hours_orders import validate_extended_hours_order

    return await validate_extended_hours_order(symbol, order_type, extended_hours)


@mcp.tool()
async def place_extended_hours_order(
    symbol: str,
    side: str,
    quantity: float,
    order_type: str = "limit",
    limit_price: float = None,
    extended_hours: bool = None,
    time_in_force: str = "day",
) -> str:
    """Place order with automatic extended hours detection."""
    from .tools.extended_hours_orders import place_extended_hours_order

    return await place_extended_hours_order(
        symbol, side, quantity, order_type, limit_price, extended_hours, time_in_force
    )


@mcp.tool()
async def get_extended_hours_info() -> str:
    """Get comprehensive information about extended hours trading."""
    from .tools.extended_hours_orders import get_extended_hours_info

    return await get_extended_hours_info()


# ============================================================================
# SERVER INITIALIZATION
# ============================================================================


def get_server():
    """Get the MCP server instance."""
    return mcp


if __name__ == "__main__":
    mcp.run()

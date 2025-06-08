"""Master trading capabilities discovery prompt."""


async def list_trading_capabilities() -> str:
    """List all Alpaca trading capabilities with guided workflows."""

    return """# 🚀 Alpaca Trading Assistant Capabilities

## 📝 Prompts (Guided Trading Workflows)
Interactive conversation starters and trading guides:

• **account_analysis** () - Complete portfolio health check with risk assessment
• **position_management** (symbol=None) - Strategic position review and optimization
• **market_analysis** (symbols=None, timeframe="1Day") - Real-time market insights and opportunities

## 🔧 Tools (Individual Trading Actions)
Direct access to all trading functionality:

### Account & Position Management
• **get_account_info** () - View balance, buying power, and account status
• **get_positions** () - List all open positions with P&L
• **get_open_position** (symbol) - Detailed position info for specific symbol
• **close_position** (symbol, qty, percentage) - Close specific position
• **close_all_positions** (cancel_orders) - Liquidate entire portfolio

### Market Data & Analysis
• **get_stock_quote** (symbol) - Real-time bid/ask quotes
• **get_stock_snapshots** (symbols) - Comprehensive market data with analysis
• **get_stock_bars** (symbol, days) - Historical OHLCV data
• **get_stock_bars_intraday** (symbol, timeframe, start_date, end_date) - Professional intraday analysis
• **get_stock_latest_trade** (symbol) - Most recent trade execution
• **get_stock_latest_bar** (symbol) - Latest minute bar data

### Order Management
• **place_stock_order** (symbol, side, quantity, order_type, limit_price, stop_price) - Execute any order type
• **get_orders** (status, limit) - View order history and status
• **cancel_order_by_id** (order_id) - Cancel specific order
• **cancel_all_orders** () - Cancel all pending orders

### Options Trading
• **place_option_market_order** (legs, order_class, quantity) - Execute single or multi-leg strategies

---

**🎯 Quick Start Guide:**
1. New to trading? Start with `account_analysis()` for portfolio overview
2. Planning trades? Use `market_analysis(["AAPL"])` for opportunities
3. Managing risk? Run `account_analysis()` for portfolio assessment

**💡 Pro Tips:**
• Prompts provide guided workflows with built-in risk management
• Tools offer direct access for experienced traders
• All functions work in both paper and live trading modes

**⚠️ Risk Notice:**
This assistant can place real trades. Always review recommendations carefully,
especially for options strategies and position sizing decisions.
"""

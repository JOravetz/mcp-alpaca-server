# 🚀 Professional Alpaca MCP Server

A sophisticated **Model Context Protocol (MCP) server** that transforms Alpaca's Trading API into an intelligent trading assistant for LLMs. Built with advanced prompt engineering, modular architecture, and institutional-grade market analysis capabilities.

## 🌟 Why This MCP Server is Superior

### 🧠 **Advanced Prompt Engineering**
- **Intelligent Trading Prompts**: Pre-built analysis functions that combine multiple data sources
- **Contextual Insights**: Prompts automatically interpret market conditions and provide actionable recommendations
- **Professional Analysis**: Institutional-quality portfolio reviews, risk assessments, and position management

### 🏗️ **Enterprise Architecture**
```
alpaca_mcp_server/
├── prompts/           # Intelligent analysis prompts
├── tools/            # 40+ specialized trading tools
├── resources/        # Real-time market analysis engines
├── config/           # Flexible client management
└── models/           # Type-safe data structures
```

### 📊 **Institutional-Grade Analysis**
- **Market Momentum Detection**: Real-time SPY analysis with configurable indicators
- **Data Quality Monitoring**: Latency, spread, and feed quality metrics
- **Intraday P&L Tracking**: Professional performance analytics
- **Streaming Infrastructure**: High-frequency data processing for active trading

---

## 🎯 Core Capabilities

### 📈 **Market Data & Analysis**
- **Enhanced Intraday Bars**: 10,000-bar historical data with 1-minute granularity
- **Real-time Streaming**: Professional-grade data feeds for active trading
- **Market Momentum**: Configurable technical analysis with SMA crossovers
- **Data Quality Monitoring**: Latency and spread analysis for optimal execution

### 💼 **Portfolio Management**
- **Intelligent Position Analysis**: Automated performance categorization and recommendations
- **Risk Assessment**: Multi-factor risk scoring and concentration analysis
- **Account Health Monitoring**: Comprehensive portfolio health checks
- **Professional Reporting**: Institutional-style analysis and insights

### 🎛️ **Advanced Trading Tools**
- **Multi-Asset Support**: Stocks, options, ETFs with unified interface
- **Order Management**: All order types including multi-leg options strategies
- **Extended Hours Trading**: Pre-market and after-hours order validation
- **Watchlist Intelligence**: Dynamic portfolio tracking and management

---

## 🚀 Quick Start

### 1. **Installation**

```bash
# Clone the repository
git clone <your-repo-url>
cd alpaca-mcp-server

# Install dependencies with UV (recommended)
uv sync

# Or use pip
pip install -r requirements.txt
```

### 2. **Security Setup**

```bash
# Copy environment template
cp .env.example .env

# Edit with your Alpaca credentials
nano .env
```

```env
# Your Alpaca API credentials
APCA_API_KEY_ID="your_alpaca_api_key"
APCA_API_SECRET_KEY="your_alpaca_secret_key"
PAPER="true"  # Use paper trading for safety
```

### 3. **MCP Configuration**

```bash
# Copy MCP template
cp .mcp.json.example .mcp.json

# The server automatically reads from .env
```

### 4. **Start Trading**

```bash
# Test the server
python run_alpaca_mcp.py

# Or use the MCP client integration
```

---

## 💡 Usage Examples

### 🔍 **Intelligent Market Analysis**

The MCP server provides sophisticated analysis prompts that combine multiple data sources:

```python
# Get comprehensive portfolio health check
result = await account_analysis()
```

**What you get:**
- Portfolio value and cash allocation analysis
- Risk level assessment with specific factors
- Concentration risk warnings
- Strategic recommendations for rebalancing
- Next steps for optimization

### 📊 **Advanced Position Management**

```python
# Analyze specific position with intelligent insights
result = await position_management("AAPL")
```

**Professional analysis includes:**
- Performance categorization (Strong Winner, Underperforming, etc.)
- Specific action recommendations
- Risk-adjusted position sizing guidance
- Exit strategy suggestions based on market conditions

### 🎯 **Market Momentum Detection**

```python
# Real-time market momentum analysis
result = await get_market_momentum(
    symbol="SPY",
    timeframe_minutes=1,
    analysis_hours=2,
    sma_short=5,
    sma_long=20
)
```

**Advanced metrics:**
- Dynamic SMA calculations with trend direction
- Momentum strength scoring (0-10 scale)
- Volume confirmation analysis
- Price volatility assessment
- Short-term momentum indicators

### 🚀 **Enhanced Intraday Analysis**

```python
# Get detailed intraday analysis with 10,000 bars
result = await get_stock_bars_intraday(
    symbol="NVDA",
    timeframe="1Min",
    limit=10000  # Industry-leading data depth
)
```

**Professional insights:**
- Volume surge detection (36x normal patterns)
- Block trade identification (>10K shares)
- Institutional vs retail activity analysis
- Liquidity assessment via bid-ask spreads
- Price action momentum classification

### 📡 **Real-time Streaming Analysis**

```python
# Start professional streaming for active trading
result = await start_global_stock_stream(
    symbols=["AAPL", "NVDA", "TSLA"],
    data_types=["trades", "quotes", "bars"],
    feed="sip",  # All exchanges
    buffer_size_per_symbol=None  # Unlimited for active stocks
)
```

**Advanced streaming features:**
- Configurable buffer management
- Multi-symbol concurrent streaming
- Real-time trade and quote analysis
- Professional-grade data quality monitoring

---

## 🏗️ Architecture Deep Dive

### 🧠 **Prompt Engineering System**

Our prompts go far beyond simple API calls - they provide **intelligent analysis**:

```python
# Example: Position Management Prompt
async def position_management(symbol: Optional[str] = None) -> str:
    """Strategic position review with actionable guidance"""
    
    # Combines multiple data sources
    position_data = get_position(symbol)
    market_data = get_snapshot(symbol)
    account_info = get_account()
    
    # Intelligent analysis
    if unrealized_pnl_pct > 20:
        return "Strong Winner - Consider profit-taking strategies..."
    elif unrealized_pnl_pct < -15:
        return "Significant Loss - Urgent review recommended..."
```

### 🛠️ **Tool Architecture**

**40+ Specialized Tools** organized by function:

```
tools/
├── account/          # Account and portfolio tools
├── market_data/      # Advanced market data tools
├── orders/           # Professional order management
├── streaming/        # Real-time data processing
└── watchlist/        # Portfolio tracking tools
```

### 📊 **Resource System**

**Real-time Analysis Engines** for institutional-grade insights:

```
resources/
├── market_momentum.py    # Technical analysis engine
├── data_quality.py      # Feed quality monitoring
├── intraday_pnl.py      # Performance tracking
└── streaming_resources.py # Real-time data management
```

---

## 🎛️ Configuration Options

### 📈 **Market Data Configuration**

```python
# Configurable analysis parameters
market_momentum_config = {
    "timeframe_minutes": 1,     # 1, 5, 15, 30, 60
    "analysis_hours": 2,        # Historical depth
    "sma_short": 5,            # Short-term MA
    "sma_long": 20,            # Long-term MA
}

# Data quality thresholds
data_quality_config = {
    "latency_threshold_ms": 500.0,
    "quote_age_threshold_seconds": 60.0,
    "spread_threshold_pct": 1.0,
}
```

### 🚀 **Streaming Configuration**

```python
# Professional streaming setup
streaming_config = {
    "feed": "sip",              # All exchanges vs "iex"
    "buffer_size": None,        # Unlimited for active stocks
    "data_types": ["trades", "quotes", "bars"],
    "duration_seconds": None,   # Run indefinitely
}
```

---

## 🔧 Integration Examples

### 📱 **Claude Desktop Integration**

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "alpaca": {
      "type": "stdio",
      "command": "bash",
      "args": ["-c", "source .venv/bin/activate && python run_alpaca_mcp.py"],
      "cwd": "/path/to/alpaca-mcp-server"
    }
  }
}
```

### 💬 **Natural Language Trading**

With Claude Desktop, you can now:

```
"Analyze my portfolio and give me a comprehensive health check"
→ Triggers account_analysis() prompt with professional insights

"Check the market momentum for SPY over the last 2 hours"
→ Executes market_momentum analysis with technical indicators

"Start streaming NVDA and TSLA for real-time analysis"
→ Initiates professional streaming with optimal configuration

"What's the intraday action on AAPL with volume analysis?"
→ Gets 10,000 1-minute bars with institutional-grade analysis
```

---

## 🔒 Security & Best Practices

### ⚠️ **Critical Security**
- **Never commit API keys** - Use environment variables only
- **Paper trading first** - Always test with `PAPER="true"`
- **Regular key rotation** - Update credentials periodically
- **See SECURITY.md** for comprehensive guidelines

### 🎯 **Trading Best Practices**
- **Start with small positions** when testing live trading
- **Use position limits** to manage risk exposure
- **Monitor data quality** before making trading decisions
- **Review prompts and analysis** before taking action

---

## 📚 Advanced Features

### 🧮 **Institutional Analysis Tools**

Coming soon (stored as todo features):
- **Volcanic Accumulation Detector**: Identify institutional buying patterns
- **Pre-Breakout Scanner**: Detect acceleration in trade frequency
- **Microstructure Analysis**: Raw data access for velocity calculations
- **Block Trade Detection**: Identify large institutional orders

### 📊 **Professional Reporting**

The server provides institutional-quality analysis:
- Multi-factor risk assessment
- Performance attribution analysis
- Concentration risk monitoring
- Cash allocation optimization
- Strategic rebalancing recommendations

---

## 🤝 Contributing

This MCP server represents a new standard for trading AI integration. Contributions welcome:

1. **Prompt Engineering**: Enhance analysis capabilities
2. **Tool Development**: Add specialized trading functions
3. **Resource Building**: Create new analysis engines
4. **Documentation**: Improve examples and guides

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🚀 Get Started Now

1. **Clone the repository**
2. **Follow the security setup** in SECURITY.md
3. **Configure your environment** with .env
4. **Start with paper trading**
5. **Experience professional-grade trading AI**

Transform your trading workflow with intelligent analysis, institutional-grade tools, and advanced prompt engineering. This isn't just an API wrapper - it's a comprehensive trading intelligence platform.
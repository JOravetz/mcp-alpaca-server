"""Market analysis prompt implementation."""

from typing import Optional, List
from datetime import datetime


async def market_analysis(
    symbols: Optional[List[str]] = None,
    timeframe: str = "1Day",
    analysis_type: str = "comprehensive",
) -> str:
    """Real-time market analysis with trading opportunities and risk assessment."""

    try:
        # Default symbols if none provided
        if symbols is None:
            symbols = ["SPY", "QQQ", "IWM", "AAPL", "MSFT", "NVDA"]

        # Generate market analysis
        result = f"""# Market Analysis Report
        
## Market Overview
Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Timeframe: {timeframe}
Symbols Analyzed: {', '.join(symbols)}

## Market Assessment

For comprehensive market analysis, use individual tools:
"""

        for symbol in symbols:
            result += f"""
### {symbol}
• Use get_stock_snapshots('{symbol}') for current data
• Use get_stock_bars_intraday('{symbol}', '5Min') for detailed analysis
"""

        result += f"""
## Trading Opportunities

Based on market analysis, consider:
• Technology sector exposure through {symbols[3] if len(symbols) > 3 else 'AAPL'}
• Broad market exposure through {symbols[0] if len(symbols) > 0 else 'SPY'}
• Growth vs value assessment via QQQ vs SPY performance

## Strategic Recommendations

Immediate Actions:
1. Review opportunities identified above
2. Use account_analysis() for portfolio assessment
3. Follow risk management best practices

Market Timing Considerations:
• Bull Market: Strong momentum, sector rotation
• Bear Market: Defensive positioning, volatility management
• Neutral Market: Range-bound, await directional signals

## Risk Assessment

Market Risk Factors:
• Monitor VIX levels for volatility
• Check sector concentration
• Consider correlation between holdings

## Advanced Analysis Options

Deep Dive Analysis:
• get_stock_bars_intraday('SYMBOL', '5Min') for detailed patterns
• market_analysis(['SECTOR_ETF1', 'SECTOR_ETF2']) for sector rotation

Risk Management:
• Use account_analysis() for portfolio assessment
• Monitor position sizes and diversification
• Consider hedging in uncertain markets

## Key Insights

Market Structure:
• Current phase: Monitor for trend changes
• Volatility: Check VIX and individual stock volatility
• Liquidity: Observe bid-ask spreads

Next Steps:
• Deep dive: get_stock_snapshots() for specific symbols
• Portfolio review: position_management() for holdings
• Risk check: account_analysis() for comprehensive view
"""

        return result

    except Exception as e:
        return f"""Error in market analysis: {str(e)}

Troubleshooting:
• Check market connectivity
• Verify symbols are valid
• Try get_stock_snapshots(['SPY', 'QQQ']) for basic data
"""

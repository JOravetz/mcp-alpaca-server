"""Market momentum resource with real SPY data analysis."""

from datetime import datetime, timedelta
from ..config.settings import get_stock_historical_client
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame


async def get_market_momentum(
    symbol: str = "SPY",
    timeframe_minutes: int = 1,
    analysis_hours: int = 2,
    sma_short: int = 5,
    sma_long: int = 20,
) -> dict:
    """Calculate real market momentum using configurable parameters.

    Args:
        symbol: Stock symbol to analyze (default: SPY)
        timeframe_minutes: Bar timeframe in minutes (default: 1)
        analysis_hours: Hours of data to analyze (default: 2)
        sma_short: Short moving average period (default: 5)
        sma_long: Long moving average period (default: 20)
    """
    try:
        data_client = get_stock_historical_client()

        # Get data for specified symbol and timeframe
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=analysis_hours)

        # Map minutes to TimeFrame
        if timeframe_minutes == 1:
            timeframe = TimeFrame.Minute
        elif timeframe_minutes == 5:
            timeframe = TimeFrame(5, "Minute")
        elif timeframe_minutes == 15:
            timeframe = TimeFrame(15, "Minute")
        elif timeframe_minutes == 30:
            timeframe = TimeFrame(30, "Minute")
        elif timeframe_minutes == 60:
            timeframe = TimeFrame.Hour
        else:
            timeframe = TimeFrame.Minute  # Default fallback

        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=timeframe,
            start=start_time,
            end=end_time,
        )

        bars = data_client.get_stock_bars(request)
        symbol_bars = list(bars[symbol]) if symbol in bars else []

        if len(symbol_bars) < max(sma_short, sma_long):
            return {
                "error": f"Insufficient {symbol} data for momentum calculation",
                "bars_received": len(symbol_bars),
                "required_bars": max(sma_short, sma_long),
                "symbol": symbol,
                "last_updated": datetime.now().isoformat(),
            }

        # Calculate momentum metrics using configurable parameters
        prices = [float(bar.close) for bar in symbol_bars]
        current_price = prices[-1]

        # Dynamic SMA calculations based on user parameters
        sma_short_value = (
            sum(prices[-sma_short:]) / sma_short
            if len(prices) >= sma_short
            else current_price
        )
        sma_long_value = (
            sum(prices[-sma_long:]) / sma_long
            if len(prices) >= sma_long
            else current_price
        )

        # Trend direction calculation using dynamic SMAs
        if current_price > sma_short_value > sma_long_value:
            direction = "bullish"
        elif current_price < sma_short_value < sma_long_value:
            direction = "bearish"
        else:
            direction = "neutral"

        # Momentum strength calculation (0-10 scale)
        price_change_pct = ((current_price - prices[0]) / prices[0]) * 100
        momentum_strength = min(10, abs(price_change_pct) * 2)

        # Volume analysis for confirmation
        volume_analysis_bars = min(10, len(symbol_bars))
        volumes = [bar.volume for bar in symbol_bars[-volume_analysis_bars:]]
        avg_volume = sum(volumes) / len(volumes)
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

        # Price volatility (standard deviation using configurable period)
        volatility_period = min(sma_long, len(prices))
        volatility_prices = prices[-volatility_period:]
        avg_price = sum(volatility_prices) / len(volatility_prices)
        variance = sum((p - avg_price) ** 2 for p in volatility_prices) / len(
            volatility_prices
        )
        volatility = variance**0.5
        volatility_pct = (volatility / avg_price) * 100

        # Recent price action (configurable short-term momentum)
        short_term_period = min(sma_short, len(prices) // 2)
        if len(prices) >= short_term_period * 2:
            recent_prices = prices[-short_term_period:]
            previous_prices = prices[-short_term_period * 2 : -short_term_period]

            recent_avg = sum(recent_prices) / len(recent_prices)
            previous_avg = sum(previous_prices) / len(previous_prices)

            short_term_momentum = (
                ((recent_avg - previous_avg) / previous_avg) * 100
                if previous_avg > 0
                else 0
            )
        else:
            short_term_momentum = 0

        return {
            "symbol": symbol,
            "direction": direction,
            "momentum_strength": round(momentum_strength, 1),
            "price_change_pct": round(price_change_pct, 2),
            "short_term_momentum_pct": round(short_term_momentum, 2),
            "current_price": round(current_price, 2),
            f"sma_{sma_short}": round(sma_short_value, 2),
            f"sma_{sma_long}": round(sma_long_value, 2),
            "volume_ratio": round(volume_ratio, 2),
            "volatility_pct": round(volatility_pct, 2),
            "bars_analyzed": len(symbol_bars),
            "timeframe_minutes": timeframe_minutes,
            "analysis_period_hours": analysis_hours,
            "last_bar_time": symbol_bars[-1].timestamp.isoformat(),
            "parameters": {
                "symbol": symbol,
                "timeframe_minutes": timeframe_minutes,
                "analysis_hours": analysis_hours,
                "sma_short": sma_short,
                "sma_long": sma_long,
            },
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "error": str(e),
            "symbol": symbol,
            "direction": "unknown",
            "momentum_strength": 0,
            "parameters": {
                "symbol": symbol,
                "timeframe_minutes": timeframe_minutes,
                "analysis_hours": analysis_hours,
                "sma_short": sma_short,
                "sma_long": sma_long,
            },
            "last_updated": datetime.now().isoformat(),
        }

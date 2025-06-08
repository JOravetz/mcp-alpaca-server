"""Market information and calendar tools."""

from ..config.settings import get_trading_client


async def get_market_clock() -> str:
    """
    Retrieves and formats current market status and next open/close times.

    Returns:
        str: Formatted string containing:
            - Current Time
            - Market Open Status
            - Next Open Time
            - Next Close Time
    """
    try:
        client = get_trading_client()
        clock = client.get_clock()
        return f"""
Market Status:
-------------
Current Time: {clock.timestamp}
Is Open: {'Yes' if clock.is_open else 'No'}
Next Open: {clock.next_open}
Next Close: {clock.next_close}
"""
    except Exception as e:
        return f"Error fetching market clock: {str(e)}"


async def get_market_calendar(start_date: str, end_date: str) -> str:
    """
    Retrieves and formats market calendar for specified date range.

    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format

    Returns:
        str: Formatted string containing market calendar information
    """
    try:
        client = get_trading_client()
        calendar = client.get_calendar(start=start_date, end=end_date)
        result = f"Market Calendar ({start_date} to {end_date}):\n----------------------------\n"
        for day in calendar:
            result += f"Date: {day.date}, Open: {day.open}, Close: {day.close}\n"
        return result
    except Exception as e:
        return f"Error fetching market calendar: {str(e)}"

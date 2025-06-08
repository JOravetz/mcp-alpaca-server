"""Corporate actions and announcements tools."""

from typing import List, Optional
from datetime import date
from alpaca.trading.requests import GetCorporateAnnouncementsRequest
from alpaca.trading.enums import CorporateActionType, CorporateActionDateType
from ...config.settings import get_trading_client


async def get_corporate_announcements(
    ca_types: List[str],
    since: str,
    until: str,
    symbol: Optional[str] = None,
    cusip: Optional[str] = None,
    date_type: Optional[str] = None,
) -> str:
    """
    Retrieves and formats corporate action announcements.

    Args:
        ca_types (List[str]): List of corporate action types to filter by
        since (str): Start date for the announcements (YYYY-MM-DD)
        until (str): End date for the announcements (YYYY-MM-DD)
        symbol (Optional[str]): Optional stock symbol to filter by
        cusip (Optional[str]): Optional CUSIP to filter by
        date_type (Optional[str]): Optional date type to filter by

    Returns:
        str: Formatted string containing corporate announcement details
    """
    try:
        client = get_trading_client()

        # Convert string dates to date objects
        since_date = date.fromisoformat(since)
        until_date = date.fromisoformat(until)

        # Convert string types to enums
        ca_type_enums = []
        for ca_type in ca_types:
            try:
                ca_type_enums.append(CorporateActionType(ca_type))
            except ValueError:
                return f"Invalid corporate action type: {ca_type}"

        date_type_enum = None
        if date_type:
            try:
                date_type_enum = CorporateActionDateType(date_type)
            except ValueError:
                return f"Invalid date type: {date_type}"

        request = GetCorporateAnnouncementsRequest(
            ca_types=ca_type_enums,
            since=since_date,
            until=until_date,
            symbol=symbol,
            cusip=cusip,
            date_type=date_type_enum,
        )

        announcements = client.get_corporate_announcements(request)

        if not announcements:
            return "No corporate announcements found for the specified criteria."

        result = "Corporate Announcements:\n----------------------\n"
        for ann in announcements:
            result += f"""
ID: {ann.id}
Corporate Action ID: {ann.corporate_action_id}
Type: {ann.ca_type}
Sub Type: {ann.ca_sub_type}
Initiating Symbol: {ann.initiating_symbol}
Target Symbol: {ann.target_symbol}
Declaration Date: {ann.declaration_date}
Ex Date: {ann.ex_date}
Record Date: {ann.record_date}
Payable Date: {ann.payable_date}
Cash: {ann.cash}
Old Rate: {ann.old_rate}
New Rate: {ann.new_rate}
----------------------
"""
        return result

    except Exception as e:
        return f"Error fetching corporate announcements: {str(e)}"

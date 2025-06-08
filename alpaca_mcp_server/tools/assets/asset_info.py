"""Asset information and search tools."""

from typing import Optional
from alpaca.trading.requests import GetAssetsRequest
from ...config.settings import get_trading_client


async def get_all_assets(
    status: Optional[str] = None,
    asset_class: Optional[str] = None,
    exchange: Optional[str] = None,
    attributes: Optional[str] = None,
) -> str:
    """
    Get all available assets with optional filtering.

    Args:
        status: Filter by asset status (e.g., 'active', 'inactive')
        asset_class: Filter by asset class (e.g., 'us_equity', 'crypto')
        exchange: Filter by exchange (e.g., 'NYSE', 'NASDAQ')
        attributes: Comma-separated values to query for multiple attributes
    """
    try:
        client = get_trading_client()

        # Create filter if any parameters are provided
        filter_params = None
        if any([status, asset_class, exchange, attributes]):
            filter_params = GetAssetsRequest(
                status=status,
                asset_class=asset_class,
                exchange=exchange,
                attributes=attributes,
            )

        # Get all assets
        assets = client.get_all_assets(filter_params)

        if not assets:
            return "No assets found matching the criteria."

        # Format the response
        response_parts = ["Available Assets:"]
        response_parts.append("-" * 30)

        for asset in assets[:50]:  # Limit to first 50 for readability
            response_parts.append(f"Symbol: {asset.symbol}")
            response_parts.append(f"Name: {asset.name}")
            response_parts.append(f"Exchange: {asset.exchange}")
            response_parts.append(f"Class: {asset.asset_class}")
            response_parts.append(f"Status: {asset.status}")
            response_parts.append(f"Tradable: {'Yes' if asset.tradable else 'No'}")
            response_parts.append("-" * 30)

        if len(assets) > 50:
            response_parts.append(f"... and {len(assets) - 50} more assets")

        return "\n".join(response_parts)

    except Exception as e:
        return f"Error fetching assets: {str(e)}"


async def get_asset_info(symbol: str) -> str:
    """
    Retrieves and formats detailed information about a specific asset.

    Args:
        symbol (str): The symbol of the asset to get information for

    Returns:
        str: Formatted string containing asset details
    """
    try:
        client = get_trading_client()
        asset = client.get_asset(symbol)
        return f"""
Asset Information for {symbol}:
----------------------------
Name: {asset.name}
Exchange: {asset.exchange}
Class: {asset.asset_class}
Status: {asset.status}
Tradable: {'Yes' if asset.tradable else 'No'}
Marginable: {'Yes' if asset.marginable else 'No'}
Shortable: {'Yes' if asset.shortable else 'No'}
Easy to Borrow: {'Yes' if asset.easy_to_borrow else 'No'}
Fractionable: {'Yes' if asset.fractionable else 'No'}
"""
    except Exception as e:
        return f"Error fetching asset info for {symbol}: {str(e)}"

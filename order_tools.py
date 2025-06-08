"""
Order Management Tools for Alpaca MCP Server

This module contains all order-related functions extracted from the main server:
- get_orders: Retrieve orders with filtering
- place_stock_order: Place stock orders with all order types
- cancel_all_orders: Cancel all open orders
- cancel_order_by_id: Cancel specific orders
- place_option_market_order: Place option orders (single and multi-leg)
"""

import os
import time
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    GetOrdersRequest, MarketOrderRequest, LimitOrderRequest, 
    ClosePositionRequest, OptionLegRequest, StopOrderRequest, 
    StopLimitOrderRequest, TrailingStopOrderRequest
)
from alpaca.trading.enums import (
    OrderSide, TimeInForce, QueryOrderStatus, OrderType, OrderClass
)
from alpaca.common.exceptions import APIError

# Initialize environment
load_dotenv()

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
PAPER = os.getenv("PAPER", "true").lower() in ["true", "1", "yes"]

# Check if keys are available
if not API_KEY or not API_SECRET:
    raise ValueError("Alpaca API credentials not found in environment variables.")

# Initialize trading client
trade_client = TradingClient(API_KEY, API_SECRET, paper=PAPER)

# Initialize FastMCP server
mcp = FastMCP("alpaca-order-tools")

@mcp.tool()
async def get_orders(status: str = "all", limit: int = 10) -> str:
    """
    Retrieves and formats orders with the specified status.
    
    Args:
        status (str): Order status to filter by (open, closed, all)
        limit (int): Maximum number of orders to return (default: 10)
    
    Returns:
        str: Formatted string containing order details including:
            - Symbol
            - ID
            - Type
            - Side
            - Quantity
            - Status
            - Submission Time
            - Fill Details (if applicable)
    """
    try:
        # Convert status string to enum
        if status.lower() == "open":
            query_status = QueryOrderStatus.OPEN
        elif status.lower() == "closed":
            query_status = QueryOrderStatus.CLOSED
        else:
            query_status = QueryOrderStatus.ALL
            
        request_params = GetOrdersRequest(
            status=query_status,
            limit=limit
        )
        
        orders = trade_client.get_orders(request_params)
        
        if not orders:
            return f"No {status} orders found."
        
        result = f"{status.capitalize()} Orders (Last {len(orders)}):\n"
        result += "-----------------------------------\n"
        
        for order in orders:
            result += f"""
Symbol: {order.symbol}
ID: {order.id}
Type: {order.type}
Side: {order.side}
Quantity: {order.qty}
Status: {order.status}
Submitted At: {order.submitted_at}
"""
            if hasattr(order, 'filled_at') and order.filled_at:
                result += f"Filled At: {order.filled_at}\n"
                
            if hasattr(order, 'filled_avg_price') and order.filled_avg_price:
                result += f"Filled Price: ${float(order.filled_avg_price):.2f}\n"
                
            result += "-----------------------------------\n"
            
        return result
    except Exception as e:
        return f"Error fetching orders: {str(e)}"

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
    client_order_id: str = None
) -> str:
    """
    Places an order of any supported type (MARKET, LIMIT, STOP, STOP_LIMIT, TRAILING_STOP) using the correct Alpaca request class.

    Args:
        symbol (str): Stock ticker symbol (e.g., AAPL, MSFT)
        side (str): Order side (buy or sell)
        quantity (float): Number of shares to buy or sell
        order_type (str): Order type (MARKET, LIMIT, STOP, STOP_LIMIT, TRAILING_STOP). Default is MARKET.
        time_in_force (str): Time in force for the order (default: DAY)
        limit_price (float): Limit price (required for LIMIT, STOP_LIMIT)
        stop_price (float): Stop price (required for STOP, STOP_LIMIT)
        trail_price (float): Trail price (for TRAILING_STOP)
        trail_percent (float): Trail percent (for TRAILING_STOP)
        extended_hours (bool): Allow execution during extended hours (default: False)
        client_order_id (str): Optional custom identifier for the order

    Returns:
        str: Formatted string containing order details or error message.
    """
    try:
        # Validate side
        if side.lower() == "buy":
            order_side = OrderSide.BUY
        elif side.lower() == "sell":
            order_side = OrderSide.SELL
        else:
            return f"Invalid order side: {side}. Must be 'buy' or 'sell'."

        # Validate time_in_force
        try:
            tif_enum = TimeInForce[time_in_force.upper()]
        except KeyError:
            return f"Invalid time_in_force: {time_in_force}."

        # Validate order_type
        order_type_upper = order_type.upper()
        if order_type_upper == "MARKET":
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                type=OrderType.MARKET,
                time_in_force=tif_enum,
                extended_hours=extended_hours,
                client_order_id=client_order_id or f"order_{int(time.time())}"
            )
        elif order_type_upper == "LIMIT":
            if limit_price is None:
                return "limit_price is required for LIMIT orders."
            order_data = LimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                type=OrderType.LIMIT,
                time_in_force=tif_enum,
                limit_price=limit_price,
                extended_hours=extended_hours,
                client_order_id=client_order_id or f"order_{int(time.time())}"
            )
        elif order_type_upper == "STOP":
            if stop_price is None:
                return "stop_price is required for STOP orders."
            order_data = StopOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                type=OrderType.STOP,
                time_in_force=tif_enum,
                stop_price=stop_price,
                extended_hours=extended_hours,
                client_order_id=client_order_id or f"order_{int(time.time())}"
            )
        elif order_type_upper == "STOP_LIMIT":
            if stop_price is None or limit_price is None:
                return "Both stop_price and limit_price are required for STOP_LIMIT orders."
            order_data = StopLimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                type=OrderType.STOP_LIMIT,
                time_in_force=tif_enum,
                stop_price=stop_price,
                limit_price=limit_price,
                extended_hours=extended_hours,
                client_order_id=client_order_id or f"order_{int(time.time())}"
            )
        elif order_type_upper == "TRAILING_STOP":
            if trail_price is None and trail_percent is None:
                return "Either trail_price or trail_percent is required for TRAILING_STOP orders."
            order_data = TrailingStopOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                type=OrderType.TRAILING_STOP,
                time_in_force=tif_enum,
                trail_price=trail_price,
                trail_percent=trail_percent,
                extended_hours=extended_hours,
                client_order_id=client_order_id or f"order_{int(time.time())}"
            )
        else:
            return f"Invalid order type: {order_type}. Must be one of: MARKET, LIMIT, STOP, STOP_LIMIT, TRAILING_STOP."

        # Submit order
        order = trade_client.submit_order(order_data)
        return f"""
Order Placed Successfully:
-------------------------
Order ID: {order.id}
Symbol: {order.symbol}
Side: {order.side}
Quantity: {order.qty}
Type: {order.type}
Time In Force: {order.time_in_force}
Status: {order.status}
Client Order ID: {order.client_order_id}
"""
    except Exception as e:
        return f"Error placing order: {str(e)}"

@mcp.tool()
async def cancel_all_orders() -> str:
    """
    Cancel all open orders.
    
    Returns:
        A formatted string containing the status of each cancelled order.
    """
    try:
        # Cancel all orders
        cancel_responses = trade_client.cancel_orders()
        
        if not cancel_responses:
            return "No orders were found to cancel."
        
        # Format the response
        response_parts = ["Order Cancellation Results:"]
        response_parts.append("-" * 30)
        
        for response in cancel_responses:
            status = "Success" if response.status == 200 else "Failed"
            response_parts.append(f"Order ID: {response.id}")
            response_parts.append(f"Status: {status}")
            if response.body:
                response_parts.append(f"Details: {response.body}")
            response_parts.append("-" * 30)
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"Error cancelling orders: {str(e)}"

@mcp.tool()
async def cancel_order_by_id(order_id: str) -> str:
    """
    Cancel a specific order by its ID.
    
    Args:
        order_id: The UUID of the order to cancel
        
    Returns:
        A formatted string containing the status of the cancelled order.
    """
    try:
        # Cancel the specific order
        response = trade_client.cancel_order_by_id(order_id)
        
        # Format the response
        status = "Success" if response.status == 200 else "Failed"
        result = f"""
Order Cancellation Result:
------------------------
Order ID: {response.id}
Status: {status}
"""
        
        if response.body:
            result += f"Details: {response.body}\n"
            
        return result
        
    except Exception as e:
        return f"Error cancelling order {order_id}: {str(e)}"

@mcp.tool()
async def place_option_market_order(
    legs: List[Dict[str, Any]],
    order_class: Optional[Union[str, OrderClass]] = None,
    quantity: int = 1,
    time_in_force: TimeInForce = TimeInForce.DAY,
    extended_hours: bool = False
) -> str:
    """
    Places a market order for options (single or multi-leg) and returns the order details.
    Supports up to 4 legs for multi-leg orders.
    
    Args:
        legs (List[Dict[str, Any]]): List of option legs, where each leg is a dictionary containing:
            - symbol (str): Option contract symbol (e.g., 'AAPL230616C00150000')
            - side (str): 'buy' or 'sell'
            - ratio_qty (int): Quantity ratio for the leg (1-4)
        order_class (Optional[Union[str, OrderClass]]): Order class ('simple', 'bracket', 'oco', 'oto', 'mleg' or OrderClass enum)
            Defaults to 'simple' for single leg, 'mleg' for multi-leg
        quantity (int): Base quantity for the order (default: 1)
        time_in_force (TimeInForce): Time in force for the order (default: DAY)
        extended_hours (bool): Whether to allow execution during extended hours (default: False)
    
    Returns:
        str: Formatted string containing order details including:
            - Order ID and Client Order ID
            - Order Class and Type
            - Time in Force and Status
            - Quantity
            - Leg Details (for multi-leg orders):
                * Symbol and Side
                * Ratio Quantity
                * Status
                * Asset Class
                * Created/Updated Timestamps
                * Filled Price (if filled)
                * Filled Time (if filled)
    
    Note:
        Some option strategies may require specific account permissions:
        - Level 1: Covered calls, Covered puts, Cash-Secured put, etc.
        - Level 2: Long calls, Long puts, cash-secured puts, etc.
        - Level 3: Spreads and combinations: Butterfly Spreads, Straddles, Strangles, Calendar Spreads (except for short call calendar spread, short strangles, short straddles)
        - Level 4: Uncovered options (naked calls/puts), Short Strangles, Short Straddles, Short Call Calendar Spread, etc.
        If you receive a permission error, please check your account's option trading level.
    """
    try:
        # Validate legs
        if not legs:
            return "Error: No option legs provided"
        if len(legs) > 4:
            return "Error: Maximum of 4 legs allowed for option orders"
        
        # Validate quantity
        if quantity <= 0:
            return "Error: Quantity must be positive"
        
        # Convert order_class string to enum if needed
        if isinstance(order_class, str):
            order_class = order_class.upper()
            if order_class == 'SIMPLE':
                order_class = OrderClass.SIMPLE
            elif order_class == 'BRACKET':
                order_class = OrderClass.BRACKET
            elif order_class == 'OCO':
                order_class = OrderClass.OCO
            elif order_class == 'OTO':
                order_class = OrderClass.OTO
            elif order_class == 'MLEG':
                order_class = OrderClass.MLEG
            else:
                return f"Invalid order class: {order_class}. Must be one of: simple, bracket, oco, oto, mleg"
        
        # Determine order class if not provided
        if order_class is None:
            order_class = OrderClass.MLEG if len(legs) > 1 else OrderClass.SIMPLE
        
        # Convert legs to OptionLegRequest objects
        order_legs = []
        for leg in legs:
            # Validate ratio_qty
            if not isinstance(leg['ratio_qty'], int) or leg['ratio_qty'] <= 0:
                return f"Error: Invalid ratio_qty for leg {leg['symbol']}. Must be positive integer."
            
            # Convert side string to enum
            if leg['side'].lower() == "buy":
                order_side = OrderSide.BUY
            elif leg['side'].lower() == "sell":
                order_side = OrderSide.SELL
            else:
                return f"Invalid order side: {leg['side']}. Must be 'buy' or 'sell'."
            
            order_legs.append(OptionLegRequest(
                symbol=leg['symbol'],
                side=order_side,
                ratio_qty=leg['ratio_qty']
            ))
        
        # Create market order request
        if order_class == OrderClass.MLEG:
            order_data = MarketOrderRequest(
                qty=quantity,
                order_class=order_class,
                time_in_force=time_in_force,
                extended_hours=extended_hours,
                client_order_id=f"mcp_opt_{int(time.time())}",
                type=OrderType.MARKET,
                legs=order_legs  # Set legs directly in the constructor for multi-leg orders
            )
        else:
            # For single-leg orders
            order_data = MarketOrderRequest(
                symbol=order_legs[0].symbol,
                qty=quantity,
                order_class=order_class,
                time_in_force=time_in_force,
                extended_hours=extended_hours,
                client_order_id=f"mcp_opt_{int(time.time())}",
                type=OrderType.MARKET
            )
        
        # Submit order
        order = trade_client.submit_order(order_data)
        
        # Format the response
        result = f"""
Option Market Order Placed Successfully:
--------------------------------------
Order ID: {order.id}
Client Order ID: {order.client_order_id}
Order Class: {order.order_class}
Order Type: {order.type}
Time In Force: {order.time_in_force}
Status: {order.status}
Quantity: {order.qty}
Created At: {order.created_at}
Updated At: {order.updated_at}
"""
        
        if order_class == OrderClass.MLEG and order.legs:
            result += "\nLegs:\n"
            for leg in order.legs:
                result += f"""
Symbol: {leg.symbol}
Side: {leg.side}
Ratio Quantity: {leg.ratio_qty}
Status: {leg.status}
Asset Class: {leg.asset_class}
Created At: {leg.created_at}
Updated At: {leg.updated_at}
Filled Price: {leg.filled_avg_price if hasattr(leg, 'filled_avg_price') else 'Not filled'}
Filled Time: {leg.filled_at if hasattr(leg, 'filled_at') else 'Not filled'}
-------------------------
"""
        else:
            result += f"""
Symbol: {order.symbol}
Side: {order_legs[0].side}
Filled Price: {order.filled_avg_price if hasattr(order, 'filled_avg_price') else 'Not filled'}
Filled Time: {order.filled_at if hasattr(order, 'filled_at') else 'Not filled'}
-------------------------
"""
        
        return result
        
    except APIError as api_error:
        error_message = str(api_error)
        if "40310000" in error_message and "not eligible to trade uncovered option contracts" in error_message:
            # Check if it's a short straddle by examining the legs
            is_short_straddle = False
            is_short_strangle = False
            is_short_calendar = False
            
            if order_class == OrderClass.MLEG and len(order_legs) == 2:
                # Check for short straddle (same strike, same expiration, both short)
                if (order_legs[0].side == OrderSide.SELL and 
                    order_legs[1].side == OrderSide.SELL and
                    order_legs[0].symbol.split('C')[0] == order_legs[1].symbol.split('P')[0]):
                    is_short_straddle = True
                # Check for short strangle (different strikes, same expiration, both short)
                elif (order_legs[0].side == OrderSide.SELL and 
                      order_legs[1].side == OrderSide.SELL):
                    is_short_strangle = True
                # Check for short calendar spread (same strike, different expirations, both short)
                elif (order_legs[0].side == OrderSide.SELL and 
                      order_legs[1].side == OrderSide.SELL):
                    # Extract option type (C for call, P for put) and expiration dates
                    leg1_type = 'C' if 'C' in order_legs[0].symbol else 'P'
                    leg2_type = 'C' if 'C' in order_legs[1].symbol else 'P'
                    leg1_exp = order_legs[0].symbol.split(leg1_type)[1][:6]
                    leg2_exp = order_legs[1].symbol.split(leg2_type)[1][:6]
                    
                    # Check if it's a short call calendar spread (both calls, longer-term is sold)
                    if (leg1_type == 'C' and leg2_type == 'C' and 
                        leg1_exp != leg2_exp):
                        is_short_calendar = True
            
            if is_short_straddle:
                return """
Error: Account not eligible to trade short straddles.

This error occurs because short straddles require Level 4 options trading permission.
A short straddle involves:
- Selling a call option
- Selling a put option
- Both options have the same strike price and expiration

Required Account Level:
- Level 4 options trading permission is required
- Please contact your broker to upgrade your account level if needed

Alternative Strategies:
- Consider using a long straddle instead
- Use a debit spread strategy
- Implement a covered call or cash-secured put
"""
            elif is_short_strangle:
                return """
Error: Account not eligible to trade short strangles.

This error occurs because short strangles require Level 4 options trading permission.
A short strangle involves:
- Selling an out-of-the-money call option
- Selling an out-of-the-money put option
- Both options have the same expiration

Required Account Level:
- Level 4 options trading permission is required
- Please contact your broker to upgrade your account level if needed

Alternative Strategies:
- Consider using a long strangle instead
- Use a debit spread strategy
- Implement a covered call or cash-secured put
"""
            elif is_short_calendar:
                return """
Error: Account not eligible to trade short calendar spreads.

This error occurs because short calendar spreads require Level 4 options trading permission.
A short calendar spread involves:
- Selling a longer-term option
- Selling a shorter-term option
- Both options have the same strike price

Required Account Level:
- Level 4 options trading permission is required
- Please contact your broker to upgrade your account level if needed

Alternative Strategies:
- Consider using a long calendar spread instead
- Use a debit spread strategy
- Implement a covered call or cash-secured put
"""
            else:
                return """
Error: Account not eligible to trade uncovered option contracts.

This error occurs when attempting to place an order that could result in an uncovered position.
Common scenarios include:
1. Selling naked calls
2. Calendar spreads where the short leg expires after the long leg
3. Other strategies that could leave uncovered positions

Required Account Level:
- Level 4 options trading permission is required for uncovered options
- Please contact your broker to upgrade your account level if needed

Alternative Strategies:
- Consider using covered calls instead of naked calls
- Use debit spreads instead of calendar spreads
- Ensure all positions are properly hedged
"""
        elif "403" in error_message:
            return f"""
Error: Permission denied for option trading.

Possible reasons:
1. Insufficient account level for the requested strategy
2. Account restrictions on option trading
3. Missing required permissions

Please check:
1. Your account's option trading level
2. Any specific restrictions on your account
3. Required permissions for the strategy you're trying to implement

Original error: {error_message}
"""
        else:
            return f"""
Error placing option order: {error_message}

Please check:
1. All option symbols are valid
2. Your account has sufficient buying power
3. The market is open for trading
4. Your account has the required permissions
"""
            
    except Exception as e:
        return f"""
Unexpected error placing option order: {str(e)}

Please try:
1. Verifying all input parameters
2. Checking your account status
3. Ensuring market is open
4. Contacting support if the issue persists
"""

# Run the server
if __name__ == "__main__":
    mcp.run(transport='stdio')
#!/usr/bin/env python3
"""Standard MCP server implementation for better compatibility."""

import asyncio
from mcp.server import Server
from mcp.types import (
    Resource, Tool, Prompt, 
    TextContent, ImageContent, EmbeddedResource
)
import mcp.server.stdio

# Import your existing modules
from alpaca_mcp_server.tools import (
    account_tools,
    position_tools, 
    order_tools,
    market_data_tools,
    market_info_tools,
    options_tools,
    watchlist_tools,
    asset_tools,
    corporate_action_tools,
    streaming_tools
)

from alpaca_mcp_server.prompts import (
    list_trading_capabilities,
    account_analysis_prompt,
    position_management_prompt,
    market_analysis_prompt
)

# Create server instance
server = Server("alpaca-mcp-server")

# Register tools
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_account_info",
            description="Get current account information including balances and status",
        ),
        Tool(
            name="get_positions", 
            description="Get all current positions in the portfolio",
        ),
        Tool(
            name="get_market_clock",
            description="Get current market status and next open/close times",
        ),
        Tool(
            name="start_global_stock_stream",
            description="Start global real-time stock data stream for day trading",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {"type": "array", "items": {"type": "string"}},
                    "data_types": {"type": "array", "items": {"type": "string"}},
                    "feed": {"type": "string", "default": "sip"}
                },
                "required": ["symbols"]
            }
        ),
        # Add more tools as needed...
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "get_account_info":
            result = await account_tools.get_account_info()
        elif name == "get_positions":
            result = await account_tools.get_positions()
        elif name == "get_market_clock":
            result = await market_info_tools.get_market_clock()
        elif name == "start_global_stock_stream":
            symbols = arguments.get("symbols", [])
            data_types = arguments.get("data_types", ["trades", "quotes"])
            feed = arguments.get("feed", "sip")
            result = await streaming_tools.start_global_stock_stream(symbols, data_types, feed)
        else:
            result = f"Unknown tool: {name}"
            
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

# Register prompts
@server.list_prompts()
async def handle_list_prompts() -> list[Prompt]:
    """List available prompts."""
    return [
        Prompt(
            name="list_trading_capabilities",
            description="List all Alpaca trading capabilities with guided workflows",
        ),
        Prompt(
            name="account_analysis", 
            description="Complete portfolio health check with actionable insights",
        ),
        Prompt(
            name="position_management",
            description="Strategic position review and optimization",
        ),
        Prompt(
            name="market_analysis",
            description="Real-time market insights and opportunities",
        ),
    ]

@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict) -> str:
    """Handle prompt requests."""
    try:
        if name == "list_trading_capabilities":
            return await list_trading_capabilities.list_trading_capabilities()
        elif name == "account_analysis":
            return await account_analysis_prompt.account_analysis()
        elif name == "position_management":
            symbol = arguments.get("symbol")
            return await position_management_prompt.position_management(symbol)
        elif name == "market_analysis":
            symbols = arguments.get("symbols")
            timeframe = arguments.get("timeframe", "1Day")
            return await market_analysis_prompt.market_analysis(symbols, timeframe)
        else:
            return f"Unknown prompt: {name}"
    except Exception as e:
        return f"Error: {str(e)}"

async def main():
    """Run the server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    print("🚀 Starting Standard MCP Server")
    asyncio.run(main())
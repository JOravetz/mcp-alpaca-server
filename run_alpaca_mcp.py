#!/usr/bin/env python3
"""Entry script for the new modular Alpaca MCP Server."""
import sys
import os
# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))
try:
    from alpaca_mcp_server.server import mcp
    
    if __name__ == "__main__":
        print("🚀 Starting Alpaca Trading MCP Server (Modular Architecture)")
        print("📊 Prompt-driven workflows enabled")
        print("⚡ Use list_trading_capabilities() to explore features")
        print("=" * 60)
        mcp.run(transport='stdio')
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure alpaca-py is installed: pip install alpaca-py")
    print("2. Ensure mcp is installed: pip install mcp")
    print("3. Check your API credentials in .env file")
    sys.exit(1)
except Exception as e:
    print(f"❌ Server Error: {e}")
    sys.exit(1)

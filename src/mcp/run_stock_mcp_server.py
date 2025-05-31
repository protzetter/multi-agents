#!/usr/bin/env python3
"""
Run the Stock Agent MCP Server
"""

import os
import sys
import logging
import argparse
import uvicorn

# Add the project root to the path so we can import our modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

def main():
    """Run the Stock Agent MCP Server"""
    parser = argparse.ArgumentParser(description="Run the Stock Agent MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    
    # Start the server
    print(f"Starting Stock Agent MCP Server on {args.host}:{args.port}...")
    uvicorn.run("src.mcp.stock_agent_mcp_server:app", host=args.host, port=args.port, reload=False)

if __name__ == "__main__":
    main()

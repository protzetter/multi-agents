"""
Tools Package

Custom tools for the multi-agent system.
"""

from .data_catalog_tool import (
    search_data_catalog,
    get_data_product_attributes,
    list_data_products,
    get_data_product_location
)

from .excel_tools_strands import (
    read_excel_file,
    read_csv_file,
    analyze_with_excel_agent
)

from .stock_info_tool import (
    analyze_with_stock_agent,
    get_stock_price,
    compare_multiple_stocks,
    get_market_overview,
    search_stocks_by_name,
    get_stock_agent_capabilities
)

__all__ = [
    # Data catalog tools
    "search_data_catalog",
    "get_data_product_attributes", 
    "list_data_products",
    "get_data_product_location",
    # Excel tools
    "read_excel_file",
    "read_csv_file",
    "analyze_with_excel_agent",
    # Stock info tools
    "analyze_with_stock_agent",
    "get_stock_price",
    "compare_multiple_stocks",
    "get_market_overview",
    "search_stocks_by_name",
    "get_stock_agent_capabilities"
]

"""
MCP Server for Excel Tools

This module provides an MCP server that exposes Excel file reading functionality.
"""
import os
import sys
import logging
from typing import Dict, Any, Optional, List

# Add the project root to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Import the MCP server library
from mcp.server.fastmcp import FastMCP
# Initialize FastMCP server
mcp = FastMCP("excel")
# Import the Excel tools
from src.tools.excel_tools_strands import read_excel_file, read_csv_file

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool()
def read_excel(file_path: str, sheet_name: Optional[str] = None, max_rows: int = 100) -> Dict[str, Any]:
    """
    Read an Excel file and return its contents.
    
    Args:
        file_path: Path to the Excel file
        sheet_name: Optional name of the sheet to read. If None, reads the first sheet.
        max_rows: Maximum number of rows to return in the data sample (default: 100)
        
    Returns:
        dict: Dictionary containing the Excel data and metadata
    """
    logger.info(f"Reading Excel file: {file_path}")
    
    try:
        # Call the underlying tool
        result = read_excel_file(file_path, sheet_name)
        
        # Limit the number of rows in the data sample if needed
        if 'data_sample' in result and len(result['data_sample']) > max_rows:
            result['data_sample'] = result['data_sample'][:max_rows]
            result['note'] = f"Data sample limited to {max_rows} rows. Total rows: {result['total_rows']}"
        
        return result
    except Exception as e:
        error_msg = f"Failed to read Excel file: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool()
def read_csv(file_path: str, delimiter: str = ',', encoding: str = 'utf-8', max_rows: int = 100) -> Dict[str, Any]:
    """
    Read a CSV file and return its contents.
    
    Args:
        file_path: Path to the CSV file
        delimiter: The delimiter used in the CSV file (default: ',')
        encoding: The encoding of the CSV file (default: 'utf-8')
        max_rows: Maximum number of rows to return in the data sample (default: 100)
        
    Returns:
        dict: Dictionary containing the CSV data and metadata
    """
    logger.info(f"Reading CSV file: {file_path}")
    
    try:
        # Call the underlying tool
        result = read_csv_file(file_path, delimiter, encoding)
        
        # Limit the number of rows in the data sample if needed
        if 'data_sample' in result and len(result['data_sample']) > max_rows:
            result['data_sample'] = result['data_sample'][:max_rows]
            result['note'] = f"Data sample limited to {max_rows} rows. Total rows: {result['total_rows']}"
        
        return result
    except Exception as e:
        error_msg = f"Failed to read CSV file: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool()
def list_sheets(file_path: str) -> Dict[str, Any]:
    """
    List all sheets in an Excel file.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        dict: Dictionary containing the list of sheet names
    """
    logger.info(f"Listing sheets in Excel file: {file_path}")
    
    try:
        # Call the underlying tool to get all sheets
        result = read_excel_file(file_path)
        
        return {
            "file_path": file_path,
            "sheet_names": result.get('all_sheets', [])
        }
    except Exception as e:
        error_msg = f"Failed to list sheets in Excel file: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool()
def get_column_stats(file_path: str, column_name: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistics for a specific column in an Excel or CSV file.
    
    Args:
        file_path: Path to the file
        column_name: Name of the column to analyze
        sheet_name: Optional name of the sheet (for Excel files)
        
    Returns:
        dict: Dictionary containing column statistics
    """
    logger.info(f"Getting stats for column '{column_name}' in file: {file_path}")
    
    try:
        # Determine file type and call appropriate function
        if file_path.lower().endswith('.csv'):
            result = read_csv_file(file_path)
        else:
            result = read_excel_file(file_path, sheet_name)
        
        # Check if column exists
        if column_name not in result.get('column_names', []):
            return {"error": f"Column '{column_name}' not found in the file"}
        
        # Find column info
        column_info = None
        for col in result.get('columns', []):
            if col.get('name') == column_name:
                column_info = col
                break
        
        # Get column data from sample
        column_data = [row.get(column_name) for row in result.get('data_sample', [])]
        
        return {
            "file_path": file_path,
            "column_name": column_name,
            "column_info": column_info,
            "data_sample": column_data[:10],  # First 10 values
            "statistics": result.get('statistics', {}).get(column_name, {})
        }
    except Exception as e:
        error_msg = f"Failed to get column stats: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

if __name__ == "__main__":
    # Run the server
    mcp.run()

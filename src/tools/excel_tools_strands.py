from strands import tool
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import os
import sys

# Add the project root to the path so we can import our agents
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the excel agent (lazy import to avoid circular dependencies)
def get_excel_agent():
    """Lazy import of excel agent to avoid circular dependencies."""
    try:
        from agents.strands.excel_agent import excel_agent
        return excel_agent
    except ImportError as e:
        print(f"Warning: Could not import excel_agent: {e}")
        return None


@tool
def read_excel_file(file_path: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Read an Excel file and return its contents as a dictionary.
    
    Args:
        file_path: Path to the Excel file
        sheet_name: Optional name of the sheet to read. If None, reads the first sheet.
        
    Returns:
        dict: Dictionary containing the Excel data and metadata
    """
    try:
        # Read the Excel file
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            # Get all sheets
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            if not sheet_names:
                return {"error": "No sheets found in the Excel file"}
            
            # Read the first sheet by default
            df = pd.read_excel(file_path, sheet_name=sheet_names[0])
            
        # Get basic statistics
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        stats = {}
        if numeric_columns:
            stats = df[numeric_columns].describe().to_dict()
        
        # Get column information
        columns_info = []
        for col in df.columns:
            col_type = str(df[col].dtype)
            unique_values = df[col].nunique()
            missing_values = df[col].isna().sum()
            
            columns_info.append({
                "name": col,
                "type": col_type,
                "unique_values": int(unique_values),
                "missing_values": int(missing_values)
            })
        
        # Convert DataFrame to dictionary for the first 100 rows (to avoid overwhelming the model)
        data_sample = df.head(100).to_dict(orient='records')
        
        # Get all sheet names
        all_sheets = pd.ExcelFile(file_path).sheet_names
        
        return {
            "file_path": file_path,
            "sheet_name": sheet_name if sheet_name else all_sheets[0],
            "all_sheets": all_sheets,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": columns_info,
            "statistics": stats,
            "data_sample": data_sample,
            "column_names": df.columns.tolist()
        }
    except Exception as e:
        return {"error": f"Failed to read Excel file: {str(e)}"}


@tool
def read_csv_file(file_path: str, delimiter: str = ',', encoding: str = 'utf-8') -> Dict[str, Any]:
    """
    Read a CSV file and return its contents as a dictionary.
    
    Args:
        file_path: Path to the CSV file
        delimiter: The delimiter used in the CSV file (default: ',')
        encoding: The encoding of the CSV file (default: 'utf-8')
        
    Returns:
        dict: Dictionary containing the CSV data and metadata
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
        
        # Get basic statistics
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        stats = {}
        if numeric_columns:
            stats = df[numeric_columns].describe().to_dict()
        
        # Get column information
        columns_info = []
        for col in df.columns:
            col_type = str(df[col].dtype)
            unique_values = df[col].nunique()
            missing_values = df[col].isna().sum()
            
            columns_info.append({
                "name": col,
                "type": col_type,
                "unique_values": int(unique_values),
                "missing_values": int(missing_values)
            })
        
        # Convert DataFrame to dictionary for the first 100 rows (to avoid overwhelming the model)
        data_sample = df.head(100).to_dict(orient='records')
        
        return {
            "file_path": file_path,
            "delimiter": delimiter,
            "encoding": encoding,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": columns_info,
            "statistics": stats,
            "data_sample": data_sample,
            "column_names": df.columns.tolist()
        }
    except Exception as e:
        return {"error": f"Failed to read CSV file: {str(e)}"}


@tool
def analyze_with_excel_agent(query: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Use the specialized Excel agent to analyze data and answer questions.
    
    This tool provides access to a specialized Excel analysis agent that can:
    - Read and interpret Excel/CSV files
    - Analyze data patterns and trends
    - Generate insights and visualizations
    - Answer natural language questions about data
    - Provide business-friendly explanations
    
    Args:
        query: The question or analysis request for the Excel agent
        file_path: Optional path to Excel/CSV file to analyze
        
    Returns:
        dict: Response from the Excel agent with analysis results
    """
    try:
        # Get the excel agent
        excel_agent = get_excel_agent()
        
        if excel_agent is None:
            return {
                "error": "Excel agent is not available",
                "message": "Could not load the Excel analysis agent. Please check the agent configuration."
            }
        
        # Construct the query for the agent
        if file_path:
            full_query = f"Please analyze the file at '{file_path}' and answer this question: {query}"
        else:
            full_query = query
        
        # Get response from the excel agent
        response = excel_agent(full_query)
        
        # Extract the message content
        if hasattr(response, 'message'):
            if isinstance(response.message, dict) and 'content' in response.message:
                # Handle structured message format
                content = response.message['content']
                if isinstance(content, list) and len(content) > 0:
                    message_text = content[0].get('text', str(response.message))
                else:
                    message_text = str(content)
            else:
                # Handle simple string message
                message_text = str(response.message)
        else:
            message_text = str(response)
        
        return {
            "status": "success",
            "query": query,
            "file_path": file_path,
            "analysis": message_text,
            "agent": "Excel Analysis Agent",
            "message": "Analysis completed successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to analyze with Excel agent: {str(e)}",
            "query": query,
            "file_path": file_path,
            "message": "Analysis failed due to an error"
        }


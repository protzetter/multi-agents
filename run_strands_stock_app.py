#!/usr/bin/env python3
"""
Runner script for the Strands Stock Information Agent Streamlit app.
"""
import os
import subprocess
import sys

def main():
    """Run the Strands Stock Information Agent Streamlit app."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Streamlit app
    app_path = os.path.join(script_dir, 'src', 'ui', 'streamlit_strands_stock_app.py')
    
    # Check if the app file exists
    if not os.path.exists(app_path):
        print(f"Error: Could not find the Streamlit app at {app_path}")
        sys.exit(1)
    
    # Run the Streamlit app
    print(f"Starting Strands Stock Information Agent Streamlit app...")
    subprocess.run(['streamlit', 'run', app_path])

if __name__ == "__main__":
    main()

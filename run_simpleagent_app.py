#!/usr/bin/env python3
"""
Script to run the Stock SimpleAgent Streamlit application.
"""
import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'config', '.env'))

def main():
    """Run the Streamlit application."""
    # Check if Streamlit is installed
    try:
        import streamlit
        print("Streamlit is installed. Starting application...")
    except ImportError:
        print("Streamlit is not installed. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
        print("Streamlit installed successfully.")
    
    # Run the Streamlit app
    app_path = os.path.join(os.path.dirname(__file__), 'src', 'ui', 'streamlit_simpleagent_app.py')
    
    print(f"Starting Stock SimpleAgent App from: {app_path}")
    subprocess.run([
        "streamlit", "run", app_path,
        "--server.port", "8502",  # Use a different port from the main stock app
        "--server.address", "localhost"
    ])

if __name__ == "__main__":
    main()

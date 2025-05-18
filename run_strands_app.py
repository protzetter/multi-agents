#!/usr/bin/env python3

import streamlit.web.cli as stcli
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", str(Path(__file__).parent / "src" / "ui" / "streamlit_strands_app.py")]
    sys.exit(stcli.main())

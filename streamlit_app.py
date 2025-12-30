#!/usr/bin/env python3
"""Streamlit app entry point."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.storage.database import Database
from src.ui.dashboard import render_dashboard

# Initialize database
db = Database()

# Render dashboard
render_dashboard(db)


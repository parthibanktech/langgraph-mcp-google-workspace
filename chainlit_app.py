"""
Launcher for Chainlit App (backend/chainlit_app.py)
Run with: chainlit run backend/chainlit_app.py
"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from backend.chainlit_app import *

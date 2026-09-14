"""
Launcher for LangGraph Agent (backend/langgraph_agent.py)
"""
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Run backend agent
if __name__ == "__main__":
    from backend.langgraph_agent import run_agent
    run_agent("What are my unread emails?")

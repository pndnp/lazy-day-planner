"""Pytest configuration for bot_tests."""

import sys
from pathlib import Path

# Add project root so `from bot.xxx` imports work
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

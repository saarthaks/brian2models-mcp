#!/usr/bin/env python
"""Standalone script to seed the Brian2 model library.

Can be run directly: python scripts/seed_library.py
Or via CLI: brian2models seed
"""

import sys
from pathlib import Path

# Add src to path so this script works standalone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from brian2models_mcp.seeder import seed

if __name__ == "__main__":
    seed()

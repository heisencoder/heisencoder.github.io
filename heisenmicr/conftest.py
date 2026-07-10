"""Put the project root on sys.path so the flat modules (spec/build/test/preview)
are importable from the tests/ package."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

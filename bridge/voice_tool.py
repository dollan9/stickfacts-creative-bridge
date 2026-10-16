"""
Voice Tool Module for Creative Pipeline Bridge.
Re-exports and integrates pipeline_bridge.voice_tool for the main bridge.
"""
import sys
from pathlib import Path

# Add project root to sys.path
SCRATCH_DIR = Path(__file__).resolve().parent.parent.parent
if str(SCRATCH_DIR) not in sys.path:
    sys.path.insert(0, str(SCRATCH_DIR))

from pipeline_bridge.voice_tool import (
    VoiceTool,
    apply_dewhistle_filter,
    generate_f5_clean_test,
    generate_kokoro_studio_test,
    main,
)

__all__ = [
    "VoiceTool",
    "apply_dewhistle_filter",
    "generate_f5_clean_test",
    "generate_kokoro_studio_test",
    "main",
]

if __name__ == "__main__":
    main()

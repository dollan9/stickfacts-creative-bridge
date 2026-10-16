"""
Unit test for Voice Tool module in creative pipeline bridge.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bridge.voice_tool import test_stickfacts_voiceover


def test_voice():
    print("[*] Testing Voice Tool (Official SWivid/F5-TTS on CUDA)...")
    result = test_stickfacts_voiceover()
    assert result["exists"] is True, "Voiceover file was not generated!"
    assert result["duration_seconds"] > 0, "Voiceover duration is invalid!"
    print(f"    [+] Voice Tool verification passed! Generated {result['duration_seconds']:.2f}s audio.")


if __name__ == "__main__":
    test_voice()

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bridge.premiere_tool import PremiereTool
from bridge.config_loader import get_config

def test_premiere():
    print("[*] Testing Adobe Premiere Pro 2026 Bridge Module...")
    tool = PremiereTool()
    print(f"    Premiere Exe: {tool.exe_path}")
    print(f"    Headless Exe: {tool.headless_exe}")

    out_dir = get_config().get_output_dir()
    xml_out_path = out_dir / "test_premiere_sequence.xml"

    video_clips = [
        {
            "name": "Scene_01_Background",
            "file_path": out_dir / "test_character_vector.svg",
            "start_frame": 0,
            "end_frame": 72, # 3 seconds @ 24fps
            "in_frame": 0,
            "out_frame": 72
        },
        {
            "name": "Scene_01_Character_Rig",
            "file_path": out_dir / "test_character_rig.psd",
            "start_frame": 72,
            "end_frame": 144, # 3 seconds @ 24fps
            "in_frame": 0,
            "out_frame": 72
        }
    ]

    audio_clips = [
        {
            "name": "Voiceover_Track",
            "file_path": out_dir / "voiceover.wav",
            "start_frame": 0,
            "end_frame": 144,
            "in_frame": 0,
            "out_frame": 144
        }
    ]

    print("    [1/2] Generating Premiere Pro / FCP XML v4 sequence...")
    xml_path = tool.generate_timeline_xml(
        sequence_name="Action_Scene_01",
        output_xml_path=xml_out_path,
        width=3840,
        height=2160,
        fps=24,
        video_clips=video_clips,
        audio_clips=audio_clips
    )
    print(f"          Created XML: {xml_path}")
    assert xml_path.exists(), f"XML file not created at {xml_path}"
    print(f"          XML File Size: {xml_path.stat().st_size} bytes")

    print("    [2/2] Validating XML structure and node tree...")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    assert root.tag == "xmeml", "Root tag is not xmeml"
    assert root.attrib.get("version") == "4", "xmeml version is not 4"

    seq = root.find(".//sequence")
    assert seq is not None, "Sequence tag not found"
    assert seq.find("name").text == "Action_Scene_01", "Sequence name mismatch"

    v_tracks = root.findall(".//video/track")
    assert len(v_tracks) >= 1, "No video tracks found"
    clipitems = v_tracks[0].findall("clipitem")
    assert len(clipitems) == 2, f"Expected 2 clipitems, found {len(clipitems)}"
    print(f"          Verified {len(clipitems)} video clip items and audio track.")

    print("[+] Adobe Premiere Pro 2026 Verification: PASSED\n")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    test_premiere()

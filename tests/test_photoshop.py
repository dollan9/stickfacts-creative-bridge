import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bridge.photoshop_tool import PhotoshopTool, CHARACTER_RIG_LAYERS
from bridge.config_loader import get_config

def test_photoshop():
    print("[*] Testing Adobe Photoshop 2026 Bridge Module...")
    tool = PhotoshopTool()
    print(f"    COM ProgID: {tool.progid}")
    
    out_dir = get_config().get_output_dir()
    psd_path = out_dir / "test_character_rig.psd"

    print("    [1/3] Creating 3840x2160 document with 14 character rig layers...")
    res = tool.create_character_rig_document(
        width=3840,
        height=2160,
        dpi=300,
        doc_name="Test_Character_Rig",
        layers=CHARACTER_RIG_LAYERS
    )
    print(f"          Result: {res}")

    print("    [2/3] Saving document to PSD...")
    save_res = tool.save_as_psd(psd_path)
    print(f"          Result: {save_res}")

    assert psd_path.exists(), f"PSD file not found at {psd_path}"
    file_size = psd_path.stat().st_size
    print(f"          PSD File Size: {file_size} bytes")
    assert file_size > 0, "PSD file is empty!"

    print("    [3/3] Closing active test document...")
    close_res = tool.close_active_document(save=False)
    print(f"          Result: {close_res}")

    print("[+] Adobe Photoshop 2026 Verification: PASSED\n")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    test_photoshop()

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bridge.illustrator_tool import IllustratorTool
from bridge.photoshop_tool import CHARACTER_RIG_LAYERS
from bridge.config_loader import get_config

def test_illustrator():
    print("[*] Testing Adobe Illustrator 2026 Bridge Module...")
    tool = IllustratorTool()
    print(f"    COM ProgID: {tool.progid}")

    out_dir = get_config().get_output_dir()
    ai_path = out_dir / "test_character_vector.ai"
    svg_path = out_dir / "test_character_vector.svg"

    print("    [1/4] Creating 3840x2160 document with character layers...")
    create_res = tool.create_character_document(
        width=3840,
        height=2160,
        doc_name="Test_Character_Vector",
        layers=CHARACTER_RIG_LAYERS
    )
    print(f"          Result: {create_res}")

    print("    [2/4] Drawing vector element on 'Head' layer...")
    draw_res = tool.draw_sample_vector("Head", 100, 100, 400, 300, 240, 80, 80)
    print(f"          Result: {draw_res}")

    print("    [3/4] Exporting to SVG and saving AI...")
    svg_res = tool.export_svg(svg_path)
    print(f"          SVG Result: {svg_res}")
    assert svg_path.exists(), f"SVG file not found at {svg_path}"
    print(f"          SVG File Size: {svg_path.stat().st_size} bytes")

    ai_res = tool.save_as_ai(ai_path)
    print(f"          AI Result: {ai_res}")
    assert ai_path.exists(), f"AI file not found at {ai_path}"
    print(f"          AI File Size: {ai_path.stat().st_size} bytes")

    print("    [4/4] Closing active document...")
    close_res = tool.close_all_documents(save=False)
    print(f"          Result: {close_res}")

    print("[+] Adobe Illustrator 2026 Verification: PASSED\n")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    test_illustrator()

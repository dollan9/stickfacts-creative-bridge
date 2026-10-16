import sys
from pathlib import Path
import zipfile
import json
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bridge.moho_tool import MohoTool
from bridge.photoshop_tool import CHARACTER_RIG_LAYERS
from bridge.config_loader import get_config

def test_moho():
    print("[*] Testing Moho Pro 14.5 Bridge Module...")
    tool = MohoTool()
    print(f"    Moho Executable: {tool.exe_path}")
    print(f"    Scripts Directory: {tool.scripts_dir}")

    out_dir = get_config().get_output_dir()
    moho_out_path = out_dir / "test_character_rig.moho"

    print("    [1/3] Building programmatic .moho project (JSON + ZIP archive)...")
    created_path = tool.create_character_project(
        output_path=moho_out_path,
        name="Test_Character_Rig",
        width=3840,
        height=2160,
        fps=24.0,
        layers=CHARACTER_RIG_LAYERS
    )
    print(f"          Created file: {created_path}")
    assert created_path.exists(), f"Moho file not found at {created_path}"
    print(f"          Moho File Size: {created_path.stat().st_size} bytes")

    print("    [2/3] Verifying .moho internal structure & JSON schema...")
    assert zipfile.is_zipfile(created_path), "Created .moho is not a valid zip archive!"
    
    parsed_data = tool.read_project(created_path)
    assert parsed_data.get("mime_type") == "application/x-vnd.lm_mohodoc", "Invalid mime_type"
    assert parsed_data.get("version") == 1040, "Invalid Moho version"
    
    root_layers = parsed_data.get("layers", [])
    assert len(root_layers) == 1, "Expected 1 root BoneLayer"
    
    bone_layer = root_layers[0]
    assert bone_layer.get("type") == "BoneLayer", "Root layer is not BoneLayer"
    
    bones = bone_layer.get("skeleton", {}).get("bones", [])
    assert len(bones) == len(CHARACTER_RIG_LAYERS), f"Expected {len(CHARACTER_RIG_LAYERS)} bones, got {len(bones)}"
    
    child_layers = bone_layer.get("layers", [])
    assert len(child_layers) == len(CHARACTER_RIG_LAYERS), f"Expected {len(CHARACTER_RIG_LAYERS)} child layers"
    print(f"          Verified {len(bones)} bones and {len(child_layers)} rigged child layers.")

    print("    [3/3] Generating Lua automation script...")
    lua_path = out_dir / "test_automation.lua"
    tool.create_lua_script(
        output_script_path=lua_path,
        script_body="""    print("Hello from Moho Lua Scripting!");
    moho:FileSave();
    moho:Quit();"""
    )
    assert lua_path.exists(), f"Lua script not found at {lua_path}"
    print(f"          Generated Lua Script Size: {lua_path.stat().st_size} bytes")

    print("[+] Moho Pro 14.5 Verification: PASSED\n")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    test_moho()

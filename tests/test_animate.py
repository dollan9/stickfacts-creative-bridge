import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bridge.animate_tool import AnimateTool
from bridge.photoshop_tool import CHARACTER_RIG_LAYERS
from bridge.config_loader import get_config

def test_animate():
    print("[*] Testing Adobe Animate 2024 Bridge Module...")
    tool = AnimateTool()
    print(f"    Executable: {tool.exe_path}")
    print(f"    Commands Directory: {tool.commands_dir}")

    assert tool.exe_path.exists(), "Animate executable does not exist"
    assert tool.commands_dir.exists(), "Animate Commands directory does not exist"

    out_dir = get_config().get_output_dir()
    fla_path = out_dir / "character_rig.fla"

    print("    [1/3] Generating character rig JSFL script...")
    jsfl_code = tool.generate_character_fla_jsfl(
        output_fla_path=fla_path,
        width=1920,
        height=1080,
        fps=24,
        layers=CHARACTER_RIG_LAYERS,
        close_when_done=True
    )
    assert "fl.createDocument()" in jsfl_code, "Missing fl.createDocument in JSFL"
    assert "Head" in jsfl_code and "Torso" in jsfl_code, "Missing character layers in JSFL"
    print("          JSFL script generated successfully.")

    print("    [2/3] Deploying script to native Animate Commands menu...")
    installed_path = tool.install_command_script("Create_Character_Rig", jsfl_code)
    assert installed_path.exists(), f"Failed to install script at {installed_path}"
    print(f"          Installed command: {installed_path} ({installed_path.stat().st_size} bytes)")

    print("    [3/3] Saving local copy to output directory...")
    local_script = out_dir / "Create_Character_Rig.jsfl"
    local_script.write_text(jsfl_code, encoding="utf-8")
    assert local_script.exists(), "Local JSFL copy missing"
    print(f"          Local copy: {local_script} ({local_script.stat().st_size} bytes)")

    print("[+] Adobe Animate 2024 Verification: PASSED\n")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    test_animate()

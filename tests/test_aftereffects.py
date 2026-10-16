import sys
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bridge.aftereffects_tool import AfterEffectsTool
from bridge.config_loader import get_config

def test_aftereffects():
    print("[*] Testing Adobe After Effects 2026 Bridge Module...")
    tool = AfterEffectsTool()
    print(f"    AfterFX Exe: {tool.afterfx_exe}")
    print(f"    aerender Exe: {tool.aerender_exe}")

    print("    [1/3] Testing aerender -version CLI engine...")
    res = subprocess.run([str(tool.aerender_exe), "-version"], capture_output=True, text=True, timeout=15)
    print(f"          aerender output: {res.stdout.strip()}")
    assert "aerender" in res.stdout.lower() or res.returncode == 0 or len(res.stdout) > 0, "aerender engine check failed"

    print("    [2/3] Generating composition automation script (3840x2160, 24fps, camera shake, render queue)...")
    out_dir = get_config().get_output_dir()
    aep_path = out_dir / "test_production_comp.aep"
    render_mov = out_dir / "test_production_render.mov"

    jsx = tool.generate_composition_jsx(
        output_aep_path=aep_path,
        comp_name="Final_Action_Shot",
        width=3840,
        height=2160,
        fps=24.0,
        duration_secs=5.0,
        background_path=out_dir / "test_character_vector.svg",
        character_pass_paths=[out_dir / "test_character_rig.psd"],
        apply_camera_shake=True,
        output_render_path=render_mov
    )

    assert "Final_Action_Shot" in jsx, "Comp name not found in JSX"
    assert "wiggle(2, 25)" in jsx, "Camera shake expression missing in JSX"
    assert "app.project.renderQueue.items.add" in jsx, "Render queue setup missing in JSX"
    assert "app.project.save" in jsx, "Project save command missing in JSX"
    print("          JSX composition script generated and validated.")

    print("    [3/3] Saving generated composition script to disk...")
    jsx_test_file = out_dir / "test_comp_builder.jsx"
    jsx_test_file.write_text(jsx, encoding="utf-8")
    assert jsx_test_file.exists(), "JSX script file was not written"
    print(f"          Script written: {jsx_test_file} ({jsx_test_file.stat().st_size} bytes)")

    print("[+] Adobe After Effects 2026 Verification: PASSED\n")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    test_aftereffects()

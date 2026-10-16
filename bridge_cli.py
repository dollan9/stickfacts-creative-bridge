import os
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bridge.config_loader import get_config
from bridge.comfy_tool import ComfyTool
from bridge.photoshop_tool import PhotoshopTool, CHARACTER_RIG_LAYERS
from bridge.illustrator_tool import IllustratorTool
from bridge.animate_tool import AnimateTool
from bridge.moho_tool import MohoTool
from bridge.aftereffects_tool import AfterEffectsTool
from bridge.premiere_tool import PremiereTool

def cmd_status(args):
    print("=" * 60, flush=True)
    print("CREATIVE PIPELINE BRIDGE - STATUS & ENVIRONMENT", flush=True)
    print("=" * 60, flush=True)
    cfg = get_config().data
    for app_key, info in cfg.get("applications", {}).items():
        name = info.get("name", app_key)
        ver = info.get("version", "N/A")
        method = info.get("control_method", "N/A")
        print(f"  {name:<30} v{ver:<12} [{method}]", flush=True)
    print("=" * 60, flush=True)

def cmd_test_all(args):
    print("=" * 60, flush=True)
    print("RUNNING ALL MODULE VERIFICATION TESTS", flush=True)
    print("=" * 60, flush=True)
    tests = [
        ("ComfyUI", "tests.test_comfy", "test_comfy"),
        ("Photoshop", "tests.test_photoshop", "test_photoshop"),
        ("Illustrator", "tests.test_illustrator", "test_illustrator"),
        ("Animate", "tests.test_animate", "test_animate"),
        ("Moho Pro", "tests.test_moho", "test_moho"),
        ("After Effects", "tests.test_aftereffects", "test_aftereffects"),
        ("Premiere Pro", "tests.test_premiere", "test_premiere"),
        ("F5-TTS Voice", "tests.test_voice", "test_voice"),
    ]
    results = {}
    for name, module_path, func_name in tests:
        print(f"\n>>> Running verification: {name} ...", flush=True)
        try:
            mod = __import__(module_path, fromlist=[func_name])
            func = getattr(mod, func_name)
            func()
            results[name] = "PASSED"
        except Exception as e:
            print(f"[!] {name} FAILED: {e}", flush=True)
            results[name] = f"FAILED: {e}"

    print("\n" + "=" * 60, flush=True)
    print("FINAL TEST MATRIX:", flush=True)
    print("=" * 60, flush=True)
    all_passed = True
    for name, status in results.items():
        print(f"  {name:<25} : {status}", flush=True)
        if status != "PASSED":
            all_passed = False
    print("=" * 60, flush=True)
    if all_passed:
        print("[+] ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!", flush=True)
    else:
        print("[!] SOME TESTS FAILED", flush=True)

def cmd_build_rig(args):
    name = args.name
    width = args.width
    height = args.height
    out_dir = get_config().get_output_dir()
    print(f"[*] Building complete multi-app 2D character rig: {name} ({width}x{height})...", flush=True)

    # 1. Moho
    moho = MohoTool()
    moho_file = out_dir / f"{name}_rig.moho"
    moho.create_character_project(moho_file, name=name, width=width, height=height)
    print(f"  [+] Moho Rig created: {moho_file}", flush=True)

    # 2. Animate
    animate = AnimateTool()
    jsfl = animate.generate_character_fla_jsfl(out_dir / f"{name}_rig.fla", width=width, height=height)
    installed = animate.install_command_script(f"Build_{name}_Rig", jsfl)
    print(f"  [+] Animate JSFL installed: {installed}", flush=True)

    # 3. Photoshop
    ps = PhotoshopTool()
    ps_file = out_dir / f"{name}_rig.psd"
    ps.create_character_rig_document(width=width, height=height, doc_name=f"{name}_Rig")
    ps.save_as_psd(ps_file)
    ps.close_active_document(save=False)
    print(f"  [+] Photoshop PSD created: {ps_file}", flush=True)

    # 4. Illustrator
    ai = IllustratorTool()
    ai_file = out_dir / f"{name}_vector.ai"
    svg_file = out_dir / f"{name}_vector.svg"
    ai.create_character_document(width=width, height=height, doc_name=f"{name}_Vector")
    ai.draw_sample_vector("Head", 100, 100, 400, 300)
    ai.export_svg(svg_file)
    ai.save_as_ai(ai_file)
    ai.close_all_documents(save=False)
    print(f"  [+] Illustrator AI & SVG created: {ai_file}, {svg_file}", flush=True)

    print(f"\n[+] Character Rig '{name}' successfully generated across all 4 2D applications!", flush=True)

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Multi-App 2D Animation & Video Production Bridge")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # status
    p_status = subparsers.add_parser("status", help="Show system and application bridge status")
    p_status.set_defaults(func=cmd_status)

    # test-all
    p_test = subparsers.add_parser("test-all", help="Run incremental verification tests for all modules")
    p_test.set_defaults(func=cmd_test_all)

    # build-rig
    p_rig = subparsers.add_parser("build-rig", help="Build synchronized character rig across 2D applications")
    p_rig.add_argument("--name", default="HeroCharacter", help="Character rig name")
    p_rig.add_argument("--width", type=int, default=3840, help="Document width")
    p_rig.add_argument("--height", type=int, default=2160, help="Document height")
    p_rig.set_defaults(func=cmd_build_rig)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)

if __name__ == "__main__":
    main()

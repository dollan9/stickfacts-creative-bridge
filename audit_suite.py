import os
import sys
import json
import socket
import urllib.request
from pathlib import Path

def run_audit():
    bridge_dir = Path(r"C:\Users\jofin\.gemini\antigravity\scratch\creative_pipeline_bridge")
    config_path = bridge_dir / "config.json"
    
    print("=== STARTING STRICT SYSTEM AUDIT ===", flush=True)
    
    # 1. Read config
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    apps = cfg.get("applications", {})
    
    # SECTION 1: Paths Check
    print("\n--- SECTION 1: DISCOVERED APPLICATION PATHS ---", flush=True)
    for app_id, data in apps.items():
        name = data.get("name", app_id)
        print(f"\n[{name}] (ID: {app_id})")
        for k, v in data.items():
            if isinstance(v, str) and (":\\" in v or "/" in v):
                p = Path(v)
                status = "FOUND" if p.exists() else "MISSING"
                print(f"  - {k}: {v} -> [{status}]")
            else:
                print(f"  - {k}: {v}")

    # Check DaVinci Resolve paths specifically (since user asked for Resolve.exe and DaVinciResolveScript.py)
    resolve_exe = Path(r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe")
    resolve_sdk = Path(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules\DaVinciResolveScript.py")
    print(f"\n[DaVinci Resolve Studio Deep Path Check]")
    print(f"  - Resolve.exe: {resolve_exe} -> [{'FOUND' if resolve_exe.exists() else 'MISSING'}]")
    print(f"  - DaVinciResolveScript.py: {resolve_sdk} -> [{'FOUND' if resolve_sdk.exists() else 'MISSING'}]")

    # Check Moho Scripts directory
    moho_app_dir = Path(r"C:\Program Files\Moho 14")
    moho_custom_dir = Path(os.environ.get("APPDATA", "")) / "Smith Micro" / "Moho Pro" / "14"
    moho_custom_alt = Path(os.environ.get("APPDATA", "")) / "Lost Marble" / "Moho Pro" / "14"
    print(f"\n[Moho Pro 14 Folder Checks]")
    print(f"  - Install dir: {moho_app_dir} -> [{'FOUND' if moho_app_dir.exists() else 'MISSING'}]")
    print(f"  - AppData Smith Micro: {moho_custom_dir} -> [{'FOUND' if moho_custom_dir.exists() else 'MISSING'}]")
    print(f"  - AppData Lost Marble: {moho_custom_alt} -> [{'FOUND' if moho_custom_alt.exists() else 'MISSING'}]")

    # SECTION 2: Project Tree & Byte Sizes
    print("\n--- SECTION 2: CREATED PROJECT DIRECTORY & BRIDGE FILES ---", flush=True)
    for root, dirs, files in os.walk(bridge_dir):
        rel_dir = Path(root).relative_to(bridge_dir)
        indent = "  " * len(rel_dir.parts)
        if rel_dir.parts:
            print(f"{indent}[DIR] {rel_dir.parts[-1]}/")
        else:
            print(f"[ROOT] {bridge_dir}")
        for file in sorted(files):
            file_path = Path(root) / file
            size = file_path.stat().st_size
            print(f"{indent}  - {file:<35} ({size:>8} bytes)")

    # SECTION 3: Live Connectivity & API Tests
    print("\n--- SECTION 3: LIVE CONNECTIVITY & API TESTS ---", flush=True)
    
    # Test A: Photoshop COM / JSX
    print("\n[TEST A: Photoshop COM / JSX]")
    try:
        import win32com.client
        ps = win32com.client.Dispatch("Photoshop.Application")
        ps_name = getattr(ps, "Name", "Unknown")
        ps_ver = getattr(ps, "Version", "Unknown")
        print(f"  STATUS: SUCCESS")
        print(f"  Application: {ps_name}")
        print(f"  Version: {ps_ver}")
        # Run small JSX
        jsx_res = ps.DoJavaScript(" 'JSX Execution OK: ' + app.name + ' v' + app.version; ")
        print(f"  JSX Result: {jsx_res}")
    except Exception as e:
        print(f"  STATUS: FAILED")
        print(f"  Error: {e}")

    # Test B: Moho File / CLI Check
    print("\n[TEST B: Moho File / CLI Check]")
    try:
        moho_exe = Path(r"C:\Program Files\Moho 14\Moho.exe")
        print(f"  Moho Executable exists: {moho_exe.exists()} ({moho_exe})")
        # Check generated .moho file inspection
        test_moho_file = bridge_dir / "output" / "test_character_rig.moho"
        if test_moho_file.exists():
            import zipfile
            with zipfile.ZipFile(test_moho_file, "r") as zf:
                file_list = zf.namelist()
                proj_bytes = zf.read("Project.mohoproj")
                proj_json = json.loads(proj_bytes.decode("utf-8"))
            print(f"  STATUS: SUCCESS")
            print(f"  Inspected .moho file: {test_moho_file.name} ({test_moho_file.stat().st_size} bytes)")
            print(f"  Archive members: {file_list}")
            print(f"  Document format version: {proj_json.get('version')}")
            print(f"  Layer count in project: {len(proj_json.get('layers', []))}")
            bone_layer = next((l for l in proj_json.get("layers", []) if l.get("type") == "BoneLayer"), None)
            if bone_layer:
                bones = bone_layer.get("skeleton", {}).get("bones", [])
                sublayers = bone_layer.get("layers", [])
                print(f"  Rig Skeleton Bones: {len(bones)}")
                print(f"  Rig Mesh Sublayers: {len(sublayers)}")
        else:
            print(f"  STATUS: FAILED (Output file {test_moho_file} missing)")
    except Exception as e:
        print(f"  STATUS: FAILED")
        print(f"  Error: {e}")

    # Test C: DaVinci Resolve Scripting API
    print("\n[TEST C: DaVinci Resolve Scripting API]")
    resolve_module_dir = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
    if resolve_module_dir not in sys.path:
        sys.path.append(resolve_module_dir)
    try:
        import DaVinciResolveScript as bmd
        print("  Import DaVinciResolveScript: SUCCESS")
        resolve_app = bmd.scriptapp("Resolve")
        if resolve_app is not None:
            print(f"  bmd.scriptapp('Resolve') SUCCESS: Connected to running instance!")
            pm = resolve_app.GetProjectManager()
            curr_proj = pm.GetCurrentProject() if pm else None
            proj_name = curr_proj.GetName() if curr_proj else "None"
            print(f"  Current Project: {proj_name}")
        else:
            print("  bmd.scriptapp('Resolve'): None (DaVinci Resolve is not actively running or 'External scripting using' is not set to 'Local/All users' in Preferences -> System -> General).")
    except Exception as e:
        print(f"  Import DaVinciResolveScript FAILED: {e}")

    # Test D: ComfyUI Local API
    print("\n[TEST D: ComfyUI Local API]")
    comfy_url = "http://127.0.0.1:8188"
    is_online = False
    try:
        req = urllib.request.urlopen(f"{comfy_url}/system_stats", timeout=2)
        if req.status == 200:
            is_online = True
            stats = json.loads(req.read().decode("utf-8"))
            print(f"  Connection to {comfy_url}: ONLINE")
            print(f"  System Stats: {stats}")
    except Exception as e:
        print(f"  Connection to {comfy_url}: OFFLINE ({e})")
    
    checkpoints_dir = Path(r"C:\Users\jofin\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\checkpoints")
    print(f"  Checkpoints Directory: {checkpoints_dir}")
    if checkpoints_dir.exists():
        ckpts = [f.name for f in checkpoints_dir.iterdir() if f.is_file()]
        print(f"  Available Checkpoints ({len(ckpts)}): {ckpts if ckpts else 'None found in directory'}")
    else:
        print(f"  Checkpoints Directory MISSING")

    # SECTION 4: Dependencies check
    print("\n--- SECTION 4: DEPENDENCIES & ENVIRONMENT CHECK ---", flush=True)
    deps = ["win32com.client", "requests", "aiohttp", "websocket", "zipfile", "xml.etree.ElementTree"]
    for d in deps:
        try:
            __import__(d)
            print(f"  Python package '{d}': INSTALLED")
        except ImportError:
            print(f"  Python package '{d}': MISSING")

    print("\n=== AUDIT COMPLETE ===", flush=True)

if __name__ == "__main__":
    run_audit()

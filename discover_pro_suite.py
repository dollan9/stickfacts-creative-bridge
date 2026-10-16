import os
import sys
import json
from pathlib import Path

def scan_plugins():
    print("=" * 70)
    print("SCANNING PROFESSIONAL PLUGINS & TOOLS ON SYSTEM")
    print("=" * 70)

    report = {}

    # Paths to search
    search_paths = {
        "OFX_Plugins": Path(r"C:\Program Files\Common Files\OFX\Plugins"),
        "VST3_Plugins": Path(r"C:\Program Files\Common Files\VST3"),
        "VST2_Plugins": Path(r"C:\Program Files\Steinberg\VstPlugins"),
        "VST2_Plugins_Alt": Path(r"C:\Program Files\VSTPlugins"),
        "AE_Common_Plugins": Path(r"C:\Program Files\Adobe\Common\Plug-ins\7.0\MediaCore"),
        "AE_2026_Plugins": Path(r"C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\Plug-ins"),
        "AE_2026_Scripts": Path(r"C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\Scripts\ScriptUI Panels"),
        "CEP_User_Extensions": Path(os.environ.get("APPDATA", "")) / "Adobe" / "CEP" / "extensions",
        "CEP_System_Extensions": Path(r"C:\Program Files (x86)\Common Files\Adobe\CEP\extensions"),
        "CEP_System64_Extensions": Path(r"C:\Program Files\Common Files\Adobe\CEP\extensions"),
        "ProgramFiles": Path(r"C:\Program Files"),
        "ProgramFilesX86": Path(r"C:\Program Files (x86)"),
        "LocalAppData": Path(os.environ.get("LOCALAPPDATA", "")),
        "RoamingAppData": Path(os.environ.get("APPDATA", "")),
        "Drive_D": Path(r"D:"),
    }

    # Target keywords to match
    targets = {
        "DaVinci Resolve Studio": ["DaVinci Resolve", "Resolve.exe"],
        "Adobe After Effects": ["Adobe After Effects", "AfterFX.exe"],
        "Neat Video": ["Neat Video", "NeatVideo", "ReduceNoise"],
        "Topaz Video AI": ["Topaz Video AI", "Topaz", "videoai.exe", "ffmpeg.exe"],
        "Boris FX Sapphire": ["Sapphire", "GenArts", "BorisFX Sapphire"],
        "Boris FX Mocha Pro": ["Mocha Pro", "Mocha", "mocha.exe"],
        "GEOlayers 3": ["GEOlayers", "geolayers", "GEOlayers3"],
        "Submachine": ["Submachine", "submachine"],
        "Battle Axe Overlord": ["Overlord", "BattleAxe", "battleaxe"],
        "iZotope RX Advanced": ["iZotope", "RX", "RX 10", "RX 11", "iZotope RX"],
        "FabFilter (Pro-Q 3, Pro-L 2)": ["FabFilter", "Pro-Q 3", "Pro-L 2", "Pro-C 2", "Pro-MB"],
        "Waves Clarity VX": ["Waves", "Clarity VX", "Clarity", "WavesCentral"],
        "ActionVFX": ["ActionVFX", "Action VFX"],
        "True Grit Texture Supply": ["True Grit", "TrueGrit", "TGTS"],
        "Mister Horse (Animation Composer)": ["Mister Horse", "Animation Composer", "AnimationComposer"],
        "Soundly": ["Soundly", "Soundly.exe"]
    }

    results = {k: {"status": "NOT FOUND", "locations": []} for k in targets}

    # 1. Quick folder checks in known plugin directories
    for p_name, p_path in search_paths.items():
        if p_path.exists():
            print(f"[*] Scanning {p_name}: {p_path}")
            try:
                for item in p_path.rglob("*"):
                    item_str = str(item).lower()
                    for target_name, keywords in targets.items():
                        for kw in keywords:
                            if kw.lower() in item.name.lower():
                                if str(item) not in results[target_name]["locations"]:
                                    results[target_name]["locations"].append(str(item))
                                    results[target_name]["status"] = "FOUND"
            except Exception as e:
                print(f"    Error reading {p_path}: {e}")

    # 2. Check installed programs in Start Menu and Program Files specifically
    for target_name, keywords in targets.items():
        for kw in keywords:
            # Check Program Files
            cand1 = Path(r"C:\Program Files") / kw
            cand2 = Path(r"C:\Program Files (x86)") / kw
            cand3 = Path(r"D:\Program Files") / kw
            cand4 = Path(r"D:\AI_Tools") / kw
            for c in [cand1, cand2, cand3, cand4]:
                if c.exists() and str(c) not in results[target_name]["locations"]:
                    results[target_name]["locations"].append(str(c))
                    results[target_name]["status"] = "FOUND"

    print("\n" + "=" * 70)
    print("DETECTION SUMMARY:")
    print("=" * 70)
    for target, data in results.items():
        print(f"\n[{data['status']}] {target}")
        if data["locations"]:
            for loc in data["locations"][:6]:
                print(f"    -> {loc}")
            if len(data["locations"]) > 6:
                print(f"    ... and {len(data['locations']) - 6} more files.")

    # Save findings to json
    out_file = Path(r"C:\Users\jofin\.gemini\antigravity\scratch\creative_pipeline_bridge\pro_suite_detected.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Saved detection report to: {out_file}")

if __name__ == "__main__":
    scan_plugins()

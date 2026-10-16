import os
import sys
import json
from pathlib import Path

def audit_all():
    print("=" * 70)
    print("AUDITING DOWNLOADED VS INSTALLED PRO TOOLS & PLUGINS")
    print("=" * 70)

    # 1. Check installed applications and plugins
    installed_checks = {
        "DaVinci Resolve Studio": [
            Path(r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe")
        ],
        "Adobe After Effects": [
            Path(r"C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\AfterFX.exe")
        ],
        "Neat Video": [
            Path(r"C:\Program Files\Common Files\OFX\Plugins\NeatVideo6.ofx.bundle"),
            Path(r"C:\Program Files\Adobe\Common\Plug-ins\7.0\MediaCore\NeatVideo6")
        ],
        "Topaz Video AI": [
            Path(r"C:\Program Files\Topaz Labs LLC\Topaz Video AI\Topaz Video AI.exe"),
            Path(r"C:\Program Files\Topaz Labs LLC\Topaz Video AI Pro\Topaz Video AI Pro.exe")
        ],
        "Boris FX Sapphire": [
            Path(r"C:\Program Files\Common Files\OFX\Plugins\Sapphire.ofx.bundle"),
            Path(r"C:\Program Files\Adobe\Common\Plug-ins\7.0\MediaCore\Sapphire"),
            Path(r"C:\Program Files\BorisFX\Sapphire 2026")
        ],
        "Boris FX Mocha Pro": [
            Path(r"C:\Program Files\Adobe\Common\Plug-ins\7.0\MediaCore\MochaPro"),
            Path(r"C:\Program Files\Common Files\OFX\Plugins\MochaPro.ofx.bundle"),
            Path(r"C:\Program Files\BorisFX\Mocha Pro 2026")
        ],
        "GEOlayers 3": [
            Path(os.environ.get("APPDATA", "")) / "Adobe" / "CEP" / "extensions" / "GEOlayers 3",
            Path(r"C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\GEOlayers 3"),
            Path(r"C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\Scripts\ScriptUI Panels\GEOlayers 3.jsxbin")
        ],
        "Submachine": [
            Path(os.environ.get("APPDATA", "")) / "Adobe" / "CEP" / "extensions" / "Submachine",
            Path(r"C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\Submachine")
        ],
        "Battle Axe Overlord": [
            Path(os.environ.get("APPDATA", "")) / "Adobe" / "CEP" / "extensions" / "Overlord",
            Path(r"C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\Overlord")
        ],
        "iZotope RX Advanced": [
            Path(r"C:\Program Files\iZotope\RX 10 Audio Editor\win64\iZotope RX 10 Audio Editor.exe"),
            Path(r"C:\Program Files\iZotope\RX 11 Audio Editor\win64\iZotope RX 11 Audio Editor.exe"),
            Path(r"C:\Program Files\iZotope\RX 12 Audio Editor\win64\iZotope RX 12 Audio Editor.exe"),
            Path(r"C:\Program Files\Common Files\VST3\iZotope")
        ],
        "FabFilter Total Bundle": [
            Path(r"C:\Program Files\Common Files\VST3\FabFilter"),
            Path(r"C:\Program Files\FabFilter")
        ],
        "Waves Clarity VX": [
            Path(r"C:\Program Files\Common Files\VST3\WaveShell1-VST3 15.0_x64.vst3"),
            Path(r"C:\Program Files\WavesCentral\Waves Central.exe"),
            Path(r"C:\Program Files (x86)\Waves")
        ],
        "Mister Horse (Animation Composer)": [
            Path(r"C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\Scripts\ScriptUI Panels\Animation Composer.jsxbin"),
            Path(os.environ.get("APPDATA", "")) / "Mister Horse"
        ],
        "Soundly": [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Soundly" / "Soundly.exe",
            Path(r"C:\Program Files\Soundly\Soundly.exe")
        ]
    }

    print("\n--- 1. CHECKING INSTALLED STATUS ---")
    installed_results = {}
    for name, paths in installed_checks.items():
        found = []
        for p in paths:
            if p.exists():
                found.append(str(p))
            # Also check parent directory if it contains keyword
            parent = p.parent
            if parent.exists() and name.split()[0].lower() in parent.name.lower():
                found.append(str(parent))
        if found:
            installed_results[name] = {"status": "INSTALLED", "paths": found}
            print(f"[INSTALLED] {name}: {found[0]}")
        else:
            installed_results[name] = {"status": "NOT INSTALLED", "paths": []}
            print(f"[NOT INSTALLED] {name}")

    # 2. Check Downloads
    print("\n--- 2. CHECKING DOWNLOADED ARCHIVES / INSTALLERS ---")
    dl_dir = Path(r"C:\Users\jofin\Downloads")
    dl_map = {
        "DaVinci Resolve Studio": ["BlackmagicDesignDaVinciResolveStudio", "Resolve 21"],
        "Adobe After Effects": ["Adobe After Effects 2026"],
        "Neat Video": ["Neat Video"],
        "Topaz Video AI": ["Topaz Video AI"],
        "Boris FX Sapphire": ["Sapphire"],
        "Boris FX Mocha Pro": ["Mocha Pro"],
        "GEOlayers 3": ["GEOlayers"],
        "Submachine": ["Submachine"],
        "Battle Axe Overlord": ["Overlord"],
        "iZotope RX Advanced": ["iZotope RX"],
        "FabFilter Total Bundle": ["FabFilter"],
        "Waves Clarity VX": ["WavesUltimate"],
        "Mister Horse (Animation Composer)": ["Animation Composer", "Mister Horse"],
        "Soundly": ["soundly-setup"],
        "ActionVFX": ["ActionVFX"],
        "True Grit Texture Supply": ["True Grit", "TGTS"]
    }

    download_results = {}
    dl_files = list(dl_dir.iterdir())
    for target, kws in dl_map.items():
        matched = []
        for f in dl_files:
            for kw in kws:
                if kw.lower() in f.name.lower():
                    matched.append(f)
                    break
        if matched:
            download_results[target] = [str(m) for m in matched]
            print(f"[DOWNLOADED] {target}: {matched[0].name} ({matched[0].stat().st_size:,} bytes)")
        else:
            download_results[target] = []
            print(f"[MISSING DOWNLOAD] {target}")

    return installed_results, download_results

if __name__ == "__main__":
    audit_all()

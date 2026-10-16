import os
import sys
import zipfile
import shutil
from pathlib import Path
import win32com.client

def setup_desktop_suite():
    print("=" * 70)
    print("ORGANIZING CREATIVE SUITE & PLUGINS ON DESKTOP")
    print("=" * 70)

    desktop = Path(r"C:\Users\jofin\Desktop")
    suite_dir = desktop / "StickFacts_Creative_Suite"
    plugins_dir = suite_dir / "Plugins"

    suite_dir.mkdir(parents=True, exist_ok=True)
    plugins_dir.mkdir(parents=True, exist_ok=True)

    shell = win32com.client.Dispatch("WScript.Shell")

    def create_shortcut(target_exe: Path, lnk_path: Path, description: str):
        if target_exe.exists():
            shortcut = shell.CreateShortcut(str(lnk_path))
            shortcut.TargetPath = str(target_exe)
            shortcut.WorkingDirectory = str(target_exe.parent)
            shortcut.Description = description
            shortcut.Save()
            print(f"[+] Created Shortcut: {lnk_path.name} -> {target_exe}")

    # -------------------------------------------------------------
    # 1. CREATE SHORTCUTS FOR INSTALLED STANDALONE APPLICATIONS
    # -------------------------------------------------------------
    print("\n--- 1. CREATING APPLICATION SHORTCUTS ON DESKTOP ---")
    app_targets = [
        (Path(r"C:\Program Files\Topaz Labs LLC\Topaz Video AI\Topaz Video AI.exe"), suite_dir / "Topaz Video AI.lnk", "AI Video Upscaler & Enhancer"),
        (Path(r"C:\Program Files\iZotope\RX 12 Audio Editor\win64\iZotope RX 12 Audio Editor.exe"), suite_dir / "iZotope RX 12 Audio Editor.lnk", "Pro Audio Restoration & Spectral Editing"),
        (Path(r"C:\Program Files\Soundly\Soundly.exe"), suite_dir / "Soundly SFX Manager.lnk", "Sound Effects Browser & SFX Library"),
        (Path(r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"), suite_dir / "DaVinci Resolve Studio.lnk", "Video Editing, Fusion VFX & Fairlight Audio"),
        (Path(r"C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\AfterFX.exe"), suite_dir / "Adobe After Effects 2026.lnk", "Motion Graphics & Compositing"),
        (Path(r"C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe"), suite_dir / "Adobe Photoshop 2026.lnk", "2D Asset & Character Design")
    ]

    for exe, lnk, desc in app_targets:
        create_shortcut(exe, lnk, desc)

    # -------------------------------------------------------------
    # 2. EXTRACT & PLACE DOWNLOADED PLUGINS INTO Plugins/
    # -------------------------------------------------------------
    print("\n--- 2. ORGANIZING & EXTRACTING PLUGINS INTO Plugins/ ---")
    dl_dir = Path(r"C:\Users\jofin\Downloads")

    plugin_zips = [
        ("Neat_Video_Pro_Resolve", dl_dir / "Neat Video Pro 6.1.3 for Resolve [FileCR].zip"),
        ("FabFilter_Total_Bundle", dl_dir / "FabFilter Total Bundle 2026.06.25 [FileCR].zip"),
        ("GEOlayers_3", dl_dir / "Aescripts GEOlayers 3 v1.19.0 [FileCR].zip"),
        ("Battle_Axe_Overlord", dl_dir / "Battle Axe Overlord v2.7.3 (WiNMAC) for After Effects, Photoshop & Illustrator [FileCR].zip"),
        ("Boris_FX_Sapphire", dl_dir / "Boris FX Sapphire 2026.52 (x64) for Photoshop [FileCR].zip"),
        ("Boris_FX_Mocha_Pro", dl_dir / "Boris FX Mocha Pro 2026.5.1 (x64) for Adobe [FileCR].zip"),
        ("Waves_Ultimate_2026", dl_dir / "WavesUltimate20260727.zip")
    ]

    for folder_name, zip_path in plugin_zips:
        if zip_path.exists():
            target_extract = plugins_dir / folder_name
            target_extract.mkdir(parents=True, exist_ok=True)
            print(f"[*] Extracting {zip_path.name} -> {target_extract.name}/ ...")
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(target_extract)
                print(f"    [OK] Extracted {len(zf.namelist())} files.")
            except Exception as e:
                print(f"    [!] Extract failed (or large zip): {e}. Copying zip file directly.")
                shutil.copy2(zip_path, target_extract / zip_path.name)
        else:
            print(f"    [!] Not found in downloads: {zip_path.name}")

    # Copy standalone installers as well for convenience
    standalone_installers = [
        dl_dir / "soundly-setup.exe",
        dl_dir / "Topaz Video AI Pro 7.1.6 (x64) [FileCR].zip",
        dl_dir / "iZotope RX 12 Audio Editor Advanced 12.0.0 [FileCR].zip"
    ]
    installers_dir = suite_dir / "Installers"
    installers_dir.mkdir(parents=True, exist_ok=True)
    for inst in standalone_installers:
        if inst.exists():
            dst = installers_dir / inst.name
            if not dst.exists():
                print(f"[*] Copying {inst.name} -> Installers/")
                shutil.copy2(inst, dst)

    print("\n" + "=" * 70)
    print("DESKTOP SUITE SETUP COMPLETE!")
    print(f"Suite Directory:   {suite_dir}")
    print(f"Plugins Directory: {plugins_dir}")
    print("=" * 70)

if __name__ == "__main__":
    setup_desktop_suite()

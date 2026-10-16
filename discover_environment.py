import os
import sys
import winreg
import json
import glob
import urllib.request
import subprocess
from pathlib import Path

def query_reg_key(hkey, subkey, value_name=None):
    try:
        with winreg.OpenKey(hkey, subkey) as key:
            if value_name is None:
                val, _ = winreg.QueryValueEx(key, "")
            else:
                val, _ = winreg.QueryValueEx(key, value_name)
            return val
    except Exception:
        return None

def scan_registry_uninstall():
    installed = {}
    hkeys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    for root, path in hkeys:
        try:
            with winreg.OpenKey(root, path) as key:
                num_subkeys = winreg.QueryInfoKey(key)[0]
                for i in range(num_subkeys):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            display_name = None
                            install_loc = None
                            display_ver = None
                            uninstall_str = None
                            try:
                                display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            except Exception:
                                pass
                            try:
                                install_loc, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                            except Exception:
                                pass
                            try:
                                display_ver, _ = winreg.QueryValueEx(subkey, "DisplayVersion")
                            except Exception:
                                pass
                            try:
                                uninstall_str, _ = winreg.QueryValueEx(subkey, "UninstallString")
                            except Exception:
                                pass

                            if display_name:
                                name_lower = display_name.lower()
                                if any(target in name_lower for target in ["adobe", "photoshop", "illustrator", "animate", "after effects", "premiere", "moho", "comfy", "resolve"]):
                                    installed[display_name] = {
                                        "version": display_ver,
                                        "location": install_loc,
                                        "uninstall": uninstall_str
                                    }
                    except Exception:
                        continue
        except Exception:
            continue
    return installed

def scan_app_paths():
    results = {}
    exes = [
        "Photoshop.exe", "Illustrator.exe", "Animate.exe", 
        "AfterFX.exe", "aerender.exe", "Adobe Premiere Pro.exe", 
        "Moho.exe", "Resolve.exe", "ComfyUI.exe"
    ]
    for exe in exes:
        path = query_reg_key(winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe}")
        if path:
            results[exe] = path
    return results

def search_start_menu_shortcuts():
    shortcuts = {}
    dirs = [
        Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    ]
    for d in dirs:
        if d.exists():
            for p in d.rglob("*.lnk"):
                name_lower = p.name.lower()
                if any(t in name_lower for t in ["photoshop", "illustrator", "animate", "after effects", "premiere", "moho", "comfy", "resolve"]):
                    shortcuts[p.name] = str(p)
    return shortcuts

def check_comfy_api():
    url = "http://127.0.0.1:8188/system_stats"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'PipelineDiscovery'})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                return {"online": True, "stats": data}
    except Exception as e:
        return {"online": False, "error": str(e)}

def discover_adobe():
    adobe_root = Path("C:/Program Files/Adobe")
    adobe_apps = {}
    if adobe_root.exists():
        for item in adobe_root.iterdir():
            if item.is_dir():
                adobe_apps[item.name] = {
                    "path": str(item),
                    "files": [f.name for f in item.glob("*.exe")]
                }
                # Check for Support Files if applicable (e.g., Illustrator, After Effects)
                support_files = item / "Support Files"
                if support_files.exists():
                    adobe_apps[item.name]["support_files_exes"] = [f.name for f in support_files.glob("*.exe")]
                    contents_win = support_files / "Contents" / "Windows"
                    if contents_win.exists():
                        adobe_apps[item.name]["contents_win_exes"] = [f.name for f in contents_win.glob("*.exe")]
    return adobe_apps

def discover_moho():
    moho_candidates = [
        Path("C:/Program Files/Lost Marble"),
        Path("C:/Program Files/Victor Paredes"),
        Path("C:/Program Files/Smith Micro"),
        Path("C:/Program Files (x86)/Lost Marble"),
        Path("C:/Program Files (x86)/Smith Micro")
    ]
    found = []
    for cand in moho_candidates:
        if cand.exists():
            for sub in cand.iterdir():
                found.append({
                    "folder": str(sub),
                    "exes": [f.name for f in sub.glob("*.exe")],
                    "has_scripts": (sub / "Scripts").exists()
                })
    
    # Check User Documents for Custom Content folder
    docs = Path(os.environ.get("USERPROFILE", "")) / "Documents"
    moho_custom = []
    if docs.exists():
        for item in docs.glob("*Moho*"):
            moho_custom.append(str(item))

    # Check AppData
    appdata = Path(os.environ.get("APPDATA", ""))
    appdata_moho = []
    for match in appdata.glob("*Moho*"):
        appdata_moho.append(str(match))
    for sm in appdata.glob("*Lost Marble*"):
        appdata_moho.append(str(sm))

    return {
        "installations": found,
        "custom_content_docs": moho_custom,
        "appdata_paths": appdata_moho
    }

def discover_comfy():
    local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
    app_data = Path(os.environ.get("APPDATA", ""))
    user_prof = Path(os.environ.get("USERPROFILE", ""))

    candidates = [
        local_app_data / "Programs" / "comfyorgcomfyui-electron",
        local_app_data / "ComfyUI",
        app_data / "ComfyUI",
        user_prof / "ComfyUI",
        Path("C:/ComfyUI"),
        Path("C:/ComfyUI_windows_portable"),
        Path("D:/ComfyUI"),
        Path("D:/ComfyUI_windows_portable"),
        Path("E:/ComfyUI"),
        Path("E:/ComfyUI_windows_portable"),
    ]

    found = []
    for cand in candidates:
        if cand.exists():
            found.append({
                "path": str(cand),
                "is_dir": cand.is_dir(),
                "exes": [f.name for f in cand.glob("*.exe")] if cand.is_dir() else [],
                "has_main_py": (cand / "main.py").exists() if cand.is_dir() else False,
                "has_comfy": (cand / "ComfyUI" / "main.py").exists() if cand.is_dir() else False
            })

    api_status = check_comfy_api()
    return {
        "candidates_found": found,
        "api_status": api_status
    }

def discover_davinci():
    resolve_exe = Path("C:/Program Files/Blackmagic Design/DaVinci Resolve/Resolve.exe")
    scripting_mod = Path(os.environ.get("PROGRAMDATA", "C:/ProgramData")) / "Blackmagic Design" / "DaVinci Resolve" / "Support" / "Developer" / "Scripting" / "Modules" / "DaVinciResolveScript.py"
    return {
        "resolve_exe": str(resolve_exe) if resolve_exe.exists() else None,
        "scripting_module": str(scripting_mod) if scripting_mod.exists() else None
    }

def main():
    print("=" * 60)
    print("PHASE 1: ENVIRONMENT & PATH DISCOVERY")
    print("=" * 60)

    report = {
        "app_paths_registry": scan_app_paths(),
        "uninstall_registry": scan_registry_uninstall(),
        "start_menu_shortcuts": search_start_menu_shortcuts(),
        "adobe_folders": discover_adobe(),
        "moho": discover_moho(),
        "comfy": discover_comfy(),
        "davinci": discover_davinci()
    }

    out_path = Path("discovered_paths.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n[+] Raw discovery report saved to: {out_path.resolve()}\n")

    print("-" * 60)
    print("1. APP PATHS (Registry)")
    print("-" * 60)
    for exe, p in report["app_paths_registry"].items():
        print(f"  {exe:<25} -> {p}")

    print("\n" + "-" * 60)
    print("2. ADOBE APPLICATIONS (C:\\Program Files\\Adobe)")
    print("-" * 60)
    for name, info in report["adobe_folders"].items():
        exes = info.get("files", [])
        if "support_files_exes" in info:
            exes += [f"Support Files/{x}" for x in info["support_files_exes"]]
        if "contents_win_exes" in info:
            exes += [f"Support Files/Contents/Windows/{x}" for x in info["contents_win_exes"]]
        print(f"  {name:<35} : {', '.join(exes) if exes else 'No direct exes'}")

    print("\n" + "-" * 60)
    print("3. MOHO PRO")
    print("-" * 60)
    if report["moho"]["installations"]:
        for inst in report["moho"]["installations"]:
            print(f"  Install: {inst['folder']} (exes: {inst['exes']}, scripts: {inst['has_scripts']})")
    else:
        print("  No installation folder found in standard Program Files directories.")
    if report["moho"]["custom_content_docs"]:
        print(f"  User Docs Content: {report['moho']['custom_content_docs']}")
    if report["moho"]["appdata_paths"]:
        print(f"  AppData Paths: {report['moho']['appdata_paths']}")

    print("\n" + "-" * 60)
    print("4. COMFYUI")
    print("-" * 60)
    print(f"  API Status (127.0.0.1:8188): {report['comfy']['api_status']}")
    if report["comfy"]["candidates_found"]:
        for c in report["comfy"]["candidates_found"]:
            print(f"  Path: {c['path']} (exes: {c['exes']}, main.py: {c['has_main_py']}, comfy/main.py: {c['has_comfy']})")
    else:
        print("  No installation directory found in standard candidate paths.")

    print("\n" + "-" * 60)
    print("5. DAVINCI RESOLVE (For Reference)")
    print("-" * 60)
    print(f"  Resolve.exe: {report['davinci']['resolve_exe']}")
    print(f"  DaVinciResolveScript.py: {report['davinci']['scripting_module']}")

    print("\n" + "-" * 60)
    print("6. INSTALLED UNINSTALL REGISTRY ENTRIES (Summary)")
    print("-" * 60)
    for name, details in report["uninstall_registry"].items():
        print(f"  {name} (v{details.get('version')}) -> {details.get('location')}")

if __name__ == "__main__":
    main()

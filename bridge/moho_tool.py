import os
import sys
import zipfile
import json
import uuid
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from .config_loader import get_config
from .photoshop_tool import CHARACTER_RIG_LAYERS

class MohoTool:
    def __init__(self):
        cfg = get_config()
        self.app_cfg = cfg.get_app("moho")
        self.exe_path = Path(self.app_cfg.get("exe", "C:/Program Files/Moho 14/Moho.exe"))
        self.scripts_dir = Path(self.app_cfg.get("scripts_dir", "C:/Program Files/Moho 14/Resources/Support/Scripts"))

    # ==========================================
    # 1. DIRECT PROJECT MANIPULATION (ZIP / JSON)
    # ==========================================

    def read_project(self, moho_path: Path) -> Dict[str, Any]:
        """
        Unpacks and parses Project.mohoproj from a .moho archive.
        """
        if not moho_path.exists():
            raise FileNotFoundError(f"Moho file not found: {moho_path}")

        if zipfile.is_zipfile(moho_path):
            with zipfile.ZipFile(moho_path, "r") as z:
                if "Project.mohoproj" not in z.namelist():
                    raise ValueError(f"Invalid .moho file (missing Project.mohoproj): {moho_path}")
                raw = z.read("Project.mohoproj")
                return json.loads(raw.decode("utf-8"))
        else:
            # Handle uncompressed JSON
            with open(moho_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def write_project(
        self,
        moho_data: Dict[str, Any],
        output_moho_path: Path,
        preview_jpg: Optional[bytes] = None
    ) -> Path:
        """
        Packs Project.mohoproj (+ optional preview.jpg) into a compliant .moho ZIP archive.
        """
        output_moho_path.parent.mkdir(parents=True, exist_ok=True)
        json_bytes = json.dumps(moho_data, ensure_ascii=False, indent=2).encode("utf-8")

        with zipfile.ZipFile(output_moho_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("Project.mohoproj", json_bytes)
            if preview_jpg:
                z.writestr("preview.jpg", preview_jpg)

        return output_moho_path

    def create_character_project(
        self,
        output_path: Path,
        name: str = "Character_Rig",
        width: int = 3840,
        height: int = 2160,
        fps: float = 24.0,
        layers: Optional[List[str]] = None
    ) -> Path:
        """
        Builds a programmatic, schema-compliant Moho project with root BoneLayer,
        hierarchical skeleton (Torso -> Head, Arms, Legs), and separate child layers.
        """
        parts = layers or CHARACTER_RIG_LAYERS
        
        # Skeleton bones with parent links
        # Index 0: Root / Torso (parent -1)
        # Index 1: Head (parent 0)
        # Index 2: UpperArm_L (parent 0), 3: LowerArm_L (parent 2), 4: Hand_L (parent 3)
        # Index 5: UpperArm_R (parent 0), 6: LowerArm_R (parent 5), 7: Hand_R (parent 6)
        # Index 8: UpperLeg_L (parent 0), 9: LowerLeg_L (parent 8), 10: Foot_L (parent 9)
        # Index 11: UpperLeg_R (parent 0), 12: LowerLeg_R (parent 11), 13: Foot_R (parent 12)
        parent_map = {
            "Torso": -1,
            "Head": 0,
            "UpperArm_L": 0,
            "LowerArm_L": 2,
            "Hand_L": 3,
            "UpperArm_R": 0,
            "LowerArm_R": 5,
            "Hand_R": 6,
            "UpperLeg_L": 0,
            "LowerLeg_L": 8,
            "Foot_L": 9,
            "UpperLeg_R": 0,
            "LowerLeg_R": 11,
            "Foot_R": 12
        }

        bones = []
        for i, part in enumerate(parts):
            bones.append({
                "name": part,
                "parent": parent_map.get(part, -1),
                "length": 0.2,
                "strength": 0.25,
                "pos": [0.0, 0.0],
                "angle": 0.0,
                "color": 0,
                "ignored_by_layer_picker": False
            })

        child_layers = []
        for part in parts:
            child_layers.append({
                "type": "MeshLayer",
                "name": part,
                "uuid": str(uuid.uuid4()),
                "visible": True,
                "origin": [0.0, 0.0, 0.0],
                "parent_bone": parent_map.get(part, -1),
                "mesh": {
                    "points": [],
                    "curves": [],
                    "shapes": []
                }
            })

        root_bone_layer = {
            "type": "BoneLayer",
            "name": name,
            "uuid": str(uuid.uuid4()),
            "visible": True,
            "origin": [0.0, 0.0, 0.0],
            "skeleton": {
                "bones": bones
            },
            "layers": child_layers
        }

        moho_doc = {
            "mime_type": "application/x-vnd.lm_mohodoc",
            "version": 1040,
            "major_version": 1,
            "rev_version": 0,
            "comment": "Generated programmatically by Creative Pipeline Bridge",
            "doc_uuid": str(uuid.uuid4()),
            "created_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "modified_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_data": {
                "width": width,
                "height": height,
                "start_frame": 1,
                "end_frame": 240,
                "fps": fps,
                "back_color": [1.0, 1.0, 1.0, 1.0],
                "antialiasing": True
            },
            "layers": [root_bone_layer]
        }

        return self.write_project(moho_doc, output_path)

    # ==========================================
    # 2. LUA SCRIPTING API & CLI RUNNER
    # ==========================================

    def create_lua_script(
        self,
        output_script_path: Path,
        script_body: str
    ) -> Path:
        output_script_path.parent.mkdir(parents=True, exist_ok=True)
        content = f"""-- Auto-generated Moho Lua Automation Script
function MohoScript(moho)
{script_body}
end
"""
        output_script_path.write_text(content, encoding="utf-8")
        return output_script_path

    def run_lua_script(
        self,
        script_path: Path,
        moho_doc_path: Optional[Path] = None,
        timeout: float = 30.0
    ) -> subprocess.CompletedProcess:
        if not self.exe_path.exists():
            raise FileNotFoundError(f"Moho executable not found at: {self.exe_path}")

        cmd = [str(self.exe_path)]
        if moho_doc_path:
            cmd.append(str(moho_doc_path.resolve()))
        cmd.append(str(script_path.resolve()))

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

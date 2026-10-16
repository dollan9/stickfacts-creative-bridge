import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

from .config_loader import get_config
from .photoshop_tool import CHARACTER_RIG_LAYERS

class AnimateTool:
    def __init__(self):
        cfg = get_config()
        self.app_cfg = cfg.get_app("animate")
        self.exe_path = Path(self.app_cfg.get("exe", "C:/Program Files/Adobe/Adobe Animate 2024/Animate.exe"))
        
        # User local Commands directory (sv_SE language folder verified on this system)
        local_app = Path(os.environ.get("LOCALAPPDATA", "C:/Users/jofin/AppData/Local"))
        self.commands_dir = local_app / "Adobe" / "Animate 2024" / "sv_SE" / "Configuration" / "Commands"
        if not self.commands_dir.exists():
            # Fallback to en_US if sv_SE does not exist
            self.commands_dir = local_app / "Adobe" / "Animate 2024" / "en_US" / "Configuration" / "Commands"

    @staticmethod
    def to_jsfl_uri(path: Path) -> str:
        """
        Converts Windows path to official Animate URI format:
        file:///c:/path/to/file
        """
        resolved = str(path.resolve()).replace("\\", "/")
        return f"file:///{resolved}"

    def install_command_script(self, command_name: str, jsfl_content: str) -> Path:
        """
        Deploys a JSFL script directly into Animate's native Commands folder.
        This makes it instantly accessible in Animate's Commands menu and IPC.
        """
        self.commands_dir.mkdir(parents=True, exist_ok=True)
        target_path = self.commands_dir / f"{command_name}.jsfl"
        target_path.write_text(jsfl_content, encoding="utf-8")
        return target_path

    def generate_character_fla_jsfl(
        self,
        output_fla_path: Path,
        width: int = 1920,
        height: int = 1080,
        fps: int = 24,
        layers: Optional[List[str]] = None,
        close_when_done: bool = True
    ) -> str:
        layer_list = layers or CHARACTER_RIG_LAYERS
        fla_uri = self.to_jsfl_uri(output_fla_path)
        layers_array_str = str(layer_list).replace("'", '"')

        jsfl = f"""// Adobe Animate Character Rig Generator
(function() {{
    var doc = fl.createDocument();
    doc.width = {width};
    doc.height = {height};
    doc.frameRate = {fps};

    var timeline = doc.getTimeline();
    var layerNames = {layers_array_str};

    // Name the root layer
    timeline.layers[0].name = layerNames[layerNames.length - 1];

    // Add character rig layers in hierarchical order
    for (var i = layerNames.length - 2; i >= 0; i--) {{
        timeline.addNewLayer(layerNames[i], "normal", true);
    }}

    // Save document to destination
    var saveURI = "{fla_uri}";
    fl.saveDocument(doc, saveURI);

    if ({str(close_when_done).lower()}) {{
        fl.closeDocument(doc, false);
    }}
}})();
"""
        return jsfl

    def execute_jsfl(self, jsfl_path: Path, timeout: float = 30.0) -> subprocess.CompletedProcess:
        """
        Executes JSFL script via Animate.exe with official flags --run-jsfl and -AlwaysRunJSFL.
        """
        cmd = [
            str(self.exe_path),
            "--run-jsfl",
            str(jsfl_path.resolve()),
            "-AlwaysRunJSFL"
        ]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

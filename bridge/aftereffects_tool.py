import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from .config_loader import get_config

class AfterEffectsTool:
    def __init__(self):
        cfg = get_config()
        self.app_cfg = cfg.get_app("after_effects")
        self.afterfx_exe = Path(self.app_cfg.get("afterfx_exe", "C:/Program Files/Adobe/Adobe After Effects 2026/Support Files/AfterFX.exe"))
        self.aerender_exe = Path(self.app_cfg.get("aerender_exe", "C:/Program Files/Adobe/Adobe After Effects 2026/Support Files/aerender.exe"))

        if not self.afterfx_exe.exists():
            raise FileNotFoundError(f"AfterFX.exe not found: {self.afterfx_exe}")
        if not self.aerender_exe.exists():
            raise FileNotFoundError(f"aerender.exe not found: {self.aerender_exe}")

    def generate_composition_jsx(
        self,
        output_aep_path: Path,
        comp_name: str = "Main_Comp",
        width: int = 3840,
        height: int = 2160,
        fps: float = 24.0,
        duration_secs: float = 5.0,
        background_path: Optional[Path] = None,
        character_pass_paths: Optional[List[Path]] = None,
        apply_camera_shake: bool = True,
        output_render_path: Optional[Path] = None
    ) -> str:
        aep_norm = str(output_aep_path.resolve()).replace("\\", "/")
        bg_norm = str(background_path.resolve()).replace("\\", "/") if background_path else ""
        render_norm = str(output_render_path.resolve()).replace("\\", "/") if output_render_path else ""
        
        char_passes_js = "[]"
        if character_pass_paths:
            paths_list = [str(p.resolve()).replace("\\", "/") for p in character_pass_paths]
            char_passes_js = str(paths_list).replace("'", '"')

        jsx = f"""
        (function() {{
            // Create new project
            app.newProject();

            // Create main composition
            var comp = app.project.items.addComp(
                "{comp_name}",
                {width},
                {height},
                1.0, // Pixel aspect ratio
                {duration_secs},
                {fps}
            );

            // Import and add background layer if provided
            var bgPath = "{bg_norm}";
            if (bgPath !== "") {{
                var bgFile = new File(bgPath);
                if (bgFile.exists) {{
                    var importOptions = new ImportOptions(bgFile);
                    var bgItem = app.project.importFile(importOptions);
                    var bgLayer = comp.layers.add(bgItem);
                    bgLayer.moveToEnd();
                }}
            }}

            // Import character passes
            var charPaths = {char_passes_js};
            for (var i = 0; i < charPaths.length; i++) {{
                var cFile = new File(charPaths[i]);
                if (cFile.exists) {{
                    var cOpt = new ImportOptions(cFile);
                    var cItem = app.project.importFile(cOpt);
                    var cLayer = comp.layers.add(cItem);
                }}
            }}

            // Apply camera shake via null and expression
            if ({str(apply_camera_shake).lower()}) {{
                var nullLayer = comp.layers.addNull();
                nullLayer.name = "Camera_Controller";
                nullLayer.property("Position").expression = "wiggle(2, 25);";
                // Parent all other layers to camera controller
                for (var j = 1; j <= comp.layers.length; j++) {{
                    var l = comp.layers[j];
                    if (l !== nullLayer) {{
                        l.parent = nullLayer;
                    }}
                }}
            }}

            // Setup Render Queue item if render path provided
            var renderPath = "{render_norm}";
            if (renderPath !== "") {{
                var rqItem = app.project.renderQueue.items.add(comp);
                if (rqItem.outputModules.length > 0) {{
                    rqItem.outputModules[1].file = new File(renderPath);
                }}
            }}

            // Save AEP file
            var saveFile = new File("{aep_norm}");
            app.project.save(saveFile);
        }})();
        """
        return jsx

    def run_script(self, jsx_content: str, timeout: float = 60.0) -> subprocess.CompletedProcess:
        out_dir = get_config().get_output_dir()
        jsx_file = out_dir / f"ae_script_{int(time.time()*1000)}.jsx"
        jsx_file.write_text(jsx_content, encoding="utf-8")

        cmd = [str(self.afterfx_exe), "-r", str(jsx_file.resolve())]
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        finally:
            if jsx_file.exists():
                try:
                    jsx_file.unlink()
                except Exception:
                    pass

    def batch_render(
        self,
        project_path: Path,
        comp_name: Optional[str] = None,
        output_path: Optional[Path] = None,
        start_frame: Optional[int] = None,
        end_frame: Optional[int] = None,
        timeout: float = 180.0
    ) -> subprocess.CompletedProcess:
        """
        Executes aerender.exe batch render with verified flags.
        """
        cmd = [
            str(self.aerender_exe),
            "-project", str(project_path.resolve()),
            "-close", "DO_NOT_SAVE_CHANGES",
            "-continueOnMissingFootage"
        ]

        if comp_name:
            cmd.extend(["-comp", comp_name])
        if output_path:
            cmd.extend(["-output", str(output_path.resolve())])
        if start_frame is not None:
            cmd.extend(["-s", str(start_frame)])
        if end_frame is not None:
            cmd.extend(["-e", str(end_frame)])

        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

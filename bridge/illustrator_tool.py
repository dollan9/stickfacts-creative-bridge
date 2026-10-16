import os
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import win32com.client

from .config_loader import get_config
from .photoshop_tool import CHARACTER_RIG_LAYERS

class IllustratorTool:
    def __init__(self):
        cfg = get_config()
        self.app_cfg = cfg.get_app("illustrator")
        self.progid = self.app_cfg.get("com_progid", "Illustrator.Application")
        self._app = None

    def get_app(self, retries: int = 5, delay: float = 2.0):
        if self._app is not None:
            return self._app
        
        last_err = None
        for attempt in range(retries):
            try:
                self._app = win32com.client.Dispatch(self.progid)
                break
            except Exception as e:
                last_err = e
                time.sleep(delay)
                    
        if self._app is None:
            raise RuntimeError(f"Failed to connect to Illustrator via COM ({self.progid}): {last_err}")
        return self._app

    def quit_app(self):
        if self._app is not None:
            try:
                self._app.Quit()
            except Exception:
                pass
            self._app = None

    def execute_jsx(self, jsx_body: str) -> Any:
        app = self.get_app()
        full_jsx = f"""
        (function() {{
            try {{
                app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
            }} catch(e) {{}}
            {jsx_body}
        }})();
        """
        try:
            return app.DoJavaScript(full_jsx)
        except Exception as e:
            raise RuntimeError(f"Illustrator JSX Execution Failed:\n{full_jsx}\nError: {e}")

    def create_character_document(
        self,
        width: int = 3840,
        height: int = 2160,
        doc_name: str = "Character_Vector",
        layers: Optional[List[str]] = None
    ) -> str:
        layer_list = layers or CHARACTER_RIG_LAYERS
        layers_json = str(layer_list).replace("'", '"')

        body = f"""
        var docPreset = new DocumentPreset();
        docPreset.title = "{doc_name}";
        docPreset.width = {width};
        docPreset.height = {height};
        docPreset.units = RulerUnits.Pixels;
        docPreset.colorMode = DocumentColorSpace.RGB;

        var newDoc = app.documents.addDocument(DocumentColorSpace.RGB, docPreset);

        var layerNames = {layers_json};
        for (var i = layerNames.length - 1; i >= 0; i--) {{
            var l = newDoc.layers.add();
            l.name = layerNames[i];
        }}

        return "SUCCESS: Created Illustrator document with " + layerNames.length + " layers.";
        """
        return self.execute_jsx(body)

    def draw_sample_vector(self, layer_name: str, x: float, y: float, w: float, h: float, r: int = 255, g: int = 100, b: int = 50) -> str:
        body = f"""
        var doc = app.activeDocument;
        var targetLayer = null;
        try {{
            targetLayer = doc.layers.getByName("{layer_name}");
        }} catch(e) {{
            targetLayer = doc.layers[0];
        }}

        var rect = targetLayer.pathItems.rectangle({y}, {x}, {w}, {h});
        var color = new RGBColor();
        color.red = {r};
        color.green = {g};
        color.blue = {b};
        rect.fillColor = color;
        rect.stroked = false;

        return "SUCCESS: Drawn vector rectangle on layer " + targetLayer.name;
        """
        return self.execute_jsx(body)

    def save_as_ai(self, destination_path: Path) -> str:
        dest_norm = str(destination_path.resolve()).replace("\\", "/")
        parent_dir = str(destination_path.resolve().parent).replace("\\", "/")
        body = f"""
        var doc = app.activeDocument;
        var folder = new Folder("{parent_dir}");
        if (!folder.exists) folder.create();

        var saveFile = new File("{dest_norm}");
        var saveOpts = new IllustratorSaveOptions();
        saveOpts.pdfCompatible = true;
        saveOpts.compressed = true;

        doc.saveAs(saveFile, saveOpts);
        return "SUCCESS: Saved AI file to {dest_norm}";
        """
        return self.execute_jsx(body)

    def export_svg(self, destination_path: Path) -> str:
        dest_norm = str(destination_path.resolve()).replace("\\", "/")
        parent_dir = str(destination_path.resolve().parent).replace("\\", "/")
        body = f"""
        var doc = app.activeDocument;
        var folder = new Folder("{parent_dir}");
        if (!folder.exists) folder.create();

        var exportFile = new File("{dest_norm}");
        var exportOpts = new ExportOptionsSVG();
        exportOpts.embedRasterImages = true;
        exportOpts.fontSubsetting = SVGFontSubsetting.GLYPHSUSED;

        doc.exportFile(exportFile, ExportType.SVG, exportOpts);
        return "SUCCESS: Exported SVG to {dest_norm}";
        """
        return self.execute_jsx(body)

    def close_all_documents(self, save: bool = False) -> str:
        save_opt = "SaveOptions.SAVECHANGES" if save else "SaveOptions.DONOTSAVECHANGES"
        body = f"""
        var count = 0;
        while (app.documents.length > 0) {{
            app.activeDocument.close({save_opt});
            count++;
        }}
        return "SUCCESS: Closed " + count + " document(s)";
        """
        return self.execute_jsx(body)

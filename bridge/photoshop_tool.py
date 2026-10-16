import os
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import win32com.client

from .config_loader import get_config

CHARACTER_RIG_LAYERS = [
    "Head",
    "Torso",
    "UpperArm_L",
    "LowerArm_L",
    "Hand_L",
    "UpperArm_R",
    "LowerArm_R",
    "Hand_R",
    "UpperLeg_L",
    "LowerLeg_L",
    "Foot_L",
    "UpperLeg_R",
    "LowerLeg_R",
    "Foot_R"
]

class PhotoshopTool:
    def __init__(self):
        cfg = get_config()
        self.app_cfg = cfg.get_app("photoshop")
        self.progid = self.app_cfg.get("com_progid", "Photoshop.Application")
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
            raise RuntimeError(f"Failed to connect to Photoshop via COM ({self.progid}): {last_err}")
            
        try:
            self._app.DisplayDialogs = 3 # psDisplayNoDialogs
        except Exception:
            pass
            
        return self._app

    def quit_app(self):
        if self._app is not None:
            try:
                self._app.Quit()
            except Exception:
                pass
            self._app = None

    def execute_jsx(self, jsx_code: str) -> Any:
        app = self.get_app()
        try:
            return app.DoJavaScript(jsx_code)
        except Exception as e:
            raise RuntimeError(f"Photoshop JSX Execution Failed:\n{jsx_code}\nError: {e}")

    def create_character_rig_document(
        self,
        width: int = 3840,
        height: int = 2160,
        dpi: int = 300,
        doc_name: str = "Character_Rig",
        layers: Optional[List[str]] = None
    ) -> str:
        layer_list = layers or CHARACTER_RIG_LAYERS
        layers_json = str(layer_list).replace("'", '"')

        jsx = f"""
        (function() {{
            var docName = "{doc_name}";
            var width = {width};
            var height = {height};
            var resolution = {dpi};
            var layers = {layers_json};

            // Units: Pixels
            app.preferences.rulerUnits = Units.PIXELS;

            // Create document (RGB, 8-bit, Transparent fill)
            var newDoc = app.documents.add(
                UnitValue(width, "px"),
                UnitValue(height, "px"),
                resolution,
                docName,
                NewDocumentMode.RGB,
                DocumentFill.TRANSPARENT
            );

            // Group: Character Rig
            var charGroup = newDoc.layerSets.add();
            charGroup.name = "Character_Rig";

            // Add each specific character layer in reverse order so top is on top
            for (var i = layers.length - 1; i >= 0; i--) {{
                var artLayer = charGroup.artLayers.add();
                artLayer.name = layers[i];
            }}

            return "SUCCESS: Created " + docName + " with " + layers.length + " layers.";
        }})();
        """
        return self.execute_jsx(jsx)

    def import_and_place_image(self, image_path: Path, target_layer: str) -> str:
        normalized_path = str(image_path).replace("\\", "/")
        jsx = f"""
        (function() {{
            var doc = app.activeDocument;
            var fileRef = new File("{normalized_path}");
            if (!fileRef.exists) {{
                return "ERROR: File not found: " + "{normalized_path}";
            }}

            // Open the asset document
            var assetDoc = app.open(fileRef);
            assetDoc.selection.selectAll();
            assetDoc.selection.copy();
            assetDoc.close(SaveOptions.DONOTSAVECHANGES);

            // Activate original document and find layer
            app.activeDocument = doc;
            var layerFound = null;
            try {{
                layerFound = doc.artLayers.getByName("{target_layer}");
            }} catch(e) {{
                // Try searching in layer sets
                for (var i = 0; i < doc.layerSets.length; i++) {{
                    try {{
                        layerFound = doc.layerSets[i].artLayers.getByName("{target_layer}");
                        if (layerFound) break;
                    }} catch(e2) {{}}
                }}
            }}

            if (layerFound) {{
                doc.activeLayer = layerFound;
            }}
            doc.paste();
            if (doc.activeLayer && layerFound) {{
                doc.activeLayer.name = "{target_layer}_Asset";
            }}
            return "SUCCESS: Placed asset into {target_layer}";
        }})();
        """
        return self.execute_jsx(jsx)

    def select_subject_and_isolate(self) -> str:
        """
        Executes Photoshop's native Select Subject ActionDescriptor and inverts/clears background.
        """
        jsx = """
        (function() {
            var doc = app.activeDocument;
            try {
                // Execute Select Subject command
                var desc = new ActionDescriptor();
                var idautoCutout = stringIDToTypeID("autoCutout");
                var idsampleAllLayers = stringIDToTypeID("sampleAllLayers");
                desc.putBoolean(idsampleAllLayers, false);
                executeAction(idautoCutout, desc, DialogModes.NO);

                return "SUCCESS: Subject selected";
            } catch(e) {
                return "FALLBACK: Native subject selection failed: " + e.message;
            }
        })();
        """
        return self.execute_jsx(jsx)

    def save_as_psd(self, destination_path: Path) -> str:
        dest_norm = str(destination_path.resolve()).replace("\\", "/")
        parent_dir = str(destination_path.resolve().parent).replace("\\", "/")
        jsx = f"""
        (function() {{
            var doc = app.activeDocument;
            var folder = new Folder("{parent_dir}");
            if (!folder.exists) {{
                folder.create();
            }}
            var saveFile = new File("{dest_norm}");
            var psdOptions = new PhotoshopSaveOptions();
            psdOptions.embedColorProfile = true;
            psdOptions.alphaChannels = true;
            psdOptions.layers = true;
            psdOptions.spotColors = true;

            doc.saveAs(saveFile, psdOptions, true, Extension.LOWERCASE);
            return "SUCCESS: Saved PSD to {dest_norm}";
        }})();
        """
        return self.execute_jsx(jsx)

    def export_layers_as_png(self, output_dir: Path) -> List[Path]:
        out_norm = str(output_dir.resolve()).replace("\\", "/")
        output_dir.mkdir(parents=True, exist_ok=True)
        jsx = f"""
        (function() {{
            var doc = app.activeDocument;
            var exportFolder = new Folder("{out_norm}");
            if (!exportFolder.exists) exportFolder.create();

            var exportedFiles = [];
            
            function exportLayerRec(parent) {{
                for (var i = 0; i < parent.artLayers.length; i++) {{
                    var layer = parent.artLayers[i];
                    var origVisible = layer.visible;
                    
                    // Hide all other artlayers
                    for (var j = 0; j < parent.artLayers.length; j++) {{
                        parent.artLayers[j].visible = (j === i);
                    }}
                    
                    var pngFile = new File("{out_norm}/" + layer.name + ".png");
                    var pngOptions = new ExportOptionsSaveForWeb();
                    pngOptions.format = SaveDocumentType.PNG;
                    pngOptions.PNG8 = false;
                    pngOptions.transparency = true;
                    pngOptions.interlaced = false;
                    pngOptions.includeProfile = false;

                    doc.exportDocument(pngFile, ExportType.SAVEFORWEB, pngOptions);
                    exportedFiles.push(pngFile.fsName);
                    
                    layer.visible = origVisible;
                }}
                for (var k = 0; k < parent.layerSets.length; k++) {{
                    exportLayerRec(parent.layerSets[k]);
                }}
            }}

            exportLayerRec(doc);
            return exportedFiles.join("|||");
        }})();
        """
        result = self.execute_jsx(jsx)
        if result and "|||" in str(result):
            return [Path(p) for p in str(result).split("|||") if p]
        elif result:
            return [Path(result)]
        return []

    def close_active_document(self, save: bool = False) -> str:
        save_opt = "SaveOptions.SAVECHANGES" if save else "SaveOptions.DONOTSAVECHANGES"
        jsx = f"""
        (function() {{
            if (app.documents.length > 0) {{
                app.activeDocument.close({save_opt});
                return "SUCCESS: Closed active document";
            }}
            return "NO_DOCUMENT";
        }})();
        """
        return self.execute_jsx(jsx)

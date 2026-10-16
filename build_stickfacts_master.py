import os
import sys
import math
import json
import uuid
import time
import zipfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bridge.photoshop_tool import PhotoshopTool
from bridge.config_loader import get_config

def build_stickfacts_character():
    print("=" * 65)
    print("STICKFACTS MASTER CHARACTER & RIG GENERATOR")
    print("=" * 65)

    out_dir = Path(r"C:\Users\jofin\.gemini\antigravity\scratch\creative_pipeline_bridge\output")
    out_dir.mkdir(parents=True, exist_ok=True)

    psd_path = out_dir / "StickFacts_Master_Character.psd"
    png_path = out_dir / "StickFacts_Preview.png"
    moho_path = out_dir / "StickFacts_Master_Rig.moho"

    print(f"[*] Target PSD:  {psd_path}")
    print(f"[*] Target PNG:  {png_path}")
    print(f"[*] Target MOHO: {moho_path}")

    # -------------------------------------------------------------
    # 1. PHOTOSHOP 4K MASTER CHARACTER GENERATION VIA EXTENDSCRIPT
    # -------------------------------------------------------------
    print("\n[1/3] Connecting to Adobe Photoshop 2026 via COM...")
    ps_tool = PhotoshopTool()
    ps = ps_tool.get_app()
    print(f"      Photoshop Instance: {ps.Name} v{ps.Version}")

    psd_norm = str(psd_path.resolve()).replace("\\", "/")
    png_norm = str(png_path.resolve()).replace("\\", "/")

    jsx_script = f"""
    (function() {{
        app.displayDialogs = DialogModes.NO;
        app.preferences.rulerUnits = Units.PIXELS;

        var doc = app.documents.add(
            UnitValue(3840, "px"),
            UnitValue(2160, "px"),
            300,
            "StickFacts_Master_Character",
            NewDocumentMode.RGB,
            DocumentFill.TRANSPARENT
        );

        // Helper: Colors
        var colCharcoal = new SolidColor();
        colCharcoal.rgb.hexValue = "1A1A1A";

        var colWhite = new SolidColor();
        colWhite.rgb.hexValue = "FFFFFF";

        var colCyan = new SolidColor();
        colCyan.rgb.hexValue = "00E5FF"; // Official StickFacts Cyan

        var colCyanDark = new SolidColor();
        colCyanDark.rgb.hexValue = "00B4D8";

        // Geometry Helpers
        function circlePts(cx, cy, r, segments) {{
            var segs = segments || 32;
            var pts = [];
            for (var i = 0; i < segs; i++) {{
                var a = (i / segs) * 2 * Math.PI;
                pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
            }}
            return pts;
        }}

        function capsulePts(x1, y1, x2, y2, radius) {{
            var dx = x2 - x1;
            var dy = y2 - y1;
            var len = Math.sqrt(dx * dx + dy * dy);
            if (len === 0) return circlePts(x1, y1, radius);

            var nx = -dy / len;
            var ny = dx / len;

            var pts = [];
            // Cap at (x1, y1)
            var startAngle = Math.atan2(ny, nx);
            for (var i = 0; i <= 16; i++) {{
                var a = startAngle + (i / 16) * Math.PI;
                pts.push([x1 + radius * Math.cos(a), y1 + radius * Math.sin(a)]);
            }}
            // Cap at (x2, y2)
            for (var j = 0; j <= 16; j++) {{
                var b = startAngle + Math.PI + (j / 16) * Math.PI;
                pts.push([x2 + radius * Math.cos(b), y2 + radius * Math.sin(b)]);
            }}
            return pts;
        }}

        // Character Rig Group
        var rigGroup = doc.layerSets.add();
        rigGroup.name = "StickFacts_Character_Rig";

        function addLayer(name) {{
            var l = rigGroup.artLayers.add();
            l.name = name;
            return l;
        }}

        // ==========================================
        // DRAW LAYERS (From back to front)
        // ==========================================

        // 1. Torso
        var layerTorso = addLayer("Torso");
        doc.selection.select(capsulePts(1920, 950, 1920, 1420, 24));
        doc.selection.fill(colCharcoal);

        // 2. UpperLeg_L & LowerLeg_L & Foot_L
        var lUpperLegL = addLayer("UpperLeg_L");
        doc.selection.select(capsulePts(1850, 1420, 1820, 1700, 22));
        doc.selection.fill(colCharcoal);

        var lLowerLegL = addLayer("LowerLeg_L");
        doc.selection.select(capsulePts(1820, 1700, 1800, 1980, 20));
        doc.selection.fill(colCharcoal);

        var lFootL = addLayer("Foot_L");
        doc.selection.select(capsulePts(1800, 1980, 1720, 2000, 26));
        doc.selection.fill(colCharcoal);

        // 3. UpperLeg_R & LowerLeg_R & Foot_R
        var lUpperLegR = addLayer("UpperLeg_R");
        doc.selection.select(capsulePts(1990, 1420, 2020, 1700, 22));
        doc.selection.fill(colCharcoal);

        var lLowerLegR = addLayer("LowerLeg_R");
        doc.selection.select(capsulePts(2020, 1700, 2040, 1980, 20));
        doc.selection.fill(colCharcoal);

        var lFootR = addLayer("Foot_R");
        doc.selection.select(capsulePts(2040, 1980, 2120, 2000, 26));
        doc.selection.fill(colCharcoal);

        // 4. UpperArm_L & LowerArm_L & Hand_L
        var lUpperArmL = addLayer("UpperArm_L");
        doc.selection.select(capsulePts(1900, 980, 1700, 1150, 20));
        doc.selection.fill(colCharcoal);

        var lLowerArmL = addLayer("LowerArm_L");
        doc.selection.select(capsulePts(1700, 1150, 1600, 1380, 18));
        doc.selection.fill(colCharcoal);

        var lHandL = addLayer("Hand_L");
        doc.selection.select(circlePts(1590, 1400, 32));
        doc.selection.fill(colWhite);
        doc.selection.stroke(colCharcoal, 10, StrokeLocation.OUTSIDE);

        // 5. UpperArm_R & LowerArm_R & Hand_R (Raised/pointing gesture)
        var lUpperArmR = addLayer("UpperArm_R");
        doc.selection.select(capsulePts(1940, 980, 2150, 1080, 20));
        doc.selection.fill(colCharcoal);

        var lLowerArmR = addLayer("LowerArm_R");
        doc.selection.select(capsulePts(2150, 1080, 2280, 920, 18));
        doc.selection.fill(colCharcoal);

        var lHandR = addLayer("Hand_R");
        doc.selection.select(circlePts(2300, 900, 32));
        doc.selection.fill(colWhite);
        doc.selection.stroke(colCharcoal, 10, StrokeLocation.OUTSIDE);

        // 6. Head
        var lHead = addLayer("Head");
        doc.selection.select(circlePts(1920, 680, 220));
        doc.selection.fill(colWhite);
        doc.selection.stroke(colCharcoal, 16, StrokeLocation.OUTSIDE);

        // 7. Eyes_Switch
        var lEyes = addLayer("Eyes_Switch");
        // Left Eye
        doc.selection.select(circlePts(1840, 650, 28));
        doc.selection.fill(colCharcoal);
        doc.selection.select(circlePts(1848, 642, 9));
        doc.selection.fill(colWhite);
        // Right Eye
        doc.selection.select(circlePts(2000, 650, 28));
        doc.selection.fill(colCharcoal);
        doc.selection.select(circlePts(2008, 642, 9));
        doc.selection.fill(colWhite);

        // 8. Mouth_Switch (Confident smile)
        var lMouth = addLayer("Mouth_Switch");
        var mouthPts = [];
        for (var m = 0; m <= 16; m++) {{
            var ma = Math.PI * 0.15 + (m / 16) * Math.PI * 0.7;
            mouthPts.push([1920 + 85 * Math.cos(ma), 740 + 55 * Math.sin(ma)]);
        }}
        for (var mb = 16; mb >= 0; mb--) {{
            var mb_a = Math.PI * 0.15 + (mb / 16) * Math.PI * 0.7;
            mouthPts.push([1920 + 85 * Math.cos(mb_a), 748 + 55 * Math.sin(mb_a)]);
        }}
        doc.selection.select(mouthPts);
        doc.selection.fill(colCharcoal);

        // 9. Cyan Brand Scarf / Tie (#00E5FF)
        var lScarf = addLayer("Brand_Scarf");
        // Neck loop
        doc.selection.select(capsulePts(1840, 910, 2000, 910, 38));
        doc.selection.fill(colCyan);
        doc.selection.stroke(colCharcoal, 8, StrokeLocation.OUTSIDE);

        // Flowing scarf tails (dynamic flutter)
        var tailPts = [
            [1900, 930],
            [1830, 1140],
            [1750, 1220],
            [1775, 1230],
            [1880, 1150],
            [1950, 950]
        ];
        doc.selection.select(tailPts);
        doc.selection.fill(colCyan);
        doc.selection.stroke(colCharcoal, 8, StrokeLocation.OUTSIDE);

        var tail2Pts = [
            [1930, 940],
            [1960, 1120],
            [1910, 1260],
            [1935, 1270],
            [2010, 1120],
            [1980, 940]
        ];
        doc.selection.select(tail2Pts);
        doc.selection.fill(colCyanDark);
        doc.selection.stroke(colCharcoal, 8, StrokeLocation.OUTSIDE);

        doc.selection.deselect();

        // ---------------------------------------------------------
        // Save Master PSD
        // ---------------------------------------------------------
        var saveFilePSD = new File("{psd_norm}");
        var psdOpts = new PhotoshopSaveOptions();
        psdOpts.embedColorProfile = true;
        psdOpts.alphaChannels = true;
        psdOpts.layers = true;
        doc.saveAs(saveFilePSD, psdOpts, true, Extension.LOWERCASE);

        // ---------------------------------------------------------
        // Export 4K PNG Preview
        // ---------------------------------------------------------
        var previewFile = new File("{png_norm}");
        var pngOpts = new ExportOptionsSaveForWeb();
        pngOpts.format = SaveDocumentType.PNG;
        pngOpts.PNG8 = false;
        pngOpts.transparency = true;
        pngOpts.interlaced = false;
        pngOpts.includeProfile = false;
        doc.exportDocument(previewFile, ExportType.SAVEFORWEB, pngOpts);

        doc.close(SaveOptions.DONOTSAVECHANGES);
        return "SUCCESS: Generated StickFacts Master PSD & PNG Preview";
    }})();
    """

    print("      Executing character drawing JSX script in Photoshop...")
    jsx_res = ps.DoJavaScript(jsx_script)
    print(f"      Result: {jsx_res}")

    assert psd_path.exists(), f"PSD not created at {psd_path}"
    assert png_path.exists(), f"PNG not created at {png_path}"
    psd_size = psd_path.stat().st_size
    png_size = png_path.stat().st_size
    print(f"      [OK] StickFacts_Master_Character.psd ({psd_size:,} bytes)")
    print(f"      [OK] StickFacts_Preview.png ({png_size:,} bytes)")

    # -------------------------------------------------------------
    # 2. MOHO PRO 14 RIG GENERATION WITH VERIFIED TEMPLATE HEADER
    # -------------------------------------------------------------
    print("\n[2/3] Generating rigged StickFacts Moho project...")
    template_path = Path(r"C:\Program Files\Moho 14\Resources\MohoFiles\StylePreview.moho")
    with zipfile.ZipFile(template_path, "r") as z:
        moho_proj = json.loads(z.read("Project.mohoproj").decode("utf-8"))

    # Update document headers
    moho_proj["doc_uuid"] = str(uuid.uuid4())
    moho_proj["created_date"] = time.strftime("%Y-%m-%d %H:%M:%S")
    moho_proj["modified_date"] = time.strftime("%Y-%m-%d %H:%M:%S")
    moho_proj["comment"] = "StickFacts Official Master Rig (Creative Pipeline Bridge)"
    moho_proj["project_data"]["width"] = 3840
    moho_proj["project_data"]["height"] = 2160
    moho_proj["project_data"]["fps"] = 24.0

    # StickFacts Character Parts
    parts = [
        "Torso",
        "Head",
        "Eyes_Switch",
        "Mouth_Switch",
        "Brand_Scarf",
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

    parent_map = {
        "Torso": -1,
        "Head": 0,
        "Eyes_Switch": 1,
        "Mouth_Switch": 1,
        "Brand_Scarf": 0,
        "UpperArm_L": 0,
        "LowerArm_L": 5,
        "Hand_L": 6,
        "UpperArm_R": 0,
        "LowerArm_R": 8,
        "Hand_R": 9,
        "UpperLeg_L": 0,
        "LowerLeg_L": 11,
        "Foot_L": 12,
        "UpperLeg_R": 0,
        "LowerLeg_R": 14,
        "Foot_R": 15
    }

    # Build bones
    bones = []
    for i, part in enumerate(parts):
        bones.append({
            "name": part,
            "parent": parent_map.get(part, -1),
            "length": 0.25,
            "strength": 0.35,
            "pos": [0.0, 0.0],
            "angle": 0.0,
            "color": 0,
            "ignored_by_layer_picker": False
        })

    # Build child mesh/image layers linked to PSD
    child_layers = []
    for i, part in enumerate(parts):
        child_layers.append({
            "type": "ImageLayer",
            "name": part,
            "uuid": str(uuid.uuid4()),
            "visible": True,
            "origin": [0.0, 0.0, 0.0],
            "parent_bone": parent_map.get(part, -1),
            "image_path": str(psd_path.name),
            "source_file": str(psd_path.resolve()),
            "psd_layer": i,
            "psd_layer_identifier": part,
            "psd_trim_alpha": True
        })

    # Root BoneLayer
    root_bone_layer = {
        "type": "BoneLayer",
        "name": "StickFacts_Master_Rig",
        "uuid": str(uuid.uuid4()),
        "visible": True,
        "origin": [0.0, 0.0, 0.0],
        "skeleton": {
            "bones": bones
        },
        "layers": child_layers
    }

    moho_proj["layers"] = [root_bone_layer]

    # Write .moho ZIP archive
    json_bytes = json.dumps(moho_proj, ensure_ascii=False, indent=2).encode("utf-8")
    with zipfile.ZipFile(moho_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("Project.mohoproj", json_bytes)

    assert moho_path.exists(), f"Moho rig not created at {moho_path}"
    moho_size = moho_path.stat().st_size
    print(f"      [OK] StickFacts_Master_Rig.moho ({moho_size:,} bytes)")

    # -------------------------------------------------------------
    # 3. PRINT VERIFICATION TABLE
    # -------------------------------------------------------------
    print("\n" + "=" * 65)
    print("VERIFICATION COMPLETED: ALL ARTIFACTS VERIFIED ON DISK")
    print("=" * 65)
    print(f"{'Filename':<35} {'Size (bytes)':>15} {'Status':>10}")
    print("-" * 65)
    for p in [psd_path, png_path, moho_path]:
        print(f"{p.name:<35} {p.stat().st_size:>15,} {'OK':>10}")
    print("=" * 65)

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    build_stickfacts_character()

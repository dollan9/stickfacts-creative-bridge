import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bridge.photoshop_tool import PhotoshopTool

def generate_official_mascot():
    print("=" * 70)
    print("GENERATING OFFICIAL STICKFACTS BRAND MASCOT PSD (4K 3840x2160)")
    print("=" * 70)

    out_dir = Path(r"C:\Users\jofin\.gemini\antigravity\scratch\creative_pipeline_bridge\output")
    out_dir.mkdir(parents=True, exist_ok=True)

    psd_path = out_dir / "StickFacts_Master_Character.psd"
    png_path = out_dir / "StickFacts_Preview.png"

    psd_norm = str(psd_path.resolve()).replace("\\", "/")
    png_norm = str(png_path.resolve()).replace("\\", "/")

    print(f"[*] Target PSD: {psd_path}")
    print(f"[*] Target PNG: {png_path}")

    ps_tool = PhotoshopTool()
    ps = ps_tool.get_app()
    print(f"[*] Connected to Photoshop COM: {ps.Name} v{ps.Version}")

    jsx = f"""
    (function() {{
        app.displayDialogs = DialogModes.NO;
        app.preferences.rulerUnits = Units.PIXELS;

        // Create 4K 3840x2160 Document (Transparent fill, 300 DPI)
        var doc = app.documents.add(
            UnitValue(3840, "px"),
            UnitValue(2160, "px"),
            300,
            "StickFacts_Master_Character",
            NewDocumentMode.RGB,
            DocumentFill.TRANSPARENT
        );

        // -----------------------------------------------------------------
        // Color Definitions
        // -----------------------------------------------------------------
        var colInk = new SolidColor();
        colInk.rgb.hexValue = "111111"; // Thick brand outline

        var colWhite = new SolidColor();
        colWhite.rgb.hexValue = "FFFFFF"; // Crisp white body fill

        var colHatOrange = new SolidColor();
        colHatOrange.rgb.hexValue = "FF8000"; // Official Hat Orange

        var colHatBand = new SolidColor();
        colHatBand.rgb.hexValue = "CC6600"; // Hat accent band

        var colScarfCyan = new SolidColor();
        colScarfCyan.rgb.hexValue = "00E5FF"; // Electric Cyan

        var colScarfDark = new SolidColor();
        colScarfDark.rgb.hexValue = "00B4D8"; // Cyan shade

        var colLensGlass = new SolidColor();
        colLensGlass.rgb.hexValue = "B2EBF2"; // Translucent glass tint

        var colWoodHandle = new SolidColor();
        colWoodHandle.rgb.hexValue = "8D6E63"; // Magnifier handle

        var STROKE_WIDTH = 18;

        // -----------------------------------------------------------------
        // Geometry Drawing Helpers
        // -----------------------------------------------------------------
        function circlePts(cx, cy, r, segments) {{
            var segs = segments || 36;
            var pts = [];
            for (var i = 0; i < segs; i++) {{
                var a = (i / segs) * 2 * Math.PI;
                pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
            }}
            return pts;
        }}

        function arcPts(cx, cy, r, startAngle, endAngle, segs) {{
            var pts = [];
            for (var i = 0; i <= segs; i++) {{
                var a = startAngle + (i / segs) * (endAngle - startAngle);
                pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
            }}
            return pts;
        }}

        // Perfect Capsule / Pill with rounded joint caps
        function capsulePts(x1, y1, x2, y2, radius) {{
            var dx = x2 - x1;
            var dy = y2 - y1;
            var len = Math.sqrt(dx * dx + dy * dy);
            if (len === 0) return circlePts(x1, y1, radius);

            var nx = -dy / len;
            var ny = dx / len;

            var baseAngle = Math.atan2(ny, nx);
            var pts = [];

            // Joint cap 1 around (x1, y1)
            for (var i = 0; i <= 18; i++) {{
                var a = baseAngle + (i / 18) * Math.PI;
                pts.push([x1 + radius * Math.cos(a), y1 + radius * Math.sin(a)]);
            }}
            // Joint cap 2 around (x2, y2)
            for (var j = 0; j <= 18; j++) {{
                var b = baseAngle + Math.PI + (j / 18) * Math.PI;
                pts.push([x2 + radius * Math.cos(b), y2 + radius * Math.sin(b)]);
            }}
            return pts;
        }}

        // Stroke & Fill helper
        function drawShape(layer, pts, fillColor, strokeColor, strokeWidth) {{
            doc.activeLayer = layer;
            doc.selection.select(pts);
            if (fillColor) {{
                doc.selection.fill(fillColor);
            }}
            if (strokeColor && strokeWidth > 0) {{
                doc.selection.stroke(strokeColor, strokeWidth, StrokeLocation.CENTER);
            }}
            doc.selection.deselect();
        }}

        // Helper to add layer to parent set
        function makeLayer(parent, name) {{
            var l = parent.artLayers.add();
            l.name = name;
            return l;
        }}

        function makeGroup(parent, name) {{
            var g = parent.layerSets.add();
            g.name = name;
            return g;
        }}

        // =================================================================
        // HIERARCHY CONSTRUCTION (Bottom to Top in PSD stacking order)
        // Groups are created from bottom layer to top layer
        // =================================================================

        // 1. Group: Leg_L (Back Leg)
        var gLegL = doc.layerSets.add();
        gLegL.name = "Leg_L";

        var lUpperLegL = makeLayer(gLegL, "UpperLeg_L");
        drawShape(lUpperLegL, capsulePts(1865, 1230, 1825, 1550, 32), colWhite, colInk, STROKE_WIDTH);

        var lLowerLegL = makeLayer(gLegL, "LowerLeg_L");
        drawShape(lLowerLegL, capsulePts(1825, 1550, 1805, 1880, 28), colWhite, colInk, STROKE_WIDTH);

        var lFootL = makeLayer(gLegL, "Foot_L");
        drawShape(lFootL, capsulePts(1805, 1880, 1690, 1910, 40), colWhite, colInk, STROKE_WIDTH);


        // 2. Group: Leg_R (Front Leg)
        var gLegR = doc.layerSets.add();
        gLegR.name = "Leg_R";

        var lUpperLegR = makeLayer(gLegR, "UpperLeg_R");
        drawShape(lUpperLegR, capsulePts(1975, 1230, 2015, 1550, 32), colWhite, colInk, STROKE_WIDTH);

        var lLowerLegR = makeLayer(gLegR, "LowerLeg_R");
        drawShape(lLowerLegR, capsulePts(2015, 1550, 2035, 1880, 28), colWhite, colInk, STROKE_WIDTH);

        var lFootR = makeLayer(gLegR, "Foot_R");
        drawShape(lFootR, capsulePts(2035, 1880, 2150, 1910, 40), colWhite, colInk, STROKE_WIDTH);


        // 3. Group: Arm_L (Back Arm, viewer's left)
        var gArmL = doc.layerSets.add();
        gArmL.name = "Arm_L";

        var lUpperArmL = makeLayer(gArmL, "UpperArm_L");
        drawShape(lUpperArmL, capsulePts(1860, 790, 1710, 970, 30), colWhite, colInk, STROKE_WIDTH);

        var lLowerArmL = makeLayer(gArmL, "LowerArm_L");
        drawShape(lLowerArmL, capsulePts(1710, 970, 1600, 1180, 26), colWhite, colInk, STROKE_WIDTH);

        // Subgroup: Hand_L_Switch
        var gHandLSwitch = makeGroup(gArmL, "Hand_L_Switch");

        var lHandLFist = makeLayer(gHandLSwitch, "Hand_L_Fist");
        drawShape(lHandLFist, circlePts(1590, 1200, 42), colWhite, colInk, STROKE_WIDTH);
        lHandLFist.visible = false;

        var lHandLPoint = makeLayer(gHandLSwitch, "Hand_L_Point");
        drawShape(lHandLPoint, capsulePts(1590, 1200, 1510, 1220, 24), colWhite, colInk, STROKE_WIDTH);
        lHandLPoint.visible = false;

        var lHandLOpen = makeLayer(gHandLSwitch, "Hand_L_Open");
        drawShape(lHandLOpen, circlePts(1590, 1200, 46), colWhite, colInk, STROKE_WIDTH);
        lHandLOpen.visible = true; // Default visible


        // 4. Layer: Torso (Vertical body pill)
        var lTorso = doc.artLayers.add();
        lTorso.name = "Torso";
        drawShape(lTorso, capsulePts(1920, 720, 1920, 1250, 56), colWhite, colInk, STROKE_WIDTH);


        // 5. Group: Arm_R (Front Arm, viewer's right, holding magnifying glass)
        var gArmR = doc.layerSets.add();
        gArmR.name = "Arm_R";

        var lUpperArmR = makeLayer(gArmR, "UpperArm_R");
        drawShape(lUpperArmR, capsulePts(1980, 790, 2190, 890, 30), colWhite, colInk, STROKE_WIDTH);

        var lLowerArmR = makeLayer(gArmR, "LowerArm_R");
        drawShape(lLowerArmR, capsulePts(2190, 890, 2300, 740, 26), colWhite, colInk, STROKE_WIDTH);

        // Layer: Magnifying_Glass (Examiner's accessory)
        var lMagnifier = makeLayer(gArmR, "Magnifying_Glass");
        // Handle
        drawShape(lMagnifier, capsulePts(2280, 780, 2340, 640, 18), colWoodHandle, colInk, STROKE_WIDTH);
        // Lens Rim
        drawShape(lMagnifier, circlePts(2420, 520, 130), colLensGlass, colInk, 24);
        // Glint on glass (crescent highlight)
        doc.activeLayer = lMagnifier;
        doc.selection.select(arcPts(2400, 500, 95, -0.6 * Math.PI, 0.1 * Math.PI, 20));
        doc.selection.stroke(colWhite, 14, StrokeLocation.CENTER);
        doc.selection.deselect();

        // Subgroup: Hand_R_Switch
        var gHandRSwitch = makeGroup(gArmR, "Hand_R_Switch");

        var lHandROpen = makeLayer(gHandRSwitch, "Hand_R_Open");
        drawShape(lHandROpen, circlePts(2300, 740, 46), colWhite, colInk, STROKE_WIDTH);
        lHandROpen.visible = false;

        var lHandRPoint = makeLayer(gHandRSwitch, "Hand_R_Point");
        drawShape(lHandRPoint, capsulePts(2300, 740, 2390, 680, 24), colWhite, colInk, STROKE_WIDTH);
        lHandRPoint.visible = false;

        var lHandRHolding = makeLayer(gHandRSwitch, "Hand_R_Holding_Glass");
        drawShape(lHandRHolding, circlePts(2300, 740, 44), colWhite, colInk, STROKE_WIDTH);
        // Finger grip lines around magnifier handle
        doc.activeLayer = lHandRHolding;
        doc.selection.select(circlePts(2310, 725, 14));
        doc.selection.stroke(colInk, 10, StrokeLocation.CENTER);
        doc.selection.select(circlePts(2315, 755, 14));
        doc.selection.stroke(colInk, 10, StrokeLocation.CENTER);
        doc.selection.deselect();
        lHandRHolding.visible = true; // Default visible


        // 6. Layer: Brand_Scarf (Electric Cyan #00E5FF Neck Scarf)
        var lScarf = doc.artLayers.add();
        lScarf.name = "Brand_Scarf";

        // Main neck wrap collar
        drawShape(lScarf, capsulePts(1840, 690, 2000, 690, 42), colScarfCyan, colInk, STROKE_WIDTH);

        // Flapping tail 1
        var tail1 = [
            [1880, 710],
            [1800, 890],
            [1710, 980],
            [1735, 995],
            [1840, 910],
            [1930, 730]
        ];
        drawShape(lScarf, tail1, colScarfCyan, colInk, STROKE_WIDTH);

        // Flapping tail 2 (contrast/depth)
        var tail2 = [
            [1910, 720],
            [1950, 890],
            [1890, 1020],
            [1920, 1035],
            [1995, 890],
            [1960, 720]
        ];
        drawShape(lScarf, tail2, colScarfDark, colInk, STROKE_WIDTH);


        // 7. Group: Head_Group (Top group)
        var gHead = doc.layerSets.add();
        gHead.name = "Head_Group";

        // Head_Base: Circle centered at (1920, 550, r=180)
        var lHeadBase = makeLayer(gHead, "Head_Base");
        drawShape(lHeadBase, circlePts(1920, 550, 180), colWhite, colInk, STROKE_WIDTH);

        // Glasses_Or_Brows: Floating expressive eyebrows
        var lBrows = makeLayer(gHead, "Glasses_Or_Brows");
        drawShape(lBrows, capsulePts(1805, 470, 1875, 460, 10), colInk, null, 0);
        drawShape(lBrows, capsulePts(1965, 455, 2035, 475, 10), colInk, null, 0);

        // Subgroup: Mouth_Switch
        var gMouthSwitch = makeGroup(gHead, "Mouth_Switch");

        var lMouthClosed = makeLayer(gMouthSwitch, "Mouth_Closed");
        drawShape(lMouthClosed, capsulePts(1885, 630, 1955, 625, 8), colInk, null, 0);
        lMouthClosed.visible = false;

        var lMouthTalk = makeLayer(gMouthSwitch, "Mouth_Open_Talk");
        var talkPts = [
            [1880, 625],
            [1960, 625],
            [1945, 665],
            [1895, 665]
        ];
        drawShape(lMouthTalk, talkPts, colInk, null, 0);
        lMouthTalk.visible = false;

        var lMouthShock = makeLayer(gMouthSwitch, "Mouth_O_Shock");
        drawShape(lMouthShock, circlePts(1920, 635, 25), colInk, null, 0);
        lMouthShock.visible = false;

        var lMouthSmile = makeLayer(gMouthSwitch, "Mouth_Smile");
        // Confident, curved smile
        var smilePts = [];
        for (var m = 0; m <= 16; m++) {{
            var ma = Math.PI * 0.18 + (m / 16) * Math.PI * 0.64;
            smilePts.push([1920 + 75 * Math.cos(ma), 575 + 60 * Math.sin(ma)]);
        }}
        for (var mb = 16; mb >= 0; mb--) {{
            var mb_a = Math.PI * 0.18 + (mb / 16) * Math.PI * 0.64;
            smilePts.push([1920 + 75 * Math.cos(mb_a), 585 + 60 * Math.sin(mb_a)]);
        }}
        drawShape(lMouthSmile, smilePts, colInk, null, 0);
        lMouthSmile.visible = true; // Default visible

        // Subgroup: Eyes_Switch
        var gEyesSwitch = makeGroup(gHead, "Eyes_Switch");

        var lEyesSquint = makeLayer(gEyesSwitch, "Eyes_Squint");
        drawShape(lEyesSquint, capsulePts(1815, 540, 1865, 540, 8), colInk, null, 0);
        drawShape(lEyesSquint, capsulePts(1975, 540, 2025, 540, 8), colInk, null, 0);
        lEyesSquint.visible = false;

        var lEyesShocked = makeLayer(gEyesSwitch, "Eyes_Shocked");
        drawShape(lEyesShocked, circlePts(1840, 540, 36), colWhite, colInk, 12);
        drawShape(lEyesShocked, circlePts(1840, 540, 12), colInk, null, 0);
        drawShape(lEyesShocked, circlePts(2000, 540, 36), colWhite, colInk, 12);
        drawShape(lEyesShocked, circlePts(2000, 540, 12), colInk, null, 0);
        lEyesShocked.visible = false;

        var lEyesNeutral = makeLayer(gEyesSwitch, "Eyes_Neutral");
        // Inquisitive black eyes with bright white pupil highlight
        drawShape(lEyesNeutral, circlePts(1840, 540, 26), colInk, null, 0);
        drawShape(lEyesNeutral, circlePts(1848, 532, 9), colWhite, null, 0);
        drawShape(lEyesNeutral, circlePts(2000, 540, 26), colInk, null, 0);
        drawShape(lEyesNeutral, circlePts(2008, 532, 9), colWhite, null, 0);
        lEyesNeutral.visible = true; // Default visible

        // Layer: Hat (Orange Explorer Cap #FF8000)
        var lHat = makeLayer(gHead, "Hat");
        // Crown Dome
        var hatDome = [
            [1780, 440],
            [1800, 310],
            [1870, 250],
            [1970, 250],
            [2040, 310],
            [2060, 440]
        ];
        drawShape(lHat, hatDome, colHatOrange, colInk, STROKE_WIDTH);
        // Darker Hat band
        var hatBand = [
            [1775, 440],
            [1770, 410],
            [2070, 410],
            [2065, 440]
        ];
        drawShape(lHat, hatBand, colHatBand, colInk, 10);
        // Wide curved brim
        var hatBrim = [
            [1670, 455],
            [1760, 430],
            [2080, 430],
            [2170, 455],
            [2120, 485],
            [1920, 480],
            [1720, 485]
        ];
        drawShape(lHat, hatBrim, colHatOrange, colInk, STROKE_WIDTH);


        // -----------------------------------------------------------------
        // SAVE 4K PSD & EXPORT PNG PREVIEW
        // -----------------------------------------------------------------
        var psdFile = new File("{psd_norm}");
        var psdOpts = new PhotoshopSaveOptions();
        psdOpts.embedColorProfile = true;
        psdOpts.alphaChannels = true;
        psdOpts.layers = true;
        psdOpts.spotColors = true;
        doc.saveAs(psdFile, psdOpts, true, Extension.LOWERCASE);

        var pngFile = new File("{png_norm}");
        var pngOpts = new ExportOptionsSaveForWeb();
        pngOpts.format = SaveDocumentType.PNG;
        pngOpts.PNG8 = false;
        pngOpts.transparency = true;
        pngOpts.interlaced = false;
        pngOpts.includeProfile = false;
        doc.exportDocument(pngFile, ExportType.SAVEFORWEB, pngOpts);

        doc.close(SaveOptions.DONOTSAVECHANGES);
        return "SUCCESS: Built Official StickFacts Master Character PSD & PNG Preview";
    }})();
    """

    print("[*] Executing ExtendScript master generation in Photoshop 2026...")
    res = ps.DoJavaScript(jsx)
    print(f"[*] Photoshop Result: {res}")

    assert psd_path.exists(), f"PSD file not found: {psd_path}"
    assert png_path.exists(), f"PNG file not found: {png_path}"

    psd_size = psd_path.stat().st_size
    png_size = png_path.stat().st_size

    print("\n" + "=" * 70)
    print("STICKFACTS MASCOT GENERATION COMPLETE!")
    print("=" * 70)
    print(f"PSD File:  {psd_path} ({psd_size:,} bytes)")
    print(f"PNG Image: {png_path} ({png_size:,} bytes)")
    print("=" * 70)

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    generate_official_mascot()

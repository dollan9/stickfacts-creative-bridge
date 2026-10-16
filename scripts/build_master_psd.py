import os
import sys
import time
from pathlib import Path
import win32com.client

def build_psd():
    base_dir = Path(r"C:\Users\jofin\.gemini\antigravity\scratch\creative_pipeline_bridge")
    layers_dir = base_dir / "output" / "character_layers"
    output_psd = base_dir / "output" / "StickFacts_Master_Character.psd"
    desktop_suite_psd = Path(r"C:\Users\jofin\Desktop\StickFacts_Creative_Suite\StickFacts_Master_Character.psd")
    desktop_direct_psd = Path(r"C:\Users\jofin\Desktop\StickFacts_Master_Character.psd")

    print("[1/5] Connecting to Photoshop via COM...")
    ps = win32com.client.Dispatch("Photoshop.Application")
    ps.DisplayDialogs = 3 # psDisplayNoDialogs
    print(f"Connected to {ps.Name} {ps.Version}")

    # Prepare normalized paths for ExtendScript
    p_hero = str(layers_dir / "Hero_Mascot_Vector.png").replace("\\", "/")
    p_pose1 = str(layers_dir / "Pose_1_Investigating.png").replace("\\", "/")
    p_pose2 = str(layers_dir / "Pose_2_Explaining.png").replace("\\", "/")
    p_pose3 = str(layers_dir / "Pose_3_Shocked.png").replace("\\", "/")
    p_pose4 = str(layers_dir / "Pose_4_Thinking.png").replace("\\", "/")
    
    p_expr1 = str(layers_dir / "Expression_1_Curious.png").replace("\\", "/")
    p_expr2 = str(layers_dir / "Expression_2_Eureka.png").replace("\\", "/")
    p_expr3 = str(layers_dir / "Expression_3_Shocked.png").replace("\\", "/")
    p_expr4 = str(layers_dir / "Expression_4_Smug.png").replace("\\", "/")

    p_save = str(output_psd).replace("\\", "/")

    jsx = f"""
    (function() {{
        app.preferences.rulerUnits = Units.PIXELS;

        // Close any document named StickFacts_Master_Character if open
        for (var i = app.documents.length - 1; i >= 0; i--) {{
            if (app.documents[i].name.indexOf("StickFacts_Master_Character") !== -1) {{
                app.documents[i].close(SaveOptions.DONOTSAVECHANGES);
            }}
        }}

        // Create 3840x2160 300DPI document
        var doc = app.documents.add(
            UnitValue(3840, "px"),
            UnitValue(2160, "px"),
            300,
            "StickFacts_Master_Character",
            NewDocumentMode.RGB,
            DocumentFill.WHITE
        );

        function importToLayer(path, layerName, isVisible) {{
            var f = new File(path);
            if (!f.exists) return null;
            var assetDoc = app.open(f);
            assetDoc.selection.selectAll();
            assetDoc.selection.copy();
            assetDoc.close(SaveOptions.DONOTSAVECHANGES);

            app.activeDocument = doc;
            var newLayer = doc.paste();
            newLayer.name = layerName;
            newLayer.visible = isVisible;
            return newLayer;
        }}

        // 1. Group: Facial Expressions
        var exprGroup = doc.layerSets.add();
        exprGroup.name = "Expressions (Växla mellan ansiktsuttryck)";
        
        var e4 = importToLayer("{p_expr4}", "Expression 4 - Smug Knowing Smile", false);
        if (e4) e4.move(exprGroup, ElementPlacement.INSIDE);

        var e3 = importToLayer("{p_expr3}", "Expression 3 - Shocked Baffled", false);
        if (e3) e3.move(exprGroup, ElementPlacement.INSIDE);

        var e2 = importToLayer("{p_expr2}", "Expression 2 - Excited Eureka", false);
        if (e2) e2.move(exprGroup, ElementPlacement.INSIDE);

        var e1 = importToLayer("{p_expr1}", "Expression 1 - Curious Investigator (Default)", true);
        if (e1) e1.move(exprGroup, ElementPlacement.INSIDE);

        // 2. Group: Character Poses
        var poseGroup = doc.layerSets.add();
        poseGroup.name = "Poses (Växla mellan poser för animation)";

        var p4 = importToLayer("{p_pose4}", "Pose 4 - Thinking & Deducing (Hand på haka)", false);
        if (p4) p4.move(poseGroup, ElementPlacement.INSIDE);

        var p3 = importToLayer("{p_pose3}", "Pose 3 - Shocked & Mind-Blown (Hoppar bakåt)", false);
        if (p3) p3.move(poseGroup, ElementPlacement.INSIDE);

        var p2 = importToLayer("{p_pose2}", "Pose 2 - Explaining & Presenting (Pekar uppåt)", false);
        if (p2) p2.move(poseGroup, ElementPlacement.INSIDE);

        var p1 = importToLayer("{p_pose1}", "Pose 1 - Detective Investigating (Förstoringsglas)", true);
        if (p1) p1.move(poseGroup, ElementPlacement.INSIDE);

        // 3. Group: Hero Mascot Master
        var heroGroup = doc.layerSets.add();
        heroGroup.name = "Master Hero Mascot (Officiell Maskot Vektor)";
        
        var hero = importToLayer("{p_hero}", "StickFacts Hero Master Character", true);
        if (hero) hero.move(heroGroup, ElementPlacement.INSIDE);

        // Rename background
        try {{
            doc.backgroundLayer.name = "Studio White Background";
        }} catch(e) {{}}

        // Save as PSD
        var psdSaveOptions = new PhotoshopSaveOptions();
        psdSaveOptions.embedColorProfile = true;
        psdSaveOptions.alphaChannels = true;
        psdSaveOptions.layers = true;
        
        doc.saveAs(new File("{p_save}"), psdSaveOptions, true, Extension.LOWERCASE);

        return "SUCCESS: Master PSD generated with all groups, poses and expressions.";
    }})();
    """

    print("[2/5] Executing JSX in Photoshop...")
    res = ps.DoJavaScript(jsx)
    print("JSX Result:", res)

    print("[3/5] Verifying output file...")
    if output_psd.exists():
        size_mb = output_psd.stat().st_size / (1024 * 1024)
        print(f"Created: {output_psd} ({size_mb:.2f} MB)")
        
        # Copy to Desktop Suite and direct Desktop
        import shutil
        shutil.copy2(output_psd, desktop_suite_psd)
        print(f"Copied to: {desktop_suite_psd}")
        shutil.copy2(output_psd, desktop_direct_psd)
        print(f"Copied to: {desktop_direct_psd}")
    else:
        print("ERROR: Output PSD file not found!")

    # Bring Photoshop window to front so user sees it
    try:
        ps.Visible = True
    except Exception:
        pass
    print("[4/5] Photoshop brought to foreground.")
    print("[5/5] Complete!")

if __name__ == "__main__":
    build_psd()

// Adobe Animate Character Rig Generator
(function() {
    var doc = fl.createDocument();
    doc.width = 1920;
    doc.height = 1080;
    doc.frameRate = 24;

    var timeline = doc.getTimeline();
    var layerNames = ["Head", "Torso", "UpperArm_L", "LowerArm_L", "Hand_L", "UpperArm_R", "LowerArm_R", "Hand_R", "UpperLeg_L", "LowerLeg_L", "Foot_L", "UpperLeg_R", "LowerLeg_R", "Foot_R"];

    // Name the root layer
    timeline.layers[0].name = layerNames[layerNames.length - 1];

    // Add character rig layers in hierarchical order
    for (var i = layerNames.length - 2; i >= 0; i--) {
        timeline.addNewLayer(layerNames[i], "normal", true);
    }

    // Save document to destination
    var saveURI = "file:///C:/Users/jofin/.gemini/antigravity/scratch/creative_pipeline_bridge/output/character_rig.fla";
    fl.saveDocument(doc, saveURI);

    if (true) {
        fl.closeDocument(doc, false);
    }
})();

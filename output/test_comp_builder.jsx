
        (function() {
            // Create new project
            app.newProject();

            // Create main composition
            var comp = app.project.items.addComp(
                "Final_Action_Shot",
                3840,
                2160,
                1.0, // Pixel aspect ratio
                5.0,
                24.0
            );

            // Import and add background layer if provided
            var bgPath = "C:/Users/jofin/.gemini/antigravity/scratch/creative_pipeline_bridge/output/test_character_vector.svg";
            if (bgPath !== "") {
                var bgFile = new File(bgPath);
                if (bgFile.exists) {
                    var importOptions = new ImportOptions(bgFile);
                    var bgItem = app.project.importFile(importOptions);
                    var bgLayer = comp.layers.add(bgItem);
                    bgLayer.moveToEnd();
                }
            }

            // Import character passes
            var charPaths = ["C:/Users/jofin/.gemini/antigravity/scratch/creative_pipeline_bridge/output/test_character_rig.psd"];
            for (var i = 0; i < charPaths.length; i++) {
                var cFile = new File(charPaths[i]);
                if (cFile.exists) {
                    var cOpt = new ImportOptions(cFile);
                    var cItem = app.project.importFile(cOpt);
                    var cLayer = comp.layers.add(cItem);
                }
            }

            // Apply camera shake via null and expression
            if (true) {
                var nullLayer = comp.layers.addNull();
                nullLayer.name = "Camera_Controller";
                nullLayer.property("Position").expression = "wiggle(2, 25);";
                // Parent all other layers to camera controller
                for (var j = 1; j <= comp.layers.length; j++) {
                    var l = comp.layers[j];
                    if (l !== nullLayer) {
                        l.parent = nullLayer;
                    }
                }
            }

            // Setup Render Queue item if render path provided
            var renderPath = "C:/Users/jofin/.gemini/antigravity/scratch/creative_pipeline_bridge/output/test_production_render.mov";
            if (renderPath !== "") {
                var rqItem = app.project.renderQueue.items.add(comp);
                if (rqItem.outputModules.length > 0) {
                    rqItem.outputModules[1].file = new File(renderPath);
                }
            }

            // Save AEP file
            var saveFile = new File("C:/Users/jofin/.gemini/antigravity/scratch/creative_pipeline_bridge/output/test_production_comp.aep");
            app.project.save(saveFile);
        })();
        
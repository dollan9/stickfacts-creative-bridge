# GOAL: Multi-App 2D Animation & Video Production Bridge

## 1. Objective
Build an automation bridge (modular Python CLI/Daemon and MCP-compatible architecture) on Windows to grant programmatic, zero-guessing control over the installed creative production suite:
- Adobe Photoshop 2026
- Adobe Illustrator 2026
- Adobe Animate 2024
- Adobe After Effects 2026
- Adobe Premiere Pro 2026
- Moho Pro 14.5
- ComfyUI Desktop
*(DaVinci Resolve Studio is explicitly handled via the existing active DaVinci Resolve MCP server).*

## 2. Acceptance Criteria & Definition of Done (DoD)
1. **Zero Hallucination Discovery (Phase 1)**: All executable paths, registry ProgIDs, CLI arguments, and native scripting SDK directories verified empirically on the local system. Done and documented in `config.json`.
2. **Modular Architecture (Phase 2)**:
   - Shared verified configuration loader.
   - Independent tool wrappers:
     - `comfy_tool.py`: REST API & WebSocket client, prompt injection, queue monitoring, output retrieval.
     - `photoshop_tool.py`: COM + JSX bridge for document generation, character layer hierarchy, asset import/export.
     - `illustrator_tool.py`: COM + JSX bridge for vector asset generation, symbol management, SVG/AI export.
     - `animate_tool.py`: CLI + JSFL bridge for FLA creation, timeline management, symbol conversion, video/sprite export.
     - `moho_tool.py`: Direct ZIP/JSON (`Project.mohoproj`) manipulation + headless Lua scripting execution (`Moho.exe script.lua`).
     - `aftereffects_tool.py`: CLI JSX execution (`AfterFX.exe -r`) + batch rendering (`aerender.exe`).
     - `premiere_tool.py`: Timeline assembly, media linking, FCP/Premiere XML generation.
3. **End-to-End Verification (Phase 3)**:
   - Safe, minimal automated "Hello World" verification tests executed and validated for each module.
   - External audit via `hermes-review`.

# STICKFACTS PRODUCTION SYSTEM & PIPELINE HANDOVER
**Version:** 1.0.0 (Master Brand Voice Approved)  
**Location:** `C:\Users\jofin\.gemini\antigravity\scratch\creative_pipeline_bridge`  
**Platform:** Windows 10/11 | NVIDIA RTX 3080 (10 GB VRAM) | Python 3.11/3.12 | CUDA enabled

---

## 🎙️ 1. Den Godkända Röstmodellen (StickFacts Brand Voice)

Rösten är godkänd och permanent låst. Den drivs av **SWivid/F5-TTS** med en skräddarsydd linjär Notch-EQ filterkedja som eliminerar visseltoppar från Vocos-vocodern utan att påverka flyt eller volym.

### Nyckeldata:
- **Godkänd Master-fil (Hook):**  
  `creative_pipeline_bridge/output/stickfacts_hook_master_approved.wav`  
  *(Manus: "Did you know your brain actually eats itself when you don't get enough sleep? Here is what happens inside your head after just 24 hours awake.")*
- **Referensljud (Brand Voice Anchor):**  
  `creative_pipeline_bridge/assets/voice_ref/stickfacts_brand_voice.wav`  
  `creative_pipeline_bridge/assets/voice_ref/stickfacts_brand_voice.txt`  
  *(Text: "Some call me nature, others call me mother nature.")*
- **F5-TTS Parametrar:**  
  `speed = 1.0` | `cfg_strength = 2.0` | `nfe_step = 32` | `seed = 42` | `dewhistle = True`
- **Integrerad De-Whistle Filterkedja (FFmpeg LTI):**  
  `volume=0.92,equalizer=f=7450:t=q:w=1.8:g=-6.5,equalizer=f=8350:t=q:w=2.0:g=-6.5,lowpass=f=9800`  
  *Gör att rösten är 100 % ren från visselljud och garanterat fri från lagg/hack.*
- **Studio Fallback (om F5 inte körs):**  
  **Kokoro-82M** med röstpreset `am_adam` (`creative_pipeline_bridge/output/kokoro_studio_test.wav`).

---

## ⚡ 2. Hur en ny chatt/agent genererar röst direkt

### Alternativ A: Via Python-kod
```python
import sys
from pathlib import Path

# Lägg till repot i sys.path
sys.path.insert(0, r"C:\Users\jofin\.gemini\antigravity\scratch")

from creative_pipeline_bridge.bridge.voice_tool import VoiceTool

# Initiera verktyget (laddar automatiskt F5-TTS på CUDA)
tool = VoiceTool()

# Generera röst med den godkända StickFacts-rösten och automatisk de-whistling:
result = tool.generate_f5(
    text="Your script text goes here for the YouTube Short.",
    output_path=Path(r"C:\Users\jofin\.gemini\antigravity\scratch\creative_pipeline_bridge\output\my_new_episode.wav")
)
print("Genererad fil:", result["path"], f"Längd: {result['duration_seconds']:.2f}s")
```

### Alternativ B: Via Terminal / PowerShell CLI
```powershell
python -m creative_pipeline_bridge.bridge.voice_tool --text "Did you know your brain actually eats itself when you don't get enough sleep?" --output "creative_pipeline_bridge/output/episode_voice.wav"
```

---

## 🎨 3. Karaktärsriggar & Visuella Tillgångar

All grafik och alla riggar är skapade, testade och sparade i `creative_pipeline_bridge/output/`:

| Resurs | Sökväg | Beskrivning |
| :--- | :--- | :--- |
| **Photoshop Master Rig** | `output/StickFacts_Master_Character.psd` | Full lageruppdelad karaktär (Huvud, Ögon, Mungipor, Kropp, Armar, Ben) för direkt import |
| **Moho Rig** | `output/StickFacts_Master_Rig.moho` | Riggar med ben och smart-bones för 2D-animation |
| **Adobe Animate Rig** | `output/Create_Character_Rig.jsfl` | Automatiserat JSFL-skript för Adobe Animate |
| **Illustrator Vektor** | `output/test_character_vector.ai` & `.svg` | Vektoriserad StickFacts-karaktär i 4K-skalbarhet |
| **Pose Model Sheet** | `output/StickFacts_Pose_Model_Sheet.png` | Godkända vinklar och poser |
| **Expressions Sheet** | `output/StickFacts_Expressions_Sheet.png` | Godkända ansiktsuttryck (Glad, Chockad, Tänkande, Trött) |
| **Concept Art** | `output/StickFacts_Concept_Art.png` | Visuell stilguide för StickFacts |

---

## 🎬 4. Pipeline-verktygen i `bridge/`

Varje verktyg i `creative_pipeline_bridge/bridge/` kan anropas programmatiskt:

- **`voice_tool.py`**: Skapar voiceovers med F5-TTS eller Kokoro-82M.
- **`photoshop_tool.py`**: Automatiserar lager, montering och PSD-export.
- **`illustrator_tool.py`**: Vektorkonvertering och AI-filshantering.
- **`animate_tool.py`**: Genererar JSFL-makron för Adobe Animate.
- **`moho_tool.py`**: Genererar Moho-riggfiler och Lua-skript.
- **`premiere_tool.py`**: Skapar tidslinjer, klipper röst och exporterar FCPXML (`output/test_premiere_sequence.xml`).
- **`aftereffects_tool.py`**: Bygger animationer och kompositioner via ExtendScript (`output/test_comp_builder.jsx`).
- **`comfy_tool.py`**: Renderar bakgrunder och effekter via lokalt ComfyUI API.

---

## 📋 5. Prompt att klistra in i en ny chatt

Kopiera och klistra in följande text i den nya chatten för att den omedelbart ska veta allt:

```text
Vi bygger YouTube Shorts för StickFacts i mappen:
C:\Users\jofin\.gemini\antigravity\scratch\creative_pipeline_bridge

All infrastruktur är redan färdigställd och godkänd:
1. Röstmotorn är F5-TTS (låst med varumärkesrösten och automatisk Notch-EQ filterkedja):
   - Modul: creative_pipeline_bridge.bridge.voice_tool (Klass: VoiceTool)
   - Godkänd master-fil: output/stickfacts_hook_master_approved.wav
   - Referensljud: assets/voice_ref/stickfacts_brand_voice.wav ("Some call me nature, others call me mother nature.")
   - CLI: python -m creative_pipeline_bridge.bridge.voice_tool --text "..." --output "..."

2. Färdiga riggar och visuella assets finns i creative_pipeline_bridge/output:
   - StickFacts_Master_Character.psd (Lager för ansikte, mun, ögon, kropp)
   - StickFacts_Master_Rig.moho (Moho-rigg med ben och smart bones)
   - StickFacts_Expressions_Sheet.png & StickFacts_Pose_Model_Sheet.png
   - Create_Character_Rig.jsfl (Adobe Animate)
   - test_premiere_sequence.xml & test_comp_builder.jsx

Läs specifikationen i creative_pipeline_bridge/STICKFACTS_MASTER_SYSTEM.md och hjälp mig producera nästa StickFacts-video!
```

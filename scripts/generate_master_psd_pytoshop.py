import os
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import pytoshop
from pytoshop import enums
from pytoshop.user import nested_layers
import shutil

def create_layer_from_image(img_path: Path, layer_name: str, canvas_w: int, canvas_h: int, target_h: int = 1500, center_x: int = 1920, center_y: int = 1080):
    pil_img = Image.open(img_path).convert("RGBA")
    
    # Scale proportionally
    w, h = pil_img.size
    aspect = w / h
    new_h = target_h
    new_w = int(new_h * aspect)
    pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    arr = np.array(pil_img) # (new_h, new_w, 4)
    
    top = max(0, center_y - (new_h // 2))
    left = max(0, center_x - (new_w // 2))
    bottom = top + new_h
    right = left + new_w
    
    # pytoshop nested_layers.Image
    layer = nested_layers.Image(
        name=layer_name,
        top=top,
        left=left,
        bottom=bottom,
        right=right,
        channels={
            -1: arr[:, :, 3], # Alpha
            0: arr[:, :, 0],  # Red
            1: arr[:, :, 1],  # Green
            2: arr[:, :, 2],  # Blue
        }
    )
    return layer

def build_master_psd():
    base_dir = Path(r"C:\Users\jofin\.gemini\antigravity\scratch\creative_pipeline_bridge")
    layers_dir = base_dir / "output" / "character_layers"
    output_psd = base_dir / "output" / "StickFacts_Master_Character.psd"
    desktop_suite_psd = Path(r"C:\Users\jofin\Desktop\StickFacts_Creative_Suite\StickFacts_Master_Character.psd")
    desktop_direct_psd = Path(r"C:\Users\jofin\Desktop\StickFacts_Master_Character.psd")

    canvas_w = 3840
    canvas_h = 2160

    print("[1/4] Preparing layers and groups...")
    
    # 1. Poses Group
    pose_group = nested_layers.Group(name="Poses (Animation)")
    pose_files = [
        ("Pose 1 - Detective Investigating", layers_dir / "Pose_1_Investigating.png"),
        ("Pose 2 - Explaining & Presenting", layers_dir / "Pose_2_Explaining.png"),
        ("Pose 3 - Shocked & Mind-Blown", layers_dir / "Pose_3_Shocked.png"),
        ("Pose 4 - Thinking & Deducing", layers_dir / "Pose_4_Thinking.png")
    ]
    for name, p in pose_files:
        if p.exists():
            layer = create_layer_from_image(p, name, canvas_w, canvas_h, target_h=1500, center_x=1920, center_y=1120)
            pose_group.layers.append(layer)
            print(f"  Added pose: {name}")

    # 2. Expressions Group
    expr_group = nested_layers.Group(name="Expressions (Ansiktsuttryck)")
    expr_files = [
        ("Expression 1 - Curious Investigator", layers_dir / "Expression_1_Curious.png"),
        ("Expression 2 - Excited Eureka", layers_dir / "Expression_2_Eureka.png"),
        ("Expression 3 - Shocked Baffled", layers_dir / "Expression_3_Shocked.png"),
        ("Expression 4 - Smug Knowing Smile", layers_dir / "Expression_4_Smug.png")
    ]
    for name, p in expr_files:
        if p.exists():
            layer = create_layer_from_image(p, name, canvas_w, canvas_h, target_h=1100, center_x=1920, center_y=1080)
            expr_group.layers.append(layer)
            print(f"  Added expression: {name}")

    # 3. Hero Master Group
    hero_group = nested_layers.Group(name="Master Hero Mascot")
    hero_file = layers_dir / "Hero_Mascot_Vector.png"
    if hero_file.exists():
        layer = create_layer_from_image(hero_file, "StickFacts Hero Official Vector", canvas_w, canvas_h, target_h=1650, center_x=1920, center_y=1100)
        hero_group.layers.append(layer)
        print("  Added hero vector master")

    # 4. Background Group
    bg_group = nested_layers.Group(name="Background")
    white_bg = nested_layers.Image(
        name="Studio White Background",
        top=0,
        left=0,
        bottom=canvas_h,
        right=canvas_w,
        channels={
            -1: np.full((canvas_h, canvas_w), 255, dtype=np.uint8),
            0: np.full((canvas_h, canvas_w), 255, dtype=np.uint8),
            1: np.full((canvas_h, canvas_w), 255, dtype=np.uint8),
            2: np.full((canvas_h, canvas_w), 255, dtype=np.uint8),
        }
    )
    bg_group.layers.append(white_bg)

    # Combine all groups
    groups = [pose_group, expr_group, hero_group, bg_group]

    print("[2/4] Converting to Adobe Photoshop PSD structure (4K 3840x2160, RAW compression)...")
    psd = nested_layers.nested_layers_to_psd(
        groups,
        color_mode=enums.ColorMode.rgb,
        compression=enums.Compression.raw
    )

    print(f"[3/4] Writing to {output_psd}...")
    with open(output_psd, "wb") as f:
        psd.write(f)

    file_size_mb = output_psd.stat().st_size / (1024 * 1024)
    print(f"Successfully generated {output_psd.name} ({file_size_mb:.2f} MB)")

    print("[4/4] Copying to Desktop folders...")
    shutil.copy2(output_psd, desktop_suite_psd)
    print(f"  Copied to: {desktop_suite_psd}")
    shutil.copy2(output_psd, desktop_direct_psd)
    print(f"  Copied to: {desktop_direct_psd}")

    # Verify with psd-tools
    from psd_tools import PSDImage
    verify_doc = PSDImage.open(output_psd)
    print(f"Verification: Found {len(verify_doc)} root groups/layers in PSD.")
    for g in verify_doc:
        subcount = len(g) if g.is_group() else 0
        print(f"  - Group '{g.name.strip(chr(0))}': {subcount} sub-layers")

if __name__ == "__main__":
    build_master_psd()

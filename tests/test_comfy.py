import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bridge.comfy_tool import ComfyTool

def test_comfy():
    print("[*] Testing ComfyUI Tool Module...")
    tool = ComfyTool()
    print(f"    Base URL: {tool.base_url}")
    print(f"    Output Directory: {tool.output_dir}")
    print(f"    Input Directory: {tool.input_dir}")
    
    online = tool.is_online()
    print(f"    Server Online: {online}")
    if online:
        stats = tool.get_system_stats()
        print(f"    System Stats: {stats.get('system', {})}")
    else:
        print("    Server is currently offline (will start on demand via tool.start_daemon()).")

    # Test parameter injection with a mock API workflow
    sample_workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 8,
                "denoise": 1,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler",
                "scheduler": "normal",
                "seed": 123456789,
                "steps": 20
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "v1-5-pruned-emaonly.safetensors"
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "batch_size": 1,
                "height": 512,
                "width": 512
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": "masterpiece, best quality, anime character standing pose"
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": "bad anatomy, blurry, low quality"
            }
        }
    }

    injected = tool.inject_parameters(
        sample_workflow,
        positive_prompt="cyberpunk anime protagonist, detailed layers, full body",
        negative_prompt="ugly, bad proportions, noisy",
        seed=999888,
        width=1024,
        height=1024,
        steps=25,
        cfg=7.5,
        checkpoint="dreamshaper_8.safetensors"
    )

    # Assertions
    assert injected["3"]["inputs"]["seed"] == 999888, "Seed injection failed"
    assert injected["3"]["inputs"]["steps"] == 25, "Steps injection failed"
    assert injected["3"]["inputs"]["cfg"] == 7.5, "CFG injection failed"
    assert injected["5"]["inputs"]["width"] == 1024, "Width injection failed"
    assert injected["5"]["inputs"]["height"] == 1024, "Height injection failed"
    assert injected["4"]["inputs"]["ckpt_name"] == "dreamshaper_8.safetensors", "Checkpoint injection failed"
    assert "cyberpunk" in injected["6"]["inputs"]["text"], "Positive prompt injection failed"
    assert "ugly" in injected["7"]["inputs"]["text"], "Negative prompt injection failed"

    print("    [OK] Parameter injection logic verified successfully!")
    print("[+] ComfyUI Tool Verification: PASSED\n")

if __name__ == "__main__":
    test_comfy()

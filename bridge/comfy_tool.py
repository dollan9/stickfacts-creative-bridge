import os
import sys
import json
import uuid
import time
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
import urllib.request
import urllib.parse
import aiohttp
import requests

from .config_loader import get_config

class ComfyTool:
    def __init__(self, base_url: Optional[str] = None):
        cfg = get_config()
        self.app_cfg = cfg.get_app("comfyui")
        self.base_url = (base_url or self.app_cfg.get("api_url", "http://127.0.0.1:8188")).rstrip("/")
        self.ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://") + "/ws"
        self.output_dir = Path(self.app_cfg.get("output_dir", ""))
        self.input_dir = Path(self.app_cfg.get("input_dir", ""))

    def is_online(self, timeout: float = 2.0) -> bool:
        try:
            r = requests.get(f"{self.base_url}/system_stats", timeout=timeout)
            return r.status_code == 200
        except Exception:
            return False

    def get_system_stats(self) -> Dict[str, Any]:
        r = requests.get(f"{self.base_url}/system_stats", timeout=5.0)
        r.raise_for_status()
        return r.json()

    def start_daemon(self, wait_seconds: int = 15) -> bool:
        if self.is_online():
            return True

        py_exe = self.app_cfg.get("python_exe")
        main_py = self.app_cfg.get("main_py")

        if not py_exe or not Path(py_exe).exists():
            raise FileNotFoundError(f"ComfyUI python executable not found: {py_exe}")
        if not main_py or not Path(main_py).exists():
            raise FileNotFoundError(f"ComfyUI main.py not found: {main_py}")

        working_dir = Path(main_py).parent
        cmd = [py_exe, main_py, "--listen", "127.0.0.1", "--port", "8188"]

        # Launch detached background process on Windows
        creationflags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
        subprocess.Popen(cmd, cwd=str(working_dir), creationflags=creationflags)

        # Wait until server responds
        start = time.time()
        while time.time() - start < wait_seconds:
            if self.is_online(timeout=1.0):
                return True
            time.sleep(1.0)
        return False

    def load_workflow(self, workflow_source: Any) -> Dict[str, Any]:
        if isinstance(workflow_source, dict):
            return workflow_source
        p = Path(workflow_source)
        if not p.exists():
            raise FileNotFoundError(f"Workflow file not found: {p}")
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)

    def inject_parameters(
        self,
        workflow: Dict[str, Any],
        positive_prompt: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        batch_size: Optional[int] = None,
        steps: Optional[int] = None,
        cfg: Optional[float] = None,
        checkpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Injects parameters into ComfyUI workflow_api format (node dictionary).
        """
        wf = json.loads(json.dumps(workflow))

        # If wrapped in 'prompt' key
        nodes = wf.get("prompt", wf)

        clip_nodes = []
        for nid, node in nodes.items():
            if not isinstance(node, dict):
                continue
            class_type = node.get("class_type", "")
            inputs = node.get("inputs", {})

            # Checkpoint
            if checkpoint and class_type in ["CheckpointLoaderSimple", "CheckpointLoader"]:
                inputs["ckpt_name"] = checkpoint

            # EmptyLatentImage
            if class_type in ["EmptyLatentImage", "EmptySD3LatentImage"]:
                if width is not None:
                    inputs["width"] = width
                if height is not None:
                    inputs["height"] = height
                if batch_size is not None:
                    inputs["batch_size"] = batch_size

            # KSampler
            if "KSampler" in class_type:
                if seed is not None:
                    inputs["seed"] = seed
                if steps is not None:
                    inputs["steps"] = steps
                if cfg is not None:
                    inputs["cfg"] = cfg

            # Text Prompts (CLIPTextEncode)
            if class_type == "CLIPTextEncode" and "text" in inputs:
                clip_nodes.append((nid, node))

        # Assign positive / negative prompts if found
        if len(clip_nodes) == 1 and positive_prompt is not None:
            clip_nodes[0][1]["inputs"]["text"] = positive_prompt
        elif len(clip_nodes) >= 2:
            if positive_prompt is not None:
                clip_nodes[0][1]["inputs"]["text"] = positive_prompt
            if negative_prompt is not None:
                clip_nodes[1][1]["inputs"]["text"] = negative_prompt

        return wf

    def queue_prompt(self, workflow: Dict[str, Any], client_id: Optional[str] = None) -> str:
        cid = client_id or str(uuid.uuid4())
        nodes = workflow.get("prompt", workflow)
        payload = {
            "prompt": nodes,
            "client_id": cid
        }
        r = requests.post(f"{self.base_url}/prompt", json=payload, timeout=10.0)
        r.raise_for_status()
        data = r.json()
        prompt_id = data.get("prompt_id")
        if not prompt_id:
            raise ValueError(f"ComfyUI rejected prompt: {data}")
        return prompt_id

    async def _track_ws_async(
        self,
        prompt_id: str,
        client_id: str,
        timeout: float = 120.0,
        on_progress: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        url = f"{self.ws_url}?clientId={client_id}"
        outputs = {}
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(url) as ws:
                start_time = time.time()
                while time.time() - start_time < timeout:
                    try:
                        msg = await asyncio.wait_for(ws.receive(), timeout=timeout - (time.time() - start_time))
                    except asyncio.TimeoutError:
                        break

                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        msg_type = data.get("type")
                        payload = data.get("data", {})

                        if msg_type == "progress":
                            val = payload.get("value", 0)
                            max_val = payload.get("max", 0)
                            node_id = payload.get("node")
                            if on_progress:
                                on_progress(val, max_val, str(node_id))

                        elif msg_type == "executing":
                            if payload.get("node") is None and payload.get("prompt_id") == prompt_id:
                                # Execution complete
                                break

                        elif msg_type == "executed":
                            if payload.get("prompt_id") == prompt_id:
                                nid = payload.get("node")
                                outputs[nid] = payload.get("output")

                    elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        break
        return outputs

    def track_execution(
        self,
        prompt_id: str,
        client_id: str,
        timeout: float = 120.0,
        on_progress: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        return asyncio.run(self._track_ws_async(prompt_id, client_id, timeout, on_progress))

    def get_history(self, prompt_id: str) -> Dict[str, Any]:
        r = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=10.0)
        r.raise_for_status()
        return r.json().get(prompt_id, {})

    def download_view_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        }
        r = requests.get(f"{self.base_url}/view", params=params, timeout=30.0)
        r.raise_for_status()
        return r.content

    def retrieve_outputs(self, prompt_id: str, destination_dir: Optional[Path] = None) -> List[Path]:
        history = self.get_history(prompt_id)
        outputs_map = history.get("outputs", {})
        saved_files = []

        target_dir = destination_dir or (get_config().get_output_dir() / "comfy_renders")
        target_dir.mkdir(parents=True, exist_ok=True)

        for nid, nout in outputs_map.items():
            images = nout.get("images", [])
            for img in images:
                fn = img.get("filename")
                sub = img.get("subfolder", "")
                ftype = img.get("type", "output")
                
                # Check local output directory first
                local_path = self.output_dir / sub / fn if self.output_dir.exists() else None
                dest_file = target_dir / fn

                if local_path and local_path.exists():
                    dest_file.write_bytes(local_path.read_bytes())
                else:
                    data = self.download_view_image(fn, sub, ftype)
                    dest_file.write_bytes(data)

                saved_files.append(dest_file)

        return saved_files

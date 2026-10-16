import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import xml.etree.ElementTree as ET
from xml.dom import minidom

from .config_loader import get_config

class PremiereTool:
    def __init__(self):
        cfg = get_config()
        self.app_cfg = cfg.get_app("premiere")
        self.exe_path = Path(self.app_cfg.get("exe", "C:/Program Files/Adobe/Adobe Premiere Pro 2026/Adobe Premiere Pro.exe"))
        self.headless_exe = Path(self.app_cfg.get("headless_exe", "C:/Program Files/Adobe/Adobe Premiere Pro 2026/PProHeadless.exe"))

    @staticmethod
    def file_to_pathurl(file_path: Path) -> str:
        """
        Converts file path to FCP XML pathurl format:
        file://localhost/C:/path/to/file.mp4
        """
        resolved = str(file_path.resolve()).replace("\\", "/")
        return f"file://localhost/{resolved}"

    def generate_timeline_xml(
        self,
        sequence_name: str,
        output_xml_path: Path,
        width: int = 3840,
        height: int = 2160,
        fps: int = 24,
        video_clips: Optional[List[Dict[str, Any]]] = None,
        audio_clips: Optional[List[Dict[str, Any]]] = None
    ) -> Path:
        """
        Generates an authentic Premiere / Final Cut Pro XML (xmeml v4) sequence.
        Premiere Pro natively imports this XML to assemble complex multi-track timelines.
        """
        xmeml = ET.Element("xmeml", version="4")
        project = ET.SubElement(xmeml, "project")
        ET.SubElement(project, "name").text = f"{sequence_name}_Project"

        children = ET.SubElement(project, "children")
        sequence = ET.SubElement(children, "sequence", id="sequence-1")
        ET.SubElement(sequence, "name").text = sequence_name

        # Calculate total duration
        total_duration = 0
        all_clips = (video_clips or []) + (audio_clips or [])
        for c in all_clips:
            end_f = c.get("end_frame", 0)
            if end_f > total_duration:
                total_duration = end_f
        if total_duration == 0:
            total_duration = fps * 10 # default 10 seconds

        ET.SubElement(sequence, "duration").text = str(total_duration)

        rate = ET.SubElement(sequence, "rate")
        ET.SubElement(rate, "timebase").text = str(fps)
        ET.SubElement(rate, "ntsc").text = "FALSE"

        # Media container
        media = ET.SubElement(sequence, "media")

        # Video Section
        video = ET.SubElement(media, "video")
        format_el = ET.SubElement(video, "format")
        sample_char = ET.SubElement(format_el, "samplecharacteristics")
        ET.SubElement(sample_char, "width").text = str(width)
        ET.SubElement(sample_char, "height").text = str(height)
        ET.SubElement(sample_char, "pixelaspectratio").text = "square"
        rate_v = ET.SubElement(sample_char, "rate")
        ET.SubElement(rate_v, "timebase").text = str(fps)
        ET.SubElement(rate_v, "ntsc").text = "FALSE"

        # Video Track
        v_track = ET.SubElement(video, "track")
        v_clips = video_clips or []
        for i, clip in enumerate(v_clips):
            clip_id = f"vclip-{i+1}"
            start_f = clip.get("start_frame", 0)
            end_f = clip.get("end_frame", start_f + fps * 5)
            in_f = clip.get("in_frame", 0)
            out_f = clip.get("out_frame", in_f + (end_f - start_f))
            c_name = clip.get("name", f"Video_{i+1}")
            file_p = Path(clip.get("file_path", "clip.mp4"))

            clip_item = ET.SubElement(v_track, "clipitem", id=clip_id)
            ET.SubElement(clip_item, "name").text = c_name
            ET.SubElement(clip_item, "duration").text = str(end_f - start_f)
            
            c_rate = ET.SubElement(clip_item, "rate")
            ET.SubElement(c_rate, "timebase").text = str(fps)
            ET.SubElement(c_rate, "ntsc").text = "FALSE"

            ET.SubElement(clip_item, "start").text = str(start_f)
            ET.SubElement(clip_item, "end").text = str(end_f)
            ET.SubElement(clip_item, "in").text = str(in_f)
            ET.SubElement(clip_item, "out").text = str(out_f)

            file_el = ET.SubElement(clip_item, "file", id=f"file-{clip_id}")
            ET.SubElement(file_el, "name").text = file_p.name
            ET.SubElement(file_el, "pathurl").text = self.file_to_pathurl(file_p)
            f_rate = ET.SubElement(file_el, "rate")
            ET.SubElement(f_rate, "timebase").text = str(fps)
            ET.SubElement(f_rate, "ntsc").text = "FALSE"
            ET.SubElement(file_el, "duration").text = str(end_f - start_f)

        # Audio Section
        audio = ET.SubElement(media, "audio")
        a_track = ET.SubElement(audio, "track")
        a_clips = audio_clips or []
        for j, aclip in enumerate(a_clips):
            aclip_id = f"aclip-{j+1}"
            start_f = aclip.get("start_frame", 0)
            end_f = aclip.get("end_frame", start_f + fps * 5)
            in_f = aclip.get("in_frame", 0)
            out_f = aclip.get("out_frame", in_f + (end_f - start_f))
            c_name = aclip.get("name", f"Audio_{j+1}")
            file_p = Path(aclip.get("file_path", "audio.wav"))

            aclip_item = ET.SubElement(a_track, "clipitem", id=aclip_id)
            ET.SubElement(aclip_item, "name").text = c_name
            ET.SubElement(aclip_item, "duration").text = str(end_f - start_f)

            ac_rate = ET.SubElement(aclip_item, "rate")
            ET.SubElement(ac_rate, "timebase").text = str(fps)
            ET.SubElement(ac_rate, "ntsc").text = "FALSE"

            ET.SubElement(aclip_item, "start").text = str(start_f)
            ET.SubElement(aclip_item, "end").text = str(end_f)
            ET.SubElement(aclip_item, "in").text = str(in_f)
            ET.SubElement(aclip_item, "out").text = str(out_f)

            afile_el = ET.SubElement(aclip_item, "file", id=f"file-{aclip_id}")
            ET.SubElement(afile_el, "name").text = file_p.name
            ET.SubElement(afile_el, "pathurl").text = self.file_to_pathurl(file_p)
            af_rate = ET.SubElement(afile_el, "rate")
            ET.SubElement(af_rate, "timebase").text = str(fps)
            ET.SubElement(af_rate, "ntsc").text = "FALSE"
            ET.SubElement(afile_el, "duration").text = str(end_f - start_f)

        # Pretty-print XML
        raw_xml = ET.tostring(xmeml, encoding="utf-8")
        parsed_dom = minidom.parseString(raw_xml)
        pretty_xml = parsed_dom.toprettyxml(indent="  ", encoding="utf-8")

        output_xml_path.parent.mkdir(parents=True, exist_ok=True)
        output_xml_path.write_bytes(pretty_xml)
        return output_xml_path

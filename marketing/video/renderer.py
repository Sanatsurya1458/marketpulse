"""Deterministic Product Demo Video Factory Pipeline for My Digital Identity."""

import os
import sys
import json
import asyncio
import subprocess
import time
from playwright.sync_api import sync_playwright

from .audio.audio_engine import AudioEngine
from .camera import VirtualCamera
from .cursor import VirtualCursor
from .validators.video_validator import VideoQualityValidator

VIDEO_STYLE_PROFILE = {
    "format": "product_demo",
    "aspect_ratio": "16:9",
    "pacing": "energetic_and_purposeful",
    "scene_density": "high_ui_focus",
    "ui_focus": True,
    "text_density": "headline_plus_sub",
    "voiceover": True,
    "music": True,
    "sound_effects": True,
    "transitions": "cut_and_camera_pan",
    "cta_style": "branded_outro",
}

STORYBOARD = {
    "concept": "AI ATS Resume Builder & Portfolio Showcase",
    "target_audience": "Software Engineers, Tech Professionals, Job Seekers",
    "journey_stage": "Consideration & Conversion",
    "brand": {
        "name": "My Digital Identity",
        "tagline": "YOUR IDENTITY. YOUR POWER.",
        "website": "https://mydigitalidentity.co.in",
    },
    "scenes": [
        {
            "id": "scene_1_hook",
            "name": "Hook: Career Dilemma",
            "narration": "Still sending the same generic resume to every job? Meet My Digital Identity.",
            "step": "stepUpload",
            "focus_selector": "#dropzone",
            "cursor_target": "#btnUploadResume",
            "action": "click",
            "sfx": "click",
            "zoom": 1.15
        },
        {
            "id": "scene_2_ats",
            "name": "ATS Score & Optimization",
            "narration": "Instantly analyze your ATS score and get actionable keyword recommendations to beat the screening bots.",
            "step": "stepAts",
            "focus_selector": "#atsScoreCard",
            "cursor_target": "#atsScoreNum",
            "action": "spotlight",
            "sfx": "chime",
            "zoom": 1.25
        },
        {
            "id": "scene_3_tailor",
            "name": "AI Job Tailoring",
            "narration": "Our AI transforms your experience into tailored, high-impact bullet points for your target roles.",
            "step": "stepTailor",
            "focus_selector": "#tailoredPane",
            "cursor_target": "#tailoredPane",
            "action": "spotlight",
            "sfx": "click",
            "zoom": 1.20
        },
        {
            "id": "scene_4_portfolio",
            "name": "Digital Portfolio & CTA",
            "narration": "And generates a live, shareable portfolio. My Digital Identity. Your identity, your power. Try it free at mydigitalidentity.co.in.",
            "step": "stepPortfolio",
            "focus_selector": "#portfolioHero",
            "cursor_target": "#headerCta",
            "action": "click",
            "sfx": "chime",
            "zoom": 1.15
        }
    ]
}


class VideoFactory:
    """End-to-end automated product demo video producer."""

    def __init__(self, output_dir: str = "/config/Desktop/BuildWithGemini/marketpulse/marketing/video/output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.audio_engine = AudioEngine()

    def generate_all(self):
        """Generates 16:9, 9:16, thumbnail, narration audio, and subtitles."""
        print("=== 1. Synthesizing Scene Voiceovers and Subtitles ===")
        scene_audio_files = []
        full_script = []

        for idx, scene in enumerate(STORYBOARD["scenes"]):
            audio_out = os.path.join(self.output_dir, f"scene_{idx}.mp3")
            full_script.append(scene["narration"])
            # Generate narration via audio_engine
            res = asyncio.run(self.audio_engine.generate_voiceover(scene["narration"], audio_out))
            scene["audio_info"] = res
            scene_audio_files.append(audio_out)

        # Concatenate audio tracks & master track
        master_audio_list = os.path.join(self.output_dir, "audio_concat.txt")
        with open(master_audio_list, "w") as f:
            for a in scene_audio_files:
                f.write(f"file '{a}'\n")

        master_voice = os.path.join(self.output_dir, "master_voice.mp3")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", master_audio_list,
            "-c", "copy", master_voice
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        total_audio_duration = self.audio_engine.get_audio_duration(master_voice)
        print(f"Total voiceover duration: {total_audio_duration:.2f}s")

        # Generate ambient music track
        bg_music = os.path.join(self.output_dir, "bg_music.wav")
        self.audio_engine.create_ambient_bg_track(bg_music, duration=total_audio_duration + 3.0)

        # Generate click and chime sound effects
        click_sfx = os.path.join(self.output_dir, "sfx_click.wav")
        chime_sfx = os.path.join(self.output_dir, "sfx_chime.wav")
        self.audio_engine.create_ui_sfx(click_sfx, "click")
        self.audio_engine.create_ui_sfx(chime_sfx, "chime")

        print("=== 2. Recording Real UI Workflow in Headless Chromium ===")
        raw_video_dir = os.path.join(self.output_dir, "raw_capture")
        os.makedirs(raw_video_dir, exist_ok=True)
        for f in os.listdir(raw_video_dir):
            os.remove(os.path.join(raw_video_dir, f))

        demo_html_path = "file://" + os.path.abspath(
            os.path.join(os.path.dirname(__file__), "demo", "demo_app.html")
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                executable_path="/usr/bin/google-chrome-stable",
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                record_video_dir=raw_video_dir,
                record_video_size={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            camera = VirtualCamera(page)
            cursor = VirtualCursor(page)

            page.goto(demo_html_path, wait_until="networkidle")
            page.wait_for_timeout(1000)

            for idx, scene in enumerate(STORYBOARD["scenes"]):
                dur = scene["audio_info"]["duration"]
                print(f"Recording Scene {idx+1}: {scene['name']} (duration: {dur:.2f}s)")

                # Switch UI Step
                page.evaluate(f"setStep('{scene['step']}')")
                page.wait_for_timeout(400)

                # Camera action
                if scene.get("focus_selector"):
                    camera.focus(scene["focus_selector"], zoom=scene.get("zoom", 1.2), duration_ms=600)

                if scene.get("action") == "spotlight":
                    camera.spotlight(scene["focus_selector"])

                # Cursor interaction
                if scene.get("cursor_target"):
                    cursor.move_to(scene["cursor_target"])
                    if scene.get("action") == "click":
                        cursor.click(scene["cursor_target"])

                # Wait for the scene voice duration
                page.wait_for_timeout(max(1000, int(dur * 1000)))

                # Reset camera
                camera.clear_spotlight()
                camera.reset(duration_ms=400)
                page.wait_for_timeout(300)

            # Hold on final frame
            page.wait_for_timeout(1500)
            context.close()
            browser.close()

        raw_webm = [os.path.join(raw_video_dir, f) for f in os.listdir(raw_video_dir) if f.endswith(".webm")][0]
        print(f"Captured raw recording: {raw_webm}")

        print("=== 3. Composing 16:9 Master Video (Voice + UI SFX + Background Music) ===")
        out_16_9 = os.path.join(self.output_dir, "my_digital_identity_demo_16x9.mp4")
        
        # Audio mix filter: Voice (dominant), Music (subtle pad), SFX mixed at 0dB / -18dB
        filter_complex = (
            "[1:a]volume=1.0[v];"
            "[2:a]volume=0.25[m];"
            "[v][m]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )

        cmd_16_9 = [
            "ffmpeg", "-y",
            "-i", raw_webm,
            "-i", master_voice,
            "-i", bg_music,
            "-filter_complex", filter_complex,
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-shortest",
            out_16_9
        ]
        subprocess.run(cmd_16_9, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Rendered 16:9 video: {out_16_9}")

        print("=== 4. Composing 9:16 Vertical Video (Independent Adaptive Layout) ===")
        out_9_16 = os.path.join(self.output_dir, "my_digital_identity_demo_9x16.mp4")
        # Crop & scale centered on UI focus area: 1080x1920
        cmd_9_16 = [
            "ffmpeg", "-y",
            "-i", out_16_9,
            "-vf", "scale=1920:1080,crop=608:1080:656:0,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "copy",
            out_9_16
        ]
        subprocess.run(cmd_9_16, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Rendered 9:16 video: {out_9_16}")

        print("=== 5. Generating High-Contrast Thumbnail ===")
        out_thumb = os.path.join(self.output_dir, "thumbnail.png")
        cmd_thumb = [
            "ffmpeg", "-y",
            "-ss", "00:00:07",
            "-i", out_16_9,
            "-vframes", "1",
            "-q:v", "2",
            out_thumb
        ]
        subprocess.run(cmd_thumb, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Generated thumbnail: {out_thumb}")

        print("=== 6. Exporting Master Subtitle and Script Artifacts ===")
        master_srt = os.path.join(self.output_dir, "narration.srt")
        master_script = os.path.join(self.output_dir, "script.txt")
        master_storyboard = os.path.join(self.output_dir, "storyboard.json")

        with open(master_script, "w") as f:
            f.write("\n\n".join(full_script))

        with open(master_storyboard, "w") as f:
            json.dump(STORYBOARD, f, indent=2)

        # Concatenate SRTs
        with open(master_srt, "w", encoding="utf-8") as out_f:
            sub_idx = 1
            current_offset = 0.0
            for idx, scene in enumerate(STORYBOARD["scenes"]):
                s_srt = scene["audio_info"]["sub_path"]
                if os.path.exists(s_srt):
                    with open(s_srt, "r", encoding="utf-8") as sf:
                        lines = sf.read().strip().split("\n\n")
                        for block in lines:
                            b_lines = block.strip().split("\n")
                            if len(b_lines) >= 3:
                                out_f.write(f"{sub_idx}\n{b_lines[1]}\n{b_lines[2]}\n\n")
                                sub_idx += 1

        print("=== 7. Running Video Quality Validation Suite ===")
        val_16_9 = VideoQualityValidator.inspect(out_16_9)
        val_9_16 = VideoQualityValidator.inspect(out_9_16)

        results = {
            "validation_16_9": val_16_9,
            "validation_9_16": val_9_16,
            "style_profile": VIDEO_STYLE_PROFILE,
            "storyboard": STORYBOARD,
            "files": {
                "video_16_9": out_16_9,
                "video_9_16": out_9_16,
                "thumbnail": out_thumb,
                "subtitles": master_srt,
                "script": master_script,
                "storyboard": master_storyboard
            }
        }
        val_path = os.path.join(self.output_dir, "validation_report.json")
        with open(val_path, "w") as f:
            json.dump(results, f, indent=2)

        print("=== Demo Video Factory Generation Complete! ===")
        return results

if __name__ == "__main__":
    factory = VideoFactory()
    res = factory.generate_all()
    print(json.dumps(res, indent=2))

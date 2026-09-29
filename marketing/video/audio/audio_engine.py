"""Audio engine: synthesizes voiceover via edge-tts, generates UI sound effects, and mixes audio with FFmpeg."""

import asyncio
import os
import wave
import math
import struct
import subprocess
from typing import List, Dict, Any, Optional

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False


class AudioEngine:
    """Manages narration, sound effects, and audio mixing."""

    def __init__(self, voice: str = "en-US-GuyNeural"):
        self.voice = voice

    async def generate_voiceover(self, text: str, output_path: str) -> Dict[str, Any]:
        """Generates voiceover audio and synchronized subtitle word boundaries using edge-tts."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        sub_path = os.path.splitext(output_path)[0] + ".srt"

        if not HAS_EDGE_TTS:
            # Fallback mock speech using silent audio or tone if edge_tts is missing
            self._create_mock_audio(output_path, duration=3.0)
            return {"audio_path": output_path, "sub_path": sub_path, "duration": 3.0}

        tts = edge_tts.Communicate(text, self.voice)
        sub_maker = edge_tts.SubMaker()
        with open(output_path, "wb") as f:
            async for chunk in tts.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    sub_maker.feed(chunk)

        with open(sub_path, "w", encoding="utf-8") as f:
            f.write(sub_maker.get_srt())

        duration = self.get_audio_duration(output_path)
        return {
            "audio_path": output_path,
            "sub_path": sub_path,
            "duration": duration,
        }

    @staticmethod
    def get_audio_duration(path: str) -> float:
        """Calculates audio duration in seconds using ffprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path
            ]
            res = subprocess.check_output(cmd).decode().strip()
            return float(res)
        except Exception:
            return 3.0

    @staticmethod
    def create_ui_sfx(output_path: str, effect_type: str = "click"):
        """Generates subtle synthetic UI sound effects without external audio files."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        sample_rate = 44100
        
        if effect_type == "click":
            freq, duration, volume = 950, 0.04, 0.18
        elif effect_type == "chime":
            freq, duration, volume = 659.25, 0.35, 0.22
        elif effect_type == "whoosh":
            freq, duration, volume = 320, 0.20, 0.15
        else:
            freq, duration, volume = 440, 0.10, 0.15

        n_samples = int(sample_rate * duration)
        with wave.open(output_path, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            for i in range(n_samples):
                env = math.exp(-4.0 * (i / n_samples))
                val = int(volume * env * 32767.0 * math.sin(2.0 * math.pi * freq * (i / sample_rate)))
                wav.writeframes(struct.pack('<h', max(-32768, min(32767, val))))

    @staticmethod
    def create_ambient_bg_track(output_path: str, duration: float = 30.0):
        """Generates a warm, subtle, modern ambient chord progression pad for demo background music."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        # Soft chords: C maj7 -> Am7 -> F maj7 -> G sus
        chords = [
            [261.63, 329.63, 392.00, 493.88],  # Cmaj7
            [220.00, 261.63, 329.63, 392.00],  # Am7
            [174.61, 220.00, 261.63, 329.63],  # Fmaj7
            [196.00, 261.63, 293.66, 392.00],  # Gsus4
        ]
        chord_len = 4.0  # seconds per chord

        with wave.open(output_path, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            for i in range(n_samples):
                t = i / sample_rate
                chord_idx = int((t % (chord_len * len(chords))) / chord_len)
                chord = chords[chord_idx]
                
                # blend frequencies with gentle tremolo
                val = 0
                for f in chord:
                    val += math.sin(2.0 * math.pi * f * t)
                val = val / len(chord)
                # low-volume background pad
                volume = 0.045 * (0.8 + 0.2 * math.sin(2.0 * math.pi * 0.5 * t))
                sample = int(volume * 32767.0 * val)
                wav.writeframes(struct.pack('<h', max(-32768, min(32767, int(val * 1000)))))

    def _create_mock_audio(self, path: str, duration: float):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        with wave.open(path, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(b'\x00\x00' * n_samples)

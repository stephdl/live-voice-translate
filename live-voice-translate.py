#!/usr/bin/env python3
"""
live-voice-translate - Real-time Italian→English audio translation
Copyright (C) 2026 Stéphane de Labrusse

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Author: Stéphane de Labrusse
"""

import os
import sys
import subprocess
from pathlib import Path

# ============================================================================
# VIRTUALENV SETUP - Runs first, before any other imports
# ============================================================================

VENV_DIR = Path.home() / ".local/share/live-voice-translate/venv"
REQUIRED_PACKAGES = ["faster-whisper", "argostranslate"]

def setup_virtualenv():
    """Create virtualenv and install dependencies if needed"""
    if not VENV_DIR.exists():
        print("═══════════════════════════════════════════")
        print("   First Run Setup")
        print("═══════════════════════════════════════════")
        print("\nCreating isolated environment...")
        print(f"Location: {VENV_DIR}\n")
        
        # Create virtualenv
        VENV_DIR.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        
        # Install dependencies
        pip = VENV_DIR / "bin" / "pip"
        print(f"Installing dependencies: {', '.join(REQUIRED_PACKAGES)}")
        print("This may take 2-3 minutes...\n")
        
        subprocess.run(
            [str(pip), "install", "--upgrade", "pip"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        
        subprocess.run(
            [str(pip), "install"] + REQUIRED_PACKAGES,
            check=True
        )
        
        print("\n✅ Setup complete!")
        print("Starting translation...\n")
    
    # Re-execute with virtualenv Python if not already in it
    venv_python = VENV_DIR / "bin" / "python"
    if Path(sys.executable).resolve() != venv_python.resolve():
        os.execv(str(venv_python), [str(venv_python)] + sys.argv)

# Setup virtualenv BEFORE importing dependencies
setup_virtualenv()

# ============================================================================
# NOW SAFE TO IMPORT - We're running in virtualenv
# ============================================================================

import argparse
import wave
import io
import re
import textwrap
from datetime import datetime

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

import argostranslate.package
import argostranslate.translate
from faster_whisper import WhisperModel


# ============================================================================
# CORE APPLICATION CODE
# ============================================================================

class AudioCapture:
    """Handle audio stream capture using PipeWire/PulseAudio"""
    
    @staticmethod
    def get_active_stream():
        """Detect active audio monitor stream"""
        try:
            result = subprocess.run(
                ["pactl", "list", "short", "sources"],
                capture_output=True, text=True, check=True
            )
            
            for line in result.stdout.splitlines():
                if "monitor" in line and "RUNNING" in line:
                    return line.split()[0]
            
            return None
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    @staticmethod
    def capture_audio(stream_id, segment_size):
        """Capture audio segment from stream"""
        cmd = [
            "parec",
            f"--monitor-stream={stream_id}",
            "--format=s16le",
            "--rate=16000",
            "--channels=1"
        ]
        
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        audio_data = proc.stdout.read(segment_size)
        proc.terminate()
        
        return audio_data


class ModelConfig:
    """Whisper model configurations - optimized for Italian"""
    
    CONFIGS = {
        "tiny": {
            "fast": {"segment": 64000, "beam": 1, "precision": "60%", "latency": "0.5s"},
            "normal": {"segment": 128000, "beam": 1, "precision": "60%", "latency": "1.5s"},
            "slow": {"segment": 160000, "beam": 1, "precision": "60%", "latency": "2s"},
        },
        "base": {
            "fast": {"segment": 96000, "beam": 3, "precision": "85%", "latency": "2s"},
            "normal": {"segment": 160000, "beam": 3, "precision": "85%", "latency": "4s"},
            "slow": {"segment": 192000, "beam": 3, "precision": "85%", "latency": "5s"},
        },
        "small": {
            "fast": {"segment": 128000, "beam": 3, "precision": "90%", "latency": "3s"},
            "normal": {"segment": 192000, "beam": 3, "precision": "90%", "latency": "5s"},
            "slow": {"segment": 256000, "beam": 3, "precision": "90%", "latency": "7s"},
        },
        "medium": {
            "fast": {"segment": 128000, "beam": 4, "precision": "95%", "latency": "4s"},
            "normal": {"segment": 256000, "beam": 4, "precision": "95%", "latency": "8s"},
            "slow": {"segment": 320000, "beam": 4, "precision": "95%", "latency": "10s"},
        },
        "large-v3": {
            "fast": {"segment": 160000, "beam": 5, "precision": "98%", "latency": "6s"},
            "normal": {"segment": 320000, "beam": 5, "precision": "98%", "latency": "12s"},
            "slow": {"segment": 480000, "beam": 5, "precision": "98%", "latency": "18s"},
        },
    }
    
    @classmethod
    def get_config(cls, model, mode="normal"):
        """Get configuration for model and mode"""
        return cls.CONFIGS.get(model, cls.CONFIGS["medium"])[mode]


class TranscriptWriter:
    """Handle saving transcripts to Markdown files"""
    
    def __init__(self, filepath, model, mode):
        self.filepath = filepath
        self.file_handle = None
        
        if filepath:
            try:
                self.file_handle = open(filepath, 'w', encoding='utf-8')
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.file_handle.write(f"# Live Voice Translation\n\n")
                self.file_handle.write(f"**Date:** {now}  \n")
                self.file_handle.write(f"**Model:** {model}  \n")
                self.file_handle.write(f"**Mode:** {mode}  \n\n")
                self.file_handle.write("---\n\n")
                self.file_handle.flush()
                print(f"💾 Saving to: {filepath}\n", flush=True)
            except Exception as e:
                print(f"⚠️  Warning: Could not open save file: {e}\n", flush=True)
                self.file_handle = None
    
    def write(self, timestamp, text_it, text_en):
        """Write translation to file"""
        if self.file_handle:
            self.file_handle.write(f"**[{timestamp}]**\n\n")
            self.file_handle.write(f"🇮🇹 *{text_it}*\n\n")
            self.file_handle.write(f"🇬🇧 {text_en}\n\n")
            self.file_handle.write("---\n\n")
            self.file_handle.flush()
    
    def close(self):
        """Close file with end timestamp"""
        if self.file_handle:
            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.file_handle.write(f"\n**End of session:** {end_time}\n")
            self.file_handle.close()
            print(f"\n💾 Transcript saved to: {self.filepath}")


class LiveTranslator:
    """Main translation engine"""
    
    def __init__(self, model_name, mode, save_file=None):
        self.model_name = model_name
        self.mode = mode
        self.config = ModelConfig.get_config(model_name, mode)
        self.writer = TranscriptWriter(save_file, model_name, mode)
        self.model = None
        
    def setup(self):
        """Initialize Whisper model and translation"""
        # Ensure IT→EN model is installed
        self._install_translation_model()
        
        # Load Whisper model
        print(f"⏳ Loading model {self.model_name}...", flush=True)
        self.model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
        print("✅ Ready\n", flush=True)
    
    @staticmethod
    def _install_translation_model():
        """Ensure Argos IT→EN model is installed"""
        try:
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            
            # Check if already installed
            installed_packages = argostranslate.package.get_installed_packages()
            if any(pkg.from_code == "it" and pkg.to_code == "en" for pkg in installed_packages):
                return
            
            # Install IT→EN package
            package_to_install = next(
                filter(lambda x: x.from_code == "it" and x.to_code == "en", available_packages)
            )
            argostranslate.package.install_from_path(package_to_install.download())
        except Exception as e:
            print(f"Warning: Could not install translation model: {e}")
    
    def process_audio(self, audio_data):
        """Transcribe and translate audio segment"""
        # Skip silence
        if len(audio_data) < 50000:
            return
        
        # Create WAV buffer
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data)
        wav_buffer.seek(0)
        
        # Save to temporary file
        with open("/tmp/audio_chunk.wav", "wb") as f:
            f.write(wav_buffer.read())
        
        # Transcribe with Whisper
        segments, _ = self.model.transcribe(
            "/tmp/audio_chunk.wav",
            language="it",
            vad_filter=False,
            beam_size=self.config["beam"],
            condition_on_previous_text=True
        )
        
        # Translate and display
        for segment in segments:
            text_it = segment.text.strip()
            if text_it and len(text_it) > 3:
                # Split by sentence
                for sentence in re.split(r'(?<=[.!?])\s+', text_it):
                    sentence = sentence.strip()
                    if len(sentence) > 5:
                        self._translate_and_display(sentence)
    
    def _translate_and_display(self, text_it):
        """Translate Italian text and display/save"""
        # Translate IT→EN
        text_en = argostranslate.translate.translate(text_it, "it", "en")
        
        # Get timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Display with timestamp and word wrap
        if len(text_en) > 70:
            output = textwrap.fill(
                text_en, width=70,
                initial_indent=f"[{timestamp}] ▶ ",
                subsequent_indent=" " * 13
            )
        else:
            output = f"[{timestamp}] ▶ {text_en}"
        
        print(output, flush=True)
        
        # Save to file if enabled
        self.writer.write(timestamp, text_it, text_en)
    
    def run(self, stream_id):
        """Main translation loop"""
        try:
            while True:
                audio_data = AudioCapture.capture_audio(stream_id, self.config["segment"])
                self.process_audio(audio_data)
        except KeyboardInterrupt:
            print("\n\nStopping translation.")
        finally:
            self.writer.close()


def show_menu():
    """Interactive model selection menu"""
    print("═══════════════════════════════════════════")
    print("   Jitsi IT→EN Translation")
    print("═══════════════════════════════════════════")
    print()
    print("Available models:")
    print()
    print("  1) tiny   - Ultra fast     (60% accuracy, ~1.5s, 1GB RAM)")
    print("  2) base   - Fast           (85% accuracy, ~4s, 1.5GB RAM)")
    print("  3) small  - Balanced       (90% accuracy, ~5s, 2GB RAM)")
    print("  4) medium - Recommended    (95% accuracy, ~8s, 5GB RAM) [DEFAULT]")
    print("  5) large  - Maximum        (98% accuracy, ~12s, 10GB RAM) ⚠️  High fan")
    print()
    
    choice = input("Your choice (1-5 or Enter for default): ").strip()
    
    models = {
        "1": "tiny",
        "2": "base",
        "3": "small",
        "4": "medium",
        "5": "large-v3",
        "": "medium"
    }
    
    return models.get(choice, "medium")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Real-time Italian→English audio translation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Interactive menu
  %(prog)s medium                    # Medium model
  %(prog)s medium --save             # Save to auto-generated file
  %(prog)s large --slow --save meeting.md
        """
    )
    
    parser.add_argument(
        "model",
        nargs="?",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model to use"
    )
    
    parser.add_argument(
        "--fast", "-f",
        action="store_true",
        help="Shorter segments (faster, may cut sentences)"
    )
    
    parser.add_argument(
        "--slow", "-s",
        action="store_true",
        help="Longer segments (complete sentences)"
    )
    
    parser.add_argument(
        "--save",
        nargs="?",
        const=f"live-translate-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md",
        metavar="FILE",
        help="Save transcript to file (default: auto-generated)"
    )
    
    args = parser.parse_args()
    
    # Determine model
    if args.model:
        model = args.model if args.model != "large" else "large-v3"
    else:
        model = show_menu()
    
    # Determine mode
    if args.fast:
        mode = "fast"
    elif args.slow:
        mode = "slow"
    else:
        mode = "normal"
    
    # Get model config for display
    config = ModelConfig.get_config(model, mode)
    
    # Display configuration
    print()
    print("═══════════════════════════════════════════")
    print("   Configuration")
    print("═══════════════════════════════════════════")
    print()
    print(f"  Model      : {model}")
    print(f"  Accuracy   : {config['precision']}")
    print(f"  Latency    : ~{config['latency']}")
    if mode == "fast":
        print("  Mode       : Fast (shorter segments)")
    elif mode == "slow":
        print("  Mode       : Slow (longer segments, complete sentences)")
    if args.save:
        print(f"  Save to    : {args.save}")
    print()
    
    # Detect audio stream
    stream_id = AudioCapture.get_active_stream()
    if not stream_id:
        print("Error: No active audio stream detected", file=sys.stderr)
        print("Launch a YouTube video or Jitsi call with sound", file=sys.stderr)
        sys.exit(1)
    
    print(f"  Stream     : {stream_id}")
    print()
    print("═══════════════════════════════════════════")
    print()
    print("Translation in progress... (Ctrl+C to stop)")
    print()
    
    # Run translator
    translator = LiveTranslator(model, mode, args.save)
    translator.setup()
    translator.run(stream_id)


if __name__ == "__main__":
    main()

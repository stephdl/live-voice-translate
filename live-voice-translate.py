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
    venv_python = VENV_DIR / "bin" / "python"
    
    # Check if we're already running in the venv
    current_python = Path(sys.executable).resolve()
    
    if VENV_DIR.exists():
        venv_python_resolved = venv_python.resolve()
        
        # Already in venv, verify packages are installed
        if current_python == venv_python_resolved:
            # Check if all packages are available
            missing = []
            for pkg in REQUIRED_PACKAGES:
                pkg_import = pkg.replace("-", "_")  # faster-whisper → faster_whisper
                try:
                    result = subprocess.run(
                        [sys.executable, "-c", f"import {pkg_import}"],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode != 0:
                        missing.append(pkg)
                except Exception:
                    missing.append(pkg)
            
            # Install missing packages
            if missing:
                print(f"\n⚠️  Installing missing packages: {', '.join(missing)}\n")
                pip = VENV_DIR / "bin" / "pip"
                for pkg in missing:
                    print(f"  Installing {pkg}...", flush=True)
                    try:
                        subprocess.run([str(pip), "install", pkg], check=True)
                        print(f"  ✅ {pkg} installed\n", flush=True)
                    except subprocess.CalledProcessError as e:
                        print(f"  ❌ Failed to install {pkg}: {e}\n", flush=True)
                        sys.exit(1)
            
            # All packages present, continue normally
            return
        
        # Not in venv but venv exists, re-execute
        print(f"🔄 Switching to virtualenv Python...\n", flush=True)
        os.execv(str(venv_python), [str(venv_python)] + sys.argv)
    
    # Venv doesn't exist, create it
    print("═══════════════════════════════════════════")
    print("   First Run Setup")
    print("═══════════════════════════════════════════")
    print(f"\nCreating isolated environment...")
    print(f"Location: {VENV_DIR}\n")
    
    # Create virtualenv
    VENV_DIR.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtualenv: {e}")
        print("   Make sure python3-venv is installed:")
        print("   sudo dnf install python3-venv")
        sys.exit(1)
    
    # Install dependencies
    pip = VENV_DIR / "bin" / "pip"
    print(f"Installing dependencies: {', '.join(REQUIRED_PACKAGES)}")
    print("This may take 2-3 minutes...\n")
    
    # Upgrade pip first
    subprocess.run(
        [str(pip), "install", "--upgrade", "pip"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    
    # Install packages one by one with progress
    for pkg in REQUIRED_PACKAGES:
        print(f"  Installing {pkg}...", flush=True)
        try:
            subprocess.run([str(pip), "install", pkg], check=True)
            print(f"  ✅ {pkg} installed\n", flush=True)
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {pkg}: {e}\n", flush=True)
            sys.exit(1)
    
    print("\n✅ Setup complete!")
    print("🔄 Restarting with virtualenv Python...\n")
    
    # Re-execute with virtualenv Python
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
import select
import termios
import tty
from threading import Thread
import queue

# Force UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

import argostranslate.package
import argostranslate.translate
from faster_whisper import WhisperModel


# ============================================================================
# KEYBOARD CONTROLLER (using select - no dependencies)
# ============================================================================

class KeyboardController:
    """Handle keyboard shortcuts using select (non-blocking, no dependencies)"""
    
    def __init__(self, translator):
        """
        Initialize keyboard controller
        
        Args:
            translator: LiveTranslator instance to control
        """
        self.translator = translator
        self.old_settings = None
        
        # Keyboard shortcuts help
        self.shortcuts = {
            'p': 'Pause/Resume',
            's': 'Save transcript now',
            'm': 'Change mode (fast/normal/slow)',
            'i': 'Toggle Italian display',
            'q': 'Quit',
            'h': 'Show this help',
        }
    
    def setup(self):
        """Setup terminal for non-blocking input"""
        if sys.stdin.isatty():
            try:
                self.old_settings = termios.tcgetattr(sys.stdin)
                tty.setcbreak(sys.stdin.fileno())
                
                print("\n💡 Keyboard shortcuts enabled:")
                self._show_help()
                return True
            except Exception as e:
                print(f"\n⚠️  Could not enable keyboard shortcuts: {e}")
                return False
        return False
    
    def cleanup(self):
        """Restore terminal settings"""
        if self.old_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            except:
                pass
    
    def get_key(self, timeout=0.01):
        """
        Get key if pressed (non-blocking)
        
        Args:
            timeout: Timeout in seconds (default 0.01)
        
        Returns:
            str: Key pressed or None if no key
        """
        try:
            if select.select([sys.stdin], [], [], timeout)[0]:
                char = sys.stdin.read(1)
                # Only return single printable ASCII characters
                if char and len(char) == 1 and char.isprintable():
                    return char
            return None
        except Exception:
            return None
    
    def handle_key(self, key):
        """Handle keyboard shortcuts"""
        if not key:
            return
        
        # Convert to lowercase
        key = key.lower()
        
        # Only process single character keys
        if len(key) != 1:
            return
        
        # Handle shortcuts - STRICT checking
        if key == 'p':
            self._toggle_pause()
        elif key == 's':
            self._save_now()
        elif key == 'm':
            self._change_mode()
        elif key == 'i':
            self._toggle_italian()
        elif key == 'q':
            self._quit()
        elif key == 'h':
            self._show_help()
        # Silently ignore other keys
    
    def _toggle_pause(self):
        """Toggle pause/resume"""
        self.translator.paused = not self.translator.paused
        
        if self.translator.paused:
            print("\n⏸️  PAUSED. Press 'p' to resume.", flush=True)
        else:
            print("\n▶️  RESUMED", flush=True)
    
    def _save_now(self):
        """Force save transcript now (create file if needed)"""
        # Si pas de fichier configuré, en créer un automatiquement
        if not self.translator.writer.filepath:
            # Générer nom de fichier auto
            filename = f"live-translate-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
            
            print(f"\n💾 Creating save file: {filename}", flush=True)
            
            # Créer le writer avec le nouveau fichier
            self.translator.writer = TranscriptWriter(
                filename,
                self.translator.model_name,
                self.translator.mode
            )
            
            if self.translator.writer.filepath:
                print(f"✅ Now saving to: {filename}", flush=True)
            else:
                print(f"❌ Could not create save file", flush=True)
        else:
            # Fichier existe déjà, juste sauvegarder
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"\n💾 [{timestamp}] Saving transcript...", flush=True)
            self.translator.writer.file_handle.flush()
            print(f"✅ Saved to: {self.translator.writer.filepath}", flush=True)
    
    def _change_mode(self):
        """Cycle through modes: fast → normal → slow → fast"""
        modes = ['fast', 'normal', 'slow']
        current_idx = modes.index(self.translator.mode)
        new_idx = (current_idx + 1) % len(modes)
        new_mode = modes[new_idx]
        
        # Update mode and config
        self.translator.mode = new_mode
        self.translator.config = ModelConfig.get_config(
            self.translator.model_name,
            new_mode
        )
        
        # Show change
        latency = self.translator.config['latency']
        print(f"\n🔄 Mode changed: {new_mode.upper()} (latency ~{latency})", flush=True)
    
    def _toggle_italian(self):
        """Toggle Italian text display"""
        self.translator.show_italian = not self.translator.show_italian
        
        if self.translator.show_italian:
            print("\n🇮🇹 Italian display: ON", flush=True)
        else:
            print("\n🇮🇹 Italian display: OFF", flush=True)
    
    def _quit(self):
        """Quit gracefully"""
        print("\n\n👋 Quitting...", flush=True)
        self.translator.should_quit = True
    
    def _show_help(self):
        """Show keyboard shortcuts"""
        print("\n╔════════════════════════════════════════╗")
        print("║       Keyboard Shortcuts               ║")
        print("╠════════════════════════════════════════╣")
        for key, description in self.shortcuts.items():
            print(f"║  {key.upper()}  → {description:<30} ║")
        print("╚════════════════════════════════════════╝\n")


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
    """Main translation engine with keyboard control"""
    
    def __init__(self, model_name, mode, save_file=None, enable_keyboard=True, show_italian=False, vad_filter=True):
        self.model_name = model_name
        self.mode = mode
        self.config = ModelConfig.get_config(model_name, mode)
        self.writer = TranscriptWriter(save_file, model_name, mode)
        self.model = None
        self.vad_filter = vad_filter

        # Keyboard control
        self.enable_keyboard = enable_keyboard
        self.keyboard_controller = None
        self.paused = False
        self.should_quit = False

        # Display options
        self.show_italian = show_italian
        
        # Audio threading
        self.audio_queue = queue.Queue(maxsize=2)
        self.capture_thread = None
        
    def setup(self):
        """Initialize Whisper model, translation, and keyboard"""
        # Ensure IT→EN model is installed
        self._install_translation_model()
        
        # Load Whisper model
        print(f"⏳ Loading model {self.model_name}...", flush=True)
        self.model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
        print("✅ Ready\n", flush=True)
        
        # Start keyboard controller
        if self.enable_keyboard:
            self.keyboard_controller = KeyboardController(self)
            if not self.keyboard_controller.setup():
                self.keyboard_controller = None
    
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
    
    def _audio_capture_loop(self, stream_id):
        """Background thread for continuous audio capture"""
        while not self.should_quit:
            try:
                audio_data = AudioCapture.capture_audio(stream_id, self.config["segment"])
                
                # Try to add to queue (non-blocking)
                try:
                    self.audio_queue.put(audio_data, timeout=0.5)
                except queue.Full:
                    # Queue full, skip this segment
                    pass
                    
            except Exception as e:
                if not self.should_quit:
                    print(f"\n⚠️  Audio capture error: {e}", flush=True)
                break
    
    def process_audio(self, audio_data):
        """Transcribe and translate audio segment (with pause support)"""
        # Check if paused
        if self.paused:
            return
        
        # Skip very short audio
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
            vad_filter=self.vad_filter,
            beam_size=self.config["beam"],
            condition_on_previous_text=True
        )
        
        # Translate and display
        separator_printed = False
        for segment in segments:
            text_it = segment.text.strip()
            if text_it and len(text_it) > 3:
                for sentence in re.split(r'(?<=[.!?])\s+', text_it):
                    sentence = sentence.strip()
                    if len(sentence) > 5:
                        if not separator_printed:
                            print("─" * 50, flush=True)
                            separator_printed = True
                        self._translate_and_display(sentence)
    
    def _translate_and_display(self, text_it):
        """Translate Italian text and display/save"""
        # Translate IT→EN
        text_en = argostranslate.translate.translate(text_it, "it", "en")
        
        # Get timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Display Italian if enabled
        if self.show_italian:
            # Display Italian line (light green color)
            if len(text_it) > 70:
                output_it = textwrap.fill(
                    text_it, width=70,
                    initial_indent=f"[{timestamp}] ",
                    subsequent_indent=" " * 13
                )
            else:
                output_it = f"[{timestamp}] {text_it}"
            
            # Print Italian in light green (color code 92)
            print(f"\033[92m{output_it}\033[0m", flush=True)
        
        # Display English translation (normal white with arrow)
        if len(text_en) > 70:
            output_en = textwrap.fill(
                text_en, width=70,
                initial_indent=f"[{timestamp}] ▶ ",
                subsequent_indent=" " * 13
            )
        else:
            output_en = f"[{timestamp}] ▶ {text_en}"
        
        print(output_en, flush=True)
        
        # Save to file if enabled
        self.writer.write(timestamp, text_it, text_en)
    
    def run(self, stream_id):
        """Main translation loop with keyboard control"""
        # Start audio capture in background thread
        self.capture_thread = Thread(
            target=self._audio_capture_loop, 
            args=(stream_id,), 
            daemon=True
        )
        self.capture_thread.start()
        
        try:
            while not self.should_quit:
                # Check keyboard input (fast, non-blocking)
                if self.keyboard_controller:
                    key = self.keyboard_controller.get_key(timeout=0.01)
                    if key:
                        self.keyboard_controller.handle_key(key)
                
                # Get audio from queue (non-blocking with timeout)
                try:
                    audio_data = self.audio_queue.get(timeout=0.1)
                    self.process_audio(audio_data)
                except queue.Empty:
                    # No audio ready yet, continue checking keyboard
                    pass
                    
        except KeyboardInterrupt:
            print("\n\nStopping translation.")
        finally:
            # Signal threads to stop
            self.should_quit = True
            
            # Cleanup keyboard
            if self.keyboard_controller:
                self.keyboard_controller.cleanup()
            
            # Wait for capture thread to finish
            if self.capture_thread and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=2.0)
            
            # Close file
            self.writer.close()


def show_menu():
    """Interactive model selection menu"""
    print("═══════════════════════════════════════════")
    print("   IT→EN Live Translation")
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
  %(prog)s medium --show-italian     # Display Italian + English
  %(prog)s medium --no-vad           # Disable Voice Activity Detection

Keyboard shortcuts (during execution):
  p - Pause/Resume
  s - Save transcript now (creates file if needed)
  m - Change mode (fast/normal/slow)
  i - Toggle Italian display
  q - Quit
  h - Show help
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
    
    parser.add_argument(
        "--show-italian", "-i",
        action="store_true",
        help="Display Italian text (toggle with 'i' key)"
    )
    
    parser.add_argument(
        "--no-vad",
        action="store_true",
        help="Disable Voice Activity Detection (transcribe silence too)"
    )

    parser.add_argument(
        "--no-keyboard",
        action="store_true",
        help="Disable keyboard shortcuts"
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
    if args.show_italian:
        print(f"  Italian    : Displayed")
    print(f"  VAD        : {'Disabled' if args.no_vad else 'Enabled (skips silence)'}")
    print()
    
    # Detect audio stream
    stream_id = AudioCapture.get_active_stream()
    if not stream_id:
        print("Error: No active audio stream detected", file=sys.stderr)
        print("Launch a YouTube video or video call with sound", file=sys.stderr)
        sys.exit(1)
    
    print(f"  Stream     : {stream_id}")
    print()
    print("═══════════════════════════════════════════")
    print()
    print("Translation in progress... (Ctrl+C to stop)")
    print()
    
    # Run translator
    translator = LiveTranslator(
        model, mode, args.save,
        enable_keyboard=not args.no_keyboard,
        show_italian=args.show_italian,
        vad_filter=not args.no_vad,
    )
    translator.setup()
    translator.run(stream_id)


if __name__ == "__main__":
    main()

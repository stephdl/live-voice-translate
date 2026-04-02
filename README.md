# live-voice-translate

Real-time Italian→English, French, Spanish, German audio translation using Whisper and Argos Translate.

Captures system audio (YouTube, video calls, etc.) and provides instant transcription and translation with interactive keyboard controls.

## 🇮🇹 → 🇬🇧 Story behind this tool

As a French developer working remotely with [Nethesis](https://www.nethesis.it/) (an Italian company behind NethServer and NethSecurity), I found myself in daily Italian-language meetings and calls. Not speaking Italian fluently, I needed a practical solution to follow technical discussions in real-time.

I built this tool initially for my own needs — a simple Python script to capture audio streams and translate them live during meetings. It quickly became indispensable for my daily work, allowing me to actively participate in Italian-speaking technical sessions, understand documentation being discussed, and keep up with fast-paced conversations.

After months of refining it for personal use, I realized this could help other developers in similar situations. Whether you're:
- 🤝 Working with Italian teams or clients
- 📚 Learning from Italian technical content (YouTube, conferences, webinars)
- 🌍 Contributing to Italian open-source projects
- 🎓 Studying Italian tech tutorials

...this tool can make your life significantly easier.

It demonstrates that complex problems don't always need complex solutions — 
sometimes a straightforward Python script is all you need.

**Buon lavoro!** 🚀

## Features

- 🎤 **Real-time translation** - Italian to English, French, Spanish or German, phrase by phrase as the speaker finishes
- 🎯 **5 Whisper models** - From tiny (fast) to large-v3 (accurate), switchable on-the-fly with **W**
- ⚡ **3 speed modes** - Fast (500ms)/Normal (800ms)/Slow (1200ms) silence thresholds, switchable on-the-fly with **M**
- 🔇 **VAD-based chunking** - [webrtcvad](https://github.com/wiseman/py-webrtcvad) detects speech boundaries in real-time; flushes on silence rather than fixed intervals
- 📊 **Session statistics** - Duration, segments, word count and dropped chunks at end of session
- ⌨️ **Full keyboard control** - Pause, save, switch model, switch language, change mode on-the-fly
- 💾 **Markdown export** - Save timestamped bilingual transcripts with session stats
- 🔧 **Zero configuration** - Auto-installs dependencies in isolated venv
- ⚡ **GPU acceleration** - Experimental NVIDIA/CUDA support via `--gpu` (3-5x faster, falls back to CPU on failure)
- 🐧 **Linux native** - Works with PipeWire/PulseAudio
- 🎛️ **Smart audio source selection** - Auto-detects active stream, interactive menu when multiple sources are active
- 🇮🇹 **Bilingual display** - Toggle Italian source text visibility

## Privacy

All processing happens **entirely on your machine** — no audio, transcription, or translation data ever leaves your computer.

- **Speech recognition** is performed by [faster-whisper](https://github.com/guillaumekleindienst/faster-whisper), a local Whisper model that runs offline after the initial download.
- **Translation** is handled by [argostranslate](https://github.com/argosopentech/argos-translate), which uses locally installed language models with no network calls at runtime.
- **No cloud API** is contacted during use. There is no telemetry, no account, and no data sent to any third party.
- **Audio capture** reads your system audio stream in memory only; nothing is written to disk unless you explicitly use `--save`.

This tool is safe to use in environments where confidentiality matters (internal meetings, proprietary content, etc.).

## Requirements

- **OS**: Linux (tested on Fedora 43, Ubuntu 24.04, openSUSE Tumbleweed)
- **Python**: 3.9+ (3.11 recommandé)
- **Audio**: PulseAudio or **PipeWire** (modern Linux distributions)
- **Packages**: `python3-venv`, `python3-devel` (needed to compile `webrtcvad`)

**Note**: Most modern Linux distributions (Fedora 34+, Ubuntu 22.10+, Debian 12+) 
use PipeWire as the default audio server. The script works seamlessly with both 
PipeWire and legacy PulseAudio systems through the `pactl`/`parec` compatibility layer.

## Installation

### 1. System dependencies

**Fedora / RHEL / CentOS:**
```bash
sudo dnf install python3-venv python3-devel pulseaudio-utils
```

**openSUSE:**
```bash
sudo zypper install python3-venv python3-devel pulseaudio-utils
```

**Ubuntu / Debian:**
```bash
sudo apt install python3-venv python3-dev pulseaudio-utils
```

> `pulseaudio-utils` provides `pactl` and `parec`, which are required for audio capture under both PulseAudio and PipeWire.

### 2. Clone and run

```bash
# Clone repository
git clone https://github.com/stephdl/live-voice-translate.git
cd live-voice-translate

# Make executable
chmod +x lvt.py

# Run (first run auto-installs Python dependencies)
./lvt.py
```

**First run** creates virtualenv in `~/.local/share/live-voice-translate/venv` and installs:
- faster-whisper
- argostranslate
- webrtcvad

This takes 2-3 minutes.

### 3. Updating

```bash
cd live-voice-translate
git pull origin main
```

New Python dependencies (if any) are installed automatically on the next run.

> If you get unexpected errors after an update, delete the virtualenv to force a clean reinstall:
> ```bash
> rm -rf ~/.local/share/live-voice-translate/venv
> ./lvt.py
> ```

## Usage

### Interactive menu
```bash
./lvt.py
```

Select model (1-5), then start playing audio in another window.

### Command-line
```bash
# Medium model (recommended)
./lvt.py medium

# Large model with slow mode (best quality)
./lvt.py large --slow

# Tiny model with fast mode (lowest latency)
./lvt.py tiny --fast

# Save transcript to file
./lvt.py medium --save meeting.md

# Auto-generated filename
./lvt.py medium --save

# Display Italian + English
./lvt.py medium --show-italian

# Translate to French (via it→en→fr double translation)
./lvt.py medium --to fr

# Translate to Spanish
./lvt.py medium --to es

# Translate to German
./lvt.py medium --to de

# Disable Voice Activity Detection (transcribe everything including silence)
./lvt.py medium --no-vad

# Enable GPU acceleration (NVIDIA/CUDA only, experimental)
./lvt.py medium --gpu
```

### Keyboard shortcuts

**During execution**, press:

| Key | Action |
|-----|--------|
| **P** | Pause/Resume translation |
| **S** | Save transcript now (creates file if needed) |
| **M** | Change mode (fast → normal → slow → fast) |
| **W** | Change Whisper model (tiny → base → small → medium → large-v3) |
| **L** | Change target language (en → fr → es → de → en) |
| **I** | Toggle Italian display (ON/OFF) |
| **Q** | Quit gracefully |
| **H** | Show session config + keyboard shortcuts help |

**Note**: Shortcuts respond **instantly** (no need to press Enter).

## Models comparison

| Model | Accuracy | Latency | RAM | Use case |
|-------|----------|---------|-----|----------|
| **tiny** | 60% | ~1.5s | 1GB | Quick tests, low-end systems |
| **base** | 85% | ~4s | 1.5GB | Fast casual listening |
| **small** | 90% | ~5s | 2GB | Good balance |
| **medium** | 95% | ~8s | 5GB | **Recommended** for most uses |
| **large-v3** | 98% | ~12s | 10GB | Maximum accuracy (high CPU/fan) |

## Speed modes

| Mode | Segment size | Latency | Quality |
|------|--------------|---------|---------|
| **fast** | Shorter | Lower | May cut sentences |
| **normal** | Balanced | Medium | **Default**, good compromise |
| **slow** | Longer | Higher | Complete sentences, best context |

Change mode on-the-fly by pressing **M** during execution.

## Display modes

### English only (default)
```
[14:25:30] ▶ Today was a tough day
[14:25:45] ▶ What happened?
```

### Bilingual (Italian + English)
```bash
./lvt.py medium --show-italian
```
```
[14:25:30] Oggi è stata una giornata difficile     (green)
[14:25:30] ▶ Today was a tough day

[14:25:45] Cosa è successo?                        (green)
[14:25:45] ▶ What happened?
```

Toggle Italian display during execution with **I** key.

## Examples

### Translate YouTube video
```bash
# Start translator
./lvt.py medium

# In another window/tab, open YouTube
firefox "https://www.youtube.com/watch?v=ITALIAN_VIDEO_ID"

# Translations appear in real-time in terminal
```

### Translate video call
```bash
# Start with save
./lvt.py medium --save meeting.md

# Join video call (Zoom, Teams, Google Meet, Discord, etc.)
# Translations saved to meeting.md

# During call:
# - Press 'p' to pause (e.g., when speaking)
# - Press 'p' again to resume
# - Press 's' to force save
# - Press 'i' to show Italian text
```

### Compare models
```bash
# Test tiny (fastest)
./lvt.py tiny --fast

# Test large (best quality)
./lvt.py large --slow
```

## Output format

### Terminal output

**English only:**
```
[14:25:30] ▶ Today was a tough day
[14:25:45] ▶ What happened?
```

**Bilingual (with `--show-italian` or `i` key):**
```
[14:25:30] Oggi è stata una giornata difficile
[14:25:30] ▶ Today was a tough day
[14:25:45] Cosa è successo?
[14:25:45] ▶ What happened?
```

### Markdown file (--save)
```markdown
# Live Voice Translation

**Date:** 2026-04-01 14:25:30
**Model:** medium
**Mode:** normal

---

**[14:25:30]**

🇮🇹 *Oggi è stata una giornata difficile*

🇬🇧 Today was a tough day

---

**[14:25:45]**

🇮🇹 *Cosa è successo?*

🇬🇧 What happened?

---

**End of session:** 2026-04-01 14:57:45
**Duration:** 00:32:15
**Phrases:** 147
**Words:** 1823
```

## Audio source selection

The tool auto-detects active audio monitor streams. If only one is active, it is selected automatically. If multiple streams are active simultaneously (e.g. a video call and a YouTube video), an interactive menu is displayed:

```
  Multiple audio streams detected:

    1) USB Audio
    2) JBL LIVE650BTNC

  Select stream (1-2):
```

PipeWire internal loopback sinks are automatically filtered out.

## How it works

1. **Audio source**: Auto-detects active PulseAudio/PipeWire monitor stream, with interactive selection when multiple are available
2. **VAD chunking**: webrtcvad detects speech/silence boundaries and flushes each utterance when silence exceeds the mode threshold (500/800/1200ms)
3. **Transcription**: Whisper converts Italian audio to text
4. **Translation**: Argos Translate converts Italian → English, then English → target language if needed (fr/es/de)
5. **Display**: Shows timestamped translations in terminal
6. **Save**: Optionally exports to Markdown file

**Architecture**:
- Audio capture runs in background thread (non-blocking)
- Keyboard controller uses `select()` for instant response (no dependencies)
- Main thread processes audio queue and checks keyboard

## Troubleshooting

### No active audio stream detected

```bash
# 1. Check if PulseAudio/PipeWire is running
pactl info
# Should show server info

# 2. List all audio sources
pactl list short sources

# 3. Look for monitor sources (with RUNNING status)
pactl list short sources | grep monitor

# 4. If no monitor source is RUNNING:
# - Play audio (YouTube, music, etc.)
# - Run the check again
pactl list short sources | grep -E "monitor.*RUNNING"

# 5. If still no output, restart audio service
pactl info

# Output PipeWire :
# Server Name: PulseAudio (on PipeWire 0.3.xx)

# Output PulseAudio :
# Server Name: pulseaudio

systemctl --user restart pipewire pipewire-pulse  # For PipeWire
systemctl --user restart pulseaudio                # For PulseAudio
```

**Still not working?**

Check if audio is actually playing:
```bash
# Monitor audio levels in real-time
pavucontrol  # GUI tool - check "Recording" tab

# Or command-line
pactl subscribe  # Shows audio events
```

---

### First run fails
```bash
# Install system dependencies (python3-devel is required to compile webrtcvad)
sudo dnf install python3-venv python3-devel     # Fedora/RHEL
sudo zypper install python3-venv python3-devel  # openSUSE
sudo apt install python3-venv python3-dev       # Ubuntu/Debian

# Retry
./lvt.py
```

### Delete and reinstall virtualenv
```bash
# Remove virtualenv
rm -rf ~/.local/share/live-voice-translate/

# Rerun (recreates clean venv)
./lvt.py
```

### Keyboard shortcuts not working

Shortcuts require terminal in TTY mode. If piping output or running in non-interactive environment, use `--no-keyboard`:
```bash
./lvt.py medium --no-keyboard
```

### Italian text not displaying correctly

Ensure your terminal uses UTF-8 encoding:
```bash
# Check locale
echo $LANG
# Should show: fr_FR.UTF-8, en_US.UTF-8, or similar

# If not UTF-8:
export LANG=fr_FR.UTF-8
export LC_ALL=fr_FR.UTF-8
```

## Performance tips

- **CPU usage**: Use smaller models (tiny/base) on weak hardware
- **Latency**: Use `--fast` (500ms silence, 6s max chunk) for lowest delay — may cut mid-sentence
- **Accuracy**: Use `large --slow` (1200ms silence, 12s max chunk, max beam) for best quality
- **Balance**: `medium` (default normal mode) is the best CPU/quality tradeoff
- **RAM**: medium model needs ~5GB, large needs ~10GB
- **GPU (NVIDIA)**: Use `--gpu` for 3-5x faster transcription — requires CUDA drivers. Falls back to CPU automatically on failure. AMD is not supported (CTranslate2 has no ROCm build).

## Advanced usage

### Custom save filename
```bash
./lvt.py medium --save "$(date +%Y%m%d)-meeting.md"
```

### Create save file during execution
```bash
# Start without --save
./lvt.py medium

# During execution, press 's'
# Creates: live-translate-YYYYMMDD-HHMMSS.md
```

### Wayland compatibility

Works out-of-the-box on Wayland (tested on Fedora 43 + GNOME 49).

### X11 compatibility

Fully compatible with X11 desktop environments.

## License

GNU General Public License v3.0 or later

See [LICENSE](LICENSE) file for details.

## Author

**Stéphane de Labrusse**

Freelance developer specializing in Linux, containerization, and cybersecurity.

- GitHub: [@stephdl](https://github.com/stephdl)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Test your changes
4. Submit a pull request

## Roadmap

Potential future features:

- [x] VAD-based real-time chunking (webrtcvad) — flushes on silence, phrase by phrase
- [x] Multiple target languages (French, Spanish, German) via double translation
- [x] Smart audio source selection with interactive menu for multiple streams
- [x] GPU acceleration (experimental, NVIDIA/CUDA only, auto-fallback to CPU)
- [x] Session statistics - Duration, segments, word count, dropped chunks
- [x] On-the-fly model switching (W key) without restarting
- [x] On-the-fly language switching (L key) without restarting
- [x] Markdown export with session stats and bilingual transcript
- [ ] Multiple translators (DeepL/GPT fallback)
- [ ] Bidirectional mode (IT+EN simultaneously)
- [ ] Speaker diarization
- [ ] Web dashboard
- [ ] Export formats (PDF, DOCX, SRT subtitles)
- [x] Support for other language pairs (French, Spanish, German via double translation)
- [ ] Migrate VAD from [webrtcvad](https://github.com/wiseman/py-webrtcvad) (unmaintained since 2018) to a maintained alternative — Silero VAD investigated but requires PyTorch or has ONNX API instability; RMS energy-based VAD is a viable lightweight option

## Acknowledgments

- [Whisper](https://github.com/openai/whisper) by OpenAI
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) by Guillaume Klein
- [Argos Translate](https://github.com/argosopentech/argos-translate) by Argos Open Technologies

## Support

For bugs or feature requests, please [open an issue](https://github.com/stephdl/dev/issues).

---

**Made with ❤️ for the open-source community**

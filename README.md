# live-voice-translate

Real-time Italian→English audio translation using Whisper and Argos Translate.

Captures system audio (YouTube, video calls, etc.) and provides instant transcription and translation with interactive keyboard controls.

## Features

- 🎤 **Real-time translation** - Italian to English with ~1-18s latency
- 🎯 **5 Whisper models** - From tiny (fast) to large-v3 (accurate)
- ⚡ **3 speed modes** - Fast/Normal/Slow optimized for Italian
- ⌨️ **Keyboard shortcuts** - Pause, save, change mode, toggle Italian display on-the-fly
- 💾 **Markdown export** - Save timestamped transcripts
- 🔧 **Zero configuration** - Auto-installs dependencies in isolated venv
- 🐧 **Linux native** - Works with PipeWire/PulseAudio
- 🇮🇹 **Bilingual display** - Toggle Italian source text visibility

## Requirements

- **OS**: Linux (tested on Fedora 43, Ubuntu 24.04)
- **Python**: 3.8+
- **Audio**: PulseAudio or PipeWire
- **Packages**: `python3-venv` (auto-installs other dependencies)

## Installation
```bash
# Clone repository
git clone https://github.com/stephdl/live-voice-translate.git
cd live-voice-translate

# Make executable
chmod +x live-voice-translate.py

# Run (first run auto-installs dependencies)
./live-voice-translate.py
```

**First run** creates virtualenv in `~/.local/share/live-voice-translate/venv` and installs:
- faster-whisper
- argostranslate

This takes 2-3 minutes.

## Usage

### Interactive menu
```bash
./live-voice-translate.py
```

Select model (1-5), then start playing audio in another window.

### Command-line
```bash
# Medium model (recommended)
./live-voice-translate.py medium

# Large model with slow mode (best quality)
./live-voice-translate.py large --slow

# Tiny model with fast mode (lowest latency)
./live-voice-translate.py tiny --fast

# Save transcript to file
./live-voice-translate.py medium --save meeting.md

# Auto-generated filename
./live-voice-translate.py medium --save

# Display Italian + English
./live-voice-translate.py medium --show-italian
```

### Keyboard shortcuts

**During execution**, press:

| Key | Action |
|-----|--------|
| **P** | Pause/Resume translation |
| **S** | Save transcript now (creates file if needed) |
| **M** | Change mode (fast → normal → slow → fast) |
| **I** | Toggle Italian display (ON/OFF) |
| **Q** | Quit gracefully |
| **H** | Show keyboard shortcuts help |

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
./live-voice-translate.py medium --show-italian
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
./live-voice-translate.py medium

# In another window/tab, open YouTube
firefox "https://www.youtube.com/watch?v=ITALIAN_VIDEO_ID"

# Translations appear in real-time in terminal
```

### Translate video call
```bash
# Start with save
./live-voice-translate.py medium --save meeting.md

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
./live-voice-translate.py tiny --fast

# Test large (best quality)
./live-voice-translate.py large --slow
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
```

## How it works

1. **Audio capture**: Monitors PulseAudio/PipeWire stream (YouTube, video calls, etc.)
2. **Transcription**: Whisper converts Italian audio to text
3. **Translation**: Argos Translate converts Italian text to English
4. **Display**: Shows timestamped translations in terminal
5. **Save**: Optionally exports to Markdown file

**Architecture**:
- Audio capture runs in background thread (non-blocking)
- Keyboard controller uses `select()` for instant response (no dependencies)
- Main thread processes audio queue and checks keyboard

## Troubleshooting

### No active audio stream detected
```bash
# Check active streams
pactl list short sources | grep monitor

# Play audio (YouTube, etc.), then rerun script
```

### First run fails
```bash
# Install python3-venv
sudo dnf install python3-venv  # Fedora/RHEL
sudo apt install python3-venv  # Ubuntu/Debian

# Retry
./live-voice-translate.py
```

### Delete and reinstall virtualenv
```bash
# Remove virtualenv
rm -rf ~/.local/share/live-voice-translate/

# Rerun (recreates clean venv)
./live-voice-translate.py
```

### Keyboard shortcuts not working

Shortcuts require terminal in TTY mode. If piping output or running in non-interactive environment, use `--no-keyboard`:
```bash
./live-voice-translate.py medium --no-keyboard
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
- **Latency**: Use `--fast` mode for lower delay
- **Accuracy**: Use `large --slow` for best quality (high CPU)
- **RAM**: medium model needs ~5GB, large needs ~10GB

## Advanced usage

### Custom save filename
```bash
./live-voice-translate.py medium --save "$(date +%Y%m%d)-meeting.md"
```

### Create save file during execution
```bash
# Start without --save
./live-voice-translate.py medium

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

- [ ] VAD (Voice Activity Detection) - Reduce CPU by 70%
- [ ] Multiple translators (DeepL/GPT fallback)
- [ ] Bidirectional mode (IT+EN simultaneously)
- [ ] Speaker diarization
- [ ] GPU acceleration (CUDA)
- [ ] Web dashboard
- [ ] Export formats (PDF, DOCX, SRT subtitles)
- [ ] Support for other language pairs

## Acknowledgments

- [Whisper](https://github.com/openai/whisper) by OpenAI
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) by Guillaume Klein
- [Argos Translate](https://github.com/argosopentech/argos-translate) by Argos Open Technologies

## Support

For bugs or feature requests, please [open an issue](https://github.com/stephdl/dev/issues).

---

**Made with ❤️ for the open-source community**

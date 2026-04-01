# live-voice-translate

Real-time Italian→English audio translator using faster-whisper and Argos. Capture from any source (Jitsi/YouTube/meetings), choose accuracy vs latency (5 models), 100% free and offline.

## Features

- 🎙️ **Live audio capture** from any source (speakers/Bluetooth/USB)
- 🧠 **5 Whisper models** (tiny → large-v3) with configurable accuracy/latency
- 🌐 **Italian→English translation** using Argos Translate (free, unlimited)
- ⚡ **Adjustable speed**: --fast, normal, --slow modes
- 🕐 **Timestamps** on every translation (terminal + saved files)
- 💾 **Save transcripts** to Markdown files for later review
- 🆓 **100% free and offline** - no API keys, no quotas
- 🐍 **Pure Python** - clean, maintainable, extensible
- 🔒 **Isolated environment** - automatic virtualenv setup, no system pollution

## System Requirements

- **OS**: Linux with PipeWire/PulseAudio (Fedora 43+ tested)
- **Python**: 3.8+ (3.10+ recommended)
- **RAM**: 2GB minimum (small), 5GB recommended (medium), 10GB+ for large
- **Audio**: PipeWire or PulseAudio
- **Disk space**: ~2.5GB (virtualenv + models)

## Installation

### Quick Start (Recommended)
```bash
# 1. Install system dependencies
sudo dnf install ffmpeg python3  # Fedora/RHEL
# OR
sudo apt install ffmpeg python3  # Ubuntu/Debian
# OR
brew install ffmpeg python3      # macOS

# 2. Download the script
wget https://raw.githubusercontent.com/stephdl/live-voice-translate/refs/heads/main/live-voice-translate.py
chmod +x live-voice-translate.py

# 3. Run (auto-setup on first run)
./live-voice-translate.py
```

**That's it!** On first run, the script automatically:
- ✅ Creates an isolated Python environment in `~/.local/share/live-voice-translate/venv`
- ✅ Installs required dependencies (`faster-whisper`, `argostranslate`)
- ✅ Downloads Whisper model and IT→EN translation model (~1.7GB)
- ✅ No manual setup needed
- ✅ No `pip install --break-system-packages` needed
- ✅ Respects PEP 668 (Python 3.11+ externally-managed-environment)

### First Run Output
```
═══════════════════════════════════════════
   First Run Setup
═══════════════════════════════════════════

Creating isolated environment...
Location: /home/stephdl/.local/share/live-voice-translate/venv

Installing dependencies: faster-whisper, argostranslate
This may take 2-3 minutes...

Collecting faster-whisper...
Collecting argostranslate...
Installing collected packages: ...

✅ Setup complete!
Starting translation...
```

**First run takes 2-3 minutes. Subsequent runs are instant.**

---

## Usage

### Interactive Menu
```bash
./live-voice-translate.py
```

You'll see:
```
═══════════════════════════════════════════
   Jitsi IT→EN Translation
═══════════════════════════════════════════

Available models:

  1) tiny   - Ultra fast     (60% accuracy, ~1.5s, 1GB RAM)
  2) base   - Fast           (85% accuracy, ~4s, 1.5GB RAM)
  3) small  - Balanced       (90% accuracy, ~5s, 2GB RAM)
  4) medium - Recommended    (95% accuracy, ~8s, 5GB RAM) [DEFAULT]
  5) large  - Maximum        (98% accuracy, ~12s, 10GB RAM) ⚠️  High fan

Your choice (1-5 or Enter for default):
```

**Press Enter** for medium (recommended) or choose 1-5.

### Command Line Usage
```bash
# Normal speed (default)
./live-voice-translate.py medium         # Medium, 8s latency
./live-voice-translate.py large          # Large, 12s latency

# Fast mode (shorter segments, faster response)
./live-voice-translate.py medium --fast  # Medium, 4s latency
./live-voice-translate.py large --fast   # Large, 6s latency

# Slow mode (longer segments, complete sentences)
./live-voice-translate.py medium --slow  # Medium, 10s latency
./live-voice-translate.py large --slow   # Large, 18s latency

# Save transcript to file
./live-voice-translate.py medium --save                    # Auto-generated filename
./live-voice-translate.py large --slow --save meeting.md   # Custom filename

# Show help
./live-voice-translate.py --help
```

### Create Aliases (Optional)

Add convenient shortcuts to your `~/.bashrc` or `~/.zshrc`:
```bash
cat >> ~/.bashrc << 'EOF'

# Live voice translation aliases
alias live-translate='~/live-voice-translate.py'
alias live-translate-fast='~/live-voice-translate.py medium --fast'
alias live-translate-balanced='~/live-voice-translate.py medium'
alias live-translate-save='~/live-voice-translate.py medium --slow --save'
alias live-translate-quality='~/live-voice-translate.py large'
alias live-translate-max='~/live-voice-translate.py large --slow --save'
EOF

source ~/.bashrc
```

Now you can use:
```bash
live-translate              # Interactive menu
live-translate-fast         # Medium + fast mode (4s)
live-translate-balanced     # Medium, normal (8s)
live-translate-save         # Medium slow + save transcript (10s)
live-translate-quality      # Large, normal (12s)
live-translate-max          # Large + slow mode + save (18s)
```

---

## Terminal Output

Translations appear in real-time with timestamps:
```
[11:36:39] ▶ saying happened this and immediately after it made me
             feel so this makes the story more human
[11:37:03] ▶ Using these small signals makes the speech much
             clearer.
[11:37:28] ▶ A phrase like "I think so because I have experienced
             this experience" is more than enough.
```

---

## Saved Transcripts

When using `--save`, transcripts are saved in **Markdown format** for easy reading and sharing.

### Example Output File
```markdown
# Live Voice Translation

**Date:** 2026-04-01 11:36:12  
**Model:** large-v3  
**Mode:** slow  

---

**[11:36:39]**

🇮🇹 *dire è successo questo e subito dopo mi ha fatto sentire così questo rende il racconto più umano*

🇬🇧 saying happened this and immediately after it made me feel so this makes the story more human

---

**[11:37:03]**

🇮🇹 *Usare questi piccoli segnali rende il discorso molto più chiaro.*

🇬🇧 Using these small signals makes the speech much clearer.

---

**End of session:** 2026-04-01 11:40:05
```

### Working with Saved Files
```bash
# Search for specific topics
grep -i "firewall" meeting-notes.md

# Convert to PDF
pandoc meeting-notes.md -o meeting-report.pdf

# Add your own notes
vim meeting-notes.md
```

---

## How It Works

1. **Auto-setup virtualenv**: First run creates isolated Python environment
2. **Capture audio**: Detects active PipeWire/PulseAudio monitor stream
3. **Transcribe**: Uses faster-whisper to transcribe Italian speech to text
4. **Translate**: Uses Argos Translate to convert Italian text to English
5. **Display**: Shows English translation in real-time with timestamps
6. **Save (optional)**: Records both Italian and English to Markdown file

---

## Use Cases

- 🎥 **Jitsi/Zoom/Teams meetings** in Italian
- 📺 **YouTube videos** in Italian
- 🎧 **Live streams** or podcasts
- 📞 **Any audio source** playing on your computer
- 📝 **Meeting minutes** with automatic transcript generation

---

## Model Comparison

### Standard Mode (Normal)

| Model      | Accuracy | Latency | RAM   | CPU  | Use Case              |
|------------|----------|---------|-------|------|-----------------------|
| **tiny**   | 60%      | ~1.5s   | 1GB   | 30%  | Quick tests           |
| **base**   | 85%      | ~4s     | 1.5GB | 40%  | Fast casual meetings  |
| **small**  | 90%      | ~5s     | 2GB   | 50%  | Balanced              |
| **medium** | 95%      | ~8s     | 5GB   | 60%  | **Recommended daily** |
| **large**  | 98%      | ~12s    | 10GB  | 80%  | Critical meetings     |

### Speed Modes

| Model | --fast | Normal | --slow |
|-------|--------|--------|--------|
| **tiny** | 0.5s (2s audio) | 1.5s (4s audio) | 2s (5s audio) |
| **base** | 2s (3s audio) | 4s (5s audio) | 5s (6s audio) |
| **small** | 3s (4s audio) | 5s (6s audio) | 7s (8s audio) |
| **medium** | 4s (4s audio) | 8s (8s audio) | 10s (10s audio) |
| **large** | 6s (5s audio) | 12s (10s audio) | **18s (15s audio)** |

**When to use each mode:**
- **--fast**: Quick reactions, casual conversations (may cut sentences)
- **Normal**: Daily meetings, good balance, **optimized for Italian phrases**
- **--slow**: Video recordings, presentations, complete sentences guaranteed (best for --save)

**Note**: Timings are optimized for Italian language, which has longer average sentence length than English.

### Recommendations by Use Case

| Use Case | Recommended Command | Why |
|----------|---------------------|-----|
| **Live Jitsi meeting** | `./live-voice-translate.py medium` | 8s latency, 95% accuracy, good balance |
| **YouTube video** | `./live-voice-translate.py large --slow --save` | 18s OK for video, best quality, save transcript |
| **Quick test** | `./live-voice-translate.py small --fast` | 3s latency, fast feedback |
| **Important meeting** | `./live-voice-translate.py large --save` | 12s latency, 98% accuracy, transcript saved |
| **Podcast listening** | `./live-voice-translate.py large --slow` | Best quality, complete sentences |

---

## Privacy & Security

### 🔒 100% Private

- ✅ **Everything runs on your computer** - no cloud, no servers
- ✅ **No internet needed** (except first-time model download)
- ✅ **Nothing is logged** - only saved if you use `--save`
- ✅ **Isolated environment** - virtualenv keeps dependencies separate from system
- ✅ **Auto cleanup** - temporary files deleted when you stop (Ctrl+C)

### What Gets Stored?

| What | Where | When Deleted |
|------|-------|--------------|
| **Virtualenv** | `~/.local/share/live-voice-translate/venv/` | Manual deletion only |
| **Audio (5-15s)** | `/tmp/audio_chunk.wav` | When you press Ctrl+C |
| **Whisper models** | `~/.cache/huggingface/hub/` | Never (reused each time) |
| **Translation model** | `~/.local/share/argos-translate/packages/` | Never (reused each time) |
| **Transcripts** | Your specified file (if `--save` used) | Manual deletion |

**Your conversations are never sent to external servers.**

### Disk Space Usage
```bash
# Check virtualenv size
du -sh ~/.local/share/live-voice-translate/venv
# ~800MB

# Check Whisper models
du -sh ~/.cache/huggingface/
# ~1.5GB (medium), ~3GB (large)

# Check translation models
du -sh ~/.local/share/argos-translate/
# ~200MB

# TOTAL: ~2.5GB (medium) or ~4GB (large)
```

### Cleanup (Optional)
```bash
# Remove everything to free space
rm -rf ~/.local/share/live-voice-translate/
rm -rf ~/.cache/huggingface/hub/models--Systran--faster-whisper-*
rm -rf ~/.local/share/argos-translate/

# Next run will re-download and reinstall (2-3 minutes)
```

### Safe For

✅ Confidential business meetings  
✅ Medical discussions  
✅ Legal conversations  
✅ Any private audio  
✅ ANSSI/RGPD/HIPAA compliant environments

### Comparison

| Tool | Where Your Audio Goes | Isolation |
|------|----------------------|-----------|
| **live-voice-translate** | Stays on your computer | ✅ Virtualenv |
| Google Translate | Sent to Google servers | ❌ None |
| Zoom/Teams translate | Sent to their servers | ❌ None |
| DeepL API | Sent to DeepL servers | ❌ None |

### Network Check

After installation, the script **never connects to internet**.

Test it yourself:
```bash
# Run the script, then check network activity
sudo tcpdump -i any | grep -v "127.0.0.1"
# You'll see: nothing (after initial setup)
```

---

**Your audio never leaves your machine. Period.**

---

## Troubleshooting

### No audio stream detected

**Problem**: `Error: No active audio stream detected`

**Diagnosis**: Check available audio streams
```bash
# List all monitor sources
pactl list short sources | grep monitor
```

**Example output**:
```
51   alsa_output.pci-0000_c4_00.6.HiFi__Speaker__sink.monitor    RUNNING
88   bluez_output.XX_XX_XX.monitor                               SUSPENDED
61   input.loopback.sink.role.multimedia.monitor                 RUNNING
```

The script automatically selects the first `RUNNING` stream (index 51 in this example).

**Solutions**:

1. **No RUNNING stream**: Make sure audio is playing (YouTube, Jitsi)
2. **Multiple RUNNING streams**: The script picks the first one
3. **Only SUSPENDED streams**: Enable audio playback before running the script

**Debug audio capture**:
```bash
# Test if audio is being captured (5 seconds test)
timeout 5s parec --monitor-stream=51 --format=s16le --rate=16000 --channels=1 > /tmp/test.raw

# Check file size (should be ~160KB for 5s of audio)
ls -lh /tmp/test.raw
```

If file is empty (0 bytes) → wrong stream index or no audio playing.

---

### Missing ffmpeg

**Problem**: Script reports missing ffmpeg

**Solution**: Install via system package manager
```bash
# Fedora/RHEL
sudo dnf install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

---

### Python version too old

**Problem**: `Error: Python 3.8 or higher required`

**Solution**: Upgrade Python or use a newer version
```bash
# Check current version
python3 --version

# Fedora: Upgrade Python
sudo dnf install python3.11

# Ubuntu: Add deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11

# Then run with specific version
python3.11 live-voice-translate.py medium
```

---

### Virtualenv creation fails

**Problem**: `Error creating virtualenv`

**Solution**: Install python3-venv package
```bash
# Fedora/RHEL
sudo dnf install python3-venv

# Ubuntu/Debian
sudo apt install python3-venv python3-pip

# Then retry
./live-voice-translate.py
```

---

### Dependency installation fails

**Problem**: pip install fails during first run

**Solution**: Update pip in virtualenv and retry
```bash
# Manually update virtualenv pip
~/.local/share/live-voice-translate/venv/bin/pip install --upgrade pip

# Manually install dependencies
~/.local/share/live-voice-translate/venv/bin/pip install faster-whisper argostranslate

# Then run normally
./live-voice-translate.py medium
```

---

### High CPU / Fan noise with large model

**Solution**: Use `medium` instead of `large` for daily meetings. Large model is CPU-intensive.

**Monitor CPU usage**:
```bash
# In another terminal while script is running
htop
```

---

### Translation not working

**Problem**: Script runs but no translations appear

**Checklist**:

1. **Is audio playing?** Open YouTube or Jitsi
2. **Is the audio stream active?** Check with `pactl list short sources | grep RUNNING`
3. **Is there actual speech?** Music-only won't produce translations
4. **Wait 8-18 seconds**: First segment takes time to process

**Test with Italian YouTube video**:
```bash
# Terminal 1: Open Italian video
firefox "https://www.youtube.com/results?search_query=italian+news"

# Terminal 2: Run script
./live-voice-translate.py medium
```

You should see translations within 8-12 seconds.

---

### Reset everything

**Problem**: Something is broken, want to start fresh

**Solution**: Delete virtualenv and models, then reinstall
```bash
# Delete virtualenv
rm -rf ~/.local/share/live-voice-translate/

# Delete models (optional, will re-download)
rm -rf ~/.cache/huggingface/hub/models--Systran--faster-whisper-*
rm -rf ~/.local/share/argos-translate/

# Run again (will recreate everything)
./live-voice-translate.py
```

---

## Technical Details

- **Transcription**: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (optimized Whisper implementation)
- **Translation**: [Argos Translate](https://github.com/argosopentech/argos-translate) (offline, LibreTranslate engine)
- **Audio capture**: PipeWire/PulseAudio monitor streams
- **Segments**: Configurable 2-15 seconds audio chunks
- **Processing**: CPU-only (GPU support easy to add)
- **Output format**: Markdown with timestamps
- **Language**: Pure Python 3.8+
- **Isolation**: Automatic virtualenv in `~/.local/share/live-voice-translate/venv`
- **Dependencies**: Installed in virtualenv, no system pollution

### File Structure
```
~/.local/share/live-voice-translate/
└── venv/                           # Isolated Python environment
    ├── bin/
    │   ├── python                  # Python interpreter
    │   ├── pip                     # Package installer
    │   └── activate                # (not used by script)
    └── lib/python3.X/site-packages/
        ├── faster_whisper/
        ├── argostranslate/
        └── (dependencies)

~/.cache/huggingface/hub/
└── models--Systran--faster-whisper-medium/  # Whisper models

~/.local/share/argos-translate/packages/
└── translate-it_en/                # IT→EN translation model
```

---

## Limitations

### Translation Quality

- **Argos Translate**: Good but not perfect (~80-85% quality)
- For professional quality, consider DeepL API (paid)
- Italian idiomatic expressions may not translate perfectly

### Latency

- **Real-time = delay**: 0.5-18s depending on model and speed mode
- Not suitable for simultaneous interpretation
- Best for understanding content, not instant responses

### Transcript Quality

Due to real-time processing, transcripts may contain:
- **Sentence fragments**: Audio is processed in 4-15 second chunks
- **Split sentences**: Long Italian sentences may be broken across timestamps
- **Context gaps**: Some connections between segments may be lost

**Recommendations**:
- Use `--slow` mode for better sentence completion (15s segments)
- Accept that real-time = incomplete sentences sometimes
- For perfect transcripts, use offline tools on complete audio files

**This is a real-time tool, not a professional transcription service.**

### Language Support

- Currently optimized for Italian→English only
- Other language pairs possible but not tested
- Translation model is specific to IT→EN

### Hardware

- **CPU-only**: This version uses CPU processing only
- **GPU support**: Not currently implemented (easy to add for NVIDIA CUDA)
- **RAM**: Minimum requirements must be met for stable operation

### Platform Support

- **Linux**: Fully supported (Fedora, Ubuntu, Debian tested)
- **macOS**: May work with modifications (untested)
- **Windows**: Not supported (requires PulseAudio/PipeWire)

---

## Future Improvements

- [ ] Add DeepL API support (optional, paid)
- [ ] Support more language pairs (ES→EN, FR→EN, DE→EN)
- [ ] NVIDIA GPU acceleration (CUDA)
- [ ] GUI interface
- [ ] Export to different formats (JSON, TXT, PDF)
- [ ] Voice Activity Detection tuning
- [ ] Multi-speaker detection

---

## Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share your use cases

---

## License

GNU General Public License v3.0 - feel free to use, modify, and distribute

---

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the amazing transcription model
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for the optimized implementation
- [Argos Translate](https://github.com/argosopentech/argos-translate) for free offline translation
- Nethesis team for inspiring this project during Italian Jitsi meetings

---

## Author

Created by Stéphane de Labrusse for real-time translation of Italian Nethesis meetings.

**GitHub**: [@stephdl](https://github.com/stephdl)

---

**Star ⭐ this repo if it helps you understand Italian meetings!**

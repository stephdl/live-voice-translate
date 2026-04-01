# live-voice-translate

Real-time Italian→English audio translator in your terminal  using faster-whisper and Argos. Capture from any source (Jitsi/YouTube/meetings), choose accuracy vs latency (5 models), 100% free and offline.

## Features

- 🎙️ **Live audio capture** from any source (speakers/Bluetooth/USB)
- 🧠 **5 Whisper models** (tiny → large-v3) with configurable accuracy/latency
- 🌐 **Italian→English translation** using Argos Translate (free, unlimited)
- ⚡ **Adjustable speed**: --fast, normal, --slow modes
- 💾 **Save transcripts** to Markdown files for later review
- 🆓 **100% free and offline** - no API keys, no quotas
- 🖥️ **Interactive menu** or direct command-line launch

## System Requirements

- **OS**: Fedora 43+ (tested) - should work on other Linux distros with PipeWire/PulseAudio
- **RAM**: 2GB minimum (small), 5GB recommended (medium), 10GB+ for large
- **Python**: 3.10+
- **Audio**: PipeWire or PulseAudio

## Installation

### 1. Install system dependencies
```bash
# On Fedora 43
sudo dnf install python3 python3-pip ffmpeg
```

### 2. Download the script
```bash
# Download the script
wget https://raw.githubusercontent.com/stephdl/live-voice-translate/main/live-voice-translate.sh

# Make it executable
chmod +x live-voice-translate.sh
```

### 3. First run (automatic installation)
```bash
./live-voice-translate.sh
```

The script will automatically install:
- `faster-whisper` Python package
- `argostranslate` Python package
- Italian→English translation model

**Note**: First run may take 2-3 minutes to download dependencies (~800MB for large model if selected).

## Usage

### Interactive Menu (Recommended)
```bash
./live-voice-translate.sh
```

You'll see:
```
═══════════════════════════════════════════
   Jitsi IT→EN Translation
═══════════════════════════════════════════

Available models:

  1) tiny   - Ultra fast     (60% accuracy, ~1s, 1GB RAM)
  2) base   - Fast           (85% accuracy, ~3s, 1.5GB RAM)
  3) small  - Balanced       (90% accuracy, ~4s, 2GB RAM)
  4) medium - Recommended    (95% accuracy, ~5s, 5GB RAM) [DEFAULT]
  5) large  - Maximum        (98% accuracy, ~8s, 10GB RAM) ⚠️  High fan

Your choice (1-5 or Enter for default):
```

**Press Enter** for medium (recommended) or choose 1-5.

### Direct Launch
```bash
# Normal speed (default)
./live-voice-translate.sh medium         # Medium, 5s latency
./live-voice-translate.sh large          # Large, 8s latency

# Fast mode (shorter segments, faster response)
./live-voice-translate.sh medium --fast  # Medium, 4s latency
./live-voice-translate.sh large --fast   # Large, 6s latency

# Slow mode (longer segments, complete sentences)
./live-voice-translate.sh medium --slow  # Medium, 6s latency
./live-voice-translate.sh large --slow   # Large, 11s latency

# Save transcript to file
./live-voice-translate.sh medium --save                    # Auto-generated filename
./live-voice-translate.sh large --save meeting-notes.md    # Custom filename
./live-voice-translate.sh medium --fast --save             # Fast mode + save
```

### Create Aliases (Optional)

Add convenient shortcuts to your `~/.bashrc`:
```bash
cat >> ~/.bashrc << 'EOF'

# Live voice translation aliases
alias live-translate='~/live-voice-translate.sh'                        # Interactive menu
alias live-translate-fast='~/live-voice-translate.sh medium --fast'    # 4s latency
alias live-translate-balanced='~/live-voice-translate.sh medium'       # 5s latency (default)
alias live-translate-save='~/live-voice-translate.sh medium --save'    # With transcript
alias live-translate-quality='~/live-voice-translate.sh large'         # 8s latency
alias live-translate-max='~/live-voice-translate.sh large --slow'      # 11s, best quality
EOF

source ~/.bashrc
```

Now you can use:
```bash
live-translate              # Interactive menu
live-translate-fast         # Medium + fast mode (4s)
live-translate-balanced     # Medium, normal (5s)
live-translate-save         # Medium + save transcript
live-translate-quality      # Large, normal (8s)
live-translate-max          # Large + slow mode (11s, complete sentences)
```

## Saved Transcripts

When using `--save`, transcripts are saved in **Markdown format** for easy reading and sharing.

### Example Output File
```markdown
# Live Voice Translation

**Date:** 2026-04-01 22:30:15  
**Model:** large-v3  
**Mode:** normal  

---

**[22:30:18]**

🇮🇹 *Dobbiamo aggiornare il firewall di NethSecurity.*

🇬🇧 We need to update the NethSecurity firewall.

---

**[22:30:23]**

🇮🇹 *Il container Podman non si avvia correttamente.*

🇬🇧 The Podman container does not start correctly.

---

**End of session:** 2026-04-01 22:35:42
```

### Working with Saved Files
```bash
# Search for specific topics
grep -i "firewall" meeting-notes.md

# Convert to PDF
pandoc meeting-notes.md -o meeting-report.pdf

# Add your own notes
# Just edit the .md file and add comments anywhere
```

## How It Works

1. **Capture audio**: Detects active audio stream (speakers/Bluetooth/headset)
2. **Transcribe**: Uses faster-whisper to transcribe Italian speech to text
3. **Translate**: Uses Argos Translate to convert Italian text to English
4. **Display**: Shows English translation in real-time
5. **Save (optional)**: Records both Italian and English to Markdown file

## Use Cases

- 🎥 **Jitsi/Zoom/Teams meetings** in Italian
- 📺 **YouTube videos** in Italian
- 🎧 **Live streams** or podcasts
- 📞 **Any audio source** playing on your computer
- 📝 **Meeting minutes** with automatic transcript generation

## Model Comparison

### Standard Mode (Normal)

| Model      | Accuracy | Latency | RAM   | CPU  | Use Case              |
|------------|----------|---------|-------|------|-----------------------|
| **tiny**   | 60%      | ~1s     | 1GB   | 30%  | Quick tests           |
| **base**   | 85%      | ~3s     | 1.5GB | 40%  | Fast casual meetings  |
| **small**  | 90%      | ~4s     | 2GB   | 50%  | Balanced              |
| **medium** | 95%      | ~5s     | 5GB   | 60%  | **Recommended daily** |
| **large**  | 98%      | ~8s     | 10GB  | 80%  | Critical meetings     |

### Speed Modes

| Model | --fast | Normal | --slow |
|-------|--------|--------|--------|
| **tiny** | 0.5s | 1s | 1.5s |
| **base** | 2s | 3s | 4s |
| **small** | 3s | 4s | 5s |
| **medium** | 4s | 5s | 6s |
| **large** | 6s | 8s | **11s** |

**When to use each mode:**
- **--fast**: Quick reactions, casual conversations (may cut long sentences)
- **Normal**: Daily meetings, good balance
- **--slow**: Formal presentations, complete sentences guaranteed

## Privacy & Security

### 🔒 100% Private

- ✅ **Everything runs on your computer** - no cloud, no servers
- ✅ **No internet needed** (except first-time model download)
- ✅ **Nothing is logged** - only saved if you use `--save`
- ✅ **Auto cleanup** - temporary files deleted when you stop (Ctrl+C)

### What Gets Stored?

| What | Where | When Deleted |
|------|-------|--------------|
| Audio (5 seconds) | `/tmp/audio_chunk.wav` | When you press Ctrl+C |
| Whisper models | `~/.cache/huggingface/` | Never (reused each time) |
| Translation model | `~/.local/share/argos-translate/` | Never (reused each time) |
| Transcripts | Your specified file (if `--save` used) | Manual deletion |

**Your conversations are never sent to external servers.**

### Safe For

✅ Confidential business meetings  
✅ Medical discussions  
✅ Legal conversations  
✅ Any private audio

### Comparison

| Tool | Where Your Audio Goes |
|------|----------------------|
| **live-voice-translate** | Stays on your computer |
| Google Translate | Sent to Google servers |
| Zoom/Teams translate | Sent to their servers |
| DeepL API | Sent to DeepL servers |

### Network Check

After installation, the script **never connects to internet**.

Test it yourself:
```bash
# Run the script, then check network activity
sudo tcpdump -i any | grep -v "127.0.0.1"
# You'll see: nothing
```

---

**Your audio never leaves your machine. Period.**

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
2. **Multiple RUNNING streams**: The script picks the first one. If wrong device, disable others temporarily
3. **Only SUSPENDED streams**: Enable audio playback before running the script

**Debug audio capture**:
```bash
# Test if audio is being captured (5 seconds test)
timeout 5s parec --monitor-stream=51 --format=s16le --rate=16000 --channels=1 > /tmp/test.raw

# Check file size (should be ~160KB for 5s of audio)
ls -lh /tmp/test.raw
```

If file is empty (0 bytes) → wrong stream index or no audio playing.

### Script doesn't show menu

**Problem**: Script hangs without displaying menu

**Solution**: The menu is displayed but waiting for input. Just press **Enter** or type a number (1-5).

### High CPU / Fan noise with large model

**Solution**: Use `medium` instead of `large` for daily meetings. Large model is CPU-intensive.

**Monitor CPU usage**:
```bash
# In another terminal while script is running
htop

# Or
top -p $(pgrep -f live-voice-translate)
```

### Translation not working

**Problem**: Script runs but no translations appear

**Checklist**:

1. **Is audio playing?** Open YouTube or Jitsi
2. **Is the audio stream active?** Check with `pactl list short sources | grep RUNNING`
3. **Is there actual speech?** Music-only won't produce translations
4. **Wait 5-10 seconds**: First segment takes time to process

**Test with Italian YouTube video**:
```bash
# Terminal 1: Open Italian video
firefox "https://www.youtube.com/results?search_query=italian+news"

# Terminal 2: Run script
./live-voice-translate.sh medium
```

You should see translations within 5-10 seconds.

## Technical Details

- **Transcription**: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (optimized Whisper implementation)
- **Translation**: [Argos Translate](https://github.com/argosopentech/argos-translate) (offline, LibreTranslate engine)
- **Audio capture**: PipeWire/PulseAudio monitor streams
- **Segments**: Configurable 2-7 seconds audio chunks
- **Processing**: CPU-only (no GPU required)
- **Output format**: Markdown with timestamps

## Limitations

- **Translation quality**: Argos is good but not perfect (~85-90% quality). For professional quality, consider DeepL API (paid).
- **Latency**: Real-time = 0.5-11s delay depending on model and speed mode
- **Language**: Currently optimized for Italian→English only
- **CPU usage**: Large model requires significant CPU (80%+)
- **GPU**: Only NVIDIA CUDA supported (AMD ROCm not supported due to complexity)

## Future Improvements

- [ ] Add DeepL API support (optional, paid)
- [ ] Support more language pairs
- [ ] NVIDIA GPU acceleration (CUDA)
- [ ] GUI interface
- [ ] Export to different formats (JSON, TXT, PDF)

## Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share your use cases

## License

MIT License - feel free to use, modify, and distribute.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the amazing transcription model
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for the optimized implementation
- [Argos Translate](https://github.com/argosopentech/argos-translate) for free offline translation
- Nethesis team for inspiring this project during Italian Jitsi meetings

## Author

Created by Stéphane de Labrusse for real-time translation of Italian Nethesis meetings.

---

**Star ⭐ this repo if it helps you understand Italian meetings!**

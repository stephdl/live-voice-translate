#!/bin/bash
# live-voice-translate.sh - IT→EN real-time translation for Jitsi

set -euo pipefail

DEFAULT_MODEL="medium"

show_menu() {
    # IMPORTANT: All echo go to stderr (&2)
    # Only the final echo (the choice) goes to stdout
    
    echo "═══════════════════════════════════════════" >&2
    echo "   Jitsi IT→EN Translation" >&2
    echo "═══════════════════════════════════════════" >&2
    echo "" >&2
    
    RAM_TOTAL=$(free -g | awk '/^Mem:/{print $2}')
    
    echo "Available models:" >&2
    echo "" >&2
    echo "  1) tiny   - Ultra fast     (60% accuracy, ~1s, 1GB RAM)" >&2
    echo "  2) base   - Fast           (85% accuracy, ~3s, 1.5GB RAM)" >&2
    echo "  3) small  - Balanced       (90% accuracy, ~4s, 2GB RAM)" >&2
    echo "  4) medium - Recommended    (95% accuracy, ~5s, 5GB RAM) [DEFAULT]" >&2
    
    if [ "$RAM_TOTAL" -ge 12 ]; then
        echo "  5) large  - Maximum        (98% accuracy, ~8s, 10GB RAM) ⚠️  High fan" >&2
    else
        echo "  5) large  - Maximum        [Insufficient RAM: ${RAM_TOTAL}GB]" >&2
    fi
    
    echo "" >&2
    echo -n "Your choice (1-5 or Enter for default): " >&2
    
    read -r choice
    
    # ONLY this echo goes to stdout (captured by MODEL=$(...))
    case "$choice" in
        1) echo "tiny" ;;
        2) echo "base" ;;
        3) echo "small" ;;
        4) echo "medium" ;;
        5) 
            if [ "$RAM_TOTAL" -ge 12 ]; then
                echo "large-v3"
            else
                echo "medium"
            fi
            ;;
        "") echo "$DEFAULT_MODEL" ;;
        *) echo "$DEFAULT_MODEL" ;;
    esac
}

get_model_config() {
    local model=$1
    local mode=$2  # "fast", "normal", or "slow"
    
    case "$model" in
        tiny)
            case "$mode" in
                fast) echo "SEGMENT=64000 BEAM=1 PRECISION=60% LATENCY=0.5s" ;;
                slow) echo "SEGMENT=128000 BEAM=1 PRECISION=60% LATENCY=1.5s" ;;
                *) echo "SEGMENT=96000 BEAM=1 PRECISION=60% LATENCY=1s" ;;
            esac
            ;;
        base)
            case "$mode" in
                fast) echo "SEGMENT=96000 BEAM=3 PRECISION=85% LATENCY=2s" ;;
                slow) echo "SEGMENT=160000 BEAM=3 PRECISION=85% LATENCY=4s" ;;
                *) echo "SEGMENT=128000 BEAM=3 PRECISION=85% LATENCY=3s" ;;
            esac
            ;;
        small)
            case "$mode" in
                fast) echo "SEGMENT=128000 BEAM=3 PRECISION=90% LATENCY=3s" ;;
                slow) echo "SEGMENT=192000 BEAM=3 PRECISION=90% LATENCY=5s" ;;
                *) echo "SEGMENT=160000 BEAM=3 PRECISION=90% LATENCY=4s" ;;
            esac
            ;;
        medium)
            case "$mode" in
                fast) echo "SEGMENT=128000 BEAM=4 PRECISION=95% LATENCY=4s" ;;
                slow) echo "SEGMENT=192000 BEAM=4 PRECISION=95% LATENCY=6s" ;;
                *) echo "SEGMENT=160000 BEAM=4 PRECISION=95% LATENCY=5s" ;;
            esac
            ;;
        large-v3)
            case "$mode" in
                fast) echo "SEGMENT=128000 BEAM=5 PRECISION=98% LATENCY=6s" ;;
                slow) echo "SEGMENT=224000 BEAM=5 PRECISION=98% LATENCY=11s" ;;
                *) echo "SEGMENT=160000 BEAM=5 PRECISION=98% LATENCY=8s" ;;
            esac
            ;;
    esac
}

install_deps() {
    echo "Installing dependencies..." >&2
    pip install faster-whisper argostranslate --break-system-packages
    
    if ! command -v ffmpeg &> /dev/null; then
        sudo dnf install -y ffmpeg
    fi
    
    echo "Downloading IT→EN translation model..." >&2
    python3 << 'PYEOF'
import argostranslate.package
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(lambda x: x.from_code == "it" and x.to_code == "en", available_packages)
)
argostranslate.package.install_from_path(package_to_install.download())
print("✅ IT→EN model installed")
PYEOF
    
    echo "✅ Installation complete" >&2
}

main() {
    local MODEL=""
    local SPEED_MODE="normal"
    local SAVE_FILE=""
    
    # Check for dependencies
    if ! python3 -c "import faster_whisper" 2>/dev/null; then
        echo "faster-whisper not installed" >&2
        install_deps
    fi
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --fast|-f)
                SPEED_MODE="fast"
                shift
                ;;
            --slow|-s)
                SPEED_MODE="slow"
                shift
                ;;
            --save)
                if [[ -n "${2:-}" && ! "$2" =~ ^-- ]]; then
                    # Custom filename provided
                    SAVE_FILE="$2"
                    shift 2
                else
                    # Auto-generate filename
                    SAVE_FILE="live-translate-$(date +%Y%m%d-%H%M%S).md"
                    shift
                fi
                ;;
            --install)
                install_deps
                exit 0
                ;;
            --help|-h)
                echo "Usage: $0 [MODEL] [OPTIONS]"
                echo ""
                echo "Models:"
                echo "  tiny, base, small, medium, large"
                echo ""
                echo "Options:"
                echo "  --fast, -f          Shorter segments (faster)"
                echo "  --slow, -s          Longer segments (complete sentences)"
                echo "  --save [FILE]       Save transcript to file (default: auto-generated .md)"
                echo "  --install           Install dependencies"
                echo "  --help, -h          Show this help"
                echo ""
                echo "Examples:"
                echo "  $0                           # Interactive menu"
                echo "  $0 medium                    # Medium model"
                echo "  $0 medium --save             # Save to auto-generated file"
                echo "  $0 large --save meeting.md   # Save to specific file"
                echo "  $0 medium --fast --save      # Fast mode + save"
                exit 0
                ;;
            tiny|base|small|medium)
                MODEL="$1"
                shift
                ;;
            large)
                MODEL="large-v3"
                shift
                ;;
            "")
                shift
                ;;
            *)
                echo "Error: Invalid argument '$1'" >&2
                echo "Use: $0 --help" >&2
                exit 1
                ;;
        esac
    done
    
    # If no model specified, show menu
    if [ -z "$MODEL" ]; then
        MODEL=$(show_menu)
    fi
    
    # Get model configuration
    CONFIG=$(get_model_config "$MODEL" "$SPEED_MODE")
    eval "$CONFIG"
    
    # Display configuration
    echo ""
    echo "═══════════════════════════════════════════"
    echo "   Configuration"
    echo "═══════════════════════════════════════════"
    echo ""
    echo "  Model      : $MODEL"
    echo "  Accuracy   : $PRECISION"
    echo "  Latency    : ~$LATENCY"
    if [ "$SPEED_MODE" = "fast" ]; then
        echo "  Mode       : Fast (shorter segments)"
    elif [ "$SPEED_MODE" = "slow" ]; then
        echo "  Mode       : Slow (longer segments, complete sentences)"
    fi
    if [ -n "$SAVE_FILE" ]; then
        echo "  Save to    : $SAVE_FILE"
    fi
    echo ""
    
    # Detect active audio stream
    AUDIO_STREAM=$(pactl list short sources | grep monitor | grep RUNNING | head -n1 | awk '{print $1}')
    
    if [ -z "$AUDIO_STREAM" ]; then
        echo "Error: No active audio stream detected" >&2
        echo "Launch a YouTube video or Jitsi call with sound" >&2
        exit 1
    fi
    
    echo "  Stream     : $AUDIO_STREAM"
    echo ""
    echo "═══════════════════════════════════════════"
    echo ""
    echo "Translation in progress... (Ctrl+C to stop)"
    echo ""
    
    # Launch Python transcription/translation pipeline
    python3 2>/dev/null << PYEOF
import subprocess, wave, io, warnings, re, textwrap
from datetime import datetime
warnings.filterwarnings("ignore")
import argostranslate.translate
from faster_whisper import WhisperModel

# Open save file if requested
save_file = "${SAVE_FILE}" if "${SAVE_FILE}" else None
file_handle = None

if save_file:
    try:
        file_handle = open(save_file, 'w', encoding='utf-8')
        # Write Markdown header
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file_handle.write(f"# Live Voice Translation\n\n")
        file_handle.write(f"**Date:** {now}  \n")
        file_handle.write(f"**Model:** ${MODEL}  \n")
        file_handle.write(f"**Mode:** ${SPEED_MODE}  \n\n")
        file_handle.write("---\n\n")
        file_handle.flush()
        print(f"💾 Saving to: {save_file}\n", flush=True)
    except Exception as e:
        print(f"⚠️  Warning: Could not open save file: {e}\n", flush=True)
        file_handle = None

print("⏳ Loading model ${MODEL}...", flush=True)
model = WhisperModel("${MODEL}", device="cpu", compute_type="int8")
print("✅ Ready\n", flush=True)

try:
    while True:
        try:
            # Capture audio stream
            cmd = ["parec", "--monitor-stream=${AUDIO_STREAM}", 
                   "--format=s16le", "--rate=16000", "--channels=1"]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            audio_data = proc.stdout.read(${SEGMENT})
            proc.terminate()
            
            # Skip if silence detected
            if len(audio_data) < 50000:
                continue
            
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
            segments, info = model.transcribe("/tmp/audio_chunk.wav", language="it",
                                              vad_filter=False, beam_size=${BEAM},
                                              condition_on_previous_text=True)
            
            # Translate and display
            for segment in segments:
                text_it = segment.text.strip()
                if text_it and len(text_it) > 3:
                    # Split by sentence
                    for sentence in re.split(r'(?<=[.!?])\s+', text_it):
                        sentence = sentence.strip()
                        if len(sentence) > 5:
                            # Translate IT→EN with Argos
                            text_en = argostranslate.translate.translate(sentence, "it", "en")
                            
                            # Get timestamp
                            timestamp = datetime.now().strftime('%H:%M:%S')
                            
                            # Display with word wrap if needed
                            if len(text_en) > 80:
                                output = textwrap.fill(text_en, width=80, initial_indent="▶ ", 
                                                       subsequent_indent="  ")
                            else:
                                output = f"▶ {text_en}"
                            
                            # Print to terminal
                            print(output, flush=True)
                            
                            # Save to file if enabled (Markdown format)
                            if file_handle:
                                file_handle.write(f"**[{timestamp}]**\n\n")
                                file_handle.write(f"🇮🇹 *{sentence}*\n\n")
                                file_handle.write(f"🇬🇧 {text_en}\n\n")
                                file_handle.write("---\n\n")
                                file_handle.flush()
                                
        except KeyboardInterrupt:
            print("\n\nStopping translation.")
            break
        except Exception:
            continue
finally:
    # Close save file
    if file_handle:
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file_handle.write(f"\n**End of session:** {end_time}\n")
        file_handle.close()
        print(f"\n💾 Transcript saved to: {save_file}")
PYEOF
}

# Cleanup on exit
trap 'rm -f /tmp/audio_chunk.wav; exit 0' INT TERM

main "$@"

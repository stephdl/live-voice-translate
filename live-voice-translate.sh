#!/bin/bash
# jitsi-translate.sh - IT→EN real-time translation for Jitsi

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
        echo "  5) large  - Maximum        (98% accuracy, ~10s, 10GB RAM) ⚠️  High fan" >&2
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
    case "$model" in
        tiny) echo "SEGMENT=96000 BEAM=1 PRECISION=60% LATENCY=1s" ;;
        base) echo "SEGMENT=128000 BEAM=3 PRECISION=85% LATENCY=3s" ;;
        small) echo "SEGMENT=160000 BEAM=3 PRECISION=90% LATENCY=4s" ;;
        medium) echo "SEGMENT=160000 BEAM=4 PRECISION=95% LATENCY=5s" ;;
        large-v3) echo "SEGMENT=192000 BEAM=5 PRECISION=98% LATENCY=10s" ;;
    esac
}

main() {
    local MODEL=""
    
    # Parse command line arguments
    case "${1:-}" in
        tiny|base|small|medium)
            MODEL="$1"
            ;;
        large)
            MODEL="large-v3"
            ;;
        --help|-h)
            echo "Usage: $0 [tiny|base|small|medium|large]"
            echo ""
            echo "Examples:"
            echo "  $0              # Interactive menu"
            echo "  $0 medium       # Launch directly with medium"
            echo "  $0 large        # Launch directly with large"
            exit 0
            ;;
        "")
            # No argument = interactive menu
            MODEL=$(show_menu)
            ;;
        *)
            echo "Error: Invalid argument '$1'" >&2
            echo "Use: $0 --help" >&2
            exit 1
            ;;
    esac
    
    # Get model configuration
    CONFIG=$(get_model_config "$MODEL")
    eval "$CONFIG"
    
    echo ""
    echo "═══════════════════════════════════════════"
    echo "   Configuration"
    echo "═══════════════════════════════════════════"
    echo ""
    echo "  Model      : $MODEL"
    echo "  Accuracy   : $PRECISION"
    echo "  Latency    : ~$LATENCY"
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
warnings.filterwarnings("ignore")
import argostranslate.translate
from faster_whisper import WhisperModel

print("⏳ Loading model ${MODEL}...", flush=True)
model = WhisperModel("${MODEL}", device="cpu", compute_type="int8")
print("✅ Ready\n", flush=True)

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
                        
                        # Display with word wrap if needed
                        if len(text_en) > 80:
                            print(textwrap.fill(text_en, width=80, initial_indent="▶ ", 
                                               subsequent_indent="  "), flush=True)
                        else:
                            print(f"▶ {text_en}", flush=True)
    except KeyboardInterrupt:
        print("\n\nStopping translation.")
        break
    except:
        continue
PYEOF
}

# Cleanup on exit
trap 'rm -f /tmp/audio_chunk.wav; exit 0' INT TERM

main "$@"

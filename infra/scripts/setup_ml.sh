#!/bin/bash
# setup_ml.sh — Download datasets and train models

set -e
echo "🔧 CyberShield AI — ML Setup"

# ─── Create directories ────────────────────────────
mkdir -p data/audio_deepfake_dataset/real
mkdir -p data/audio_deepfake_dataset/fake
mkdir -p data/video_face_crops/real
mkdir -p data/video_face_crops/fake
mkdir -p models

# ─── Check if kaggle is installed ──────────────────
if ! command -v kaggle &> /dev/null; then
    echo "Installing kaggle CLI..."
    pip install kaggle
    echo "⚠️  Set up ~/.kaggle/kaggle.json with your API key"
    echo "   Get it from: https://www.kaggle.com/settings → API → Create New Token"
    exit 1
fi

# ─── Download Audio Dataset ────────────────────────
echo ""
echo "📥 Downloading audio deepfake dataset..."
if [ ! -f "data/audio_deepfake_dataset/.downloaded" ]; then
    kaggle datasets download -d birdy654/deep-voice-deepfake-voice-recognition \
        -p data/audio_raw/ --unzip
    
    # Organize into real/fake structure
    # (adjust these paths based on actual dataset structure)
    cp data/audio_raw/REAL/*.wav data/audio_deepfake_dataset/real/ 2>/dev/null || true
    cp data/audio_raw/FAKE/*.wav data/audio_deepfake_dataset/fake/ 2>/dev/null || true
    
    touch data/audio_deepfake_dataset/.downloaded
    echo "✅ Audio dataset ready"
else
    echo "✅ Audio dataset already downloaded"
fi

# ─── Download Video Dataset ────────────────────────
echo ""
echo "📥 Downloading video face crops dataset..."
if [ ! -f "data/video_face_crops/.downloaded" ]; then
    kaggle datasets download -d xhlulu/140k-real-and-fake-faces \
        -p data/video_raw/ --unzip
    
    # Organize — adjust paths based on actual structure
    cp data/video_raw/real-vs-fake/train/real/*.jpg data/video_face_crops/real/ 2>/dev/null || true
    cp data/video_raw/real-vs-fake/train/fake/*.jpg data/video_face_crops/fake/ 2>/dev/null || true
    
    touch data/video_face_crops/.downloaded
    echo "✅ Video dataset ready"
else
    echo "✅ Video dataset already downloaded"
fi

# ─── Count files ───────────────────────────────────
echo ""
echo "📊 Dataset Summary:"
echo "   Audio real:  $(ls data/audio_deepfake_dataset/real/ 2>/dev/null | wc -l) files"
echo "   Audio fake:  $(ls data/audio_deepfake_dataset/fake/ 2>/dev/null | wc -l) files"
echo "   Video real:  $(ls data/video_face_crops/real/ 2>/dev/null | wc -l) files"
echo "   Video fake:  $(ls data/video_face_crops/fake/ 2>/dev/null | wc -l) files"

# ─── Train Models ──────────────────────────────────
echo ""
echo "🏋️ Training audio deepfake model..."
cd apps/api-gateway
python -c "
import sys; sys.path.insert(0, '.')
from notebooks_runner import train_audio
train_audio()
"

echo ""
echo "🏋️ Training video deepfake model..."
python -c "
import sys; sys.path.insert(0, '.')
from notebooks_runner import train_video
train_video()
"

echo ""
echo "✅ All models trained!"
echo "   Audio model: models/audio_deepfake_cnn.pt"
echo "   Video model: models/video_deepfake_detector.pt"
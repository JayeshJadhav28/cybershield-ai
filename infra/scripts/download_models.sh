
### `infra/scripts/download_models.sh`
```bash
#!/bin/bash
# ═══════════════════════════════════════════
# Download pre-trained model weights
# ═══════════════════════════════════════════

set -e

MODEL_DIR="$(cd "$(dirname "$0")/../../models" && pwd)"
echo "📦 Downloading models to: $MODEL_DIR"

# For MVP: create placeholder models (trained in notebooks)
# Replace these URLs with actual model hosting in production

echo "⚠️  No pre-trained models hosted yet."
echo "   Please run the training notebooks in notebooks/ directory."
echo "   Or the system will use lightweight fallback heuristics."
echo ""
echo "Expected files:"
echo "  $MODEL_DIR/phishing_tfidf_vectorizer.pkl"
echo "  $MODEL_DIR/phishing_classifier.pkl"
echo "  $MODEL_DIR/audio_deepfake_cnn.h5"
echo "  $MODEL_DIR/video_deepfake_detector.h5"
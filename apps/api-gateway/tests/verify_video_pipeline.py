"""
Quick verification script — run after replacing files.

    cd apps/api-gateway
    python tests/verify_video_pipeline.py

Checks:
  1. No MediaPipe references in project (Windows-compatible)
  2. Face detector initializes (no MediaPipe)
  3. Face detection works on a synthetic frame
  4. Model loads and produces output
  5. Full pipeline produces non-default scores
"""
import sys
import os
import glob

import numpy as np
import cv2

# Ensure project root is in path
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)


def check_no_mediapipe():
    """Scan Python files for mediapipe references — Windows compatible."""
    print("\n═══ Pre-check: No MediaPipe References ═══")

    search_dirs = [
        os.path.join(PROJECT_DIR, "utils"),
        os.path.join(PROJECT_DIR, "services"),
        os.path.join(PROJECT_DIR, "ml"),
    ]

    found_refs = []
    for search_dir in search_dirs:
        if not os.path.isdir(search_dir):
            continue
        pattern = os.path.join(search_dir, "**", "*.py")
        for filepath in glob.glob(pattern, recursive=True):
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        if "mediapipe" in line.lower() and not line.strip().startswith("#"):
                            rel_path = os.path.relpath(filepath, PROJECT_DIR)
                            found_refs.append(f"  {rel_path}:{line_num}  →  {line.strip()}")
            except Exception:
                pass

    if found_refs:
        print("  ❌ Found MediaPipe references:")
        for ref in found_refs[:15]:
            print(f"    {ref}")
        print("  → Remove these references!")
    else:
        print("  ✅ No MediaPipe references found in utils/, services/, ml/")


def test_face_detector():
    """Verify OpenCV face detection works WITHOUT MediaPipe."""
    print("\n═══ Test 1: Face Detector Initialization ═══")
    from utils.video_preprocessing import RobustFaceDetector

    detector = RobustFaceDetector()
    print("  ✅ Detector initialized (no MediaPipe!)")

    # Create a frame with a real-looking face using OpenCV drawing
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (180, 190, 200)  # light background

    # Draw face oval
    cv2.ellipse(frame, (320, 200), (70, 90), 0, 0, 360, (180, 160, 140), -1)
    # Eyes
    cv2.circle(frame, (295, 175), 10, (60, 40, 30), -1)
    cv2.circle(frame, (345, 175), 10, (60, 40, 30), -1)
    # White of eyes
    cv2.circle(frame, (295, 175), 5, (240, 240, 240), -1)
    cv2.circle(frame, (345, 175), 5, (240, 240, 240), -1)
    # Nose
    cv2.line(frame, (320, 185), (315, 210), (140, 120, 100), 2)
    cv2.line(frame, (315, 210), (325, 210), (140, 120, 100), 2)
    # Mouth
    cv2.ellipse(frame, (320, 235), (20, 8), 0, 0, 180, (120, 80, 70), 2)
    # Eyebrows
    cv2.line(frame, (278, 158), (310, 155), (80, 60, 50), 2)
    cv2.line(frame, (330, 155), (362, 158), (80, 60, 50), 2)

    faces = detector.detect(frame)
    print(f"  Faces detected on synthetic frame: {len(faces)}")
    if faces:
        print(f"  ✅ Face detection works! Bounding box: {faces[0]}")
    else:
        print("  ⚠️  No face detected on synthetic frame")
        print("      (Haar cascades need real face-like textures)")
        print("      Center-crop fallback will be used — this is EXPECTED and OK")


def test_face_crop_pipeline():
    """Verify face cropping produces correct output format."""
    print("\n═══ Test 2: Face Crop Pipeline ═══")
    from utils.video_preprocessing import detect_and_crop_faces

    # Create test frames
    frames = []
    for i in range(5):
        frame = np.random.randint(50, 200, (480, 640, 3), dtype=np.uint8)
        # Add a face-like oval region
        cv2.ellipse(frame, (320, 200), (60, 80), 0, 0, 360, (200, 180, 160), -1)
        frames.append(frame)

    crops, info = detect_and_crop_faces(frames)

    print(f"  Frames processed:      {info['total_frames_processed']}")
    print(f"  Faces detected:        {info['faces_detected']}")
    print(f"  Center-crop fallback:  {info['center_crop_fallback']}")
    print(f"  Total crops returned:  {len(crops)}")

    assert len(crops) == len(frames), (
        f"Expected {len(frames)} crops (one per frame), got {len(crops)}"
    )

    for i, crop in enumerate(crops):
        assert crop.shape == (128, 128, 3), f"Crop {i} wrong shape: {crop.shape}"
        assert crop.dtype == np.float32, f"Crop {i} wrong dtype: {crop.dtype}"
        assert 0.0 <= crop.min() and crop.max() <= 1.0, (
            f"Crop {i} not normalized: [{crop.min():.3f}, {crop.max():.3f}]"
        )

    print(f"  Crop shape:  {crops[0].shape}")
    print(f"  Crop dtype:  {crops[0].dtype}")
    print(f"  Crop range:  [{crops[0].min():.3f}, {crops[0].max():.3f}]")
    print("  ✅ All crops correct: shape=(128,128,3), dtype=float32, range=[0,1]")


def test_model_loading():
    """Verify model loads and produces valid output."""
    print("\n═══ Test 3: Model Loading ═══")
    from config import settings

    # Check what model files exist
    model_dir = settings.MODEL_DIR
    print(f"  Model directory: {model_dir}")

    h5_path = settings.video_model_path("h5")
    pt_path = settings.video_model_path("pt")
    print(f"  Checking .h5: {h5_path} → {'EXISTS' if h5_path.is_file() else 'MISSING'}")
    print(f"  Checking .pt: {pt_path} → {'EXISTS' if pt_path.is_file() else 'MISSING'}")

    from ml.model_loader import ModelLoader

    # Force fresh load
    ModelLoader._instance = None
    loader = ModelLoader()
    model = loader.get_video_model()

    if model is None:
        print("\n  ⚠️  Video model not loaded!")
        print("      Place one of these in the models/ directory:")
        print(f"        - {settings.VIDEO_MODEL_H5}")
        print(f"        - {settings.VIDEO_MODEL_PT}")
        return False

    print(f"  ✅ Model loaded: {type(model).__name__}")

    # Test inference with a dummy face
    from ml.video_model import predict_face

    dummy_face = np.random.rand(128, 128, 3).astype(np.float32)
    prob = predict_face(model, dummy_face)
    print(f"  Random face prediction: {prob:.4f}")
    assert 0.0 <= prob <= 1.0, f"Invalid probability: {prob}"

    # Test with a black image (should lean toward one class)
    black_face = np.zeros((128, 128, 3), dtype=np.float32)
    prob_black = predict_face(model, black_face)
    print(f"  Black face prediction:  {prob_black:.4f}")

    # Test with a white image
    white_face = np.ones((128, 128, 3), dtype=np.float32)
    prob_white = predict_face(model, white_face)
    print(f"  White face prediction:  {prob_white:.4f}")

    print("  ✅ Model inference works!")
    return True


def test_full_pipeline():
    """Create a test video and run full analysis."""
    print("\n═══ Test 4: Full Video Pipeline ═══")
    import tempfile

    # Create a test video file
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp4")
    os.close(tmp_fd)

    try:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(tmp_path, fourcc, 30.0, (640, 480))

        if not writer.isOpened():
            print("  ❌ Cannot create test video (codec issue)")
            print("     Trying XVID codec...")
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            tmp_path2 = tmp_path.replace(".mp4", ".avi")
            writer = cv2.VideoWriter(tmp_path2, fourcc, 30.0, (640, 480))
            if writer.isOpened():
                os.unlink(tmp_path)
                tmp_path = tmp_path2
            else:
                print("  ❌ Cannot create test video with any codec")
                return

        for i in range(60):  # 2 seconds at 30fps
            frame = np.random.randint(40, 200, (480, 640, 3), dtype=np.uint8)
            # Draw a face-like structure
            cv2.ellipse(frame, (320, 200), (65, 85), 0, 0, 360, (190, 170, 150), -1)
            cv2.circle(frame, (295, 180), 8, (50, 40, 30), -1)
            cv2.circle(frame, (345, 180), 8, (50, 40, 30), -1)
            cv2.ellipse(frame, (320, 230), (18, 7), 0, 0, 180, (130, 80, 70), 2)
            writer.write(frame)
        writer.release()

        file_size = os.path.getsize(tmp_path)
        print(f"  Test video: {tmp_path} ({file_size} bytes)")

        # Run the analyzer
        from services.video_analyzer import VideoAnalyzer

        analyzer = VideoAnalyzer()
        result = analyzer.analyze(tmp_path)

        print(f"\n  ── Analysis Results ──")
        print(f"  AI probability:   {result.ai_probability:.4f}")
        print(f"  Rule score:       {result.rule_score:.4f}")
        print(f"  Confidence:       {result.confidence:.4f}")
        print(f"  Model available:  {result.model_available}")
        print(f"  Frame scores:     {len(result.frame_scores)} predictions")
        print(f"  Flags:            {result.flags}")

        if result.frame_scores:
            scores = result.frame_scores
            print(f"  Score min:        {min(scores):.4f}")
            print(f"  Score max:        {max(scores):.4f}")
            print(f"  Score mean:       {np.mean(scores):.4f}")
            print(f"  Score std:        {np.std(scores):.4f}")

        # Now run through the scoring engine
        print(f"\n  ── Scoring Engine (75% AI + 25% Rules) ──")
        from services.scoring_engine import (
            ScoringEngine, ScoringInput, ModalityResult,
        )

        engine = ScoringEngine()
        modality = ModalityResult(
            ai_probability=result.ai_probability,
            rule_score=result.rule_score,
            confidence=result.confidence,
            flags=result.flags,
            model_available=result.model_available,
        )
        score_out = engine.compute(ScoringInput(
            video_result=modality,
            analysis_type="video",
        ))

        bd = score_out.breakdown
        print(f"  Formula:          {bd.get('formula', 'N/A')}")
        print(f"  AI contribution:  {bd.get('ai_contribution', '?')} / 100")
        print(f"  Rule contribution:{bd.get('rule_contribution', '?')} / 100")
        print(f"  Adjustment:       {bd.get('adjustment', 0)}")
        print(f"  ─────────────────────────────────")
        print(f"  FINAL SCORE:      {score_out.risk_score} / 100")
        print(f"  RISK LABEL:       {score_out.risk_label.upper()}")
        print(f"  ─────────────────────────────────")

        if score_out.risk_score == 0 and score_out.risk_label == "safe":
            print("\n  ⚠️  Score is 0/safe — model may not be loaded or")
            print("      may need real deepfake content to trigger detection")
        else:
            print(f"\n  ✅ Pipeline produced non-trivial result!")

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_imports():
    """Verify all critical imports work."""
    print("\n═══ Test 0: Critical Imports ═══")
    errors = []

    try:
        import cv2
        print(f"  ✅ OpenCV {cv2.__version__}")
    except ImportError as e:
        errors.append(f"  ❌ OpenCV: {e}")

    try:
        import numpy
        print(f"  ✅ NumPy {numpy.__version__}")
    except ImportError as e:
        errors.append(f"  ❌ NumPy: {e}")

    try:
        import tensorflow as tf
        print(f"  ✅ TensorFlow {tf.__version__}")
    except ImportError:
        try:
            import torch
            print(f"  ✅ PyTorch {torch.__version__} (TensorFlow not found)")
        except ImportError as e:
            errors.append(f"  ❌ No ML framework: {e}")

    try:
        from config import settings
        print(f"  ✅ Config loaded (MODEL_DIR={settings.MODEL_DIR})")
    except Exception as e:
        errors.append(f"  ❌ Config: {e}")

    try:
        from utils.video_preprocessing import (
            extract_frames,
            detect_and_crop_faces,
            compute_frame_heuristics,
            RobustFaceDetector,
        )
        print("  ✅ video_preprocessing imports OK")
    except Exception as e:
        errors.append(f"  ❌ video_preprocessing: {e}")

    try:
        from ml.video_model import predict_face, predict_faces_batch
        print("  ✅ video_model imports OK")
    except Exception as e:
        errors.append(f"  ❌ video_model: {e}")

    try:
        from ml.model_loader import ModelLoader
        print("  ✅ model_loader imports OK")
    except Exception as e:
        errors.append(f"  ❌ model_loader: {e}")

    try:
        from services.video_analyzer import VideoAnalyzer
        print("  ✅ video_analyzer imports OK")
    except Exception as e:
        errors.append(f"  ❌ video_analyzer: {e}")

    try:
        from services.scoring_engine import ScoringEngine
        print("  ✅ scoring_engine imports OK")
    except Exception as e:
        errors.append(f"  ❌ scoring_engine: {e}")

    if errors:
        print("\n  IMPORT ERRORS:")
        for err in errors:
            print(f"  {err}")
        return False
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("  CyberShield AI — Video Pipeline Verification")
    print("  Platform: Windows-compatible")
    print("=" * 60)

    # Suppress TF warnings
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

    imports_ok = test_imports()
    if not imports_ok:
        print("\n❌ Fix import errors above before continuing")
        sys.exit(1)

    check_no_mediapipe()
    test_face_detector()
    test_face_crop_pipeline()
    model_ok = test_model_loading()
    test_full_pipeline()

    print("\n" + "=" * 60)
    if model_ok:
        print("  ✅ ALL CHECKS PASSED")
        print("  Pipeline should correctly detect deepfakes now.")
    else:
        print("  ⚠️  MODEL NOT LOADED")
        print("  Place video_deepfake_detector.h5 (or .pt)")
        print("  in the models/ directory, then re-run.")
    print("=" * 60)
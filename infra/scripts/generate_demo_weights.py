"""
Generate untrained model weights for demo/hackathon.
Models will output ~0.5 (uncertain) and heuristics fill the gap.

Usage: python infra/scripts/generate_demo_weights.py
"""
import os
import sys

# Add api-gateway to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "apps", "api-gateway"))


def generate():
    import torch
    os.makedirs("models", exist_ok=True)

    from ml.audio_model import AudioDeepfakeCNN
    audio = AudioDeepfakeCNN()
    torch.save(audio.state_dict(), "models/audio_deepfake_cnn.pt")
    print("Audio demo weights saved")

    try:
        from ml.video_model import VideoDeepfakeDetector
        video = VideoDeepfakeDetector(pretrained_backbone=True)
        torch.save(video.state_dict(), "models/video_deepfake_detector.pt")
        print("Video demo weights saved (ImageNet backbone)")
    except Exception as e:
        print(f"Video model needs torchvision: {e}")
        from ml.video_model import VideoDeepfakeDetector
        video = VideoDeepfakeDetector(pretrained_backbone=False)
        torch.save(video.state_dict(), "models/video_deepfake_detector.pt")
        print("Video demo weights saved (simple backbone)")


if __name__ == "__main__":
    generate()
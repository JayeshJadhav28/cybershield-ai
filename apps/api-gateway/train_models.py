"""
Train deepfake detection models.
Usage:
    python train_models.py                    # Train both
    python train_models.py --audio-only       # Audio only
    python train_models.py --video-only       # Video only
"""
import os
import sys
import argparse
import numpy as np
from pathlib import Path

# Base directory: resolve paths relative to THIS script's location
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # E:\cybershield-ai

sys.path.insert(0, str(SCRIPT_DIR))


def train_audio(data_dir: str = None, epochs: int = 15):
    if data_dir is None:
        data_dir = str(PROJECT_ROOT / "data" / "audio")

    data_path = Path(data_dir)
    real_count = len(list((data_path / "REAL").glob("*"))) if (data_path / "REAL").exists() else 0
    fake_count = len(list((data_path / "FAKE").glob("*"))) if (data_path / "FAKE").exists() else 0

    if real_count == 0 or fake_count == 0:
        print(f"ERROR: Dataset not found at {data_dir}")
        print(f"  REAL/ has {real_count} files, FAKE/ has {fake_count} files")
        print()
        print("Expected structure:")
        print(f"  {data_dir}/")
        print(f"  ├── REAL/   ← put real audio files here (.wav, .flac, .mp3, etc.)")
        print(f"  └── FAKE/   ← put fake audio files here")
        print()
        print("Download a dataset:")
        print("  kaggle datasets download -d birdy654/deep-voice-deepfake-voice-recognition")
        return False

    print(f"Audio dataset: {real_count} real, {fake_count} fake")

    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader, random_split
    from tqdm import tqdm
    from ml.audio_model import AudioDeepfakeCNN
    from utils.audio_preprocessing import load_audio, compute_mel_spectrogram, prepare_spectrogram_for_model

    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {DEVICE}")

    class AudioDS(Dataset):
        def __init__(self, data_dir):
            self.samples = []
            audio_exts = {'.WAV', '.FLAC', '.MP3', '.OGG', '.M4A'}
            for label, folder in [(0, "REAL"), (1, "FAKE")]:
                folder_p = Path(data_dir) / folder
                if folder_p.exists():
                    for f in folder_p.iterdir():
                        if f.suffix.upper() in audio_exts:
                            self.samples.append((str(f), label))
            np.random.shuffle(self.samples)

        def __len__(self):
            return len(self.samples)

        def __getitem__(self, idx):
            path, label = self.samples[idx]
            try:
                y, sr = load_audio(path)
                max_len = sr * 5
                if len(y) > max_len:
                    s = np.random.randint(0, len(y) - max_len)
                    y = y[s:s + max_len]
                elif len(y) < sr:
                    y = np.pad(y, (0, sr - len(y)))
                mel = compute_mel_spectrogram(y, sr)
                spec = prepare_spectrogram_for_model(mel)
                return torch.FloatTensor(spec), torch.FloatTensor([label])
            except Exception:
                return torch.zeros(1, 128, 128), torch.FloatTensor([0])

    dataset = AudioDS(data_dir)
    t_size = int(0.8 * len(dataset))
    v_size = len(dataset) - t_size
    train_set, val_set = random_split(dataset, [t_size, v_size])
    train_loader = DataLoader(train_set, batch_size=32, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_set, batch_size=32, shuffle=False, num_workers=0)

    model = AudioDeepfakeCNN().to(DEVICE)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)

    save_path = PROJECT_ROOT / "models" / "audio_deepfake_cnn.pt"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    best_acc = 0.0

    for epoch in range(epochs):
        model.train()
        correct, total = 0, 0
        for specs, labels in tqdm(train_loader, desc=f"Audio {epoch + 1}/{epochs}"):
            specs, labels = specs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            out = model(specs)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()
            correct += ((out > 0.5).float() == labels).sum().item()
            total += labels.numel()

        model.eval()
        vc, vt = 0, 0
        with torch.no_grad():
            for specs, labels in val_loader:
                specs, labels = specs.to(DEVICE), labels.to(DEVICE)
                out = model(specs)
                vc += ((out > 0.5).float() == labels).sum().item()
                vt += labels.numel()
        val_acc = vc / max(vt, 1) * 100
        print(f"  Train={correct / max(total, 1) * 100:.1f}% Val={val_acc:.1f}%")
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), str(save_path))
            print(f"  Saved (best={val_acc:.1f}%)")

    print(f"Audio training done. Best={best_acc:.1f}% → {save_path}")
    return True


def train_video(data_dir: str = None, epochs: int = 10):
    if data_dir is None:
        data_dir = str(PROJECT_ROOT / "data" / "faces" / "real-vs-fake")

    data_path = Path(data_dir)

    # Count images across train / valid / test splits
    def count_images(class_name):
        count = 0
        for split in ["train", "valid", "test"]:
            split_path = data_path / split / class_name
            if split_path.exists():
                count += len(list(split_path.glob("*")))
        return count

    real_count = count_images("real")
    fake_count = count_images("fake")

    if real_count == 0 or fake_count == 0:
        print(f"ERROR: Face crops not found at {data_dir}")
        print(f"  real/ has {real_count} files, fake/ has {fake_count} files")
        print()
        print("Expected structure:")
        print(f"  {data_dir}/")
        print(f"  ├── train/")
        print(f"  │   ├── real/")
        print(f"  │   └── fake/")
        print(f"  ├── valid/")
        print(f"  │   ├── real/")
        print(f"  │   └── fake/")
        print(f"  └── test/")
        print(f"      ├── real/")
        print(f"      └── fake/")
        print()
        print("Download face crops:")
        print("  kaggle datasets download -d xhlulu/140k-real-and-fake-faces")
        return False

    print(f"Video dataset: {real_count} real, {fake_count} fake")

    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader, random_split
    import cv2
    from tqdm import tqdm
    from ml.video_model import VideoDeepfakeDetector
    from utils.video_preprocessing import prepare_face_for_model

    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {DEVICE}")

    class FaceDS(Dataset):
        def __init__(self, data_dir, max_per_class=20000):
            self.samples = []
            exts = {".jpg", ".jpeg", ".png"}
            for label, class_name in [(0, "real"), (1, "fake")]:
                class_count = 0
                for split in ["train", "valid", "test"]:
                    split_path = Path(data_dir) / split / class_name
                    if split_path.exists():
                        files = [f for f in split_path.iterdir() if f.suffix.lower() in exts]
                        remaining = max_per_class - class_count
                        for f in files[:remaining]:
                            self.samples.append((str(f), label))
                        class_count += len(files[:remaining])
                        if class_count >= max_per_class:
                            break
            np.random.shuffle(self.samples)

        def __len__(self):
            return len(self.samples)

        def __getitem__(self, idx):
            path, label = self.samples[idx]
            try:
                img = cv2.imread(path)
                if img is None:
                    raise ValueError()
                img = cv2.resize(img, (224, 224))
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                t = prepare_face_for_model(img_rgb)
                return torch.FloatTensor(t), torch.FloatTensor([label])
            except Exception:
                return torch.zeros(3, 224, 224), torch.FloatTensor([0])

    dataset = FaceDS(data_dir)
    t_size = int(0.8 * len(dataset))
    v_size = len(dataset) - t_size
    train_set, val_set = random_split(dataset, [t_size, v_size])
    train_loader = DataLoader(train_set, batch_size=16, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_set, batch_size=16, shuffle=False, num_workers=0)

    model = VideoDeepfakeDetector(pretrained_backbone=True).to(DEVICE)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)

    save_path = PROJECT_ROOT / "models" / "video_deepfake_detector.pt"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    best_acc = 0.0

    for epoch in range(epochs):
        model.train()
        correct, total = 0, 0
        for faces, labels in tqdm(train_loader, desc=f"Video {epoch + 1}/{epochs}"):
            faces, labels = faces.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            out = model(faces)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()
            correct += ((out > 0.5).float() == labels).sum().item()
            total += labels.numel()

        model.eval()
        vc, vt = 0, 0
        with torch.no_grad():
            for faces, labels in val_loader:
                faces, labels = faces.to(DEVICE), labels.to(DEVICE)
                out = model(faces)
                vc += ((out > 0.5).float() == labels).sum().item()
                vt += labels.numel()
        val_acc = vc / max(vt, 1) * 100
        print(f"  Train={correct / max(total, 1) * 100:.1f}% Val={val_acc:.1f}%")
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), str(save_path))
            print(f"  Saved (best={val_acc:.1f}%)")

    print(f"Video training done. Best={best_acc:.1f}% → {save_path}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-only", action="store_true")
    parser.add_argument("--video-only", action="store_true")
    parser.add_argument("--audio-data", default=None, help="Path to audio data dir (contains REAL/ and FAKE/)")
    parser.add_argument("--video-data", default=None, help="Path to face image data dir (contains train/valid/test/)")
    parser.add_argument("--audio-epochs", type=int, default=15)
    parser.add_argument("--video-epochs", type=int, default=10)
    args = parser.parse_args()

    print(f"Project root: {PROJECT_ROOT}")

    if not args.video_only:
        print("=" * 50)
        print("AUDIO DEEPFAKE MODEL")
        print("=" * 50)
        train_audio(args.audio_data, args.audio_epochs)

    if not args.audio_only:
        print("\n" + "=" * 50)
        print("VIDEO DEEPFAKE MODEL")
        print("=" * 50)
        train_video(args.video_data, args.video_epochs)
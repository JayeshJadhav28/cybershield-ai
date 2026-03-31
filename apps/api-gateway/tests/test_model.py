import sys
import logging
logging.basicConfig(level=logging.INFO)
sys.path.append('e:/cybershield-ai/apps/api-gateway')
from config import settings
settings.UPLOAD_DIR='/tmp/cybershield'
from ml.model_loader import model_loader

m = model_loader.get_video_model()
print("Model type:", type(m))
if hasattr(m, "_m"):
    print("Underlying Keras type:", type(m._m))
    try:
        print("Input shape:", getattr(m._m, "input_shape", "Unknown"))
    except:
        pass
print("Status:", model_loader.status())

import os
import logging
import numpy as np
import tensorflow as tf
from PIL import Image
from scipy.signal import convolve2d
from skimage.color import rgb2yuv, yuv2rgb
from app.config import settings

logger = logging.getLogger(__name__)

CLASS_NAMES = ["Healthy", "RedRot", "RedRust"]

SHARPEN_KERNEL = np.array([
    [0, -1,  0],
    [-1,  5, -1],
    [0, -1,  0]
])


def _apply_convolution(channel, kernel):
    return convolve2d(channel, kernel, mode="same", boundary="fill", fillvalue=0)


def _sharpen_image(image: np.ndarray) -> np.ndarray:
    """
    Matches the sharpening applied during training.
    Must be identical to sugarcane_trainer.py preprocessing.
    """
    img_yuv = rgb2yuv(image)
    img_yuv[:, :, 0] = _apply_convolution(img_yuv[:, :, 0], SHARPEN_KERNEL)
    return yuv2rgb(img_yuv)


def _preprocess_image(image_path: str) -> np.ndarray:
    """Load, resize, sharpen, normalize — matches trainer pipeline exactly."""
    img = Image.open(image_path).convert("RGB")
    img = img.resize((settings.ML_IMAGE_SIZE, settings.ML_IMAGE_SIZE))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = _sharpen_image(img_array)
    img_array = np.clip(img_array, 0.0, 1.0)
    return np.expand_dims(img_array, axis=0)


class SugarcanePredictor:
    """
    Singleton ML model wrapper for sugarcane disease prediction.
    Model loaded once at startup via get_instance().
    Matches exact preprocessing from sugarcane_trainer.py.
    """

    _instance = None

    def __init__(self):
        model_path = settings.ML_MODEL_PATH

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Sugarcane model not found at: {model_path}\n"
                f"Train the model first using sugarcane_trainer.py"
            )

        logger.info(f"Loading sugarcane ML model from: {model_path}")
        self.model = tf.keras.models.load_model(model_path)
        logger.info("Sugarcane ML model loaded successfully")

    @classmethod
    def get_instance(cls) -> "SugarcanePredictor":
        """Singleton — loaded once at startup, reused across all requests."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def predict(self, image_path: str) -> dict:
        """
        Runs inference on a single crop image.
        Returns disease name, confidence score, and all class probabilities.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        image = _preprocess_image(image_path)
        predictions = self.model.predict(image, verbose=0)

        predicted_index = int(np.argmax(predictions))
        confidence = float(np.max(predictions))

        all_probabilities = {
            CLASS_NAMES[i]: round(float(predictions[0][i]), 4)
            for i in range(len(CLASS_NAMES))
        }

        result = {
            "disease": CLASS_NAMES[predicted_index],
            "confidence": round(confidence, 4),
            "all_probabilities": all_probabilities,
            "model_used": "DenseNet201",
        }

        logger.info(
            f"Prediction: {result['disease']} "
            f"confidence: {result['confidence']} "
            f"probabilities: {all_probabilities}"
        )

        return result
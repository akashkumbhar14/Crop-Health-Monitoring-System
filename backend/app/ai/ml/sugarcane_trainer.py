import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from PIL import Image
from scipy.signal import convolve2d
from skimage.color import rgb2yuv, yuv2rgb

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

import tensorflow as tf
from tensorflow.keras.applications import DenseNet201
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2
from tensorflow.keras.utils import to_categorical


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

DATA_DIR = os.path.join(BASE_DIR, "dataset")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "DenseNetSVM_Model.h5")

CLASS_NAMES = ["Healthy", "RedRot", "RedRust"]
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10

SHARPEN_KERNEL = np.array([
    [0, -1,  0],
    [-1,  5, -1],
    [0, -1,  0]
])


def apply_convolution(channel, kernel):
    return convolve2d(channel, kernel, mode="same", boundary="fill", fillvalue=0)


def sharpen_image(image):
    img_yuv = rgb2yuv(image)
    img_yuv[:, :, 0] = apply_convolution(img_yuv[:, :, 0], SHARPEN_KERNEL)
    return yuv2rgb(img_yuv)


def load_dataset():
    data = []
    labels = []

    label_map = {name: idx for idx, name in enumerate(CLASS_NAMES)}

    for class_name in CLASS_NAMES:
        class_path = os.path.join(DATA_DIR, class_name)  # fixed typo

        if not os.path.exists(class_path):
            print(f"Folder not found: {class_path}")
            continue

        for file_name in os.listdir(class_path):
            img_path = os.path.join(class_path, file_name)

            try:
                img = Image.open(img_path).convert("RGB")
                img = img.resize(IMG_SIZE)
                img = np.array(img)
                img = sharpen_image(img)
                img = img / 255.0

                data.append(img)
                labels.append(label_map[class_name])

            except Exception as e:
                print(f"Skipping {img_path}: {e}")

    X = np.array(data)
    y = to_categorical(np.array(labels), num_classes=len(CLASS_NAMES))

    return X, y


def build_model():
    base_model = DenseNet201(
        include_top=False,
        input_shape=(224, 224, 3),
        weights="imagenet",
        pooling="avg"
    )

    base_model.trainable = False

    inputs = Input(shape=(224, 224, 3))
    x = base_model(inputs, training=False)
    x = Dense(256, activation="relu")(x)
    x = Dropout(0.2)(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.2)(x)

    outputs = Dense(
        len(CLASS_NAMES),
        activation="softmax",
        kernel_regularizer=l2(0.01)
    )(x)

    model = Model(inputs, outputs)
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


def train_model():
    print("Loading dataset...")
    X, y = load_dataset()

    print(f"Dataset loaded — X: {X.shape} y: {y.shape}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=np.argmax(y, axis=1)
    )

    augmenter = ImageDataGenerator(
        rotation_range=20,
        zoom_range=0.15,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.15,
        horizontal_flip=True,
        fill_mode="nearest"
    )

    model = build_model()

    history = model.fit(
        augmenter.flow(X_train, y_train, batch_size=BATCH_SIZE),
        validation_data=(X_test, y_test),
        epochs=EPOCHS
    )

    predictions = model.predict(X_test)
    pred_classes = np.argmax(predictions, axis=1)
    true_classes = np.argmax(y_test, axis=1)

    print("\nClassification Report:\n")
    print(classification_report(true_classes, pred_classes, target_names=CLASS_NAMES))

    cm = confusion_matrix(true_classes, pred_classes)

    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

    plt.figure(figsize=(8, 4))
    plt.plot(history.history["accuracy"], label="Train Accuracy")
    plt.plot(history.history["val_accuracy"], label="Validation Accuracy")
    plt.legend()
    plt.title("Accuracy")
    plt.show()

    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save(MODEL_PATH)
    print(f"\nModel saved at: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()
# ==============================================================================
# KAGGLE SCRIPT TO TEST PRETRAINED MODEL ACCURACY
# FIXED FOR: date3k2/vit-real-fake-classification-v4
# ==============================================================================

# !pip install transformers pillow tqdm

import os
from transformers import pipeline
from PIL import Image

# ---------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------
TEST_DIR = "/kaggle/input/datasets/fmartinrguez/atlanttic-uvigo-ai-images-collection/Part02/Part02"

# ---------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------
print("Downloading and loading model...")

pipe = pipeline(
    "image-classification",
    model="haywoodsloan/ai-image-detector-deploy",
    device=0   # GPU
)

print("Model loaded successfully!\n")


def test_personal_images():

    if not os.path.exists(TEST_DIR):
        print(f"Directory {TEST_DIR} not found.")
        return

    print(f"Scanning '{TEST_DIR}' for images...\n")

    images = [
        f for f in os.listdir(TEST_DIR)
        if f.lower().endswith(
            (".png", ".jpg", ".jpeg", ".webp")
        )
    ]

    if not images:
        print("No images found in directory!")
        return

    for img_name in images:

        img_path = os.path.join(TEST_DIR, img_name)

        try:
            img = Image.open(img_path).convert("RGB")

            # Predict
            results = pipe(img)

            top_pred = max(
                results,
                key=lambda x: x["score"]
            )

            pred_label = top_pred["label"].lower()
            confidence = top_pred["score"] * 100

            # Detect fake/AI labels
            is_ai_pred = any(
                word in pred_label
                for word in [
                    "fake",
                    "generated",
                    "artificial",
                    "deepfake",
                    "ai"
                ]
            )

            final_result = (
                "🤖 AI-GENERATED"
                if is_ai_pred
                else "👤 REAL IMAGE"
            )

            print(
                f"Image: {img_name} => "
                f"{final_result} "
                f"(Confidence: {confidence:.2f}%)"
            )

        except Exception as e:
            print(
                f"Image: {img_name} => "
                f"Error reading image: {e}"
            )


if __name__ == "__main__":
    test_personal_images()

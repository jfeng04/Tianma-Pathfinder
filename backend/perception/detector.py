from functools import lru_cache
from pathlib import Path

import torch
from backend.perception.models import Detection
from PIL import Image, ImageDraw
from transformers import (
    AutoModelForZeroShotObjectDetection,
    AutoProcessor,
)


MODEL_ID = "IDEA-Research/grounding-dino-tiny"

def get_device() -> torch.device:
    """
    GPU 为首选，CPU 为后选
    """
    if torch.cuda.is_available():
        return torch.device("cuda")

    if torch.backends.mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")

@lru_cache(maxsize=1)
def get_detector():
    """
    最近最少使用，为了一次启动后，后面不用在创建
    """
    device = get_device()

    print(f"Loading Grounding DINO on {device}...")

    processor = AutoProcessor.from_pretrained(MODEL_ID)

    model = (
        AutoModelForZeroShotObjectDetection
        .from_pretrained(MODEL_ID)
    )

    model = model.to(device)
    model.eval()

    return processor, model, device


def detect_image(
    image: Image.Image,
    text_labels: list[str],
    threshold: float = 0.4,
    text_threshold: float = 0.3,
) -> list[Detection]:

    """
    - 先把图片解码成 RGB 
    - 给图片设标签
    - 使用模型进行判断，inputs 为 Pytorch 张量
    - 模型返回 outputs 值
    - 后处理 （post-processor）返回 boxes、scores、以及 text_labels
    """

    image = image.convert("RGB")

    processor, model, device = get_detector()

    labels_for_model = [
        text_labels
    ]

    inputs = processor(
        images=image,
        text=labels_for_model,
        return_tensors="pt",
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    results = (
        processor.post_process_grounded_object_detection(
            outputs,
            threshold=threshold,
            text_threshold=text_threshold,
            target_sizes=[
                (
                    image.height,
                    image.width,
                )
            ],
        )
    )

    result = results[0]

    detections: list[Detection] = []

    for box, score, label in zip(
        result["boxes"],
        result["scores"],
        result["text_labels"],
    ):
        detections.append(
            Detection(
                label=label,
                confidence=round(
                    score.item(),
                    4,
                ),
                bbox=[
                    round(value, 2)
                    for value in box.tolist()
                ],
            )
        )

    return detections


def detect_objects(
    image_path: str,
    text_labels: list[str],
    threshold: float = 0.4,
    text_threshold: float = 0.3,
) -> list[Detection]:

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {path}"
        )

    image = Image.open(path).convert("RGB")

    return detect_image(
        image=image,
        text_labels=text_labels,
        threshold=threshold,
        text_threshold=text_threshold,
    )

def annotate_pil_image(
    image: Image.Image,
    detections: list[Detection],
    output_path: str,
) -> None:

    annotated = image.copy().convert("RGB")

    draw = ImageDraw.Draw(annotated)

    for detection in detections:
        x1, y1, x2, y2 = detection.bbox

        draw.rectangle(
            [x1, y1, x2, y2],
            outline="red",
            width=4,
        )

        draw.text(
            (
                x1,
                max(0, y1 - 15),
            ),
            (
                f"{detection.label} "
                f"{detection.confidence:.2f}"
            ),
            fill="red",
        )

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    annotated.save(output)

def annotate_image(
    image_path: str,
    detections: list[Detection],
    output_path: str,
) -> None:
    """
    给图片加注释
    """

    image = Image.open(image_path).convert("RGB")

    draw = ImageDraw.Draw(image)

    for detection in detections:
        x1, y1, x2, y2 = detection.bbox

        draw.rectangle(
            [x1, y1, x2, y2],
            outline="red",
            width=4,
        )

        label_text = (
            f"{detection.label} "
            f"{detection.confidence:.2f}"
        )

        draw.text(
            (x1, max(0, y1 - 15)),
            label_text,
            fill="red",
        )

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image.save(output)

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent

    image_path = (
        base_dir
        / "samples"
        / "scene.jpg"
    )

    output_path = (
        base_dir
        / "outputs"
        / "scene_annotated.jpg"
    )

    labels = [
        "a table",
        "a couch",
        "a chair",
    ]

    detections = detect_objects(
        image_path=str(image_path),
        text_labels=labels,
    )

    print("\nDetections:\n")

    for detection in detections:
        print(
            detection.model_dump_json(
                indent=2
            )
        )

    annotate_image(
        image_path=str(image_path),
        detections=detections,
        output_path=str(output_path),
    )

    print(
        f"\nAnnotated image saved to:\n"
        f"{output_path}"
    )
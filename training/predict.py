# -*- coding: utf-8 -*-
"""用训练好的模型对单张图片（或整个目录）做预测。

用法::

    python training/predict.py --source samples/healthy_1.jpg
    python training/predict.py --source samples/
    python training/predict.py --source samples/ --model backend/model/best.pt
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def _ensure_ultralytics() -> None:
    try:
        import ultralytics  # noqa: F401
        return
    except ImportError:
        pass
    third_party = ROOT / "third_party"
    if (third_party / "ultralytics").exists():
        sys.path.insert(0, str(third_party))
        import ultralytics  # noqa: F401


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="豆类叶片病害分类预测")
    parser.add_argument("--model", default=str(ROOT / "backend" / "model" / "best.pt"))
    parser.add_argument("--source", required=True, help="图片路径或图片目录")
    parser.add_argument("--topk", type=int, default=3)
    parser.add_argument("--save", action="store_true", help="把预测结果图片保存到 runs/predict")
    return parser.parse_args()


def collect_images(source: Path) -> list:
    if source.is_file():
        return [source]
    if source.is_dir():
        return sorted(p for p in source.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
    raise SystemExit(f"路径不存在：{source}")


def main() -> None:
    args = parse_args()
    _ensure_ultralytics()
    from ultralytics import YOLO

    model_path = Path(args.model).resolve()
    if not model_path.exists():
        raise SystemExit(f"模型不存在：{model_path}")

    images = collect_images(Path(args.source).resolve())
    if not images:
        raise SystemExit("没有找到图片")

    model = YOLO(str(model_path))
    for image in images:
        result = model.predict(str(image), verbose=False)[0]
        probs = result.probs
        print(f"\n{image.name}")
        for idx, conf in zip(probs.top5[: args.topk], probs.top5conf[: args.topk].tolist()):
            print(f"  {result.names[int(idx)]:<20} {conf * 100:6.2f}%")

    if args.save:
        model.predict([str(p) for p in images], save=True, project=str(ROOT / "runs" / "predict"), name="exp", exist_ok=True)


if __name__ == "__main__":
    main()

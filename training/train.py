# -*- coding: utf-8 -*-
"""训练豆类叶片分类模型（YOLOv8-cls）。

数据目录要求（分类任务用文件夹名作为标签）::

    dataset/
    ├── train/
    │   ├── healthy/
    │   ├── angular_leaf_spot/
    │   └── bean_rust/
    └── val/
        ├── healthy/
        ├── angular_leaf_spot/
        └── bean_rust/

用法::

    python training/train.py                       # 默认读取 dataset/
    python training/train.py --epochs 20 --device cuda
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _ensure_ultralytics() -> None:
    """优先使用已安装的 ultralytics，没有则回退到仓库内置的 third_party。"""
    try:
        import ultralytics  # noqa: F401
        return
    except ImportError:
        pass
    third_party = ROOT / "third_party"
    if (third_party / "ultralytics").exists():
        sys.path.insert(0, str(third_party))
        import ultralytics  # noqa: F401


def check_dataset(data_root: Path) -> list:
    """检查数据集结构，返回类别名列表。"""
    if not data_root.exists():
        raise SystemExit(f"数据集目录不存在：{data_root}\n请参考 dataset/README.md 准备数据。")

    train_dir = data_root / "train"
    val_dir = data_root / "val"
    for split_dir in (train_dir, val_dir):
        if not split_dir.exists():
            raise SystemExit(f"缺少目录：{split_dir}")

    classes = sorted(p.name for p in train_dir.iterdir() if p.is_dir())
    if not classes:
        raise SystemExit(f"{train_dir} 下没有任何类别文件夹")

    val_classes = sorted(p.name for p in val_dir.iterdir() if p.is_dir())
    if set(classes) != set(val_classes):
        raise SystemExit(
            "训练集与验证集的类别文件夹不一致：\n"
            f"  train: {classes}\n  val:   {val_classes}"
        )

    print("类别：", classes)
    for split_dir in (train_dir, val_dir):
        counts = {c: len(list((split_dir / c).glob("*.*"))) for c in classes}
        print(f"  {split_dir.name}: {sum(counts.values())} 张 {counts}")
    return classes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="训练豆类叶片病虫害分类模型")
    parser.add_argument("--data", default=str(ROOT / "dataset"), help="数据集根目录（含 train/val）")
    parser.add_argument("--model", default="yolov8n-cls.pt", help="预训练权重，如 yolov8n-cls.pt / yolov8s-cls.pt")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--imgsz", type=int, default=224)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--device", default="cpu", help="cpu / 0 / 0,1")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--lr0", type=float, default=0.01)
    parser.add_argument("--project", default=str(ROOT / "runs" / "classify"))
    parser.add_argument("--name", default="exp")
    parser.add_argument("--exist-ok", action="store_true", help="允许覆盖同名输出目录")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _ensure_ultralytics()
    from ultralytics import YOLO

    data_root = Path(args.data).resolve()
    check_dataset(data_root)

    model = YOLO(args.model)
    model.train(
        data=str(data_root),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        workers=args.workers,
        project=args.project,
        name=args.name,
        exist_ok=args.exist_ok,
        lr0=args.lr0,
        save_period=5,
    )

    # 训练曲线（不同版本接口略有差异，失败不影响训练结果）
    if getattr(model, "trainer", None):
        try:
            model.trainer.plot_results()
            print(f"训练曲线：{Path(model.trainer.save_dir) / 'results.png'}")
        except Exception as exc:  # noqa: BLE001
            print(f"[提示] 训练曲线绘制失败（不影响权重）：{exc}")

    best = Path(args.project) / args.name / "weights" / "best.pt"
    print(f"训练完成，最佳权重：{best}")

    # 用验证集快速评估
    print("\n在验证集上评估：")
    metrics = YOLO(str(best)).val(data=str(data_root), split="val")
    print(metrics)


if __name__ == "__main__":
    main()

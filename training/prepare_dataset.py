# -*- coding: utf-8 -*-
"""数据集检查与整理工具。

分类任务不需要手工标注：图片所在文件夹名就是标签。
本脚本会检查 train/val 的目录结构、统计各类图片数量、提示数据不均衡，
并生成一份 data.yaml 方便查阅和复用。

用法::

    python training/prepare_dataset.py
    python training/prepare_dataset.py --data <数据集目录>
"""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def count_images(directory: Path) -> int:
    return sum(1 for p in directory.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES)


def main() -> None:
    parser = argparse.ArgumentParser(description="检查豆类叶片数据集结构")
    parser.add_argument("--data", default=str(ROOT / "dataset"))
    parser.add_argument("--write-yaml", action="store_true", help="生成 data.yaml")
    args = parser.parse_args()

    data_root = Path(args.data).resolve()
    train_dir, val_dir = data_root / "train", data_root / "val"

    if not train_dir.is_dir() or not val_dir.is_dir():
        raise SystemExit(
            f"数据集结构不完整：{data_root}\n"
            "请保证存在 train/ 与 val/ 两个子目录，每个子目录下按类别分文件夹。"
        )

    classes = sorted(p.name for p in train_dir.iterdir() if p.is_dir())
    if not classes:
        raise SystemExit(f"{train_dir} 下没有类别文件夹")

    print(f"数据集：{data_root}")
    print(f"类别（{len(classes)}）：{classes}\n")

    print(f"{'类别':<22}{'train':>8}{'val':>8}{'合计':>8}")
    totals = [0, 0]
    for name in classes:
        n_train = count_images(train_dir / name)
        n_val = count_images(val_dir / name)
        totals[0] += n_train
        totals[1] += n_val
        print(f"{name:<22}{n_train:>8}{n_val:>8}{n_train + n_val:>8}")
    print(f"{'合计':<20}{totals[0]:>8}{totals[1]:>8}{sum(totals):>8}")

    # 简单的不均衡检查
    counts = [count_images(train_dir / c) for c in classes]
    if counts and min(counts) * 2 < max(counts):
        print("\n[提示] 各类别图片数量差异较大，建议补充样本或使用类别权重。")

    missing_val = [c for c in classes if not (val_dir / c).is_dir()]
    if missing_val:
        print(f"\n[警告] 验证集缺少以下类别目录：{missing_val}")

    if args.write_yaml:
        yaml_path = data_root / "data.yaml"
        lines = [
            "# 由 training/prepare_dataset.py 生成",
            f"path: {data_root.name}",
            "train: train",
            "val: val",
            f"nc: {len(classes)}",
            "names: [" + ", ".join(f"'{c}'" for c in classes) + "]",
            "",
        ]
        yaml_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n已生成：{yaml_path}")


if __name__ == "__main__":
    main()

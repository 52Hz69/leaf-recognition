# -*- coding: utf-8 -*-
"""环境自检：确认依赖齐备、模型可用。

用法::

    python scripts/check_env.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples" / "healthy_1.jpg"

sys.path.insert(0, str(ROOT / "backend"))


def main() -> int:
    print(f"Python: {sys.version.split()[0]}  ({sys.executable})")

    import config  # backend/config.py

    missing = []
    for module in ("flask", "numpy", "PIL", "torch"):
        try:
            mod = __import__(module)
            print(f"[OK]   {module:<12} {getattr(mod, '__version__', '')}")
        except ImportError:
            missing.append(module)
            print(f"[MISS] {module}")

    # ultralytics 允许回退到仓库内置的 third_party 版本
    try:
        config.ensure_ultralytics()
        import ultralytics

        source = "已安装" if "third_party" not in str(Path(ultralytics.__file__)) else "仓库内置"
        print(f"[OK]   ultralytics  {ultralytics.__version__} ({source})")
    except ImportError as exc:
        missing.append("ultralytics")
        print(f"[MISS] ultralytics  ({exc})")

    if missing:
        print("\n缺少依赖，请执行：pip install -r requirements.txt")
        return 1

    from ultralytics import YOLO

    model_path = ROOT / "backend" / "model" / "best.pt"
    if not model_path.exists():
        print(f"\n[ERROR] 模型不存在：{model_path}")
        return 1

    model = YOLO(str(model_path))
    print(f"\n[OK]   模型加载成功，类别：{list(model.names.values())}")

    if SAMPLE.exists():
        result = model.predict(str(SAMPLE), verbose=False)[0]
        top1 = int(result.probs.top1)
        print(f"[OK]   样例推理：{SAMPLE.name} -> {result.names[top1]} ({float(result.probs.top1conf):.2%})")

    print("\n环境检查通过，可以启动后端：python backend/app.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

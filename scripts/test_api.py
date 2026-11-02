# -*- coding: utf-8 -*-
"""接口冒烟测试：把 samples/ 里的样例图片发给本地后端，验证服务是否正常。

先启动后端，再执行::

    python scripts/test_api.py
    python scripts/test_api.py --url http://192.168.1.10:5000
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="后端接口冒烟测试")
    parser.add_argument("--url", default="http://127.0.0.1:5000", help="后端地址")
    parser.add_argument("--image", default=str(ROOT / "samples" / "bean_rust_1.jpg"))
    args = parser.parse_args()

    try:
        import requests
    except ImportError:
        print("需要先安装 requests：pip install requests")
        return 1

    base = args.url.rstrip("/")
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"样例图片不存在：{image_path}")
        return 1

    try:
        health = requests.get(f"{base}/health", timeout=5).json()
        print("GET /health ->", json.dumps(health, ensure_ascii=False))
    except Exception as exc:  # noqa: BLE001
        print(f"无法连接后端：{exc}\n请确认已启动 python backend/app.py")
        return 1

    with image_path.open("rb") as fh:
        response = requests.post(
            f"{base}/predict",
            files={"file": (image_path.name, fh, "image/jpeg")},
            data={"confidence": 0.5},
            timeout=30,
        )

    print(f"POST /predict ({image_path.name}) -> HTTP {response.status_code}")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    return 0 if response.ok else 1


if __name__ == "__main__":
    sys.exit(main())

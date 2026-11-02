# -*- coding: utf-8 -*-
"""后端配置。

所有可变项都支持通过环境变量覆盖，代码里不写死本机路径、内网地址等信息。
"""

import os
import sys
from pathlib import Path

# 目录结构：<项目根>/backend/config.py
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
THIRD_PARTY_DIR = PROJECT_ROOT / "third_party"

# ---------- 模型 ----------
# 默认使用仓库自带的训练好的模型，可通过 BLD_MODEL_PATH 指定其他权重
MODEL_PATH = Path(os.getenv("BLD_MODEL_PATH", str(BACKEND_DIR / "model" / "best.pt")))

# ---------- 服务 ----------
# 0.0.0.0 表示允许同一局域网内的手机访问；只在本机调试可改成 127.0.0.1
HOST = os.getenv("BLD_HOST", "0.0.0.0")
PORT = int(os.getenv("BLD_PORT", "5000"))
DEBUG = os.getenv("BLD_DEBUG", "0").lower() in ("1", "true", "yes")
# 单张图片最大体积（MB）
MAX_UPLOAD_MB = int(os.getenv("BLD_MAX_UPLOAD_MB", "16"))

# ---------- 识别 ----------
# 返回前 K 个类别及概率
TOP_K = int(os.getenv("BLD_TOP_K", "5"))
# 低于该置信度时给出提示（分类模型仍会返回概率最高的类别）
CONF_THRESHOLD = float(os.getenv("BLD_CONF_THRESHOLD", "0.5"))

# ---------- 类别中文名 ----------
CLASS_NAME_ZH = {
    "healthy": "健康",
    "angular_leaf_spot": "角斑病",
    "bean_rust": "豆锈病",
}


def ensure_ultralytics() -> None:
    """让 `import ultralytics` 可用。

    优先使用环境中已安装的 ultralytics；如果没有安装，则回退到仓库内置的
    third_party/ultralytics（便于离线运行）。
    """
    try:
        import ultralytics  # noqa: F401
        return
    except ImportError:
        pass

    vendored = THIRD_PARTY_DIR / "ultralytics"
    if not vendored.exists():
        raise ImportError(
            "未找到 ultralytics。请执行 `pip install -r requirements.txt`，"
            "或确认 third_party/ultralytics 目录存在。"
        )

    path = str(THIRD_PARTY_DIR)
    if path not in sys.path:
        sys.path.insert(0, path)
    import ultralytics  # noqa: F401

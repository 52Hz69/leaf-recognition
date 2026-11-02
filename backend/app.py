# -*- coding: utf-8 -*-
"""豆类作物叶片病虫害识别系统 —— Flask 后端。

启动方式::

    python backend/app.py

接口一览::

    GET  /           服务信息
    GET  /health     健康检查（模型是否加载、运行设备）
    GET  /classes    支持的病虫害类别
    POST /predict    上传图片进行识别

/predict 支持三种请求方式：
    1. multipart/form-data，字段名 file（或 image）
    2. application/json，{"image": "data:image/jpeg;base64,..."} 
    3. 请求体直接放图片二进制
"""

import base64
import io
import time
from pathlib import Path

from flask import Flask, jsonify, request
from PIL import Image

import config

config.ensure_ultralytics()

import torch  # noqa: E402  (需要先确保 ultralytics 可用)
from ultralytics import YOLO  # noqa: E402

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_MB * 1024 * 1024
# 返回 JSON 时保留中文，不转成 \uXXXX
app.json.ensure_ascii = False

# 运行期状态：模型、类别名、推理设备
_state = {
    "model": None,
    "names": [],
    "device": "cpu",
    "error": None,
    "load_seconds": None,
}


def load_model() -> None:
    """加载分类模型。失败时记录错误信息，由 /health 反馈，不直接中断服务。"""
    started = time.time()
    try:
        if not config.MODEL_PATH.exists():
            raise FileNotFoundError(f"模型文件不存在：{config.MODEL_PATH}")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = YOLO(str(config.MODEL_PATH))
        # YOLO 对象不一定实现 .to()，推理时把 device 传给 predict 即可
        if hasattr(model, "to"):
            model.to(device)
        model.eval()

        _state.update(
            model=model,
            names=list(model.names.values()) if isinstance(model.names, dict) else list(model.names),
            device=device,
            error=None,
            load_seconds=round(time.time() - started, 2),
        )
        print(f"[OK] 模型加载完成：{config.MODEL_PATH.name}，设备：{device}，类别：{_state['names']}")
    except Exception as exc:  # noqa: BLE001 - 需要把错误暴露到 /health
        _state.update(error=str(exc))
        print(f"[ERROR] 模型加载失败：{exc}")


def _display_name(raw: str) -> str:
    return config.CLASS_NAME_ZH.get(raw, raw)


def _read_image() -> Image.Image:
    """从请求中取出一张图片（支持文件上传 / JSON base64 / 原始二进制）。"""
    if request.mimetype == "application/json":
        payload = request.get_json(silent=True) or {}
        data = payload.get("image")
        if not data:
            raise ValueError("JSON 请求体中缺少 image 字段（base64 字符串）")
        if "," in data and data.lstrip().lower().startswith("data:"):
            data = data.split(",", 1)[1]
        return Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")

    upload = request.files.get("file") or request.files.get("image")
    if upload is not None and upload.filename:
        return Image.open(io.BytesIO(upload.read())).convert("RGB")

    raw = request.get_data(cache=False)
    if raw:
        return Image.open(io.BytesIO(raw)).convert("RGB")

    raise ValueError("没有收到图片：请用 file 字段上传，或在 JSON 中提供 base64 的 image")


@app.after_request
def _allow_cross_origin(response):
    # 方便用浏览器 / 其他客户端直接调试接口
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "name": "豆类作物叶片病虫害识别系统",
            "version": "1.0.0",
            "model_loaded": _state["model"] is not None,
            "endpoints": ["/health", "/classes", "/predict"],
        }
    )


@app.route("/health", methods=["GET"])
def health():
    ok = _state["model"] is not None
    return (
        jsonify(
            {
                "status": "healthy" if ok else "unavailable",
                "model_loaded": ok,
                "model_path": config.MODEL_PATH.name,
                "device": _state["device"],
                "classes": _state["names"],
                "load_seconds": _state["load_seconds"],
                "error": _state["error"],
            }
        ),
        200 if ok else 503,
    )


@app.route("/classes", methods=["GET"])
def classes():
    return jsonify(
        {
            "classes": _state["names"],
            "classes_zh": [_display_name(name) for name in _state["names"]],
            "count": len(_state["names"]),
        }
    )


@app.route("/predict", methods=["POST", "OPTIONS"])
def predict():
    if request.method == "OPTIONS":
        return ("", 204)

    if _state["model"] is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "模型尚未加载成功",
                    "detail": _state["error"],
                }
            ),
            503,
        )

    try:
        image = _read_image()
    except (ValueError, base64.binascii.Error) as exc:  # type: ignore[attr-defined]
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001 - 图片解码失败
        return jsonify({"success": False, "error": f"图片解析失败：{exc}"}), 400

    try:
        started = time.time()
        results = _state["model"].predict(image, device=_state["device"], verbose=False)
        probs = results[0].probs
        if probs is None:
            return jsonify({"success": False, "error": "模型没有返回分类概率"}), 500

        names = _state["names"]
        top_k = max(1, min(config.TOP_K, len(names)))
        indices = [int(i) for i in probs.top5[:top_k]]
        confidences = [float(c) for c in probs.top5conf[:top_k].tolist()]

        predictions = []
        for class_id, confidence in zip(indices, confidences):
            raw = names[class_id] if class_id < len(names) else str(class_id)
            predictions.append(
                {
                    "class_id": class_id,
                    "raw_class": raw,
                    "class_name": _display_name(raw),
                    "confidence": round(confidence, 4),
                }
            )

        top1 = predictions[0]
        response = {
            "success": True,
            # 兼容旧版小程序：detections 只放最优结果
            "count": 1,
            "detections": [top1],
            "predictions": predictions,
            "low_confidence": top1["confidence"] < config.CONF_THRESHOLD,
            "image_size": {"width": image.width, "height": image.height},
            "elapsed_ms": round((time.time() - started) * 1000, 1),
        }
        return jsonify(response)

    except Exception as exc:  # noqa: BLE001 - 推理异常
        app.logger.exception("推理失败")
        return jsonify({"success": False, "error": f"识别失败：{exc}"}), 500


@app.errorhandler(413)
def _too_large(_):
    return (
        jsonify(
            {
                "success": False,
                "error": f"图片超过大小限制（{config.MAX_UPLOAD_MB} MB）",
            }
        ),
        413,
    )


# 模块导入时即加载模型，方便用 gunicorn / flask run 等方式启动
load_model()


if __name__ == "__main__":
    # use_reloader 关闭，避免重复加载模型
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        threaded=True,
        use_reloader=False,
    )

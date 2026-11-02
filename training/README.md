# 训练与预测

依赖安装：`pip install -r requirements.txt`（在项目根目录执行）。

## 1. 检查数据集

```bash
python training/prepare_dataset.py
```

输出各类别图片数量，检查 `train/`、`val/` 结构是否一致；加 `--write-yaml` 会生成 `dataset/data.yaml`。

## 2. 训练

```bash
python training/train.py                          # 默认 10 轮，CPU
python training/train.py --epochs 30 --device cuda
python training/train.py --model yolov8s-cls.pt --imgsz 256 --batch 64
```

主要参数：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--data` | `dataset/` | 数据集根目录（含 train/val） |
| `--model` | `yolov8n-cls.pt` | 预训练权重，首次运行会自动下载 |
| `--epochs` | 10 | 训练轮数 |
| `--imgsz` | 224 | 输入尺寸 |
| `--batch` | 32 | 批大小 |
| `--device` | cpu | `cpu` / `0` / `0,1` |
| `--project` / `--name` | `runs/classify` / `exp` | 输出目录 |

训练结束后：

- 最优权重：`runs/classify/exp/weights/best.pt`
- 训练曲线：`runs/classify/exp/results.png`
- 混淆矩阵：`runs/classify/exp/confusion_matrix.png`

替换线上模型：把 `best.pt` 复制到 `backend/model/best.pt`。

## 3. 命令行预测

```bash
python training/predict.py --source samples/healthy_1.jpg
python training/predict.py --source samples/ --topk 3
```

输出每个文件概率最高的前几个类别，便于在写前端之前先验证模型效果。

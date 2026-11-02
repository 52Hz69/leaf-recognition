# 数据集说明

## 目录结构

训练脚本使用 YOLOv8 的图像分类任务，**文件夹名就是类别标签**，不需要手工标注：

```
dataset/
├── train/
│   ├── healthy/            # 健康叶片
│   ├── angular_leaf_spot/  # 角斑病
│   └── bean_rust/          # 豆锈病
├── val/
│   ├── healthy/
│   ├── angular_leaf_spot/
│   └── bean_rust/
└── data.yaml               # 由 training/prepare_dataset.py 生成（可选）
```

## 当前使用的数据规模

| 类别 | train | val |
| --- | --- | --- |
| healthy | 342 | 44 |
| angular_leaf_spot | 345 | 44 |
| bean_rust | 348 | 45 |
| **合计** | **1035** | **133** |

## 为什么仓库里没有图片

原始图片约 150 MB、1000 多张，提交到 Git 会让仓库变得非常大（克隆慢、部分平台有单仓库体积限制），
因此这里只保留目录结构说明。图片也可能带有拍摄设备、地点等元信息，不建议直接公开。

## 如何准备数据

1. 获取公开的豆类叶片病害数据集（如 Kaggle 上的 *Bean Disease Dataset*，包含 health / angular leaf spot / bean rust 三类）；
2. 按上面的目录结构放入 `train/`、`val/`（划分比例约 8:1 即可）；
3. 检查结构并统计：

   ```bash
   python training/prepare_dataset.py
   ```

4. 开始训练：

   ```bash
   python training/train.py --device cuda
   ```

`val/` 可以直接从 `train/` 中按类别分层抽样得到，避免同一片叶子同时出现在训练集和验证集里。

## 演示图片

`samples/` 中保留了 6 张验证集图片（每类 2 张），用于快速验证后端与小程序是否正常。

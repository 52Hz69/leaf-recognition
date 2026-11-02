# 豆类作物叶片病虫害识别系统

基于 **YOLOv8 图像分类 + Flask + 微信小程序** 的豆类作物叶片病害识别系统。
用户在手机小程序里拍照或选图，图片上传到本地 Flask 服务，模型返回病害类别与置信度。

支持 3 个类别：

| 类别标签 | 中文名 | 说明 |
| --- | --- | --- |
| `healthy` | 健康 | 叶片正常 |
| `angular_leaf_spot` | 角斑病 | 角斑病（Angular Leaf Spot） |
| `bean_rust` | 豆锈病 | 豆锈病（Bean Rust） |

在验证集（133 张）上，模型 top-1 准确率约 **98.5%**，top-5 准确率 100%。

---

## 目录结构

```
豆类作物叶片病虫害识别系统/
├── backend/                 # Flask 后端
│   ├── app.py               # 接口实现（预测 / 健康检查 / 类别列表）
│   ├── config.py            # 配置（模型路径、端口、类别中文名等）
│   └── model/best.pt        # 训练好的分类模型
├── miniprogram/             # 微信小程序端（微信开发者工具导入此目录）
│   ├── project.config.json
│   ├── tsconfig.json
│   └── miniprogram/
│       ├── pages/index/     # 识别主页
│       └── utils/config.ts  # 后端地址配置
├── training/                # 训练与本地预测脚本
│   ├── train.py             # 训练分类模型
│   ├── predict.py           # 命令行预测
│   └── prepare_dataset.py   # 数据集检查 / 生成 data.yaml
├── dataset/                 # 数据集目录（原始图片不入库，见其 README）
├── samples/                 # 6 张样例叶片图片，用于快速验证
├── scripts/                 # 环境自检、接口测试、一键启动
├── third_party/ultralytics/ # 内置 ultralytics（离线可用，详见第三方声明）
├── requirements.txt
└── README.md
```

---

## 环境要求

- **Python 3.9 ~ 3.12**（本项目在 Python 3.9 下验证通过）
- 微信开发者工具（小程序端）
- 依赖：Flask、PyTorch、ultralytics、Pillow 等，见 `requirements.txt`
- CPU 即可运行（单张图片推理约几十毫秒）；有 NVIDIA 显卡会自动使用 CUDA

---

## 快速开始

### 1. 启动后端

```bash
pip install -r requirements.txt
python backend/app.py
```

看到下面这行说明模型加载成功：

```
[OK] 模型加载完成：best.pt，设备：cpu，类别：['healthy', 'angular_leaf_spot', 'bean_rust']
```

浏览器打开 <http://127.0.0.1:5000/health> 应返回 `"status": "healthy"`。

Windows 下也可以直接双击 `scripts/start_backend.bat` 启动（会自动检查并安装依赖）。

**验证是否正常：**

```bash
python scripts/check_env.py     # 检查依赖、模型、样例推理
python scripts/test_api.py      # 启动服务后，请求 /predict 做冒烟测试
```

### 2. 运行小程序

1. 打开微信开发者工具 →「导入项目」→ 目录选择本仓库的 `miniprogram/`；
2. AppID 选择「测试号」（项目配置里是占位符 `touristappid`，正式使用请换成自己的 AppID）；
3. 右上角「详情 → 本地设置」勾选 **不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书**；
4. 点击「选择图片」选择 `samples/` 里的图片，再点「开始识别」，即可看到类别和置信度。

**真机调试时**：手机和电脑需连同一个 Wi-Fi，把后端地址从 `127.0.0.1` 改成电脑的局域网 IP（`ipconfig` 查看 IPv4 地址），有两种方式任选其一：

- 修改 `miniprogram/miniprogram/utils/config.ts` 里的 `DEFAULT_API_BASE_URL`；
- 或者在开发者工具 Console 执行 `wx.setStorageSync('apiBaseUrl', 'http://192.168.x.x:5000')`，无需改代码。

同时需要在 Windows 防火墙中放行 5000 端口，否则手机访问会被拦截。

### 3. 重新训练（可选）

数据集按「文件夹名 = 类别」组织：

```
dataset/
├── train/{healthy, angular_leaf_spot, bean_rust}/
└── val/{healthy, angular_leaf_spot, bean_rust}/
```

```bash
python training/prepare_dataset.py     # 检查结构、统计数量、生成 data.yaml
python training/train.py --device cuda # 训练，权重输出到 runs/classify/exp/weights/
python training/predict.py --source samples/ --topk 3
```

训练完成后把 `runs/classify/exp/weights/best.pt` 复制到 `backend/model/best.pt` 即可替换线上模型。

---

## 接口说明

### `GET /health`

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "best.pt",
  "device": "cpu",
  "classes": ["healthy", "angular_leaf_spot", "bean_rust"],
  "load_seconds": 1.8
}
```

模型未加载时返回 HTTP 503，并在 `error` 字段说明原因。

### `GET /classes`

```json
{ "classes": ["healthy", "angular_leaf_spot", "bean_rust"],
  "classes_zh": ["健康", "角斑病", "豆锈病"], "count": 3 }
```

### `POST /predict`

支持三种提交方式：

1. `multipart/form-data`，字段名 `file`（或 `image`）；
2. `application/json`，`{"image": "data:image/jpeg;base64,..."}`；
3. 请求体直接放图片二进制。

返回示例：

```json
{
  "success": true,
  "count": 1,
  "detections": [
    { "class_id": 2, "raw_class": "bean_rust", "class_name": "豆锈病", "confidence": 0.9871 }
  ],
  "predictions": [
    { "class_id": 2, "raw_class": "bean_rust",  "class_name": "豆锈病", "confidence": 0.9871 },
    { "class_id": 1, "raw_class": "angular_leaf_spot", "class_name": "角斑病", "confidence": 0.0092 }
  ],
  "low_confidence": false,
  "image_size": { "width": 800, "height": 600 },
  "elapsed_ms": 42.3
}
```

`detections` 只包含最优结果，保持与旧版小程序兼容；`predictions` 按概率从高到低返回前 `BLD_TOP_K` 个类别。

---

## 配置项

后端全部配置都可用环境变量覆盖，代码中不写死任何本机信息：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `BLD_HOST` | `0.0.0.0` | 监听地址，`0.0.0.0` 允许局域网访问 |
| `BLD_PORT` | `5000` | 监听端口 |
| `BLD_DEBUG` | `0` | 设为 `1` 开启 Flask 调试模式 |
| `BLD_MODEL_PATH` | `backend/model/best.pt` | 模型权重路径 |
| `BLD_TOP_K` | `5` | 返回概率最高的前 K 类 |
| `BLD_CONF_THRESHOLD` | `0.5` | 低于该置信度时返回 `low_confidence: true` |
| `BLD_MAX_UPLOAD_MB` | `16` | 单张图片大小上限（MB） |

例如换端口：`set BLD_PORT=8080 && python backend/app.py`（PowerShell 用 `$env:BLD_PORT=8080`）。

---

## 数据集

- 类别：健康 / 角斑病 / 豆锈病，训练集 1035 张、验证集 133 张；
- 原始图片体积较大（约 150 MB），**未提交到本仓库**，避免仓库臃肿；
- 目录结构与获取方式见 [`dataset/README.md`](dataset/README.md)；
- `samples/` 中保留了 6 张验证集图片，可直接用于功能演示。

---

## 关于个人信息的处理

整理代码时对可能泄露个人或环境信息的点做了处理，上传到代码托管平台前可以放心：

| 项目 | 处理方式 |
| --- | --- |
| 本机绝对路径（`C:\...\项目目录\...`） | 全部改为基于 `__file__` 的相对路径，或通过环境变量指定 |
| 局域网/公网 IP（`http://192.168.x.x:5000`） | 小程序中统一改为 `127.0.0.1:5000`，可在 `utils/config.ts` 或运行时修改 |
| 小程序 AppID | 替换为占位符 `touristappid`，请填写自己的 AppID |
| 模型权重中的训练路径 | 已把 `train_args` 里的本机数据路径改写为相对路径 `dataset` |
| `.idea/`、`__pycache__`、`*.cache`、`project.private.config.json` | 已删除，并写入 `.gitignore` |
| 数据集中的原始图片 | 未提交（图片可能含拍摄地点等元信息） |

上传前建议再自查一遍：`自己的姓名 / 学号 / 邮箱 / 服务器 IP / 密钥`，这些内容本项目代码中均不包含。

---

## 常见问题

**Q：`pip install` 很慢或失败？**
换国内镜像：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`。
PyTorch 体积较大，可按 <https://pytorch.org/get-started/locally/> 选择 CPU/CUDA 版本单独安装。

**Q：提示 `ModuleNotFoundError: No module named 'dateutil'` / `pandas`？**
说明当前 Python 环境缺少 ultralytics 的间接依赖，执行 `pip install -r requirements.txt` 补全即可（PyCharm 项目请确认解释器选对了）。

**Q：端口被占用？**
`set BLD_PORT=5001 && python backend/app.py` 换端口，小程序里同步修改地址。

**Q：手机请求失败？**
① 手机与电脑同一局域网；② 地址填电脑 IPv4 而非 `127.0.0.1`；③ 防火墙放行端口；④ 开发者工具中已勾选「不校验合法域名」。

**Q：识别结果总是同一个类别？**
确认上传的是清晰的单张叶片照片；模型仅支持上表中的 3 个类别。

---

## 第三方组件

- [ultralytics](https://github.com/ultralytics/ultralytics) 8.3.63 —— AGPL-3.0，本项目在 `third_party/` 内置了一份以便离线运行，详见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。如果已 `pip install ultralytics`，程序会优先使用环境中安装的版本。

## 许可证

仓库暂未附带开源许可证。上传到 GitHub / Gitee 前可按需添加 `LICENSE`（例如 MIT），或保持「保留所有权利」。注意内置的 ultralytics 为 AGPL-3.0 协议，分发时需遵守其条款。

# 第三方组件声明

## ultralytics

- 版本：8.3.63
- 许可证：AGPL-3.0（<https://github.com/ultralytics/ultralytics/blob/main/LICENSE>）
- 项目主页：<https://github.com/ultralytics/ultralytics>
- 本仓库位置：`third_party/ultralytics/`

本仓库内置了一份 ultralytics 源码，目的是让项目在没有网络、未安装该库的机器上也能直接运行
（`backend/config.py` 会优先使用环境中已安装的版本，找不到时回退到 `third_party/`）。

该目录属于第三方代码，版权归 Ultralytics 所有，未做修改。使用、修改或再分发本项目时，
请同时遵守 AGPL-3.0 协议；如果不需要离线运行，可以删除该目录，改为：

```bash
pip install ultralytics
```

其他依赖（Flask、PyTorch、Pillow、NumPy 等）的许可证请参考各自项目的声明。

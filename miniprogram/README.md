# 微信小程序端

使用微信开发者工具导入**本目录**（`miniprogram/`，即包含 `project.config.json` 的这一层）。

## 导入步骤

1. 微信开发者工具 → 导入项目 → 目录选择本文件夹；
2. AppID 填自己的，或选「测试号」（`project.config.json` 里默认是占位符 `touristappid`）；
3. 「详情 → 本地设置」勾选 **不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书**；
4. 确保后端已启动（`python backend/app.py`），点击「选择图片」→「开始识别」。

## 修改后端地址

后端地址集中在 `miniprogram/miniprogram/utils/config.ts`（即本目录下 `miniprogram/utils/config.ts`）：

```ts
export const DEFAULT_API_BASE_URL = 'http://127.0.0.1:5000'
```

- 开发者工具模拟器：保持 `127.0.0.1` 即可；
- 真机预览：改成电脑的局域网 IP（`ipconfig` 查看 IPv4，例如 `http://192.168.1.10:5000`），手机与电脑连同一 Wi-Fi；
- 也可以不改代码，在 Console 执行：

  ```js
  wx.setStorageSync('apiBaseUrl', 'http://192.168.1.10:5000')
  ```

  清除：`wx.removeStorageSync('apiBaseUrl')`。

## 页面逻辑

| 文件 | 作用 |
| --- | --- |
| `pages/index/index.ts` | 选图（`wx.chooseMedia`）、上传识别（`wx.uploadFile` 请求 `/predict`）、结果处理 |
| `pages/index/index.wxml` | 界面结构：标题、选图按钮、图片预览、识别结果卡片 |
| `pages/index/index.less` | 样式 |
| `utils/config.ts` | 后端地址配置 |

上传字段为 `file`，返回的 `predictions` 数组按置信度从高到低排列，页面展示每个类别及其概率。

## 注意

- 小程序正式发布要求后端使用 **HTTPS** 并在微信后台配置合法域名；本地调试阶段勾选「不校验合法域名」即可。
- 若真机提示「网络请求失败」，依次检查：手机与电脑是否同一网段、防火墙是否放行 5000 端口、地址是否用了电脑 IP。

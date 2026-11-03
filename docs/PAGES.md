# GitHub Pages · NOVA 网页体验

NOVA 的 Pages 入口在本仓库的 `docs/index.html`，仅使用相对路径，适配项目仓库的子路径 `/NOVA/`。

## 启用发布（仅需仓库管理员操作一次）

1. 进入 [NOVA → Settings → Pages](https://github.com/RanchoTao/NOVA/settings/pages)。
2. 在 **Build and deployment** 中选择 **Deploy from a branch**。
3. Branch 选 **main**；目录选 **/docs**；保存。
4. 等待 Pages 部署完成后，访问 <https://ranchotao.github.io/NOVA/>。

如果网页显示 404，先确认 Pages 配置是 `main /docs`，再在仓库 Actions 中查看最新的 `pages build and deployment` 状态。直接打开 `index.html` 文件不等价于浏览器通过 HTTP 访问，因为假设目录需要 `fetch('./seeds.json')`。

## 本地预览

无需安装 Node 或 Python 项目依赖，在仓库根目录执行：

```bash
python -m http.server 8765 --directory docs
```

浏览器打开 <http://127.0.0.1:8765/>。

静态版支持领域/算子筛选、随机组合、随机种子、收藏（浏览器本地存储）、概念卡片、离线预审清单、JSON 导出。**它不会调用 LLM、不做实时文献查新、不执行实验。**

## 隐私与安全

- 所有概念组合在当前浏览器完成；假设目录和 JS 文件来自公开仓库。
- 收藏信息仅存储在该浏览器的 `localStorage` 中；用户清理站点数据会丢失。
- 不支持在 Pages 中输入服务端 API key。公开浏览器里保存模型密钥会泄露，真实模型模式请运行本地 NOVA 服务或另行部署具备认证与后端密钥管理的服务。
- 导出的 `nova.ranchoresearch_handoff` 仅是未审计提案，不授权 RanchoControl/RanchoResearch 自动执行。

## 开发与检查

```bash
node --test tests/site.test.mjs
python -m unittest discover -s tests -v
```

GitHub Actions 的 `static-site` job 也会对前端引擎和相对路径做离线检查。

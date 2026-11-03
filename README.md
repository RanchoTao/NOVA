# NOVA · 震撼首发！INNOVATION!

> **Think the unthinkable. Test the simplest. Prove the unexpected.**
>
> NOVA is an assumption-breaking *scientific imagination engine*: it generates testable challenges to default research assumptions, not incremental paper-title combinations.

**状态：v0.1 research prototype / 科研构想原型。** 已提供真实可运行的离线结构引擎、可选的 OpenAI-compatible 模型合成、批量研究卡片、初步反驳、只读 RanchoResearch 交接提案、localhost UI 和自动测试。**没有**论文查新后端、真正的实验执行器或已经证明具有原创性的科研成果。模型的生成质量尚未完成基准评测。

## 网页版 · GitHub Pages

NOVA 的**零部署后端、可直接体验**的浏览器演示已经放在 [`docs/index.html`](docs/index.html)。管理员在仓库 [Settings → Pages](https://github.com/RanchoTao/NOVA/settings/pages) 选择 **Deploy from a branch → main → /docs** 后，网站地址为 **https://ranchotao.github.io/NOVA/**。

网页支持科研老虎机、领域及算子筛选、随机种子、收藏、离线质疑、导出 JSON 和研究交接提案。**网页版仅为离线结构化概念生成**，不调用大模型或进行真正的论文查新。模型密钥不会放进公开网页。操作指南：[docs/PAGES.md](docs/PAGES.md)。

## 快速开始

需要 Python 3.10+；基础功能仅用 Python 标准库。

```bash
git clone https://github.com/RanchoTao/NOVA.git
cd NOVA
python -m pip install -e .
nova roll --count 3 --seed 42 --out ideas.json
nova challenge ideas.json --idea-id NOVA-替换为实际ID --out review.json
nova handoff ideas.json --idea-id NOVA-替换为实际ID --out handoff.json
nova serve --port 8765
```

打开 http://127.0.0.1:8765/ ，点击「震撼首发！」使用本地老虎机。输入已有文件执行 `challenge` 或 `handoff` 时，如果批次包含多张卡片，必须用 `--idea-id` 指明一张。

查看全部假设和算子：

```bash
nova catalog
nova roll --count 2 --domain stochastic-dynamics --operator causal_inverter
python -m unittest discover -s tests -v
```

默认 `--provider template` 是**离线结构示范**：它根据人工维护的假设目录和转换算子生成问题，并不具备创造性语义推理能力。**不能把离线卡片的文字当作智能体独立提出的原创发现。**

## 使用真实大模型进行假设合成（显式启用）

可选任何兼容 Chat Completions JSON 文本输出的 API。API 密钥只放在本地环境变量，不提交到仓库，也不会发送给浏览器前端。

```bash
export NOVA_API_KEY="<your-key>"
export NOVA_MODEL="<your-model-id>"
export NOVA_BASE_URL="https://api.openai.com/v1"
nova roll --provider model --count 3 --seed 42 --out model_ideas.json
nova challenge model_ideas.json --idea-id NOVA-替换为实际ID --provider model
nova serve --provider model --port 8765
```

Windows PowerShell 示例：

```powershell
$env:NOVA_API_KEY = '<your-key>'
$env:NOVA_MODEL = '<your-model-id>'
$env:NOVA_BASE_URL = 'https://api.openai.com/v1'
nova roll --provider model --count 3
```

此模式会调用实际第三方 API，可能产生费用；响应必须是可解析 JSON，提供商可能有输出格式差异。默认无自动重试、无计划任务、无 GPU 执行。`--seed` 固定的是结构化组合选择，**不能**保证大模型回复可复现。模型调用只接收当前种子和操作算子，不会自动读取私有论文或科研仓库。

## NOVA 的六种破坏算子

| Operator | 打破什么 |
| --- | --- |
| `necessity_breaker` | 取消默认必要条件 |
| `object_switcher` | 直接操作过去只能间接优化的对象 |
| `causal_inverter` | 重新解释失败的因果机制 |
| `representation_hacker` | 改变问题所在的表示空间 |
| `capability_arbitrage` | 用新出现的能力挑战过时假设 |
| `anomaly_amplifier` | 把失败和反常结果变成科学问题 |

研究卡片必须有：核心问题、候选机制、惊喜来源、最小可证伪实验、合理基线、明确否证条件与混杂因素。科学状态恒为 `IDEA`，原创性恒为 `UNCHECKED`；模型不能直接升格为原创发现。

## 与 RanchoResearch 的分工

```text
NOVA: 默认假设 -> 概念变换 -> 可证伪构想 -> 怀疑者初审
  |
  v  handoff JSON（不自动执行）
RanchoControl: 任务身份、授权、状态与收据
  |
  v  独立复核和实际预算批准后
RanchoResearch: 最近邻查新 -> 证据门禁 -> 最小真实实验 -> 论文
```

`nova handoff` 输出的是**惰性交接提案**，不是 RanchoControl 的 `READY` 任务，也不会自动创建 Issue、申请云 GPU、修改历史结论或投稿。接收端仍需适配实际协议、独立审计和确认执行许可。

## 为什么不是纯随机科研老虎机？

可视化「摇题」只负责让人跳出默认搜索空间。真正的核心是假设清单、操作算子、多样性选择、语义综合、反证设计、近邻查新和真实实验。v0.1 的语义综合需要显式启动 LLM；novelty 检索与实验尚未实现。我们不把模型主观的“震撼评分”当科学质量。

参见 [架构](docs/ARCHITECTURE.md)、[科研契约](docs/SCIENTIFIC_CONTRACT.md)、[RanchoResearch 接口](docs/INTEGRATION.md) 与 [里程碑](docs/ROADMAP.md)。

## 许可证

暂未选择发布许可证；仓库可见并不等于自动授予复用授权。请由仓库所有者决定开源许可证后再正式发行。

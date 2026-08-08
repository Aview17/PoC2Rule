# PoC2Rule Agent

将 PoC（Proof of Concept）自动转换为检测规则（Snort / Suricata）。

## 输入

支持三种输入形式：

| 方式 | 示例 |
|------|------|
| Python PoC 文件 | `python main.py -p poc.py` |
| HTTP 请求明文 | `python main.py -r request.txt` |
| PoC 文件 URL | `python main.py -u https://example.com/poc.py` |

## 输出

- **PCAP** — 攻击流量包
- **Detection IR** — 中间检测规则（JSON）
- **Snort Rule** — Snort 规则（后续支持 Suricata）
- **测试报告** — 规则测试结果

## 快速开始

```bash
# 1. 配置
cp config.yaml.template config.yaml
# 编辑 config.yaml，填入 LLM API Key 等信息

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python main.py -p examples/poc_sqli.py
python main.py -r examples/request.txt
python main.py -u https://example.com/poc.py

# 4. 查看输出
ls workspace/output/
```

## 项目架构

```
       输入（PoC / HTTP / URL）
              │
              ▼
    Workflow（Python 控制流程，LangGraph）
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
 Planner   Inference   Plugin
（局部决策） （单次推理） （规则格式）
    │         │         │
    └─────────┼─────────┘
              ▼
          Tool（Python 执行）
```

- **Workflow** — Python 控制整个流程，LLM 不决定流程
- **Planner** — 局部 Agent，负责单个节点的策略（如 PCAP 生成）
- **Inference** — 一次 LLM 推理，不循环、不调度 Tool
- **Plugin** — 规则格式扩展，新增格式不改 Workflow
- **Tool** — 纯 Python 执行，不含 Prompt

## 目录结构

```
├── main.py                  # 程序入口
├── workflow.py              # LangGraph 工作流
├── config.yaml.template     # 配置模板
├── requirements.txt
├── app/                     # 应用基础（State、Context、Logger）
├── llm/                     # LLM 封装（Client、Inference、Planner、PromptBuilder）
├── workflow_nodes/          # 11 个 Workflow 节点
├── tools/                   # 7 个执行工具
├── inference/               # 推理技能（SKILL + Knowledge + Examples）
├── plugins/                 # 规则格式插件
├── schemas/                 # 数据模型
├── planners/                # Planner 策略
├── workspace/               # 工作目录
└── logs/                    # 日志
```

## 扩展

### 添加新规则格式

在 `plugins/` 下新建目录，实现 `PluginBase` 接口即可，**不需修改 Workflow**。

### 添加新模型

在 `config.yaml` 中修改 `llm.provider`，支持 OpenAI / DeepSeek / Qwen / vLLM。

### 添加新抓包方式

在 `tools/` 下添加新工具，在对应 Planner 中注册即可。

## 依赖

- Python >= 3.10
- LangGraph / LangChain
- Scapy
- Docker（可选，用于沙箱运行 PoC）
- Snort（可选，用于规则验证和测试）

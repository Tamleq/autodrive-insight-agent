# AutoDrive Insight Agent

## 1. 项目名称

**AutoDrive Insight Agent** 是一个面向智能驾驶量产回传数据分析场景的 AI Agent 项目 Demo。

项目聚焦“异常事件自动筛选 -> 规则引擎命中 -> 严重度分级 -> LLM 辅助分析 -> Markdown 报告生成”的闭环流程，用模拟数据展示智能驾驶问题分析平台的基础形态。

> 说明：本项目使用的是模拟智能驾驶事件数据，不包含真实车企、真实车辆或真实用户数据。

## 2. 项目简介

AutoDrive Insight Agent 用于演示如何把智能驾驶量产回传事件转化为可筛选、可分级、可解释、可生成报告的分析工作流。

当前版本包含 FastAPI 后端、React 前端、CSV 模拟数据集、规则引擎、严重度评分模型、Mock LLM 分析模块、Agent Orchestrator 以及 Markdown 报告生成能力。项目重点不在“替代安全工程师判断”，而是展示如何通过 AI Agent 和 Skill 编排，把重复的数据初筛、证据整理和报告撰写动作自动化。

## 3. 项目背景

智能驾驶系统在量产后会持续产生回传事件，例如 AEB 触发、驾驶员接管、低 TTC、车道线置信度下降、目标识别置信度波动、规划轨迹异常等。工程分析通常需要完成几类重复工作：

- 从大量事件中筛选疑似异常样本
- 根据触发条件和车辆信号识别问题类型
- 按风险程度进行初步优先级排序
- 汇总关键证据，辅助后续人工复核
- 生成结构化分析记录或问题报告

本项目用模拟数据搭建一个轻量化分析 Agent，展示上述流程如何被规则引擎、LLM 分析和自动报告生成串联起来。

## 4. 核心功能

- **智能驾驶事件数据加载**：从 `data/demo_events.csv` 读取 500 条模拟异常事件，字段覆盖场景、天气、车速、制动、AEB、接管、TTC、感知状态、规划状态等。
- **自动化筛选**：支持按 `scene_type`、`takeover`、`aeb_triggered` 查询和筛选事件。
- **规则引擎**：对单个事件执行规则命中，识别急制动、AEB 触发、疑似误刹、高风险接管、车道线异常、低 TTC、规划异常、感知异常等风险信号。
- **严重度分级**：基于评分因子输出 S/A/B/C/D 等级、分数、原因和触发因子。
- **LLM 分析**：默认使用 Mock LLM 模式，根据事件、规则命中和严重度生成结构化分析结果；代码中保留真实 LLM 集成入口。
- **AI Agent 编排**：通过 `agent_orchestrator.py` 串联数据加载、规则筛选、严重度分级、LLM 分析和报告生成。
- **自动报告生成**：输出 Markdown 事件分析报告，并保存到 `reports/{event_id}_report.md`。
- **前端展示**：提供 Dashboard、事件列表、事件详情和报告页，用于展示事件、风险分布、规则命中、AI 分析结果和 Markdown 报告。

## 5. 技术栈

| 层级 | 技术 |
| --- | --- |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Agent / Skills | data_loader, rule_engine, severity_grader, llm_analyzer, report_generator, agent_orchestrator |
| Data | CSV 模拟数据集 |
| Frontend | React, TypeScript, Vite |
| UI | Ant Design, lucide-react, Recharts |
| Test | pytest |
| Report | Markdown |

## 6. 系统架构

```text
autodrive-insight-agent/
├── backend/
│   ├── main.py                    # FastAPI API 入口
│   ├── agent_orchestrator.py      # Agent 工作流编排
│   ├── models/
│   │   └── schemas.py             # API 响应模型
│   ├── skills/
│   │   ├── data_loader.py         # 模拟数据加载与筛选
│   │   ├── rule_engine.py         # 规则引擎
│   │   ├── severity_grader.py     # 严重度分级
│   │   ├── llm_analyzer.py        # Mock LLM 分析
│   │   └── report_generator.py    # Markdown 报告生成
│   └── tests/                     # 后端单元测试与 API 测试
├── data/
│   └── demo_events.csv            # 模拟智能驾驶事件数据
├── frontend/
│   └── src/                       # React 前端页面与组件
├── reports/                       # 生成的 Markdown 报告
├── docs/                          # 文档说明
└── screenshots/                   # 页面截图占位
```

后端以 Skill 模块拆分核心能力，Agent Orchestrator 负责把各模块组织成一个稳定的分析链路。前端通过 Vite 代理调用 FastAPI 接口，展示事件列表、风险概览、分析详情和报告内容。

## 7. Agent 工作流

```text
输入 event_id
   |
   v
load_event(event_id)
   |
   v
rule_screening(event)
   |
   v
severity_grading(event, matched_rules)
   |
   v
llm_analysis(event, matched_rules, severity)
   |
   v
report_generation(event, matched_rules, severity, ai_analysis)
   |
   v
返回分析结果并保存 Markdown 报告
```

对应实现位于 `backend/agent_orchestrator.py`，核心入口为：

```python
analyze_event(event_id: str) -> dict
```

成功结果包含：

- `event`
- `matched_rules`
- `severity`
- `ai_analysis`
- `report`
- `report_path`

## 8. 数据字段说明

模拟数据文件：`data/demo_events.csv`

| 字段 | 说明 |
| --- | --- |
| `event_id` | 事件唯一 ID，例如 `EVT_0001` |
| `vehicle_id` | 模拟车辆 ID |
| `timestamp` | 事件发生时间 |
| `scene_type` | 驾驶场景类型 |
| `weather` | 天气 |
| `road_type` | 道路类型 |
| `ego_speed` | 自车速度 |
| `brake_acc` | 制动加速度 |
| `steering_angle` | 方向盘转角 |
| `takeover` | 是否发生人工接管 |
| `aeb_triggered` | 是否触发 AEB |
| `lane_confidence` | 车道线置信度 |
| `object_type` | 目标类型 |
| `object_confidence` | 目标识别置信度 |
| `ttc` | Time To Collision，碰撞时间 |
| `lateral_offset` | 横向偏移 |
| `perception_status` | 感知状态 |
| `planning_status` | 规划状态 |
| `log_text` | 模拟事件描述文本 |

`backend/skills/data_loader.py` 会把数值字段转换为 `float`，把 `takeover` 和 `aeb_triggered` 转换为 `bool`。

## 9. 规则引擎说明

规则引擎实现文件：`backend/skills/rule_engine.py`

核心函数：

```python
screen_event_rules(event: dict) -> list
```

当前规则集：

| Rule ID | 规则含义 | 触发条件 |
| --- | --- | --- |
| `R001` | 急制动 | `brake_acc <= -3.5` |
| `R002` | AEB 触发 | `aeb_triggered == True` |
| `R003` | 疑似误刹 | `aeb_triggered == True` 且 `object_confidence < 0.5` 且 `brake_acc <= -3.0` |
| `R004` | 高风险接管 | `takeover == True` 且 `ego_speed > 40` |
| `R005` | 车道线异常 | `lane_confidence < 0.4` 且 `lateral_offset > 0.5` |
| `R006` | TTC 过低 | `ttc <= 1.5` |
| `R007` | 规划异常 | `planning_status` 包含 `abnormal` 或 `deviation` |
| `R008` | 感知异常 | `perception_status` 包含 `unstable`、`lost` 或 `low_confidence` |

每条命中规则返回 `rule_id`、`rule_name`、`description`、`evidence` 和 `risk_score`，用于后续分级、LLM 分析和报告生成。

## 10. 严重度分级模型

严重度分级实现文件：`backend/skills/severity_grader.py`

核心函数：

```python
grade_severity(event: dict, matched_rules: list) -> dict
```

评分因子：

| 因子 | 分值 |
| --- | ---: |
| `aeb_triggered == True` | +25 |
| `takeover == True` | +25 |
| `brake_acc <= -3.5` | +20 |
| `ttc <= 1.5` | +20 |
| `object_confidence < 0.5` | +10 |
| 高风险场景 | +10 |

等级映射：

| 等级 | 分数范围 | 含义 |
| --- | --- | --- |
| `S` | `score >= 80` | 最高优先级，建议人工复核 |
| `A` | `score >= 60` | 高风险，建议重点分析 |
| `B` | `score >= 40` | 中风险，需要跟踪 |
| `C` | `score >= 20` | 低风险，可常规分析 |
| `D` | `score < 20` | 普通事件 |

该模型用于 Demo 展示和初筛排序，不代表真实量产项目中的安全定级标准。

## 11. AI 分析与报告生成

AI 分析实现文件：`backend/skills/llm_analyzer.py`

核心函数：

```python
analyze_with_llm(event: dict, matched_rules: list, severity: dict) -> dict
```

当前默认运行在 Mock LLM 模式，不依赖外部 API Key，也不会访问真实模型服务。模块会根据事件字段、规则命中和严重度结果生成：

- `summary`：事件级摘要
- `scenario_description`：场景与关键驾驶信号描述
- `possible_causes`：可能原因
- `risk_assessment`：风险判断
- `recommendations`：后续处理建议
- `need_human_review`：是否建议人工复核

报告生成实现文件：`backend/skills/report_generator.py`

核心函数：

```python
generate_markdown_report(event, matched_rules, severity, ai_analysis) -> str
save_report(event_id, report_content) -> str
```

生成的报告会保存到 `reports/{event_id}_report.md`，内容包含事件基本信息、规则命中、严重度分级、AI 原因分析、关键证据、处理建议和人工复核建议。

## 12. 页面截图占位

当前仓库保留 `screenshots/` 目录用于 GitHub 展示截图。建议后续补充以下文件：

| 截图文件 | 建议内容 |
| --- | --- |
| `screenshots/dashboard.png` | Dashboard，总事件数、风险分布、问题类型 Top 5、高风险事件列表 |
| `screenshots/event-list.png` | 事件列表，展示场景、接管、AEB 筛选 |
| `screenshots/event-detail.png` | 事件详情，展示关键指标、规则命中、严重度分级、AI 分析 |
| `screenshots/report.png` | Markdown 报告页，展示复制和下载报告能力 |

截图说明见 `screenshots/README.md`。

## 13. 本地运行方式

### 后端

```bash
cd autodrive-insight-agent/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

交互式 API 文档：

```text
http://127.0.0.1:8000/docs
```

### 前端

```bash
cd autodrive-insight-agent/frontend
npm install
npm run dev
```

Vite 本地地址：

```text
http://localhost:5173
```

### 命令行运行 Agent

从仓库根目录执行：

```bash
python backend/agent_orchestrator.py --event_id EVT_0001
```

## 14. API 接口说明

| Method | Endpoint | 说明 |
| --- | --- | --- |
| `GET` | `/health` | 后端健康检查 |
| `GET` | `/api/events` | 获取事件列表 |
| `GET` | `/api/events?takeover=true&aeb_triggered=true` | 按接管和 AEB 条件筛选事件 |
| `GET` | `/api/events/{event_id}` | 获取单个事件详情 |
| `POST` | `/api/analyze/{event_id}` | 执行完整 Agent 分析流程 |
| `GET` | `/api/report/{event_id}` | 获取 Markdown 报告；如报告不存在会先自动生成 |

`POST /api/analyze/{event_id}` 返回示例结构：

```json
{
  "event": {},
  "matched_rules": [],
  "severity": {},
  "ai_analysis": {},
  "report": "Markdown content",
  "report_path": "reports/EVT_0001_report.md"
}
```

## 15. 测试方式

后端测试依赖已写入 `backend/requirements.txt`。

从仓库根目录运行：

```bash
python -m compileall backend
python -m pytest backend/tests
```

也可以只运行单个模块测试：

```bash
python -m pytest backend/tests/test_data_loader.py
python -m pytest backend/tests/test_rule_engine.py
python -m pytest backend/tests/test_severity_grader.py
python -m pytest backend/tests/test_llm_analyzer.py
python -m pytest backend/tests/test_report_generator.py
python -m pytest backend/tests/test_agent_orchestrator.py
python -m pytest backend/tests/test_api.py
```

前端构建检查：

```bash
cd frontend
npm run build
```

## 16. 项目亮点

- 以智能驾驶量产回传数据分析为背景，覆盖事件筛选、风险识别、严重度排序和报告生成的完整链路。
- 使用 Skill 模块拆分数据加载、规则筛选、分级、LLM 分析、报告生成，便于扩展和替换。
- 规则引擎输出命中证据，避免只给结论，便于后续人工复核。
- 严重度分级模型提供可解释的分数、等级、触发因子和分级原因。
- LLM 分析模块默认 Mock 运行，保证本地演示和测试不依赖外部网络或 API Key。
- Agent Orchestrator 将多个能力编排为稳定工作流，展示 AI Agent 在工程分析场景中的落地方式。
- 前端提供 Dashboard、列表、详情和报告页，便于把后端分析结果转化为可演示的产品界面。

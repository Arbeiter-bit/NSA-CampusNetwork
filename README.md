校园网态势感知系统-流量分析画像与安全可视化模块

![CI](https://github.com/Arbeiter-bit/NSA-CampusNetwork/workflows/CI/badge.svg)
![Lint](https://github.com/Arbeiter-bit/NSA-CampusNetwork/workflows/Lint/badge.svg)
![Docker Build](https://github.com/Arbeiter-bit/NSA-CampusNetwork/workflows/Docker%20Build/badge.svg)

<img width="1265" height="1052" alt="image" src="https://github.com/user-attachments/assets/cc80649a-4fe8-433b-baa5-55d49e6dde40" />


✨ 核心功能模块：

流量统计：统计总流量、流量包数量、用户数量、IP 数量、用户流量排名和应用类别分布
流量趋势分析：按小时汇总校园网流量，生成趋势图和活跃时段统计
用户应用类别分析：统计每个用户的应用类别占比、协议占比、端口访问行为和 DNS 行为
用户画像分析：按应用、时段和安全行为生成用户标签，并输出 `data/user_profiles.json`
AI 安全审查：使用本地规则识别扫描、敏感服务访问、异常流量、非活跃时段通信和 AI 辅助攻击痕迹
DeepSeek 防守复核：可选调用 DeepSeek 对本地安全审查结果进行二次研判，只发送汇总风险和少量证据
ML 异常检测：使用 IsolationForest 对用户行为做无监督异常评分，补充规则引擎无法覆盖的隐性异常
实时态势大屏：通过 SSE 事件流模拟实时流量回放，展示实时流量曲线、事件流和告警流
智能拦截建议：根据风险分数给出 `rate_limit`、`step_up_auth` 或 `quarantine` 策略
可视化展示：前端使用自定义深色态势感知界面，并通过 Chart.js 渲染交互式图表

📊 可视化图表：

- 首页控制台状态面板
- 安全仪表板攻击源追踪面板
- AI 安全审查风险状态卡片
- 总流量、流量包、活跃用户、IP 数量指标卡
- 小时流量趋势折线图
- 应用类别流量环形图
- 用户流量排行条形图
- 每小时活跃用户与包数表格
- ML 异常用户检测表格
- 用户标签卡片展示
- 用户应用占比图
- 用户协议占比图
- 用户活跃时段柱状图
- 实时大屏 KPI 指标、实时流量曲线、实时告警流和最近事件流

## Features

- **Traffic Analysis** - Aggregate traffic statistics, user ranking, application category distribution, and hourly traffic trends
- **User Profiling** - Automatic user behavior analysis with tag generation (application, time pattern, security tags)
- **AI Security Audit** - Local rule engine for port scanning detection, sensitive service access, anomalous traffic, and AI-assisted attack identification
- **DeepSeek Review** - Optional secondary verification using DeepSeek API, sending only summarized risk evidence
- **ML Anomaly Detection** - IsolationForest-based unsupervised anomaly scoring to catch hidden outliers
- **Real-time Dashboard** - SSE-powered live traffic replay with real-time curves, event streams, and alert feeds
- **Smart Blocking** - Risk-based mitigation strategies: rate limiting, step-up authentication, or quarantine
- **Interactive Visualizations** - Chart.js and Plotly-powered dark-themed security dashboards

<img width="2484" height="2127" alt="image" src="https://github.com/user-attachments/assets/05e3154f-c1af-49de-84cb-0655993f2c93" />

<img width="1613" height="555" alt="image" src="https://github.com/user-attachments/assets/bdb9bc46-a842-4c4c-810e-69b78f1b0586" />


<img width="1551" height="473" alt="image" src="https://github.com/user-attachments/assets/0af15ff9-30d2-48b1-9c8a-80ae52acccb8" />

<img width="1564" height="606" alt="image" src="https://github.com/user-attachments/assets/c3a5b761-9f84-4ae5-8330-5f37c58befa4" />


<img width="1572" height="550" alt="image" src="https://github.com/user-attachments/assets/e5fcfa99-010b-465f-bfe6-711c5db6d9a8" />


<img width="1566" height="1127" alt="image" src="https://github.com/user-attachments/assets/468017ad-41b8-4b33-9825-5c78171e3c84" />


<img width="1692" height="1093" alt="image" src="https://github.com/user-attachments/assets/82819ec1-d386-421c-84ee-dda90a4f02e8" />

## Screenshots

| View | Description |
|------|-------------|
| Home Console | System status cards, CSV upload, navigation |
| Security Dashboard | Charts, AI audit, ML anomalies, user profiles |
| Real-Time Dashboard | SSE-powered live traffic replay and alerts |
| User Profile Cards | Application, protocol, and activity time charts |

> Screenshots above show the main dashboard views. Additional screenshots are available in the project documentation.

## Project Structure

```
NSA-CampusNetwork/
│
├── app.py                      # Flask entry point, routes, global state
├── config.yaml                 # Application configuration
├── pyproject.toml              # Project metadata, tool config
├── Makefile                    # Build, test, lint commands
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Multi-service Docker setup
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
├── run.sh                      # Quick-start shell script
├── check_project.py            # Project structure validator
├── STARTUP_GUIIDE.py            # Startup guide script
│
├── utils/                      # Core analysis modules
│   ├── analysis.py             # Traffic analysis & Plotly charts
│   ├── user_profile.py         # User profiling & tag generation
│   ├── ai_security.py          # AI security audit & DeepSeek review
│   ├── ml_anomaly.py           # IsolationForest anomaly detection
│   ├── realtime.py             # SSE replay engine
│   ├── cache.py                # In-memory caching layer
│   ├── metrics.py              # Prometheus-style metrics
│   ├── constants.py            # Shared constants
│   ├── backup.py               # Data backup utilities
│   ├── database.py             # Database persistence (future)
│   ├── logging_config.py       # Logging configuration
│   └── response.py             # Response helpers
│
├── templates/                  # Jinja2 HTML templates
│   ├── index.html              # Home page (console + upload)
│   ├── dashboard.html          # Security dashboard
│   └── realtime.html           # Real-time dashboard
│
├── static/                     # Static assets (CSS, JS, images)
│
├── data/                       # Data storage
│   ├── traffic.csv             # Sample traffic data
│   └── user_profiles.json      # Generated user profiles
│
├── tests/                      # Test suite
│   ├── conftest.py             # Pytest fixtures
│   ├── test_analysis.py        # Analysis module tests
│   ├── test_analysis_extended.py
│   ├── test_ai_security.py     # AI security tests
│   ├── test_app.py             # Flask app tests
│   ├── test_constants.py       # Constants tests
│   ├── test_ml_anomaly.py      # ML anomaly tests
│   ├── test_ml_models.py       # ML model tests
│   ├── test_realtime.py        # Realtime engine tests
│   ├── test_response.py        # Response helpers tests
│   ├── test_security_rules.py  # Security rules tests
│   └── test_user_profile.py    # User profile tests
│
├── docs/                       # Documentation
│   ├── api.md                  # API reference
│   ├── deployment.md           # Deployment guide
│   ├── architecture.md         # System architecture
│   ├── development.md          # Developer guide
│   ├── troubleshooting.md      # Troubleshooting guide
│   └── faq.md                  # Frequently asked questions
│
├── scripts/                    # Utility scripts
│
├── .github/                    # GitHub Actions workflows
│
├── .env.example                # Environment variable template
├── .editorconfig               # Editor settings
├── .pre-commit-config.yaml     # Pre-commit hooks
├── .pylintrc                   # Pylint configuration
├── mypy.ini                    # MyPy type checker config
├── .gitignore                  # Git ignore rules
├── .dockerignore               # Docker ignore rules
│
├── LICENSE                     # MIT License
├── README.md                   # This file
├── CONTRIBUTING.md             # Contribution guidelines
├── CHANGELOG.md                # Version changelog
├── AUTHORS.md                  # Project authors
├── CODE_OF_CONDUCT.md          # Code of conduct
├── SECURITY.md                 # Security policy
├── SUPPORT.md                  # Support information
├── ROADMAP.md                  # Development roadmap
├── USAGE.md                    # Detailed usage guide
├── PROJECT_SUMMARY.md          # Project summary
├── DELIVERY_CHECKLIST.md       # Delivery checklist
└── SECURITY.md                 # Security disclosure
```

环境要求

- Python 3.8 或更高版本
- pip 包管理工具
- 现代浏览器（Chrome、Edge、Firefox 等）
- 网络连接：前端通过 CDN 加载 Chart.js

安装步骤

1. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

快速开始

1. 启动应用

```bash
python app.py
```

应用将运行在 `http://localhost:5001`

2. 访问应用

打开浏览器访问：`http://localhost:5001`

3. 首页操作

<img width="1247" height="385" alt="image" src="https://github.com/user-attachments/assets/36819b9c-a030-4109-af49-b1faccf146c6" />
<img width="1315" height="434" alt="image" src="https://github.com/user-attachments/assets/2a4650c2-1701-4ffb-b09b-347a1fe9a3be" />


- **查看当前统计**：首页显示已加载数据的用户数、包数量、总流量和 IP 数量
- **上传新数据**：通过 CSV 上传区域上传新流量文件，系统会覆盖 `data/traffic.csv`
- **查看安全仪表板**：点击“进入安全仪表板”进入 `/dashboard`
- **进入实时大屏**：点击“实时态势大屏”进入 `/realtime`

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Arbeiter-bit/NSA-CampusNetwork.git
cd NSA-CampusNetwork

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run with sample data
python app.py

# 5. Open in browser
# http://localhost:5001
```

Or using Docker:

```bash
docker-compose up --build
```

---

## Configuration

The application can be configured via three mechanisms (in order of precedence):

1. **Environment variables** — override all other sources
2. **`config.yaml`** — YAML configuration file in the project root
3. **Application defaults** — hardcoded in `app.py`

### Environment variables (`.env`)

Copy `.env.example` to `.env` and adjust:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `FLASK_SECRET_KEY` | `nsa-campus-network-dev-key` | Secret key for session signing |
| `FLASK_HOST` | `0.0.0.0` | Server bind address |
| `FLASK_PORT` | `5001` | Server port |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode |
| `DEEPSEEK_API_KEY` | — | DeepSeek API key (optional) |
| `DEEPSEEK_API_URL` | `https://api.deepseek.com/v1/chat/completions` | DeepSeek API endpoint |
| `DEEPSEEK_MODEL` | `deepseek-chat` | DeepSeek model name |

### `config.yaml`

All options with descriptions are documented in `config.yaml` in the project root:

```yaml
server:
  host: "0.0.0.0"       # Bind address
  port: 5001             # Listen port
  debug: false           # Debug mode
  secret_key: "..."      # Session secret

upload:
  allowed_extensions: "csv"   # Allowed file types
  max_size_mb: 50             # Max upload size (MB)

deepseek:
  api_url: "https://api.deepseek.com/v1/chat/completions"
  model: "deepseek-chat"
  timeout: 20

logging:
  level: "INFO"
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
```

---

上传的 CSV 文件应包含以下列（用逗号分隔）：

```
timestamp,src_ip,dst_ip,src_port,dst_port,protocol,bytes,app_category,user
```

列说明

| 列名         | 说明         | 格式示例                           |
| ------------ | ------------ | ---------------------------------- |
| timestamp    | 流量时间戳   | `2025-12-01 08:00:15`              |
| src_ip       | 源 IP 地址   | `192.168.1.100`                    |
| dst_ip       | 目标 IP 地址 | `8.8.8.8`                          |
| src_port     | 源端口       | `52341`                            |
| dst_port     | 目标端口     | `53`                               |
| protocol     | 协议类型     | `TCP/UDP/QUIC`                     |
| bytes        | 流量字节数   | `256`                              |
| app_category | 应用类别     | `DNS/Social Media/Video Streaming` |
| user         | 用户标识     | `student_001`                      |

CSV 示例

```csv
timestamp,src_ip,dst_ip,src_port,dst_port,protocol,bytes,app_category,user
2025-12-01 08:00:15,192.168.1.100,8.8.8.8,52341,53,UDP,256,DNS,student_001
2025-12-01 08:00:32,192.168.1.101,142.251.41.14,52456,443,TCP,4096,Social Media,student_002
2025-12-01 08:01:05,192.168.1.102,13.226.123.45,52789,80,TCP,2048,Video Streaming,student_003
```

当前示例数据

- `data/traffic.csv`：102 条流量记录
- 示例用户数：75 个
- 示例应用类别：DNS、Social Media、Video Streaming、CDN、Web Search、P2P、Web Browse
- `data/user_profiles.json`：由用户画像模块自动生成，可随上传数据刷新

API 接口

GET /api/stats

返回 JSON 格式的基础统计数据。

```bash
curl http://localhost:5001/api/stats
```

响应示例：

```json
{
  "total_traffic": {
    "total_bytes": 1234567,
    "total_packets": 456,
    "unique_users": 50,
    "unique_ips": 100
  },
  "user_ranking": [
    {"user": "student_001", "bytes": 123456},
    {"user": "student_002", "bytes": 112345}
  ],
  "app_category": [
    {"category": "Video Streaming", "bytes": 456789},
    {"category": "Social Media", "bytes": 234567}
  ],
  "active_hours": [
    {"hour": "08:00", "active_users": 25, "total_bytes": 56789, "packet_count": 45}
  ]
}
```

GET /api/dashboard_data

返回仪表板前端所需的聚合数据，包括基础统计、排行榜、应用类别、活跃时段、攻击源追踪摘要、AI 安全审查和 ML 异常检测。

```bash
curl http://localhost:5001/api/dashboard_data
```

GET /api/user_profiles

返回用户画像数据（JSON 格式）。

```bash
curl http://localhost:5001/api/user_profiles
```

GET /api/ai_security

返回本地 AI 安全审查报告，包含风险等级、告警、拦截建议和防 AI 辅助攻击策略。

```bash
curl http://localhost:5001/api/ai_security
```

POST /api/ai_security/deepseek

调用 DeepSeek 对本地安全审查结果进行防守性复核。该接口只发送汇总风险和少量证据，不发送完整原始流量。

```bash
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
curl -X POST http://localhost:5001/api/ai_security/deepseek
```

可选环境变量：

```bash
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export DEEPSEEK_MODEL="deepseek-chat"
export DEEPSEEK_TIMEOUT="20"
```

GET /api/ml_anomaly

返回 IsolationForest 用户异常检测结果。

```bash
curl http://localhost:5001/api/ml_anomaly
```

POST /api/ml_anomaly/refresh

强制重新运行 ML 异常检测。

```bash
curl -X POST http://localhost:5001/api/ml_anomaly/refresh
```

实时大屏 API

| 路由                   | 方法 | 说明                                                         |
| ---------------------- | ---- | ------------------------------------------------------------ |
| `/api/realtime/start`  | POST | 启动流量回放，可传入 `rate` 和 `loop`                        |
| `/api/realtime/stop`   | POST | 停止流量回放                                                 |
| `/api/realtime/rate`   | POST | 运行中调整回放速率                                           |
| `/api/realtime/status` | GET  | 查询回放状态、实时指标、最近事件和流量桶                     |
| `/api/realtime/stream` | GET  | SSE 事件流，推送 `snapshot`、`event`、`metrics`、`alert`、`finished` |

启动实时回放示例：

```bash
curl -X POST http://localhost:5001/api/realtime/start \
  -H "Content-Type: application/json" \
  -d "{\"rate\": 5, \"loop\": true}"
```

路由说明

| 路由                        | 方法 | 说明                                                         |
| --------------------------- | ---- | ------------------------------------------------------------ |
| `/`                         | GET  | 首页 - 显示系统入口、统计信息和文件上传表单                  |
| `/dashboard`                | GET  | 安全仪表板 - 展示攻击源追踪、AI 审查、流量图表、ML 异常和用户画像 |
| `/realtime`                 | GET  | 实时态势感知大屏 - SSE 流量回放、实时事件和告警              |
| `/upload`                   | POST | 处理 CSV 文件上传，上传后自动刷新分析                        |
| `/api/stats`                | GET  | 返回 JSON 格式基础统计数据                                   |
| `/api/dashboard_data`       | GET  | 返回仪表板完整数据                                           |
| `/api/user_profiles`        | GET  | 返回用户画像数据                                             |
| `/api/ai_security`          | GET  | 返回本地 AI 安全审查和智能拦截建议                           |
| `/api/ai_security/deepseek` | POST | 调用 DeepSeek 进行防守性复核                                 |
| `/api/ml_anomaly`           | GET  | 返回 ML 异常用户检测结果                                     |
| `/api/ml_anomaly/refresh`   | POST | 重新运行 ML 异常用户检测                                     |
| `/api/realtime/start`       | POST | 启动实时流量回放                                             |
| `/api/realtime/stop`        | POST | 停止实时流量回放                                             |
| `/api/realtime/rate`        | POST | 调整实时回放速率                                             |
| `/api/realtime/status`      | GET  | 查询实时回放状态                                             |
| `/api/realtime/stream`      | GET  | SSE 实时事件流                                               |

数据分析模块说明

TrafficAnalyzer 类

主要分析方法：

```python
# 获取总流量统计
analyzer.get_total_traffic()

# 获取用户流量排名（TOP N）
analyzer.get_user_traffic_ranking(top_n=10)

# 获取应用类别流量分布
analyzer.get_app_category_traffic()

# 获取流量趋势
analyzer.get_traffic_trend(unit='hour')

# 获取活跃时段分析
analyzer.get_active_hours()

# 获取指定用户的应用类别占比
analyzer.get_user_app_distribution(user_id='student_001')
```

图表生成函数

```python
# 生成流量趋势折线图
generate_traffic_trend_chart(analyzer)

# 生成应用类别饼图
generate_app_category_pie_chart(analyzer)

# 生成用户流量排行条形图
generate_user_ranking_chart(analyzer)

# 生成活跃时段折线图
generate_active_hours_chart(analyzer)

# 一次性生成所有 Plotly 图表 HTML
generate_all_charts(analyzer)
```

说明：当前新版前端主要通过 `/api/dashboard_data` 获取数据并使用 Chart.js 渲染图表，`utils/analysis.py` 中的 Plotly 图表生成函数仍保留，便于后续扩展或导出 HTML 图表。

用户画像分析模块

概述

用户画像分析模块（`utils/user_profile.py`）通过分析用户的网络流量行为，自动识别用户特征并生成标签体系。

画像字段

| 字段             | 说明                       |
| ---------------- | -------------------------- |
| `tags`           | 自动生成的用户标签         |
| `category_pct`   | 归一化后的应用类别流量占比 |
| `active_hours`   | 0-23 点每小时流量与记录数  |
| `protocol_ratio` | 协议流量占比               |
| `port_stats`     | 重点端口访问次数           |
| `dns_stats`      | DNS 查询次数和流量         |
| `daily_bytes`    | 每日总流量                 |

标签体系

应用标签（Application Tags）

| 标签       | 触发条件              | 说明                                        |
| ---------- | --------------------- | ------------------------------------------- |
| 游戏狂     | game > 30%            | 游戏流量占比超过 30%                        |
| 视频大户   | video > 40%           | 视频流量占比超过 40%                        |
| 社交达人   | social + chat > 30%   | 社交通讯流量占比超过 30%                    |
| 学习型用户 | edu > 20%             | 教育学习流量占比超过 20%                    |
| 技术用户   | 特殊端口访问次数 > 20 | 频繁访问 22/3389/3306/8000/8080/5000 等端口 |

时段标签（Time Pattern Tags）

| 标签     | 触发条件                                | 说明                 |
| -------- | --------------------------------------- | -------------------- |
| 夜猫子   | 22-02 时段流量占比 > 40%                | 大部分流量集中在夜间 |
| 早起族   | 06-09 时段流量占比 > 30%                | 大部分流量集中在早晨 |
| 规律用户 | 活跃时间方差低于全体用户中位数的 0.5 倍 | 每小时流量分布较稳定 |
| 波动用户 | 活跃时间方差高于全体用户中位数的 1.5 倍 | 每小时流量波动较大   |

安全标签（Security Tags）

| 标签         | 触发条件                | 说明                                |
| ------------ | ----------------------- | ----------------------------------- |
| 可疑扫描     | 访问 3 个或以上重点端口 | 可能存在端口探测行为                |
| 可疑DNS      | DNS 查询次数 > 50       | 高频 DNS 查询可能表示异常解析或扫描 |
| 异常活跃时间 | 夜间流量占比 > 60%      | 夜间大流量可能表示异常行为          |

用户画像数据结构

输出的 `data/user_profiles.json` 文件格式如下：

```json
{
  "student_001": {
    "tags": ["规律用户", "早起族"],
    "category_pct": {
      "dns": 100.0
    },
    "active_hours": {
      "8": {"bytes": 1024, "count": 4},
      "9": {"bytes": 512, "count": 2}
    },
    "protocol_ratio": {
      "UDP": 100.0
    },
    "port_stats": {},
    "dns_stats": {
      "dns_queries": 9,
      "dns_bytes": 2304
    },
    "daily_bytes": {
      "2025-12-01": 2304
    }
  }
}
```

使用用户画像模块

方法 1：独立运行 Python 脚本

```bash
python utils/user_profile.py
```

这将读取 `data/traffic.csv` 并生成 `data/user_profiles.json` 文件。

方法 2：在 Flask 中自动生成

当启动 Flask 应用或上传新的 CSV 文件时，系统会自动生成用户画像数据。

方法 3：通过 API 获取

```bash
curl http://localhost:5001/api/user_profiles
```

AI 安全审查模块

概述

AI 安全审查模块（`utils/ai_security.py`）用于对校园网流量进行防守性风险分析。模块只输出检测、审查和拦截建议，不提供攻击实现或绕过方法。

本地规则检测内容：

- 疑似横向扫描或端口探测
- 敏感服务访问异常
- 用户流量显著高于基线
- 非活跃时段异常通信
- 疑似提示词注入或 AI 安全绕过文本
- 疑似 AI 代理或自动化工具访问痕迹
- 疑似 Web 攻击载荷或命令执行痕迹

智能拦截策略：

| 风险分数 | 动作           | TTL     |
| -------- | -------------- | ------- |
| >= 85    | `quarantine`   | 30 分钟 |
| >= 75    | `rate_limit`   | 15 分钟 |
| >= 70    | `step_up_auth` | 10 分钟 |

防 AI 辅助攻击说明：

- 不按 Claude、GPT 等模型名称做单点判断，避免误伤正常用户
- 按行为模式、请求文本、载荷特征和访问频率识别 AI 代理滥用
- 命中高风险时给出限速、二次认证或临时隔离建议
- DeepSeek 复核只上传汇总风险和少量证据，不上传完整原始流量

ML 异常检测模块

概述

ML 异常检测模块（`utils/ml_anomaly.py`）使用 IsolationForest 将每个用户的行为压缩成固定维度特征向量，并输出异常分数、等级和关键证据。

检测特征：

| 特征名                 | 说明               |
| ---------------------- | ------------------ |
| `total_bytes`          | 用户总流量         |
| `total_packets`        | 用户流量记录数     |
| `unique_dst_ips`       | 访问目标 IP 数量   |
| `unique_dst_ports`     | 访问目标端口数量   |
| `suspicious_port_hits` | 重点端口命中次数   |
| `night_byte_ratio`     | 0-5 点夜间流量占比 |
| `dns_query_count`      | DNS 查询次数       |
| `max_hour_bytes`       | 单小时最大流量     |
| `active_hour_count`    | 有流量的小时数量   |
| `avg_bytes_per_packet` | 平均单包字节数     |

默认参数：

| 参数            | 默认值 | 说明                     |
| --------------- | ------ | ------------------------ |
| `contamination` | `0.1`  | 预期异常用户比例         |
| `random_state`  | `42`   | 随机种子                 |
| `top_n`         | `10`   | 最多返回异常用户数       |
| `min_users`     | `5`    | 用户数少于该值时跳过检测 |

实时态势大屏模块

概述

实时态势大屏模块（`utils/realtime.py` 和 `templates/realtime.html`）把当前 CSV 当作回放素材，通过单例 `ReplayEngine` 按指定速率推送事件，并使用 SSE 给前端持续广播。

实时大屏功能：

- 启动/停止流量回放
- 运行中调整回放速率
- 展示已发送事件数、累计流量、活跃用户、源 IP 数和实时告警数
- 以 5 秒桶展示实时流量曲线
- 展示最近 30 条流量事件
- 展示实时规则告警
- 同屏展示 ML 异常用户排行

实时告警规则：

| 告警         | 条件                                                         |
| ------------ | ------------------------------------------------------------ |
| 实时端口扫描 | 同一源 IP 在 30 秒内访问 6 个及以上不同端口                  |
| 大流量突发   | 单条流量记录 >= 50,000 字节                                  |
| 敏感端口访问 | 访问 21、22、23、25、53、135、139、445、3306、3389、6379 等重点端口 |

模板过滤器

format_bytes

格式化字节数为易读格式。

```html
<!-- 模板中使用 -->
{{ total_bytes | format_bytes }}

<!-- 输出示例 -->
<!-- 1024 -> "1.00 KB" -->
<!-- 1048576 -> "1.00 MB" -->
<!-- 1073741824 -> "1.00 GB" -->
```

前端页面说明

首页 `/`

- 展示系统状态、当前数据统计和 CSV 上传入口
- 有数据时显示“进入安全仪表板”和“实时态势大屏”入口
- 上传新 CSV 后自动重新分析并跳转到仪表板

安全仪表板 `/dashboard`

- 通过 `/api/dashboard_data` 拉取数据
- 展示攻击源追踪、AI 安全审查、拦截建议、流量统计、用户排行、ML 异常检测和用户画像
- 点击用户画像卡片可展开该用户应用、协议和活跃时段图表
- 可点击“运行 DeepSeek 审查”触发远程防守复核
- 可点击“重新跑 ML 检测”刷新异常用户评分

实时大屏 `/realtime`

- 通过 `/api/realtime/stream` 建立 SSE 连接
- 点击“启动回放”后按指定速率推送当前 CSV 记录
- 支持运行中调整速率
- 可实时查看事件流、告警流和流量曲线

限制和注意事项

- 文件大小限制：最大文件大小 50MB
- 允许格式：仅支持 CSV 格式
- 时间戳格式：建议使用 `YYYY-MM-DD HH:MM:SS`
- 默认文件名：上传的文件始终保存为 `traffic.csv`，新文件会覆盖旧文件
- DeepSeek 复核为可选功能，未配置 `DEEPSEEK_API_KEY` 时系统仍会使用本地规则完成审查
- ML 异常检测要求用户数至少为 5，用户数过少时会自动跳过
- 当前项目使用 Flask 开发服务器，生产环境应关闭 `debug=True` 并使用正式 WSGI 服务

故障排除

问题：模块导入失败

解决方案：

```bash
# 确保已安装所有依赖
pip install -r requirements.txt

# 检查虚拟环境是否已激活
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

问题：CSV 文件无法识别

解决方案：

- 检查文件格式是否为 CSV
- 确认列名是否包含 `timestamp,src_ip,dst_ip,src_port,dst_port,protocol,bytes,app_category,user`
- 验证 `timestamp` 能被 Pandas 解析为时间
- 检查 `bytes`、`src_port`、`dst_port` 是否为数字

问题：图表不显示

解决方案：

- 检查是否上传了有效的 CSV 文件
- 查看浏览器控制台是否有错误信息
- 确保浏览器可以访问 Chart.js CDN
- 确认 Flask 服务运行在 `http://localhost:5001`

问题：DeepSeek 审查不可用

解决方案：

- 检查是否设置 `DEEPSEEK_API_KEY`
- 检查网络是否能访问 `DEEPSEEK_BASE_URL`
- 检查模型名是否与 DeepSeek 当前 API 支持的模型一致
- 未配置 DeepSeek 不影响本地安全审查结果

问题：实时大屏没有事件

解决方案：

- 确认已经上传或加载了 `data/traffic.csv`
- 先访问 `/dashboard` 或首页确认数据已加载
- 在 `/realtime` 点击“启动回放”
- 检查 `/api/realtime/status` 是否显示 `running: true`

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Tech Stack

| Category | Technologies |
|---|---|
| Backend Framework | Flask 2.3.2, Werkzeug 2.3.6 |
| Data Processing | Pandas 2.0.3, NumPy |
| Data Visualization | Plotly 5.15.0, Chart.js 3.9.1 / 4.4.1 (CDN) |
| Machine Learning | scikit-learn (IsolationForest, One-Class SVM, LOF) |
| Real-Time Communication | Server-Sent Events (SSE) |
| Frontend | Jinja2 Templates, Custom CSS, Vanilla JavaScript |
| Containerization | Docker, Docker Compose |
| Testing | Pytest |
| Linting / Formatting | Flake8, Black, isort, MyPy |
| CI/CD | GitHub Actions |

开发与扩展

添加新的分析函数

在 `utils/analysis.py` 的 `TrafficAnalyzer` 类中添加新方法：

```python
def get_custom_analysis(self):
    """自定义分析函数"""
    # 分析逻辑
    return result
```

添加新的用户画像标签

在 `utils/user_profile.py` 的 `generate_tags()` 中添加规则：

```python
if app_pct.get('custom_category', 0) > 30:
    tags.append('自定义标签')
```

添加新的安全审查规则

在 `utils/ai_security.py` 的 `AISecurityAnalyzer.generate_report()` 流程中增加检测函数，并通过 `_add_alert()` 追加告警：

```python
def _detect_custom_risk(self):
    self._add_alert(
        alert_type="custom_risk",
        severity="high",
        score=75,
        title="自定义风险",
        entity="user_or_ip",
        evidence=["命中自定义规则"],
        suggested_action="建议进行人工复核。",
        block_target={"type": "user", "value": "student_001"},
    )
```

添加新的 ML 特征

在 `utils/ml_anomaly.py` 中更新 `FEATURE_NAMES` 和 `_build_features()`，保持特征顺序稳定，前端会自动展示异常分数和证据。

添加新的实时告警

在 `utils/realtime.py` 的 `_check_alerts()` 中追加规则，返回结构保持为：

```python
{
    "ts": now,
    "level": "medium",
    "title": "告警标题",
    "entity": "用户或 IP",
    "detail": "告警详情"
}
```

修改前端样式

- 首页样式：编辑 `templates/index.html`
- 安全仪表板样式：编辑 `templates/dashboard.html`
- 实时大屏样式：编辑 `templates/realtime.html`

性能优化建议

1. **大文件处理**：对超大 CSV 文件使用 Pandas 分块读取，避免一次性加载占用过多内存
2. **缓存图表数据**：对 `/api/dashboard_data` 的聚合结果加缓存，减少重复计算
3. **异步分析任务**：使用 Celery 或 RQ 处理大文件分析、DeepSeek 复核等耗时任务
4. **增量更新**：上传追加数据时只分析新增记录，而不是全量重算
5. **持久化存储**：将流量记录、画像、告警和 ML 结果写入数据库，支持历史查询

安全建议

1. **生产环境**：关闭 `debug=True`，使用 Gunicorn、uWSGI 或 Waitress 等正式服务
2. **文件上传**：验证 CSV 内容、大小、列名和行数，避免异常文件拖垮服务
3. **输入验证**：对所有 API 参数进行类型、范围和格式校验
4. **权限控制**：为上传、DeepSeek 审查和拦截策略接口增加认证授权
5. **数据隐私**：对用户标识、IP 地址和安全事件进行脱敏或最小化展示
6. **外部模型调用**：调用 DeepSeek 前确认只发送汇总风险与证据，不上传完整原始流量

---

**最后更新**：2026 年 8 月 20 日

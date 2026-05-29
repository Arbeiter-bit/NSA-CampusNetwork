校园网态势感知系统-流量分析画像与可视化模块

<img width="2000" height="1078" alt="image" src="https://github.com/user-attachments/assets/ddf8e304-6eb6-4efb-8e41-9fd084ab261d" />

✨ 核心功能模块：

流量统计：统计总流量、用户流量排名、应用类别流量分布
流量趋势分析：生成单位时间（按小时）的流量趋势折线图
用户应用类别分析：统计每个用户使用的应用类别占比
活跃时段分析：按小时统计用户活跃度和流量变化
用户画像分析：识别用户行为特征、生成标签体系
AI 安全审查：使用本地规则和 DeepSeek 复核流量风险
智能拦截建议：针对扫描、敏感服务访问、异常流量给出限速、二次认证或临时隔离建议
防 AI 辅助攻击：检测提示词注入、AI 代理痕迹和 Web 攻击载荷
可视化展示：使用 Plotly 和 Chart.js 生成交互式图表

📊 可视化图表：

- 流量趋势折线图
- 应用类别饼图
- 用户流量排行条形图
- 活跃时段双轴折线图
- 用户标签卡片展示
- 用户应用占比饼图
- 用户协议占比饼图
- 用户活跃时段柱状图
<img width="2000" height="897" alt="image" src="https://github.com/user-attachments/assets/4745c735-1fef-4286-a03b-28b67acef7cb" />
<img width="2000" height="919" alt="image" src="https://github.com/user-attachments/assets/39fd49c5-ffe4-41e8-a8f8-e0a3d8f62536" />
<img width="2000" height="1012" alt="image" src="https://github.com/user-attachments/assets/a1790299-981d-4c6d-be3b-ca2ff7958af4" />
<img width="2000" height="993" alt="image" src="https://github.com/user-attachments/assets/580daecd-0639-4c67-bf4f-56b0dae3ba11" />
<img width="2000" height="591" alt="image" src="https://github.com/user-attachments/assets/a1d1d5f2-d176-4aea-a809-fe75cfee3e3a" />

项目结构

```
流量分析/
│
├── app.py                      # Flask 主程序
├── utils/
│   ├── analysis.py             # 流量数据分析与可视化模块
│   └── user_profile.py         # 用户画像分析模块
├── templates/
│   ├── index.html              # 首页（上传文件）
│   └── dashboard.html          # 仪表板（图表 + 用户画像展示）
├── data/
│   ├── traffic.csv             # 示例流量数据
│   └── user_profiles.json      # 用户画像输出文件
├── static/
│   ├── css/
│   └── js/
├── requirements.txt            # 项目依赖
└── README.md                   # 本文件
```

 环境要求

- Python 3.8 或更高版本
- pip 包管理工具

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

### 2. 安装依赖

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
<img width="1795" height="1123" alt="image" src="https://github.com/user-attachments/assets/f58f2dfb-5fca-4878-bd8f-6e6f5f404280" />
- **查看当前统计**：首页显示已加载数据的基本统计信息
- **上传新数据**：通过文件上传表单上传 CSV 文件
- **查看仪表板**：点击"查看分析仪表板"按钮跳转到详细分析页面

 CSV 文件格式

上传的 CSV 文件应包含以下列（用逗号分隔）：

```
timestamp,src_ip,dst_ip,src_port,dst_port,protocol,bytes,app_category,user
```

 列说明

| 列名 | 说明 | 格式示例 |
|------|------|--------|
| timestamp | 流量时间戳 | `2025-12-01 08:00:15` |
| src_ip | 源IP地址 | `192.168.1.100` |
| dst_ip | 目标IP地址 | `8.8.8.8` |
| src_port | 源端口 | `52341` |
| dst_port | 目标端口 | `53` |
| protocol | 协议类型 | `TCP/UDP` |
| bytes | 流量字节数 | `256` |
| app_category | 应用类别 | `DNS/Social Media/Video Streaming` |
| user | 用户标识 | `student_001` |

 CSV 示例

```csv
timestamp,src_ip,dst_ip,src_port,dst_port,protocol,bytes,app_category,user
2025-12-01 08:00:15,192.168.1.100,8.8.8.8,52341,53,UDP,256,DNS,student_001
2025-12-01 08:00:32,192.168.1.101,142.251.41.14,52456,443,TCP,4096,Social Media,student_002
2025-12-01 08:01:05,192.168.1.102,13.226.123.45,52789,80,TCP,2048,Video Streaming,student_003
```

API 接口

 GET /api/stats

返回 JSON 格式的统计数据

```bash
curl http://localhost:5001/api/stats
```

**响应示例：**

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
export DEEPSEEK_MODEL="deepseek-v4-flash"
export DEEPSEEK_TIMEOUT="20"
```

防 AI 辅助攻击说明：

- 不按 Claude、GPT 等模型名称做单点判断，避免误伤正常用户
- 按行为模式、请求文本、载荷特征和访问频率识别 AI 代理滥用
- 命中高风险时给出 `rate_limit`、`step_up_auth` 或 `quarantine` 建议
- 模块只用于防守审查，不提供攻击实现或绕过方法

## 路由说明

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 - 显示统计信息和文件上传表单 |
| `/dashboard` | GET | 仪表板 - 展示所有分析图表 |
| `/upload` | POST | 处理文件上传 - 上传后自动刷新分析 |
| `/api/stats` | GET | API 接口 - 返回 JSON 格式数据 |
| `/api/ai_security` | GET | API 接口 - 返回本地 AI 安全审查和智能拦截建议 |
| `/api/ai_security/deepseek` | POST | API 接口 - 调用 DeepSeek 进行防守性复核 |

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

# 一次性生成所有图表
generate_all_charts(analyzer)
```

## 模板过滤器

### format_bytes

格式化字节数为易读格式

```html
<!-- 模板中使用 -->
{{ total_bytes | format_bytes }}

<!-- 输出示例 -->
<!-- 1024 -> "1.00 KB" -->
<!-- 1048576 -> "1.00 MB" -->
<!-- 1073741824 -> "1.00 GB" -->
```

 限制和注意事项

- 文件大小限制：最大文件大小 50MB
- 允许格式：仅支持 CSV 格式
- 时间戳格式：必须为 `YYYY-MM-DD HH:MM:SS` 格式
- 默认文件名：上传的文件始终保存为 `traffic.csv`，新文件覆盖旧文件

 故障排除

 问题：模块导入失败

解决方案：
```bash
# 确保已安装所有依赖
pip install -r requirements.txt

# 检查虚拟环境是否已激活
source venv/bin/activate  # macOS/Linux
```

 问题：CSV 文件无法识别

**解决方案：**
- 检查文件格式是否为 CSV
- 确认列名和顺序是否正确
- 验证时间戳格式为 `YYYY-MM-DD HH:MM:SS`

 问题：图表不显示

解决方案：
- 检查是否上传了有效的 CSV 文件
- 查看浏览器控制台是否有错误信息
- 确保 Plotly 库已正确安装

 技术栈

- **后端框架**：Flask 2.3.2
- **数据处理**：Pandas 2.0.3
- **数据可视化**：Plotly 5.15.0
- **前端框架**：Bootstrap 5.1.3
- **服务器**：Werkzeug 2.3.6

 开发与扩展

添加新的分析函数

在 `utils/analysis.py` 中的 `TrafficAnalyzer` 类中添加新方法：

```python
def get_custom_analysis(self):
    """自定义分析函数"""
    # 分析逻辑
    return result
```

 添加新的图表

在 `utils/analysis.py` 中添加新的图表生成函数：

```python
def generate_custom_chart(analyzer):
    """生成自定义图表"""
    data = analyzer.get_custom_analysis()
    
    fig = go.Figure(...)
    fig.update_layout(...)
    
    return fig.to_html(div_id="custom_chart", include_plotlyjs=False)
```

 修改前端样式

编辑 `templates/index.html` 和 `templates/dashboard.html` 中的 CSS 样式。

 用户画像分析模块

 概述

用户画像分析模块（`utils/user_profile.py`）通过分析用户的网络流量行为，自动识别用户特征并生成标签体系。

 标签体系

 应用标签（Application Tags）

| 标签 | 触发条件 | 说明 |
|------|--------|------|
| 游戏狂 | game > 30% | 游戏流量占比超过 30% |
| 视频大户 | video > 40% | 视频流量占比超过 40% |
| 社交达人 | social + chat > 30% | 社交通讯流量占比超过 30% |
| 学习型用户 | edu > 20% | 教育学习流量占比超过 20% |
| 技术用户 | 特殊端口访问次数 > 20 | 频繁访问 22/3389/3306/8000/8080/5000 等端口 |

 时段标签（Time Pattern Tags）

| 标签 | 触发条件 | 说明 |
|------|--------|------|
| 夜猫子 | 22-02 时段流量占比 > 40% | 大部分流量集中在夜间 |
| 早起族 | 06-09 时段流量占比 > 30% | 大部分流量集中在早晨 |
| 规律用户 | 活跃时间方差 < 阈值 | 每日活动时间规律 |
| 波动用户 | 活跃时间方差 > 阈值 | 每日活动时间波动大 |

 安全标签（Security Tags）

| 标签 | 触发条件 | 说明 |
|------|--------|------|
| 可疑扫描 | 多个特殊端口快速访问 | 一个时间段内访问多个特殊端口 |
| 可疑DNS | DNS 查询次数 > 50 | 高频 DNS 查询可能表示域名扫描 |
| 异常活跃时间 | 夜间流量占比 > 60% | 异常的夜间大流量可能表示异常行为 |

用户画像数据结构

输出的 `data/user_profiles.json` 文件格式如下：

```json
{
  "user_001": {
    "tags": ["游戏狂", "夜猫子", "波动用户"],
    "category_pct": {
      "game": 35.5,
      "video": 20.3,
      "social": 15.2,
      "others": 29.0
    },
    "active_hours": {
      "0": {"bytes": 1024000, "count": 10},
      "1": {"bytes": 2048000, "count": 20},
      ...
      "23": {"bytes": 512000, "count": 5}
    },
    "protocol_ratio": {
      "TCP": 70.5,
      "UDP": 29.5
    },
    "port_stats": {
      "22": 5,
      "3389": 2
    },
    "dns_stats": {
      "dns_queries": 45,
      "dns_bytes": 5120
    },
    "daily_bytes": {
      "2025-12-01": 10485760,
      "2025-12-02": 9437184
    }
  },
  ...
}
```

使用用户画像模块

 方法 1：独立运行 Python 脚本

```bash
python utils/user_profile.py
```

这将生成 `data/user_profiles.json` 文件。

 方法 2：在 Flask 中自动生成

当上传新的 CSV 文件或启动 Flask 应用时，会自动生成用户画像数据。

 方法 3：通过 API 获取

```bash
curl http://localhost:5000/api/user_profiles
```

 Dashboard 用户画像可视化

Dashboard 页面新增以下功能：

1. 用户标签卡片
   - 显示前 12 个用户的标签
   - 标签按类型颜色区分（应用/时段/安全标签）
   - 点击卡片可查看用户详情

2. 用户详情面板
   - 应用类别占比饼图
   - 协议占比饼图
   - 每小时活跃度柱状图

3. 交互式操作
   - 鼠标悬停显示卡片阴影效果
   - 点击卡片自动滚动到详情面板
   - 支持实时图表切换

 API 端点

 GET /api/stats

返回流量统计数据

```bash
curl http://localhost:5001/api/stats
```

 GET /api/user_profiles

返回用户画像数据（JSON 格式）

```bash
curl http://localhost:5001/api/user_profiles
```

 性能优化建议

1. **大文件处理**：对超大 CSV 文件可使用 Pandas 的分块读取
2. **缓存**：添加图表缓存机制，避免重复生成
3. **异步处理**：使用 Celery 处理长时间的数据分析任务
4. **增量更新**：只更新新增数据而不是全量重新分析

 安全建议

1. **生产环境**：关闭 `debug=True` 模式
2. **文件上传**：验证上传文件的内容和大小
3. **输入验证**：验证所有用户输入数据
4. **权限控制**：添加用户认证和授权机制
5. **数据隐私**：对敏感信息进行加密和脱敏处理

---

**最后更新**：2025 年 12 月 1 日




## 快速 API 参考

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/stats` | GET | 返回流量统计摘要 |
| `/api/dashboard_data` | GET | 返回仪表板完整数据 |
| `/api/user_profiles` | GET | 返回用户画像数据 |
| `/api/ai_security` | GET | 返回 AI 安全审查报告 |
| `/api/ai_security/deepseek` | POST | 触发 DeepSeek 复核 |
| `/health` | GET | 服务健康检查 |

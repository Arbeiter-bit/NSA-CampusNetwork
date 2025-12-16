# Copilot Prompt 开始
# 项目目录结构如下：
# 流量分析/
# ├─ app.py
# ├─ utils/
# ├─ templates/dashboard.html
# ├─ data/traffic.csv
# ├─ static/
# ├─ README.md

# 我需要在现有工程中增加一个“用户画像分析模块”，请生成完整代码和文档，要求如下：

# 1. Python 模块（utils/user_profile.py）
# - 读取 data/traffic.csv
# - CSV字段: timestamp(YYYY-MM-DD HH:MM:SS), src_ip, dst_ip, src_port, dst_port, protocol, bytes, app_category, user
# - 统计用户特征:
#   - 各 app_category 占比 (game/video/social/chat/edu/web/others)
#   - 每小时活跃度 (0-23)
#   - 协议占比 (TCP/UDP/QUIC)
#   - 端口行为统计 (22, 3389, 3306, 8000, 8080, 5000)
#   - DNS 行为统计 (dst_port == 53)
#   - 每日总流量
# - 根据规则生成用户标签：
#   - 应用标签: 游戏狂(game>30%), 视频大户(video>40%), 社交达人(social/chat>30%), 学习型用户(edu>20%), 技术用户(端口访问次数>20)
#   - 时段标签: 夜猫子(22-02流量占比>40%), 早起族(06-09>30%), 周末活跃用户, 规律用户/波动用户(活跃时间方差)
#   - 安全标签: 可疑扫描(多端口快速访问), 可疑DNS(高频随机子域), 异常活跃时间(突然夜间大流量), 恶意访问(黑名单)
# - 输出 JSON 文件：data/user_profiles.json
# - JSON格式：
# {
#   "user1": {
#       "tags": ["游戏狂","夜猫子","可疑DNS"],
#       "category_pct": {...},
#       "active_hours": {...},
#       "protocol_ratio": {...},
#       "daily_bytes": {...}
#   },
#   ...
# }

# 2. Flask API
# - 在 app.py 中新增 /api/user_profiles 路由
# - 返回 data/user_profiles.json 内容

# 3. Dashboard 可视化
# - 在 templates/dashboard.html 添加：
#   - 用户标签卡片显示（用户名 + 标签列表）
#   - 应用占比饼图 (ECharts)
#   - 活跃时段柱状图 (ECharts)
# - 数据通过 /api/user_profiles 获取
# - 不影响现有 dashboard 功能

# 4. README.md 更新
# - 项目简介
# - 功能说明
# - CSV 数据格式说明
# - 如何运行 Python 模块
# - 如何启动 Flask 服务
# - dashboard.html 使用说明
# - 标签体系说明（应用/时段/安全标签）
# - 输出 JSON 文件说明

# 5. 其他要求
# - 所有代码必须可运行
# - 注释清晰详细
# - 标签系统可扩展
# - Flask 结构兼容现有项目

# Copilot 请根据以上要求生成：
# - utils/user_profile.py
# - app.py 路由修改
# - dashboard.html 可视化组件
# - README.md 更新
# Copilot Prompt 结束
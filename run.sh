#!/bin/bash

# 校园网流量分析系统 - 快速启动脚本

echo "========================================="
echo "   校园网流量分析与可视化系统"
echo "========================================="
echo ""

# 检查 Python 版本
echo "检查 Python 环境..."
python3 --version

# 检查依赖
echo ""
echo "检查依赖包..."
python3 << 'EOF'
import sys
required_packages = ['flask', 'pandas', 'plotly']
missing = []

for package in required_packages:
    try:
        __import__(package)
        print(f"  ✓ {package}")
    except ImportError:
        print(f"  ✗ {package} (缺失)")
        missing.append(package)

if missing:
    print("\n请运行以下命令安装缺失的依赖:")
    print(f"  pip install -r requirements.txt")
    sys.exit(1)
EOF

# 检查数据文件
echo ""
echo "检查数据文件..."
if [ -f "data/traffic.csv" ]; then
    echo "  ✓ data/traffic.csv"
    row_count=$(wc -l < data/traffic.csv)
    echo "    (包含 $((row_count - 1)) 条流量记录)"
else
    echo "  ✗ data/traffic.csv (缺失)"
fi

# 生成用户画像
echo ""
echo "生成用户画像数据..."
python3 utils/user_profile.py

# 启动 Flask 应用
echo ""
echo "========================================="
echo "启动 Flask 应用..."
echo "========================================="
echo ""
echo "📊 访问地址: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python3 app.py

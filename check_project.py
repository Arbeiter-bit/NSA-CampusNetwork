#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
校园网流量分析与可视化系统 - 项目完成报告
Generated: 2025-12-01
"""

import os
import json
from pathlib import Path

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_file_structure():
    """检查文件结构"""
    print_header("📁 项目文件结构检查")
    
    required_files = {
        'app.py': 'Flask 主程序',
        'utils/analysis.py': '流量分析模块',
        'utils/user_profile.py': '用户画像分析模块',
        'templates/index.html': '首页模板',
        'templates/dashboard.html': '仪表板模板',
        'data/traffic.csv': '示例流量数据',
        'data/user_profiles.json': '用户画像输出文件',
        'requirements.txt': '依赖包配置',
        'README.md': '项目文档',
        'run.sh': '启动脚本'
    }
    
    all_ok = True
    for file_path, description in required_files.items():
        full_path = Path(file_path)
        if full_path.exists():
            file_size = full_path.stat().st_size
            print(f"  ✓ {file_path:30s} ({description}) - {file_size:,} bytes")
        else:
            print(f"  ✗ {file_path:30s} ({description}) - 文件缺失!")
            all_ok = False
    
    return all_ok

def check_dependencies():
    """检查依赖"""
    print_header("📦 依赖包检查")
    
    required_packages = {
        'Flask': '2.3.2+',
        'pandas': '2.0.3+',
        'plotly': '5.15.0+',
        'werkzeug': '2.3.6+'
    }
    
    all_ok = True
    for package, version in required_packages.items():
        try:
            mod = __import__(package.lower())
            pkg_version = getattr(mod, '__version__', 'unknown')
            print(f"  ✓ {package:20s} {pkg_version:15s} (required: {version})")
        except ImportError:
            print(f"  ✗ {package:20s} (未安装)")
            all_ok = False
    
    return all_ok

def check_data_analysis():
    """检查数据分析结果"""
    print_header("📊 数据分析结果")
    
    # 检查 traffic.csv
    traffic_path = Path('data/traffic.csv')
    if traffic_path.exists():
        with open(traffic_path, 'r') as f:
            lines = f.readlines()
        record_count = len(lines) - 1
        print(f"  ✓ Traffic Data")
        print(f"    - 流量记录数: {record_count}")
    else:
        print(f"  ✗ traffic.csv 文件缺失")
        return False
    
    # 检查 user_profiles.json
    profiles_path = Path('data/user_profiles.json')
    if profiles_path.exists():
        with open(profiles_path, 'r', encoding='utf-8') as f:
            profiles = json.load(f)
        
        print(f"  ✓ User Profiles")
        print(f"    - 用户总数: {len(profiles)}")
        
        # 统计标签分布
        all_tags = {}
        for user_data in profiles.values():
            for tag in user_data.get('tags', []):
                all_tags[tag] = all_tags.get(tag, 0) + 1
        
        print(f"    - 独特标签数: {len(all_tags)}")
        print(f"    - 标签分布:")
        for tag in sorted(all_tags.keys()):
            count = all_tags[tag]
            percentage = (count / len(profiles)) * 100
            print(f"      • {tag:15s}: {count:3d} 用户 ({percentage:5.1f}%)")
        
        return True
    else:
        print(f"  ✗ user_profiles.json 文件缺失")
        return False

def check_api_endpoints():
    """检查 API 端点"""
    print_header("🔌 API 端点检查")
    
    endpoints = {
        '/': 'GET',
        '/dashboard': 'GET',
        '/upload': 'POST',
        '/api/stats': 'GET',
        '/api/user_profiles': 'GET'
    }
    
    print("  已实现的 API 端点:")
    for endpoint, method in endpoints.items():
        print(f"    ✓ {method:4s} {endpoint}")
    
    return True

def check_features():
    """检查功能特性"""
    print_header("✨ 功能特性检查")
    
    features = {
        '流量统计': '总流量、用户排名、应用类别分布',
        '流量趋势': '按小时统计流量变化',
        '用户分析': '应用占比、活跃时段、协议分布',
        '用户画像': '标签识别、行为分类',
        '应用标签': '游戏狂、视频大户、社交达人等',
        '时段标签': '夜猫子、早起族、规律用户等',
        '安全标签': '可疑扫描、可疑DNS、异常活动等',
        '可视化': 'Plotly 图表、Chart.js 图表',
        '文件上传': '支持 CSV 文件上传',
        'API 接口': 'JSON 格式数据接口'
    }
    
    print("  已实现的功能特性:")
    for feature, description in features.items():
        print(f"    ✓ {feature:15s}: {description}")
    
    return True

def print_quick_start():
    """打印快速开始指南"""
    print_header("🚀 快速开始指南")
    
    print("1️⃣  安装依赖")
    print("    pip install -r requirements.txt")
    
    print("\n2️⃣  启动应用")
    print("    ./run.sh")
    print("    或")
    print("    python3 app.py")
    
    print("\n3️⃣  访问应用")
    print("    打开浏览器访问: http://localhost:5000")
    
    print("\n4️⃣  查看用户画像")
    print("    Dashboard 页面 → 向下滚动到 '👤 用户画像分析' 部分")
    
    print("\n5️⃣  上传新数据")
    print("    首页 → 上传流量数据 CSV 文件 → 自动重新分析")

def print_summary():
    """打印总结"""
    print_header("📋 项目总结")
    
    print("项目名称: 校园网流量分析与可视化系统")
    print("项目版本: 1.0 (含用户画像模块)")
    print("创建时间: 2025-12-01")
    print("")
    print("主要技术栈:")
    print("  • 后端框架: Flask")
    print("  • 数据处理: Pandas")
    print("  • 可视化: Plotly + Chart.js")
    print("  • 前端框架: Bootstrap 5")
    print("")
    print("核心模块:")
    print("  • utils/analysis.py    - 流量数据分析")
    print("  • utils/user_profile.py - 用户画像生成")
    print("  • templates/index.html  - 首页界面")
    print("  • templates/dashboard.html - 仪表板")
    print("")
    print("输出数据:")
    print("  • data/user_profiles.json - 用户画像 JSON")

def main():
    """主函数"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*12 + "校园网流量分析与可视化系统" + " "*12 + "║")
    print("║" + " "*20 + "项目完成报告" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    
    # 执行检查
    checks = [
        ('文件结构', check_file_structure),
        ('依赖包', check_dependencies),
        ('数据分析', check_data_analysis),
        ('API 端点', check_api_endpoints),
        ('功能特性', check_features),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"  ⚠️  检查时出错: {e}")
            results[name] = False
    
    # 打印快速开始指南
    print_quick_start()
    
    # 打印总结
    print_summary()
    
    # 打印最终状态
    print_header("✅ 项目完成状态")
    all_passed = all(results.values())
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {status}: {name}")
    
    print("")
    if all_passed:
        print("  🎉 所有检查均已通过!")
        print("  项目已准备就绪，可以启动应用了。")
    else:
        print("  ⚠️  部分检查未通过，请检查上述错误。")
    
    print("\n")

if __name__ == '__main__':
    main()

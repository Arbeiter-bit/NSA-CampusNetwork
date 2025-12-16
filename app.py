from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import json
from utils.analysis import TrafficAnalyzer, generate_all_charts
from utils.user_profile import UserProfileAnalyzer

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = Path(__file__).parent / 'data'
ALLOWED_EXTENSIONS = {'csv'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传文件夹存在
UPLOAD_FOLDER.mkdir(exist_ok=True)

# 全局分析器
analyzer = None
user_profile_analyzer = None
charts_html = {}
user_profiles = {}


def allowed_file(filename):
    """检查文件是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_analyzer(csv_file=None):
    """加载分析器，并生成所有图表和用户画像"""
    global analyzer, user_profile_analyzer, charts_html, user_profiles
    
    if csv_file is None:
        # 尝试加载默认的 traffic.csv
        csv_path = UPLOAD_FOLDER / 'traffic.csv'
    else:
        csv_path = csv_file
    
    if not csv_path.exists():
        return False
    
    try:
        # 加载流量分析器
        analyzer = TrafficAnalyzer(str(csv_path))
        charts_html = generate_all_charts(analyzer)
        
        # 加载用户画像分析器
        user_profile_analyzer = UserProfileAnalyzer(str(csv_path))
        user_profiles = user_profile_analyzer.analyze_all_users()
        
        # 保存用户画像到 JSON
        profiles_path = UPLOAD_FOLDER / 'user_profiles.json'
        user_profile_analyzer.save_profiles(str(profiles_path))
        
        return True
    except Exception as e:
        print(f"分析器加载失败: {e}")
        return False


@app.route('/')
def index():
    """首页 - 展示基本信息和上传表单"""
    total_traffic = {}
    if analyzer:
        total_traffic = analyzer.get_total_traffic()
    
    return render_template('index.html', total_traffic=total_traffic)


@app.route('/dashboard')
def dashboard():
    """展示所有图表"""
    if not analyzer:
        return redirect(url_for('index'))
    
    total_traffic = analyzer.get_total_traffic()
    user_ranking = analyzer.get_user_traffic_ranking(top_n=10)
    app_category = analyzer.get_app_category_traffic()
    active_hours = analyzer.get_active_hours()
    
    return render_template('dashboard.html',
                          charts_html=charts_html,
                          total_traffic=total_traffic,
                          user_ranking=user_ranking,
                          app_category=app_category,
                          active_hours=active_hours)


@app.route('/upload', methods=['POST'])
def upload():
    """处理文件上传"""
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        return redirect(url_for('index'))
    
    try:
        # 保存文件
        filename = secure_filename('traffic.csv')  # 始终用 traffic.csv
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        # 重新加载分析器
        if load_analyzer(filepath):
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('index'))
    except Exception as e:
        print(f"文件上传失败: {e}")
        return redirect(url_for('index'))


@app.route('/api/stats')
def api_stats():
    """API 接口 - 返回统计数据"""
    if not analyzer:
        return jsonify({})
    
    return jsonify({
        'total_traffic': analyzer.get_total_traffic(),
        'user_ranking': analyzer.get_user_traffic_ranking(),
        'app_category': analyzer.get_app_category_traffic(),
        'active_hours': analyzer.get_active_hours()
    })


@app.route('/api/user_profiles')
def api_user_profiles():
    """API 接口 - 返回用户画像数据"""
    if not user_profiles:
        # 尝试从保存的文件加载
        profiles_path = UPLOAD_FOLDER / 'user_profiles.json'
        if profiles_path.exists():
            try:
                with open(profiles_path, 'r', encoding='utf-8') as f:
                    return jsonify(json.load(f))
            except Exception as e:
                print(f"加载用户画像失败: {e}")
    
    return jsonify(user_profiles)


@app.template_filter('format_bytes')
def format_bytes(bytes_val):
    """格式化字节数"""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 ** 2:
        return f"{bytes_val / 1024:.2f} KB"
    elif bytes_val < 1024 ** 3:
        return f"{bytes_val / (1024 ** 2):.2f} MB"
    else:
        return f"{bytes_val / (1024 ** 3):.2f} GB"


@app.errorhandler(413)
def request_entity_too_large(error):
    """处理文件过大错误"""
    return redirect(url_for('index'))


if __name__ == '__main__':
    # 启动时加载默认分析器
    load_analyzer()
    
    # 启动 Flask 应用
    app.run(debug=True, host='0.0.0.0', port=5001)
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, Response, stream_with_context
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import json
import logging
import threading
from utils.analysis import TrafficAnalyzer, generate_all_charts
from utils.user_profile import UserProfileAnalyzer
from utils.ai_security import AISecurityAnalyzer
from utils.ml_anomaly import detect_anomalies
from utils.realtime import ReplayEngine, stream_events

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = Path(__file__).parent / 'data'
ALLOWED_EXTENSIONS = {'csv'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'nsa-campus-network-dev-key')

UPLOAD_FOLDER.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger('nsa.app')


class AnalyzerState:
    """线程安全的全局分析器状态。

    所有读写都通过 lock 保证一致性，避免并发上传时的状态错乱。
    """

    def __init__(self):
        self._lock = threading.RLock()
        self.analyzer = None
        self.user_profile_analyzer = None
        self.charts_html = {}
        self.user_profiles = {}
        self.ai_security_report = {}
        self.ml_anomaly_report = {}

    def replace(self, analyzer, user_profile_analyzer, charts_html, user_profiles, ai_security_report, ml_anomaly_report):
        with self._lock:
            self.analyzer = analyzer
            self.user_profile_analyzer = user_profile_analyzer
            self.charts_html = charts_html
            self.user_profiles = user_profiles
            self.ai_security_report = ai_security_report
            self.ml_anomaly_report = ml_anomaly_report

    def snapshot(self):
        """返回当前状态的快照，调用方拿到的引用之后即使被替换也不影响本次响应。"""
        with self._lock:
            return {
                'analyzer': self.analyzer,
                'user_profile_analyzer': self.user_profile_analyzer,
                'charts_html': self.charts_html,
                'user_profiles': self.user_profiles,
                'ai_security_report': self.ai_security_report,
                'ml_anomaly_report': self.ml_anomaly_report,
            }

    def update_security_report(self, report):
        with self._lock:
            self.ai_security_report = report

    def update_ml_report(self, report):
        with self._lock:
            self.ml_anomaly_report = report


state = AnalyzerState()


def allowed_file(filename):
    """检查文件是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_analyzer(csv_file=None):
    """加载分析器，并生成所有图表和用户画像。

    成功返回 (True, None)，失败返回 (False, 错误说明)。
    """
    csv_path = csv_file if csv_file is not None else UPLOAD_FOLDER / 'traffic.csv'

    if not csv_path.exists():
        return False, f'未找到 CSV 文件: {csv_path.name}'

    try:
        analyzer = TrafficAnalyzer(str(csv_path))
        if analyzer.df is None or len(analyzer.df) == 0:
            return False, 'CSV 文件为空或解析失败，请检查格式。'

        charts_html = generate_all_charts(analyzer)

        user_profile_analyzer = UserProfileAnalyzer(str(csv_path))
        user_profiles = user_profile_analyzer.analyze_all_users()

        profiles_path = UPLOAD_FOLDER / 'user_profiles.json'
        user_profile_analyzer.save_profiles(str(profiles_path))

        ai_security_report = AISecurityAnalyzer(analyzer.df).generate_report(include_deepseek=False)
        ml_anomaly_report = detect_anomalies(analyzer.df)

        state.replace(
            analyzer=analyzer,
            user_profile_analyzer=user_profile_analyzer,
            charts_html=charts_html,
            user_profiles=user_profiles,
            ai_security_report=ai_security_report,
            ml_anomaly_report=ml_anomaly_report,
        )
        logger.info('分析器加载成功: %s 条记录, %s 个用户, %s 个 ML 异常用户',
                    len(analyzer.df), analyzer.df['user'].nunique(),
                    ml_anomaly_report.get('summary', {}).get('anomaly_users', 0))
        return True, None
    except Exception as exc:
        logger.exception('分析器加载失败')
        return False, f'分析器加载失败: {exc}'


@app.route('/')
def index():
    """首页 - 展示基本信息和上传表单"""
    snap = state.snapshot()
    total_traffic = {}
    if snap['analyzer']:
        total_traffic = snap['analyzer'].get_total_traffic()

    return render_template('index.html', total_traffic=total_traffic)


@app.route('/dashboard')
def dashboard():
    """展示所有图表"""
    snap = state.snapshot()
    analyzer = snap['analyzer']
    if not analyzer:
        flash('请先上传 CSV 流量数据再查看仪表板。', 'warning')
        return redirect(url_for('index'))

    total_traffic = analyzer.get_total_traffic()
    user_ranking = analyzer.get_user_traffic_ranking(top_n=10)
    app_category = analyzer.get_app_category_traffic()
    active_hours = analyzer.get_active_hours()
    attack_map = _attack_map_stats(analyzer, snap['ai_security_report'])

    return render_template('dashboard.html',
                          charts_html=snap['charts_html'],
                          total_traffic=total_traffic,
                          user_ranking=user_ranking,
                          app_category=app_category,
                          active_hours=active_hours,
                          ai_security=snap['ai_security_report'],
                          ml_anomaly=snap['ml_anomaly_report'],
                          attack_map=attack_map)


def _attack_map_stats(analyzer, security_report):
    """生成攻击源追踪面板的摘要指标（基于给定的 analyzer 和报告快照）"""
    if not analyzer or analyzer.df is None or len(analyzer.df) == 0:
        return {'sources': 0, 'top_target': '暂无', 'blocked': 0}

    df = analyzer.df
    sources = df['src_ip'].nunique() if 'src_ip' in df.columns else 0
    blocked = len(security_report.get('blocked_entities', [])) if security_report else 0
    top_target = '暂无'

    if 'dst_port' in df.columns and len(df['dst_port']) > 0:
        top_port = int(df['dst_port'].mode().iloc[0])
        service_names = {
            22: 'SSH', 53: 'DNS', 80: 'HTTP', 443: 'HTTPS',
            3306: 'MySQL', 3389: 'RDP', 6379: 'Redis',
        }
        service = service_names.get(top_port, 'TCP/UDP')
        top_target = f"Port {top_port} ({service})"

    return {'sources': int(sources), 'top_target': top_target, 'blocked': blocked}


@app.route('/upload', methods=['POST'])
def upload():
    """处理文件上传"""
    if 'file' not in request.files:
        flash('未选择文件，请重新上传。', 'danger')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('文件名为空，请选择有效的 CSV 文件。', 'danger')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash('只支持 CSV 格式文件。', 'danger')
        return redirect(url_for('index'))

    try:
        filename = secure_filename('traffic.csv')
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))

        ok, err = load_analyzer(filepath)
        if ok:
            flash('上传并分析完成，已切换到最新数据。', 'success')
            return redirect(url_for('dashboard'))

        flash(err or '上传失败，请检查 CSV 内容。', 'danger')
        return redirect(url_for('index'))
    except Exception as exc:
        logger.exception('文件上传失败')
        flash(f'文件上传失败: {exc}', 'danger')
        return redirect(url_for('index'))


@app.route('/api/stats')
def api_stats():
    """API 接口 - 返回统计数据"""
    snap = state.snapshot()
    analyzer = snap['analyzer']
    if not analyzer:
        return jsonify({'error': 'no_data', 'message': '请先上传 CSV 流量数据。'}), 404

    return jsonify({
        'total_traffic': analyzer.get_total_traffic(),
        'user_ranking': analyzer.get_user_traffic_ranking(),
        'app_category': analyzer.get_app_category_traffic(),
        'active_hours': analyzer.get_active_hours()
    })


@app.route('/api/dashboard_data')
def api_dashboard_data():
    """API 接口 - 返回仪表板前端所需的完整数据"""
    snap = state.snapshot()
    analyzer = snap['analyzer']
    if not analyzer:
        return jsonify({'error': 'no_data', 'message': '请先上传 CSV 流量数据。'}), 404

    security_report = snap['ai_security_report']
    if not security_report:
        security_report = AISecurityAnalyzer(analyzer.df).generate_report(include_deepseek=False)
        state.update_security_report(security_report)

    return jsonify({
        'total_traffic': analyzer.get_total_traffic(),
        'user_ranking': analyzer.get_user_traffic_ranking(top_n=15),
        'app_category': analyzer.get_app_category_traffic(),
        'active_hours': analyzer.get_active_hours(),
        'attack_map': _attack_map_stats(analyzer, security_report),
        'ai_security': security_report,
        'ml_anomaly': snap['ml_anomaly_report'] or detect_anomalies(analyzer.df),
    })


@app.route('/api/user_profiles')
def api_user_profiles():
    """API 接口 - 返回用户画像数据"""
    snap = state.snapshot()
    if snap['user_profiles']:
        return jsonify(snap['user_profiles'])

    profiles_path = UPLOAD_FOLDER / 'user_profiles.json'
    if profiles_path.exists():
        try:
            with open(profiles_path, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except Exception:
            logger.exception('加载用户画像失败')

    return jsonify({})


@app.route('/api/ai_security')
def api_ai_security():
    """API 接口 - 返回 AI 安全审查和智能拦截建议"""
    snap = state.snapshot()
    analyzer = snap['analyzer']
    if not analyzer:
        return jsonify({'error': 'no_data', 'message': '请先上传 CSV 流量数据。'}), 404

    security_report = snap['ai_security_report']
    if not security_report:
        security_report = AISecurityAnalyzer(analyzer.df).generate_report(include_deepseek=False)
        state.update_security_report(security_report)

    return jsonify(security_report)


@app.route('/api/ai_security/deepseek', methods=['POST'])
def api_ai_security_deepseek():
    """API 接口 - 使用 DeepSeek 对本地安全审查结果进行复核"""
    snap = state.snapshot()
    analyzer = snap['analyzer']
    if not analyzer:
        return jsonify({'error': 'no_data', 'message': '请先上传 CSV 流量数据。'}), 404

    # 一次性生成包含 DeepSeek 复核的完整报告，避免重复跑本地规则
    report = AISecurityAnalyzer(analyzer.df).generate_report(include_deepseek=True)
    state.update_security_report(report)
    return jsonify(report)


@app.route('/api/ml_anomaly')
def api_ml_anomaly():
    """API 接口 - 返回 IsolationForest 异常用户检测结果"""
    snap = state.snapshot()
    analyzer = snap['analyzer']
    if not analyzer:
        return jsonify({'error': 'no_data', 'message': '请先上传 CSV 流量数据。'}), 404

    report = snap['ml_anomaly_report']
    if not report:
        report = detect_anomalies(analyzer.df)
        state.update_ml_report(report)
    return jsonify(report)


@app.route('/api/ml_anomaly/refresh', methods=['POST'])
def api_ml_anomaly_refresh():
    """API 接口 - 强制重跑 ML 检测"""
    snap = state.snapshot()
    analyzer = snap['analyzer']
    if not analyzer:
        return jsonify({'error': 'no_data', 'message': '请先上传 CSV 流量数据。'}), 404
    report = detect_anomalies(analyzer.df)
    state.update_ml_report(report)
    return jsonify(report)


@app.route('/realtime')
def realtime_view():
    """实时态势感知大屏页面"""
    snap = state.snapshot()
    if not snap['analyzer']:
        flash('请先上传 CSV 流量数据再进入实时大屏。', 'warning')
        return redirect(url_for('index'))
    return render_template('realtime.html')


@app.route('/api/realtime/start', methods=['POST'])
def api_realtime_start():
    """启动流量回放"""
    snap = state.snapshot()
    analyzer = snap['analyzer']
    if not analyzer:
        return jsonify({'error': 'no_data', 'message': '请先上传 CSV 流量数据。'}), 404

    payload = request.get_json(silent=True) or {}
    rate = float(payload.get('rate', request.args.get('rate', 5.0)))
    loop = bool(payload.get('loop', request.args.get('loop', 'true').lower() != 'false'))
    result = ReplayEngine.instance().start(analyzer.df, rate=rate, loop=loop)
    return jsonify(result)


@app.route('/api/realtime/stop', methods=['POST'])
def api_realtime_stop():
    """停止流量回放"""
    return jsonify(ReplayEngine.instance().stop())


@app.route('/api/realtime/rate', methods=['POST'])
def api_realtime_rate():
    """运行中调整回放速率"""
    payload = request.get_json(silent=True) or {}
    try:
        rate = float(payload.get('rate', request.args.get('rate', 5.0)))
    except (TypeError, ValueError):
        return jsonify({'status': 'error', 'message': '速率参数无效'}), 400
    return jsonify(ReplayEngine.instance().set_rate(rate))


@app.route('/api/realtime/status')
def api_realtime_status():
    """查询回放状态与最新指标"""
    return jsonify(ReplayEngine.instance().status())


@app.route('/api/realtime/stream')
def api_realtime_stream():
    """SSE 事件流：连接后会持续收到 event/metrics/alert/snapshot/finished 五种消息。"""
    stop_event = threading.Event()

    @stream_with_context
    def generate():
        try:
            for chunk in stream_events(stop_event):
                yield chunk
        except GeneratorExit:
            stop_event.set()
            raise

    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response


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
    flash(f'文件过大，单次上传不能超过 {MAX_CONTENT_LENGTH // (1024 * 1024)} MB。', 'danger')
    return redirect(url_for('index'))


if __name__ == '__main__':
    ok, err = load_analyzer()
    if not ok:
        logger.warning('启动时未加载默认数据: %s', err)

    app.run(debug=True, host='0.0.0.0', port=5001)

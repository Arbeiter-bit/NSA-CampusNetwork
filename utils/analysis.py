import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path


class TrafficAnalyzer:
    """校园网流量分析类"""
    
    def __init__(self, csv_path):
        """初始化分析器，加载 CSV 文件"""
        self.csv_path = csv_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        """加载 CSV 文件"""
        try:
            self.df = pd.read_csv(self.csv_path)
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df['hour'] = self.df['timestamp'].dt.hour
            self.df['date'] = self.df['timestamp'].dt.date
            return True
        except Exception as e:
            print(f"数据加载失败: {e}")
            return False
    
    def get_total_traffic(self):
        """获取总流量统计"""
        if self.df is None or len(self.df) == 0:
            return {"total_bytes": 0, "total_packets": 0, "unique_users": 0}
        
        return {
            "total_bytes": int(self.df['bytes'].sum()),
            "total_packets": len(self.df),
            "unique_users": self.df['user'].nunique(),
            "unique_ips": self.df['src_ip'].nunique() + self.df['dst_ip'].nunique()
        }
    
    def get_user_traffic_ranking(self, top_n=10):
        """获取用户流量排名"""
        if self.df is None or len(self.df) == 0:
            return []
        
        user_traffic = self.df.groupby('user')['bytes'].sum().sort_values(ascending=False).head(top_n)
        return [{"user": user, "bytes": int(bytes_val)} for user, bytes_val in user_traffic.items()]
    
    def get_app_category_traffic(self):
        """获取应用类别流量分布"""
        if self.df is None or len(self.df) == 0:
            return []
        
        app_traffic = self.df.groupby('app_category')['bytes'].sum().sort_values(ascending=False)
        return [{"category": cat, "bytes": int(bytes_val)} for cat, bytes_val in app_traffic.items()]
    
    def get_traffic_trend(self, unit='hour'):
        """获取流量趋势
        
        Args:
            unit: 'hour' 按小时, 'minute' 按分钟
        """
        if self.df is None or len(self.df) == 0:
            return []
        
        if unit == 'hour':
            trend = self.df.set_index('timestamp').resample('h')['bytes'].sum()
        else:
            trend = self.df.set_index('timestamp').resample('5T')['bytes'].sum()
        
        result = []
        for timestamp, bytes_val in trend.items():
            result.append({"time": str(timestamp), "bytes": int(bytes_val)})
        return result
    
    def get_active_hours(self):
        """获取活跃时段分析（按小时的用户活跃度）"""
        if self.df is None or len(self.df) == 0:
            return []
        
        # 按小时统计用户活跃度
        hourly_stats = self.df.groupby('hour').agg({
            'user': 'nunique',
            'bytes': 'sum',
            'timestamp': 'count'
        }).reset_index()
        
        hourly_stats.columns = ['hour', 'active_users', 'total_bytes', 'packet_count']
        hourly_stats['hour'] = hourly_stats['hour'].astype(str).str.zfill(2) + ':00'
        
        return hourly_stats.to_dict('records')
    
    def get_user_app_distribution(self, user_id):
        """获取指定用户的应用类别占比"""
        if self.df is None or len(self.df) == 0:
            return []
        
        user_data = self.df[self.df['user'] == user_id]
        if len(user_data) == 0:
            return []
        
        app_dist = user_data.groupby('app_category')['bytes'].sum().sort_values(ascending=False)
        return [{"category": cat, "bytes": int(bytes_val)} for cat, bytes_val in app_dist.items()]


def generate_traffic_trend_chart(analyzer):
    """生成流量趋势折线图（HTML）"""
    trend_data = analyzer.get_traffic_trend('hour')
    
    if not trend_data:
        return "<p>暂无数据</p>"
    
    times = [item['time'] for item in trend_data]
    bytes_vals = [item['bytes'] / (1024**2) for item in trend_data]  # 转换为 MB
    
    fig = go.Figure(data=[
        go.Scatter(
            x=times,
            y=bytes_vals,
            mode='lines+markers',
            name='流量 (MB)',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        )
    ])
    
    fig.update_layout(
        title='流量趋势分析',
        xaxis_title='时间',
        yaxis_title='流量 (MB)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig.to_html(div_id="traffic_trend_chart", include_plotlyjs=False)


def generate_app_category_pie_chart(analyzer):
    """生成应用类别饼图（HTML）"""
    app_data = analyzer.get_app_category_traffic()
    
    if not app_data:
        return "<p>暂无数据</p>"
    
    categories = [item['category'] for item in app_data]
    bytes_vals = [item['bytes'] / (1024**2) for item in app_data]  # 转换为 MB
    
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=bytes_vals,
        hovertemplate='<b>%{label}</b><br>流量: %{value:.2f} MB<extra></extra>'
    )])
    
    fig.update_layout(
        title='应用类别流量分布',
        height=400
    )
    
    return fig.to_html(div_id="app_category_pie_chart", include_plotlyjs=False)


def generate_user_ranking_chart(analyzer):
    """生成用户流量排行条形图（HTML）"""
    user_data = analyzer.get_user_traffic_ranking(top_n=15)
    
    if not user_data:
        return "<p>暂无数据</p>"
    
    users = [item['user'] for item in user_data]
    bytes_vals = [item['bytes'] / (1024**2) for item in user_data]  # 转换为 MB
    
    fig = go.Figure(data=[
        go.Bar(
            y=users,
            x=bytes_vals,
            orientation='h',
            marker=dict(color='#ff7f0e'),
            hovertemplate='<b>%{y}</b><br>流量: %{x:.2f} MB<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title='用户流量排行 TOP 15',
        xaxis_title='流量 (MB)',
        yaxis_title='用户',
        height=450,
        template='plotly_white',
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig.to_html(div_id="user_ranking_chart", include_plotlyjs=False)


def generate_active_hours_chart(analyzer):
    """生成活跃时段折线图（HTML）"""
    active_data = analyzer.get_active_hours()
    
    if not active_data:
        return "<p>暂无数据</p>"
    
    hours = [item['hour'] for item in active_data]
    active_users = [item['active_users'] for item in active_data]
    traffic = [item['total_bytes'] / (1024**2) for item in active_data]  # 转换为 MB
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hours,
        y=active_users,
        name='活跃用户数',
        yaxis='y1',
        line=dict(color='#2ca02c', width=2),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=hours,
        y=traffic,
        name='流量 (MB)',
        yaxis='y2',
        line=dict(color='#d62728', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
    title='活跃时段分析',
    xaxis_title='时间',
    yaxis=dict(
        title=dict(
            text='活跃用户数',
            font=dict(color='#2ca02c')
        ),
        tickfont=dict(color='#2ca02c')
    ),
    yaxis2=dict(
        title=dict(
            text='流量 (MB)',
            font=dict(color='#d62728')
        ),
        tickfont=dict(color='#d62728'),
        anchor='x',
        overlaying='y'
    ),
    hovermode='x unified',
    template='plotly_white',
    height=400,
    legend=dict(x=0.01, y=0.99)
)
    
    return fig.to_html(div_id="active_hours_chart", include_plotlyjs=False)


def generate_all_charts(analyzer):
    """生成所有图表"""
    return {
        'traffic_trend': generate_traffic_trend_chart(analyzer),
        'app_category': generate_app_category_pie_chart(analyzer),
        'user_ranking': generate_user_ranking_chart(analyzer),
        'active_hours': generate_active_hours_chart(analyzer)
    }

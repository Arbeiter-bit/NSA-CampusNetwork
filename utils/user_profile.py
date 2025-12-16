import pandas as pd
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np


class UserProfileAnalyzer:
    """用户画像分析类"""
    
    def __init__(self, csv_path):
        """初始化分析器"""
        self.csv_path = csv_path
        self.df = None
        self.user_profiles = {}
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
    
    def get_user_list(self):
        """获取所有用户"""
        if self.df is None or len(self.df) == 0:
            return []
        return self.df['user'].unique().tolist()
    
    def get_app_category_pct(self, user_id):
        """获取用户应用类别占比"""
        user_data = self.df[self.df['user'] == user_id]
        if len(user_data) == 0:
            return {}
        
        app_traffic = user_data.groupby('app_category')['bytes'].sum()
        total_bytes = app_traffic.sum()
        
        # 标准化类别
        normalized_categories = {
            'game': ['game', 'gaming', 'games'],
            'video': ['video streaming', 'video', 'streaming'],
            'social': ['social media', 'social'],
            'chat': ['chat', 'im', 'instant messaging'],
            'edu': ['education', 'edu', 'learning'],
            'web': ['web browse', 'web', 'http'],
            'dns': ['dns'],
        }
        
        category_pct = {}
        for cat, keywords in normalized_categories.items():
            pct = 0
            for keyword in keywords:
                matching = app_traffic[app_traffic.index.str.lower().str.contains(keyword, na=False)].sum()
                pct += matching
            if pct > 0:
                category_pct[cat] = round(pct / total_bytes * 100, 2)
        
        # 其他类别
        accounted_bytes = sum([user_data.groupby('app_category')['bytes'].sum()[cat]
                               for cat in user_data['app_category'].unique()
                               if any(kw in cat.lower() for kw in [w for keywords in normalized_categories.values() for w in keywords])])
        others_pct = round((total_bytes - accounted_bytes) / total_bytes * 100, 2) if total_bytes > 0 else 0
        if others_pct > 0:
            category_pct['others'] = others_pct
        
        return category_pct
    
    def get_active_hours(self, user_id):
        """获取用户每小时活跃度"""
        user_data = self.df[self.df['user'] == user_id]
        if len(user_data) == 0:
            return {}
        
        hourly_stats = user_data.groupby('hour').agg({
            'bytes': 'sum',
            'timestamp': 'count'
        }).reset_index()
        
        active_hours = {}
        for _, row in hourly_stats.iterrows():
            active_hours[int(row['hour'])] = {
                'bytes': int(row['bytes']),
                'count': int(row['timestamp'])
            }
        
        return active_hours
    
    def get_protocol_ratio(self, user_id):
        """获取用户协议占比"""
        user_data = self.df[self.df['user'] == user_id]
        if len(user_data) == 0:
            return {}
        
        protocol_traffic = user_data.groupby('protocol')['bytes'].sum()
        total_bytes = protocol_traffic.sum()
        
        protocol_ratio = {}
        for protocol, bytes_val in protocol_traffic.items():
            protocol_ratio[protocol] = round(bytes_val / total_bytes * 100, 2)
        
        return protocol_ratio
    
    def get_port_stats(self, user_id):
        """获取用户端口行为统计"""
        user_data = self.df[self.df['user'] == user_id]
        if len(user_data) == 0:
            return {}
        
        suspicious_ports = [22, 3389, 3306, 8000, 8080, 5000]
        port_stats = {}
        
        for port in suspicious_ports:
            count = len(user_data[user_data['dst_port'] == port])
            if count > 0:
                port_stats[port] = count
        
        return port_stats
    
    def get_dns_stats(self, user_id):
        """获取用户 DNS 行为统计"""
        user_data = self.df[self.df['user'] == user_id]
        if len(user_data) == 0:
            return {"dns_queries": 0, "dns_bytes": 0}
        
        dns_data = user_data[user_data['dst_port'] == 53]
        
        return {
            "dns_queries": len(dns_data),
            "dns_bytes": int(dns_data['bytes'].sum())
        }
    
    def get_daily_bytes(self, user_id):
        """获取用户每日总流量"""
        user_data = self.df[self.df['user'] == user_id]
        if len(user_data) == 0:
            return {}
        
        daily_stats = user_data.groupby('date')['bytes'].sum()
        
        daily_bytes = {}
        for date, bytes_val in daily_stats.items():
            daily_bytes[str(date)] = int(bytes_val)
        
        return daily_bytes
    
    def generate_tags(self, user_id):
        """根据用户特征生成标签"""
        tags = []
        
        # 获取用户数据
        app_pct = self.get_app_category_pct(user_id)
        active_hours = self.get_active_hours(user_id)
        port_stats = self.get_port_stats(user_id)
        dns_stats = self.get_dns_stats(user_id)
        daily_bytes = self.get_daily_bytes(user_id)
        
        user_data = self.df[self.df['user'] == user_id]
        total_bytes = user_data['bytes'].sum()
        
        # ========== 应用标签 ==========
        if app_pct.get('game', 0) > 30:
            tags.append('游戏狂')
        
        if app_pct.get('video', 0) > 40:
            tags.append('视频大户')
        
        if (app_pct.get('social', 0) + app_pct.get('chat', 0)) > 30:
            tags.append('社交达人')
        
        if app_pct.get('edu', 0) > 20:
            tags.append('学习型用户')
        
        if len(port_stats) > 0 and sum(port_stats.values()) > 20:
            tags.append('技术用户')
        
        # ========== 时段标签 ==========
        night_hours_bytes = sum([active_hours.get(h, {}).get('bytes', 0) 
                                 for h in list(range(22, 24)) + list(range(0, 3))])
        night_ratio = night_hours_bytes / total_bytes * 100 if total_bytes > 0 else 0
        
        if night_ratio > 40:
            tags.append('夜猫子')
        
        morning_hours_bytes = sum([active_hours.get(h, {}).get('bytes', 0) 
                                   for h in range(6, 10)])
        morning_ratio = morning_hours_bytes / total_bytes * 100 if total_bytes > 0 else 0
        
        if morning_ratio > 30:
            tags.append('早起族')
        
        # 计算活跃时间方差
        if len(active_hours) > 1:
            hour_bytes = [active_hours.get(h, {}).get('bytes', 0) for h in range(24)]
            variance = np.var(hour_bytes)
            if variance < np.var(hour_bytes) * 0.5:
                tags.append('规律用户')
            else:
                tags.append('波动用户')
        
        # ========== 安全标签 ==========
        # 多端口快速访问 - 可疑扫描
        if len(port_stats) >= 3:
            tags.append('可疑扫描')
        
        # 高频 DNS 查询 - 可疑DNS
        if dns_stats['dns_queries'] > 50:
            tags.append('可疑DNS')
        
        # 夜间异常活跃
        if night_ratio > 60:
            tags.append('异常活跃时间')
        
        return list(set(tags))  # 去重
    
    def analyze_all_users(self):
        """分析所有用户生成完整画像"""
        users = self.get_user_list()
        
        for user_id in users:
            self.user_profiles[user_id] = {
                'tags': self.generate_tags(user_id),
                'category_pct': self.get_app_category_pct(user_id),
                'active_hours': self.get_active_hours(user_id),
                'protocol_ratio': self.get_protocol_ratio(user_id),
                'port_stats': self.get_port_stats(user_id),
                'dns_stats': self.get_dns_stats(user_id),
                'daily_bytes': self.get_daily_bytes(user_id),
            }
        
        return self.user_profiles
    
    def save_profiles(self, output_path):
        """保存用户画像为 JSON 文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_profiles, f, ensure_ascii=False, indent=2)
            print(f"用户画像已保存至: {output_path}")
            return True
        except Exception as e:
            print(f"保存用户画像失败: {e}")
            return False
    
    def load_profiles(self, input_path):
        """从 JSON 文件加载用户画像"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                self.user_profiles = json.load(f)
            print(f"用户画像已从以下文件加载: {input_path}")
            return True
        except Exception as e:
            print(f"加载用户画像失败: {e}")
            return False


def generate_user_profiles(csv_path, output_path=None):
    """生成用户画像（便利函数）"""
    analyzer = UserProfileAnalyzer(csv_path)
    analyzer.analyze_all_users()
    
    if output_path:
        analyzer.save_profiles(output_path)
    
    return analyzer.user_profiles


if __name__ == '__main__':
    # 使用示例
    csv_path = Path(__file__).parent.parent / 'data' / 'traffic.csv'
    output_path = Path(__file__).parent.parent / 'data' / 'user_profiles.json'
    
    if csv_path.exists():
        profiles = generate_user_profiles(str(csv_path), str(output_path))
        print(f"\n成功分析 {len(profiles)} 个用户")
        
        # 打印示例用户画像
        if profiles:
            first_user = list(profiles.keys())[0]
            print(f"\n示例用户 {first_user} 的画像:")
            print(json.dumps(profiles[first_user], ensure_ascii=False, indent=2))
    else:
        print(f"CSV 文件未找到: {csv_path}")

"""基于 IsolationForest 的用户行为异常检测。

把每个用户的流量行为压成固定维度的特征向量，用孤立森林无监督地识别
"看起来跟大多数人不一样"的用户，作为规则引擎的补充。

设计原则：
- 不替代规则引擎，而是给规则引擎找不到的隐性异常打分。
- 输出可解释字段：每个异常用户附带触发该评分的关键特征。
- 与 AISecurityAnalyzer 输出结构对齐，方便前端统一渲染。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


SUSPICIOUS_PORTS = {21, 22, 23, 25, 53, 135, 139, 445, 1433, 1521,
                    3306, 3389, 5432, 5900, 6379, 9200, 27017}


# 特征顺序固定，方便后续解释
FEATURE_NAMES = [
    "total_bytes",
    "total_packets",
    "unique_dst_ips",
    "unique_dst_ports",
    "suspicious_port_hits",
    "night_byte_ratio",
    "dns_query_count",
    "max_hour_bytes",
    "active_hour_count",
    "avg_bytes_per_packet",
]


@dataclass
class AnomalyConfig:
    contamination: float = 0.1     # 预期异常用户比例
    random_state: int = 42
    top_n: int = 10                # 最多返回多少异常用户
    min_users: int = 5             # 用户数低于此值不跑模型


class MLAnomalyDetector:
    """基于 IsolationForest 的用户级异常检测。"""

    def __init__(self, df: Optional[pd.DataFrame], config: Optional[AnomalyConfig] = None):
        self.df = df.copy() if df is not None else pd.DataFrame()
        self.config = config or AnomalyConfig()

    def detect(self) -> Dict[str, Any]:
        if self.df.empty or "user" not in self.df.columns:
            return self._empty_report("数据为空或缺少 user 列。")

        try:
            features_df = self._build_features()
        except Exception as exc:
            logger.exception("ML 特征构造失败")
            return self._empty_report(f"特征构造失败: {exc}")

        if len(features_df) < self.config.min_users:
            return self._empty_report(
                f"用户数 {len(features_df)} 少于 {self.config.min_users}，跳过 ML 检测。"
            )

        try:
            from sklearn.ensemble import IsolationForest
            from sklearn.preprocessing import StandardScaler
        except ImportError:
            return self._empty_report("scikit-learn 未安装，已跳过 ML 检测。")

        feature_matrix = features_df[FEATURE_NAMES].to_numpy(dtype=float)
        scaler = StandardScaler()
        scaled = scaler.fit_transform(feature_matrix)

        # 自动收缩 contamination 防止用户少时报错
        contamination = min(self.config.contamination, max(1 / len(features_df), 0.01))

        model = IsolationForest(
            n_estimators=120,
            contamination=contamination,
            random_state=self.config.random_state,
        )
        model.fit(scaled)
        raw_scores = model.score_samples(scaled)        # 越小越异常
        predictions = model.predict(scaled)              # -1 异常, 1 正常

        # 归一化为 0-100 风险分数：异常用户越远离正常分布，分数越高
        normalized = self._normalize_scores(raw_scores)
        features_df = features_df.assign(
            anomaly_score=normalized,
            is_anomaly=(predictions == -1),
        )

        anomalies = (
            features_df[features_df["is_anomaly"]]
            .sort_values("anomaly_score", ascending=False)
            .head(self.config.top_n)
        )

        anomaly_records = [self._format_record(row) for _, row in anomalies.iterrows()]
        normal_count = int((~features_df["is_anomaly"]).sum())

        return {
            "status": "ok",
            "model": "IsolationForest",
            "config": {
                "contamination": round(contamination, 4),
                "n_estimators": 120,
                "feature_count": len(FEATURE_NAMES),
            },
            "summary": {
                "total_users": int(len(features_df)),
                "anomaly_users": int(features_df["is_anomaly"].sum()),
                "normal_users": normal_count,
                "max_score": float(round(features_df["anomaly_score"].max(), 2)),
                "median_score": float(round(features_df["anomaly_score"].median(), 2)),
            },
            "anomalies": anomaly_records,
            "feature_names": FEATURE_NAMES,
        }

    def _build_features(self) -> pd.DataFrame:
        df = self.df.copy()

        # 标准化字段
        for col in ["bytes", "src_port", "dst_port"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df["hour"] = df["timestamp"].dt.hour.fillna(0).astype(int)

        # 缺失列补默认值
        for col in ["dst_ip", "dst_port", "protocol"]:
            if col not in df.columns:
                df[col] = "unknown"
        if "hour" not in df.columns:
            df["hour"] = 0

        df["is_night"] = df["hour"].between(0, 5)
        df["is_dns"] = df["dst_port"] == 53
        df["is_suspicious_port"] = df["dst_port"].isin(SUSPICIOUS_PORTS)

        per_user_hour = df.groupby(["user", "hour"])["bytes"].sum().unstack(fill_value=0)
        max_hour_bytes = per_user_hour.max(axis=1)
        active_hour_count = (per_user_hour > 0).sum(axis=1)

        agg = df.groupby("user").agg(
            total_bytes=("bytes", "sum"),
            total_packets=("bytes", "count"),
            unique_dst_ips=("dst_ip", "nunique"),
            unique_dst_ports=("dst_port", "nunique"),
            suspicious_port_hits=("is_suspicious_port", "sum"),
            dns_query_count=("is_dns", "sum"),
            night_bytes=("bytes", lambda s: s[df.loc[s.index, "is_night"]].sum()),
        )

        agg["night_byte_ratio"] = np.where(
            agg["total_bytes"] > 0,
            agg["night_bytes"] / agg["total_bytes"],
            0.0,
        )
        agg["max_hour_bytes"] = max_hour_bytes.reindex(agg.index, fill_value=0)
        agg["active_hour_count"] = active_hour_count.reindex(agg.index, fill_value=0)
        agg["avg_bytes_per_packet"] = np.where(
            agg["total_packets"] > 0,
            agg["total_bytes"] / agg["total_packets"],
            0.0,
        )

        return agg[FEATURE_NAMES].fillna(0).astype(float)

    @staticmethod
    def _normalize_scores(raw_scores: np.ndarray) -> np.ndarray:
        """把 IsolationForest 的 score_samples（越小越异常）映射到 0-100。"""
        if len(raw_scores) == 0:
            return raw_scores
        inverted = -raw_scores
        lo, hi = float(inverted.min()), float(inverted.max())
        if hi - lo < 1e-9:
            return np.full_like(inverted, 50.0)
        scaled = (inverted - lo) / (hi - lo) * 100.0
        return np.round(scaled, 2)

    @staticmethod
    def _format_record(row: pd.Series) -> Dict[str, Any]:
        feature_dict = {name: float(round(row[name], 2)) for name in FEATURE_NAMES}
        # 选出该用户最突出的 3 个特征作为人话解释
        zscore = (
            (row[FEATURE_NAMES] - row[FEATURE_NAMES].mean())
            / (row[FEATURE_NAMES].std(ddof=0) or 1.0)
        )
        top_features = zscore.abs().sort_values(ascending=False).head(3).index.tolist()
        evidence = [
            f"{name}={feature_dict[name]:.2f}"
            for name in top_features
        ]
        return {
            "user": str(row.name),
            "anomaly_score": float(row["anomaly_score"]),
            "severity": _severity_from_score(float(row["anomaly_score"])),
            "evidence": evidence,
            "features": feature_dict,
        }

    @staticmethod
    def _empty_report(message: str) -> Dict[str, Any]:
        return {
            "status": "skipped",
            "message": message,
            "model": "IsolationForest",
            "summary": {
                "total_users": 0,
                "anomaly_users": 0,
                "normal_users": 0,
                "max_score": 0.0,
                "median_score": 0.0,
            },
            "anomalies": [],
            "feature_names": FEATURE_NAMES,
        }


def _severity_from_score(score: float) -> str:
    if score >= 85:
        return "critical"
    if score >= 70:
        return "high"
    if score >= 50:
        return "medium"
    return "low"


def detect_anomalies(df: pd.DataFrame, config: Optional[AnomalyConfig] = None) -> Dict[str, Any]:
    """便利函数。"""
    return MLAnomalyDetector(df, config).detect()

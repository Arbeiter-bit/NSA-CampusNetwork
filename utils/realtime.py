"""流量回放与实时事件总线。

把已上传的 CSV 当成回放素材，按可配置速率推送给前端，模拟真实
态势感知系统的实时数据流。前端通过 SSE (Server-Sent Events)
订阅事件，无需额外 WebSocket 依赖。

设计要点：
- 单例 ReplayEngine，整个应用进程共享一个回放线程。
- pub/sub：每个 SSE 客户端拿到一个 queue，引擎广播到所有 queue。
- 边推送边维护近 N 条窗口与近 M 分钟流量趋势，避免前端自己重算。
- 触发简易实时告警（端口扫描、大流量、敏感端口），让大屏看起来"会动"。
"""

from __future__ import annotations

import json
import logging
import queue
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, Iterable, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


SUSPICIOUS_PORTS = {21, 22, 23, 25, 53, 135, 139, 445, 1433, 1521,
                    3306, 3389, 5432, 5900, 6379, 9200, 27017}

WINDOW_SIZE = 200            # 大屏右侧"事件流"保留的最近事件数
TRAFFIC_BUCKETS = 30         # 实时折线图保留的桶数
BUCKET_SECONDS = 5           # 每个桶 5 秒，30 桶覆盖最近 2.5 分钟
PORT_SCAN_THRESHOLD = 6      # 同一源 IP 在 30 秒内访问的不同端口数
PORT_SCAN_WINDOW = 30        # 秒
LARGE_FLOW_BYTES = 50_000    # 单条流量超过此值视为大流量事件


@dataclass
class ReplayMetrics:
    """回放过程中累计的实时指标。"""
    sent_events: int = 0
    total_bytes: int = 0
    unique_users: set = field(default_factory=set)
    unique_src_ips: set = field(default_factory=set)
    alerts_triggered: int = 0
    started_at: Optional[float] = None
    last_event_at: Optional[float] = None

    def snapshot(self) -> Dict[str, Any]:
        return {
            "sent_events": self.sent_events,
            "total_bytes": int(self.total_bytes),
            "unique_users": len(self.unique_users),
            "unique_src_ips": len(self.unique_src_ips),
            "alerts_triggered": self.alerts_triggered,
            "started_at": self.started_at,
            "last_event_at": self.last_event_at,
        }


class ReplayEngine:
    """线程安全的流量回放引擎，单例。"""

    _instance: Optional["ReplayEngine"] = None
    _instance_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.RLock()
        self._thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._subscribers: List[queue.Queue] = []
        self._df: Optional[pd.DataFrame] = None
        self._rate: float = 5.0          # 每秒事件数
        self._loop: bool = True
        self._metrics = ReplayMetrics()
        self._recent_events: Deque[Dict[str, Any]] = deque(maxlen=WINDOW_SIZE)
        self._traffic_buckets: Deque[Dict[str, Any]] = deque(maxlen=TRAFFIC_BUCKETS)
        self._port_seen: Dict[str, Deque] = defaultdict(lambda: deque(maxlen=64))

    @classmethod
    def instance(cls) -> "ReplayEngine":
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    # ----- 控制接口 ----------------------------------------------------

    def start(self, df: pd.DataFrame, rate: float = 5.0, loop: bool = True) -> Dict[str, Any]:
        with self._lock:
            if self.is_running():
                return {"status": "already_running", "message": "回放线程已在运行。"}
            if df is None or df.empty:
                return {"status": "error", "message": "数据为空，无法启动回放。"}

            self._df = self._prepare(df)
            self._rate = max(0.5, float(rate))
            self._loop = bool(loop)
            self._stop_flag.clear()
            self._reset_state()
            self._metrics.started_at = time.time()

            self._thread = threading.Thread(target=self._run, name="replay-engine", daemon=True)
            self._thread.start()
            logger.info("流量回放已启动: rate=%.1f loop=%s rows=%d", self._rate, self._loop, len(self._df))
            return {"status": "started", "rate": self._rate, "loop": self._loop, "rows": len(self._df)}

    def stop(self) -> Dict[str, Any]:
        with self._lock:
            if not self.is_running():
                return {"status": "not_running"}
            self._stop_flag.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("流量回放已停止")
        return {"status": "stopped"}

    def set_rate(self, rate: float) -> Dict[str, Any]:
        """运行中即时改速率，无需重启。"""
        with self._lock:
            self._rate = max(0.5, float(rate))
        logger.info("回放速率已调整: %.1f/s", self._rate)
        return {"status": "ok", "rate": self._rate}

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive() and not self._stop_flag.is_set()

    def status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "running": self.is_running(),
                "rate": self._rate,
                "loop": self._loop,
                "subscribers": len(self._subscribers),
                "metrics": self._metrics.snapshot(),
                "recent_events": list(self._recent_events)[-20:],
                "traffic_buckets": list(self._traffic_buckets),
            }

    # ----- 订阅接口 ----------------------------------------------------

    def subscribe(self) -> queue.Queue:
        q: queue.Queue = queue.Queue(maxsize=512)
        with self._lock:
            self._subscribers.append(q)
            # 新订阅者先收到一份"快照"，避免大屏空白
            try:
                q.put_nowait({"type": "snapshot", "payload": self.status()})
            except queue.Full:
                pass
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    # ----- 内部实现 ----------------------------------------------------

    def _prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in ["bytes", "src_port", "dst_port"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        for col in ["user", "src_ip", "dst_ip", "protocol", "app_category"]:
            if col not in df.columns:
                df[col] = "unknown"
            else:
                df[col] = df[col].fillna("unknown").astype(str)
        return df.reset_index(drop=True)

    def _reset_state(self) -> None:
        self._metrics = ReplayMetrics(started_at=self._metrics.started_at)
        self._recent_events.clear()
        self._traffic_buckets.clear()
        self._port_seen.clear()

    def _run(self) -> None:
        assert self._df is not None
        try:
            while not self._stop_flag.is_set():
                for _, row in self._df.iterrows():
                    if self._stop_flag.is_set():
                        break
                    event = self._build_event(row)
                    self._update_state(event)
                    self._broadcast({"type": "event", "payload": event})
                    self._broadcast({"type": "metrics", "payload": self.status()})
                    # 每次循环重新读取 rate，运行中改速率才能即时生效
                    interval = 1.0 / max(0.5, self._rate)
                    time.sleep(interval)
                if not self._loop:
                    break
        except Exception:
            logger.exception("回放线程异常退出")
        finally:
            self._broadcast({"type": "finished", "payload": self._metrics.snapshot()})

    def _build_event(self, row: pd.Series) -> Dict[str, Any]:
        bytes_val = int(row.get("bytes", 0))
        return {
            "ts": time.time(),
            "user": str(row.get("user", "unknown")),
            "src_ip": str(row.get("src_ip", "unknown")),
            "dst_ip": str(row.get("dst_ip", "unknown")),
            "src_port": int(row.get("src_port", 0)),
            "dst_port": int(row.get("dst_port", 0)),
            "protocol": str(row.get("protocol", "unknown")),
            "bytes": bytes_val,
            "app_category": str(row.get("app_category", "unknown")),
        }

    def _update_state(self, event: Dict[str, Any]) -> None:
        with self._lock:
            self._metrics.sent_events += 1
            self._metrics.total_bytes += event["bytes"]
            self._metrics.unique_users.add(event["user"])
            self._metrics.unique_src_ips.add(event["src_ip"])
            self._metrics.last_event_at = event["ts"]
            self._recent_events.append(event)

            self._update_buckets(event)
            alerts = self._check_alerts(event)
            for alert in alerts:
                self._metrics.alerts_triggered += 1
                self._broadcast({"type": "alert", "payload": alert})

    def _update_buckets(self, event: Dict[str, Any]) -> None:
        bucket_ts = int(event["ts"] // BUCKET_SECONDS) * BUCKET_SECONDS
        if not self._traffic_buckets:
            self._traffic_buckets.append({"ts": bucket_ts, "bytes": 0, "events": 0})
        last_ts = self._traffic_buckets[-1]["ts"]
        # 当前事件落在新桶里，先把中间空缺的桶补 0，避免曲线变成稀疏直线
        if bucket_ts > last_ts:
            next_ts = last_ts + BUCKET_SECONDS
            while next_ts < bucket_ts:
                self._traffic_buckets.append({"ts": next_ts, "bytes": 0, "events": 0})
                next_ts += BUCKET_SECONDS
            self._traffic_buckets.append({"ts": bucket_ts, "bytes": 0, "events": 0})
        cur = self._traffic_buckets[-1]
        cur["bytes"] += event["bytes"]
        cur["events"] += 1

    def _check_alerts(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []
        now = event["ts"]

        # 端口扫描：同一源 IP 在窗口期内访问超过阈值数量的不同端口
        seen = self._port_seen[event["src_ip"]]
        seen.append((now, event["dst_port"]))
        recent = [(ts, p) for ts, p in seen if now - ts <= PORT_SCAN_WINDOW]
        unique_ports = {p for _, p in recent}
        if len(unique_ports) >= PORT_SCAN_THRESHOLD:
            alerts.append({
                "ts": now,
                "level": "high",
                "title": "实时端口扫描",
                "entity": event["src_ip"],
                "detail": f"30 秒内访问 {len(unique_ports)} 个不同端口",
            })
            seen.clear()  # 触发后清空，避免连环刷屏

        # 单条大流量
        if event["bytes"] >= LARGE_FLOW_BYTES:
            alerts.append({
                "ts": now,
                "level": "medium",
                "title": "大流量突发",
                "entity": event["user"],
                "detail": f"单条 {event['bytes']} 字节，目标 {event['dst_ip']}:{event['dst_port']}",
            })

        # 敏感端口访问
        if event["dst_port"] in SUSPICIOUS_PORTS:
            alerts.append({
                "ts": now,
                "level": "medium",
                "title": "敏感端口访问",
                "entity": f"{event['user']} / {event['src_ip']}",
                "detail": f"目标端口 {event['dst_port']}",
            })

        return alerts

    def _broadcast(self, message: Dict[str, Any]) -> None:
        with self._lock:
            dead: List[queue.Queue] = []
            for q in self._subscribers:
                try:
                    q.put_nowait(message)
                except queue.Full:
                    dead.append(q)
            for q in dead:
                self._subscribers.remove(q)


def sse_format(message: Dict[str, Any]) -> str:
    """把消息序列化为 SSE 格式。"""
    return f"event: {message.get('type', 'message')}\ndata: {json.dumps(message.get('payload'), ensure_ascii=False)}\n\n"


def stream_events(stop_event: threading.Event, heartbeat_interval: float = 15.0) -> Iterable[str]:
    """供 Flask 路由调用：订阅引擎并产出 SSE 字符串。"""
    engine = ReplayEngine.instance()
    q = engine.subscribe()
    try:
        last_heartbeat = time.time()
        while not stop_event.is_set():
            try:
                msg = q.get(timeout=1.0)
                yield sse_format(msg)
            except queue.Empty:
                pass

            now = time.time()
            if now - last_heartbeat >= heartbeat_interval:
                yield ": heartbeat\n\n"
                last_heartbeat = now
    finally:
        engine.unsubscribe(q)

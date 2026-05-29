import json
import os
import re
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd


SENSITIVE_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    110: "POP3",
    135: "RPC",
    139: "NetBIOS",
    143: "IMAP",
    389: "LDAP",
    445: "SMB",
    1433: "SQL Server",
    1521: "Oracle",
    2375: "Docker API",
    2379: "etcd",
    2380: "etcd Peer",
    3306: "MySQL",
    3389: "RDP",
    4848: "GlassFish Admin",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    6443: "Kubernetes API",
    9200: "Elasticsearch",
    10250: "Kubelet",
    27017: "MongoDB",
}

PROMPT_INJECTION_TERMS = [
    "ignore previous",
    "ignore all previous",
    "system prompt",
    "developer message",
    "jailbreak",
    "bypass policy",
    "disable safety",
    "reveal prompt",
    "泄露提示词",
    "忽略以上",
    "越狱",
    "绕过安全",
]

AI_AGENT_TERMS = [
    "claude",
    "anthropic",
    "openai",
    "gpt",
    "llm",
    "autogen",
    "langchain",
    "agent",
    "browser-use",
]

WEB_ATTACK_TERMS = [
    "union select",
    "' or '1'='1",
    " or 1=1",
    "../",
    "%2e%2e",
    "<script",
    "onerror=",
    "cmd.exe",
    "/bin/sh",
    "powershell",
    "base64",
]


@dataclass
class DeepSeekConfig:
    api_key: Optional[str]
    base_url: str
    model: str
    timeout: int

    @classmethod
    def from_env(cls) -> "DeepSeekConfig":
        return cls(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            timeout=int(os.getenv("DEEPSEEK_TIMEOUT", "20")),
        )


class DeepSeekSecurityReviewer:
    """Use DeepSeek for defensive review of summarized traffic findings."""

    def __init__(self, config: Optional[DeepSeekConfig] = None):
        self.config = config or DeepSeekConfig.from_env()

    def is_configured(self) -> bool:
        return bool(self.config.api_key)

    def review(self, local_report: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "enabled": False,
                "status": "missing_api_key",
                "message": "未配置 DEEPSEEK_API_KEY，已使用本地安全规则完成审查。",
            }

        request_body = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是校园网蓝队防护系统的安全审查员。"
                        "只做防御性分析，不提供攻击步骤、利用代码或绕过方案。"
                        "请根据本地规则报告判断是否存在入侵、自动化扫描、AI 代理滥用或提示词注入风险。"
                        "必须返回纯 JSON。"
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "task": "review_campus_network_traffic_security",
                            "local_report": self._compact_report(local_report),
                            "required_json_schema": {
                                "risk_level": "low|medium|high|critical",
                                "summary": "string",
                                "attack_hypotheses": ["string"],
                                "recommended_blocks": ["string"],
                                "recommended_actions": ["string"],
                            },
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "temperature": 0.2,
            "max_tokens": 900,
            "response_format": {"type": "json_object"},
        }

        try:
            data = json.dumps(request_body).encode("utf-8")
            req = urllib.request.Request(
                self.config.base_url.rstrip("/") + "/chat/completions",
                data=data,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            context = ssl.create_default_context()
            started = time.time()
            with urllib.request.urlopen(req, timeout=self.config.timeout, context=context) as resp:
                raw = resp.read().decode("utf-8")
            elapsed_ms = int((time.time() - started) * 1000)
            parsed = json.loads(raw)
            content = parsed["choices"][0]["message"]["content"]
            return {
                "enabled": True,
                "status": "ok",
                "model": self.config.model,
                "latency_ms": elapsed_ms,
                "result": self._parse_json_content(content),
            }
        except (urllib.error.URLError, TimeoutError) as exc:
            return {
                "enabled": True,
                "status": "network_error",
                "message": f"DeepSeek 审查请求失败: {exc}",
            }
        except Exception as exc:
            return {
                "enabled": True,
                "status": "error",
                "message": f"DeepSeek 审查解析失败: {exc}",
            }

    def _compact_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "summary": report.get("summary", {}),
            "top_alerts": report.get("alerts", [])[:8],
            "blocked_entities": report.get("blocked_entities", [])[:8],
            "ai_attack_defense": report.get("ai_attack_defense", {}),
        }

    def _parse_json_content(self, content: str) -> Dict[str, Any]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.S)
            if match:
                return json.loads(match.group(0))
            return {"summary": content}


class AISecurityAnalyzer:
    """Local defensive analytics for attack review and smart interception advice."""

    def __init__(self, df: Optional[pd.DataFrame]):
        self.df = df.copy() if df is not None else pd.DataFrame()
        self.alerts: List[Dict[str, Any]] = []
        self.blocked_entities: List[Dict[str, Any]] = []

    def generate_report(self, include_deepseek: bool = False) -> Dict[str, Any]:
        self._prepare_data()
        if self.df.empty:
            report = {
                "summary": {
                    "risk_level": "low",
                    "risk_score": 0,
                    "total_alerts": 0,
                    "critical_alerts": 0,
                    "high_alerts": 0,
                    "deepseek_configured": DeepSeekSecurityReviewer().is_configured(),
                },
                "alerts": [],
                "blocked_entities": [],
                "ai_attack_defense": self._ai_defense_summary(),
                "deepseek_review": {"status": "not_run"},
            }
            return report

        self._detect_port_scanning()
        self._detect_sensitive_service_access()
        self._detect_volume_anomalies()
        self._detect_unusual_hour_activity()
        self._detect_ai_assisted_attack_indicators()
        self._build_blocklist()

        summary = self._build_summary()
        report = {
            "summary": summary,
            "alerts": sorted(self.alerts, key=lambda item: item["score"], reverse=True),
            "blocked_entities": self.blocked_entities,
            "ai_attack_defense": self._ai_defense_summary(),
            "deepseek_review": {"status": "not_run"},
        }

        if include_deepseek:
            report["deepseek_review"] = DeepSeekSecurityReviewer().review(report)

        return report

    def _prepare_data(self) -> None:
        if self.df.empty:
            return

        if "timestamp" in self.df.columns:
            self.df["timestamp"] = pd.to_datetime(self.df["timestamp"], errors="coerce")
            self.df["hour"] = self.df["timestamp"].dt.hour

        for col in ["bytes", "src_port", "dst_port"]:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce").fillna(0).astype(int)

        for col in ["user", "src_ip", "dst_ip", "protocol", "app_category"]:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna("unknown").astype(str)

    def _detect_port_scanning(self) -> None:
        required = {"user", "src_ip", "dst_ip", "dst_port", "timestamp"}
        if not required.issubset(self.df.columns):
            return

        grouped = self.df.groupby(["user", "src_ip"]).agg(
            packet_count=("dst_port", "count"),
            unique_ports=("dst_port", "nunique"),
            unique_targets=("dst_ip", "nunique"),
            total_bytes=("bytes", "sum"),
        )

        for (user, src_ip), row in grouped.iterrows():
            packet_count = int(row["packet_count"])
            unique_ports = int(row["unique_ports"])
            unique_targets = int(row["unique_targets"])
            if unique_ports >= 8 or unique_targets >= 10 or (packet_count >= 40 and unique_ports >= 5):
                score = min(95, 45 + unique_ports * 4 + unique_targets * 3)
                self._add_alert(
                    alert_type="reconnaissance",
                    severity=self._severity(score),
                    score=score,
                    title="疑似横向扫描或端口探测",
                    entity=f"{user} / {src_ip}",
                    evidence=[
                        f"访问目标端口数: {unique_ports}",
                        f"访问目标 IP 数: {unique_targets}",
                        f"连接记录数: {packet_count}",
                    ],
                    suggested_action="建议临时限速该源 IP，并要求二次确认后加入隔离名单。",
                    block_target={"type": "src_ip", "value": src_ip},
                )

    def _detect_sensitive_service_access(self) -> None:
        required = {"user", "src_ip", "dst_ip", "dst_port"}
        if not required.issubset(self.df.columns):
            return

        sensitive_df = self.df[self.df["dst_port"].isin(SENSITIVE_PORTS.keys())]
        if sensitive_df.empty:
            return

        grouped = sensitive_df.groupby(["user", "src_ip", "dst_port"]).agg(
            hits=("dst_ip", "count"),
            targets=("dst_ip", "nunique"),
        )

        for (user, src_ip, port), row in grouped.iterrows():
            hits = int(row["hits"])
            targets = int(row["targets"])
            if hits >= 3 or targets >= 2:
                score = min(90, 38 + hits * 5 + targets * 8)
                service = SENSITIVE_PORTS.get(int(port), "sensitive service")
                self._add_alert(
                    alert_type="sensitive_service",
                    severity=self._severity(score),
                    score=score,
                    title=f"敏感服务访问异常: {service}/{port}",
                    entity=f"{user} / {src_ip}",
                    evidence=[f"命中次数: {hits}", f"目标数量: {targets}"],
                    suggested_action="建议核验该用户是否有运维授权；无授权时加入临时拦截策略。",
                    block_target={"type": "src_ip", "value": src_ip},
                )

    def _detect_volume_anomalies(self) -> None:
        required = {"user", "bytes"}
        if not required.issubset(self.df.columns):
            return

        user_bytes = self.df.groupby("user")["bytes"].sum().sort_values(ascending=False)
        if len(user_bytes) < 2:
            return

        median_bytes = max(int(user_bytes.median()), 1)
        for user, total_bytes in user_bytes.head(5).items():
            total_bytes = int(total_bytes)
            ratio = total_bytes / median_bytes
            if ratio >= 5 and total_bytes >= 10 * 1024 * 1024:
                score = min(85, int(35 + ratio * 6))
                self._add_alert(
                    alert_type="traffic_anomaly",
                    severity=self._severity(score),
                    score=score,
                    title="用户流量显著高于基线",
                    entity=str(user),
                    evidence=[
                        f"用户总流量: {self._format_bytes(total_bytes)}",
                        f"约为中位用户的 {ratio:.1f} 倍",
                    ],
                    suggested_action="建议先限速并复核下载、视频或备份任务，避免误封正常高流量业务。",
                    block_target={"type": "user", "value": str(user)},
                )

    def _detect_unusual_hour_activity(self) -> None:
        required = {"user", "hour", "bytes"}
        if not required.issubset(self.df.columns):
            return

        night_df = self.df[self.df["hour"].between(0, 5, inclusive="both")]
        if night_df.empty:
            return

        grouped = night_df.groupby("user").agg(
            packets=("bytes", "count"),
            total_bytes=("bytes", "sum"),
        )
        for user, row in grouped.iterrows():
            packets = int(row["packets"])
            total_bytes = int(row["total_bytes"])
            if packets >= 10 or total_bytes >= 5 * 1024 * 1024:
                score = min(78, 36 + packets * 2)
                self._add_alert(
                    alert_type="off_hours_activity",
                    severity=self._severity(score),
                    score=score,
                    title="非活跃时段异常通信",
                    entity=str(user),
                    evidence=[
                        f"凌晨通信记录数: {packets}",
                        f"凌晨流量: {self._format_bytes(total_bytes)}",
                    ],
                    suggested_action="建议与课程/实验时间表比对；不匹配时触发二次身份验证。",
                    block_target={"type": "user", "value": str(user)},
                )

    def _detect_ai_assisted_attack_indicators(self) -> None:
        text_columns = self._text_columns()
        if not text_columns:
            return

        combined = self.df[text_columns].astype(str).agg(" ".join, axis=1).str.lower()
        prompt_hits = combined.apply(lambda text: self._matched_terms(text, PROMPT_INJECTION_TERMS))
        ai_agent_hits = combined.apply(lambda text: self._matched_terms(text, AI_AGENT_TERMS))
        web_attack_hits = combined.apply(lambda text: self._matched_terms(text, WEB_ATTACK_TERMS))

        for idx, terms in prompt_hits[prompt_hits.map(bool)].items():
            self._row_indicator_alert(
                idx,
                terms,
                "prompt_injection",
                "疑似提示词注入或 AI 安全绕过文本",
                "建议隔离该请求并转人工复核，避免把外部输入直接送入自动化 AI 工具。",
                82,
            )

        for idx, terms in ai_agent_hits[ai_agent_hits.map(bool)].items():
            self._row_indicator_alert(
                idx,
                terms,
                "ai_agent_activity",
                "疑似 AI 代理或自动化工具访问痕迹",
                "建议叠加频率限制、设备指纹和行为验证码，按行为而不是模型名称拦截。",
                64,
            )

        for idx, terms in web_attack_hits[web_attack_hits.map(bool)].items():
            self._row_indicator_alert(
                idx,
                terms,
                "web_payload_attack",
                "疑似 Web 攻击载荷或命令执行痕迹",
                "建议阻断该源并检查目标系统日志，确认是否有成功利用迹象。",
                88,
            )

    def _row_indicator_alert(
        self,
        idx: int,
        terms: List[str],
        alert_type: str,
        title: str,
        suggested_action: str,
        score: int,
    ) -> None:
        row = self.df.loc[idx]
        src_ip = str(row.get("src_ip", "unknown"))
        user = str(row.get("user", "unknown"))
        self._add_alert(
            alert_type=alert_type,
            severity=self._severity(score),
            score=score,
            title=title,
            entity=f"{user} / {src_ip}",
            evidence=[f"命中特征: {', '.join(terms[:5])}"],
            suggested_action=suggested_action,
            block_target={"type": "src_ip", "value": src_ip},
        )

    def _build_blocklist(self) -> None:
        candidates: Dict[str, Dict[str, Any]] = {}
        for alert in self.alerts:
            if alert["score"] < 70:
                continue
            target = alert.get("block_target")
            if not target:
                continue
            key = f"{target['type']}:{target['value']}"
            current = candidates.setdefault(
                key,
                {
                    "target_type": target["type"],
                    "target": target["value"],
                    "max_score": 0,
                    "reasons": [],
                    "action": "monitor",
                },
            )
            current["max_score"] = max(current["max_score"], alert["score"])
            current["reasons"].append(alert["title"])

        for item in candidates.values():
            if item["max_score"] >= 85:
                item["action"] = "quarantine"
                item["ttl_minutes"] = 30
            elif item["max_score"] >= 75:
                item["action"] = "rate_limit"
                item["ttl_minutes"] = 15
            else:
                item["action"] = "step_up_auth"
                item["ttl_minutes"] = 10
            item["reasons"] = sorted(set(item["reasons"]))

        self.blocked_entities = sorted(
            candidates.values(),
            key=lambda item: item["max_score"],
            reverse=True,
        )

    def _build_summary(self) -> Dict[str, Any]:
        if not self.alerts:
            risk_score = 0
        else:
            risk_score = min(100, max(alert["score"] for alert in self.alerts))
        return {
            "risk_level": self._severity(risk_score),
            "risk_score": risk_score,
            "total_alerts": len(self.alerts),
            "critical_alerts": sum(1 for alert in self.alerts if alert["severity"] == "critical"),
            "high_alerts": sum(1 for alert in self.alerts if alert["severity"] == "high"),
            "deepseek_configured": DeepSeekSecurityReviewer().is_configured(),
        }

    def _ai_defense_summary(self) -> Dict[str, Any]:
        return {
            "strategy": "按行为、载荷和访问模式识别 AI 辅助攻击，不按 Claude、GPT 等模型名称做单点判断。",
            "controls": [
                "提示词注入检测：识别忽略规则、泄露提示词、越狱等文本特征。",
                "AI 代理检测：识别自动化代理、LLM 工具链和异常高频访问痕迹。",
                "本地规则兜底：端口扫描、敏感服务访问、异常流量和非活跃时段通信。",
                "智能拦截建议：根据风险分数给出限速、二次认证或临时隔离策略。",
                "DeepSeek 复核：只上传汇总风险和少量证据，不上传完整原始流量。",
            ],
            "note": "该模块用于防守审查与拦截建议，不提供攻击实现或绕过方法。",
        }

    def _text_columns(self) -> List[str]:
        preferred = [
            "payload",
            "request",
            "uri",
            "url",
            "path",
            "query",
            "user_agent",
            "message",
            "log",
            "app_category",
            "protocol",
            "user",
        ]
        return [col for col in preferred if col in self.df.columns]

    def _matched_terms(self, text: str, terms: List[str]) -> List[str]:
        return [term for term in terms if term in text]

    def _add_alert(
        self,
        alert_type: str,
        severity: str,
        score: int,
        title: str,
        entity: str,
        evidence: List[str],
        suggested_action: str,
        block_target: Optional[Dict[str, str]] = None,
    ) -> None:
        self.alerts.append(
            {
                "id": f"SEC-{len(self.alerts) + 1:04d}",
                "type": alert_type,
                "severity": severity,
                "score": int(score),
                "title": title,
                "entity": entity,
                "evidence": evidence,
                "suggested_action": suggested_action,
                "block_target": block_target,
            }
        )

    def _severity(self, score: int) -> str:
        if score >= 90:
            return "critical"
        if score >= 70:
            return "high"
        if score >= 40:
            return "medium"
        return "low"

    def _format_bytes(self, value: int) -> str:
        value = float(value)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if value < 1024:
                return f"{value:.2f} {unit}"
            value /= 1024
        return f"{value:.2f} PB"

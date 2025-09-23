from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Deque, Dict, List


@dataclass
class AuditEvent:
    ts: str
    actor: str | None
    action: str
    target: str | None
    meta: Dict[str, object] | None


_events: Deque[AuditEvent] = deque(maxlen=1000)


def record_event(action: str, actor: str | None = None, target: str | None = None, meta: Dict[str, object] | None = None) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    _events.append(AuditEvent(ts=ts, actor=actor, action=action, target=target, meta=meta))


def recent_events(limit: int = 100) -> List[Dict[str, object]]:
    items = list(_events)
    return [asdict(e) for e in items[-limit:]]
"""共通監査ログ（簡易インメモリ）。\nイベント記録と直近取得のヘルパーを提供する。"""

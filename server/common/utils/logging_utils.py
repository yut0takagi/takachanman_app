import logging
from collections import deque
from dataclasses import dataclass, asdict
from typing import Deque, Dict, List, Optional


@dataclass
class LogRecord:
    name: str
    level: str
    message: str
    created: float


class RingBufferHandler(logging.Handler):
    def __init__(self, capacity: int = 1000) -> None:
        super().__init__()
        self.buffer: Deque[LogRecord] = deque(maxlen=capacity)

    def emit(self, record: logging.LogRecord) -> None:  # type: ignore[override]
        try:
            msg = self.format(record)
        except Exception:  # pragma: no cover
            msg = record.getMessage()
        self.buffer.append(
            LogRecord(name=record.name, level=record.levelname, message=msg, created=record.created)
        )


_handler: Optional[RingBufferHandler] = None


def register_handler(capacity: int = 1000) -> None:
    global _handler
    if _handler is not None:
        return
    _handler = RingBufferHandler(capacity=capacity)
    _handler.setLevel(logging.INFO)
    # Attach to root and uvicorn loggers
    root = logging.getLogger()
    root.addHandler(_handler)
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logging.getLogger(name).addHandler(_handler)


def get_logs(limit: int = 200, level: Optional[str] = None) -> List[Dict[str, object]]:
    if _handler is None:
        return []
    items = list(_handler.buffer)
    if level:
        level = level.upper()
        items = [r for r in items if r.level == level]
    return [asdict(r) for r in items[-limit:]]


def set_log_level(name: str, level: str) -> None:
    logging.getLogger(name).setLevel(level.upper())


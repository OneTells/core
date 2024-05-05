from dataclasses import dataclass

from utils.modules.worker.utils.limit_args import LimitArgs


@dataclass(slots=True, frozen=True)
class Setting:
    timeout: float
    executor_count: int
    limited_args: LimitArgs | None = None
    timeout_reset: float = 180

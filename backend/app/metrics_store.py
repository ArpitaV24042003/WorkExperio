from __future__ import annotations

from dataclasses import dataclass
from threading import Lock


@dataclass
class MetricsSnapshot:
	total_requests: int
	total_duration_ms: int

	@property
	def average_duration_ms(self) -> float:
		if self.total_requests == 0:
			return 0.0
		return self.total_duration_ms / self.total_requests


class MetricsStore:
	def __init__(self) -> None:
		self._lock = Lock()
		self._total_requests = 0
		self._total_duration_ms = 0

	def record_request(self, duration_ms: int) -> None:
		with self._lock:
			self._total_requests += 1
			self._total_duration_ms += duration_ms

	def snapshot(self) -> MetricsSnapshot:
		with self._lock:
			return MetricsSnapshot(
				total_requests=self._total_requests,
				total_duration_ms=self._total_duration_ms,
			)


metrics_store = MetricsStore()


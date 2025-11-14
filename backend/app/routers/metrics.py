from fastapi import APIRouter

from ..metrics_store import metrics_store
from ..schemas import MetricsResponse

router = APIRouter()


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics():
	snapshot = metrics_store.snapshot()
	return MetricsResponse(
		total_requests=snapshot.total_requests,
		average_duration_ms=round(snapshot.average_duration_ms, 2),
	)


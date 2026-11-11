from fastapi import APIRouter, status

from anibattle.api.health.schemas import HealthCheckResponse

router = APIRouter(prefix="/api/health")


@router.get(
    "/",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Returns the health status of the application.",
)
async def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(status="ok")

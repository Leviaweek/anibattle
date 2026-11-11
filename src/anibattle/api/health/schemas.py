from typing import Literal

from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: ServiceStatus


type ServiceStatus = Literal["ok", "error"]

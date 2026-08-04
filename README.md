import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.src.service.AgentService import AgentService
from app.src.models.ValidationResponse import ValidationResponse
from app.src.config.Config import settings

logger = logging.getLogger(__name__)

AgentRouter = APIRouter(
    prefix=settings.app.context_path,
    tags=["Agent"]
)

agent_service = AgentService()


class ValidationRequest(BaseModel):
    document_path: str


@AgentRouter.post(
    "/validate",
    response_model=ValidationResponse
)
def validate_document(request: ValidationRequest):

    try:
        logger.info(f"Validating document : {request.document_path}")

        return agent_service.validate_document(
            document_path=request.document_path
        )

    except Exception as ex:
        logger.exception(ex)
        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.deps import get_current_user
from backend.app.graph.ResumeGraph import ResumeGraph
from backend.app.models.user import User
from backend.app.schemas.generate import GenerateResumeRequest, GenerateResumeResponse

logger = logging.getLogger("app.resume")

router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)

# Build the LangGraph orchestrator once and reuse it across requests.
_resume_graph = ResumeGraph().build()


@router.post(
    "/generate",
    response_model=GenerateResumeResponse,
)
async def generate_resume(
    data: GenerateResumeRequest,
    current_user: User = Depends(get_current_user),
):
    logger.info(
        "resume_generation_started",
        extra={"user_id": current_user.id},
    )

    try:
        result = await _resume_graph.ainvoke(
            {
                "resume_text": data.resume_text,
                "job_description": data.job_description,
            }
        )
    except Exception:
        logger.exception(
            "resume_generation_failed",
            extra={"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume generation failed. Please try again.",
        )

    logger.info(
        "resume_generation_completed",
        extra={"user_id": current_user.id},
    )

    return GenerateResumeResponse(
        profile_analysis=result["profile_analysis"],
        ats_analysis=result["ats_analysis"],
        generated_resume=result["generated_resume"],
        review_result=result["review_result"],
    )
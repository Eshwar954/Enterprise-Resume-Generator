import logging

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from backend.app.api.deps import get_current_user
from backend.app.graph.ResumeGraph import ResumeGraph
from backend.app.models.user import User
from backend.app.schemas.generate import GenerateResumeResponse
from backend.app.services.document_parser import extract_text

logger = logging.getLogger("app.resume")

router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)

# Build the LangGraph orchestrator once and reuse it.
_resume_graph = ResumeGraph().build()


@router.post(
    "/generate",
    response_model=GenerateResumeResponse,
)
async def generate_resume(
    resume_file: UploadFile = File(...),
    jd_file: UploadFile = File(...),
    company_name: str = Form(...),
    role_name: str = Form(...),
    notes: str = Form(""),
    current_user: User = Depends(get_current_user),
):
    logger.info(
        "resume_generation_started",
        extra={
            "user_id": current_user.id,
            "resume_filename": resume_file.filename,
            "jd_filename": jd_file.filename,
        },
    )

    try:
        resume_text = await extract_text(resume_file)
        job_description = await extract_text(jd_file)

        if not resume_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The uploaded resume contains no readable text.",
            )

        if not job_description.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The uploaded job description contains no readable text.",
            )

        # Keep the existing LangGraph contract intact.
        # The graph currently consumes resume_text and job_description.
        result = await _resume_graph.ainvoke(
            {
                "resume_text": resume_text,
                "job_description": job_description,
            }
        )

    except HTTPException:
        raise

    except ValueError as exc:
        logger.warning(
            "resume_input_invalid",
            extra={"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "resume_generation_failed",
            extra={"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume generation failed. Please try again.",
        ) from exc

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

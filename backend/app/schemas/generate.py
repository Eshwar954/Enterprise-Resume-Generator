from pydantic import BaseModel, Field

from backend.app.schemas.ats import ATSAnalysis
from backend.app.schemas.profile import ProfileAnalysis
from backend.app.schemas.resume import GeneratedResume
from backend.app.schemas.review import ReviewResult


class GenerateResumeRequest(BaseModel):
    resume_text: str = Field(min_length=1)
    job_description: str = Field(min_length=1)


class GenerateResumeResponse(BaseModel):
    profile_analysis: ProfileAnalysis
    ats_analysis: ATSAnalysis
    generated_resume: GeneratedResume
    review_result: ReviewResult
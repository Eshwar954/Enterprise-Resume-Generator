from typing import TypedDict
from backend.app.schemas import (
ProfileAnalysis,
ATSAnalysis,
GeneratedResume,
ReviewResult,
)

class ResumeState(TypedDict, total=False):
    resume_text: str
    job_description: str

    profile_analysis: ProfileAnalysis
    ats_analysis: ATSAnalysis

    generated_resume: GeneratedResume

    review_result: ReviewResult
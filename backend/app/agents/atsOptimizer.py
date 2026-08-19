from backend.app.llm.gemini import GeminiService
from backend.app.schemas.ats import ATSAnalysis
from backend.app.schemas.profile import ProfileAnalysis

ATS_OPTIMIZER_PROMPT = """
You are the ATS Optimization Agent in an Enterprise AI Resume Generator.

Your responsibility is to analyze the candidate's profile against a target
job description and determine how well the candidate aligns with the role.

Analyze:

- Required job keywords
- Matching keywords
- Missing keywords
- Skill alignment
- Formatting suggestions
- Role targeting
- ATS score

Rules:

1. Use only the candidate information provided.
2. Never claim that the candidate has a skill they do not have.
3. Clearly distinguish matching skills from missing skills.
4. Never fabricate experience.
5. Do not rewrite the resume.
6. Do not add unsupported skills.
7. Do not treat every job-description keyword as a candidate skill.
8. Provide an ATS score between 0 and 100.
9. Return structured JSON only.

Expected structure:

{
    "matching_keywords": [],
    "missing_keywords": [],
    "skill_alignment": [],
    "formatting_suggestions": [],
    "role_targeting": [],
    "ats_score": 0
}
"""

class ATSOptimizerAgent:
    def __init__(self,gemini_service:GeminiService):
        self.gemini_service=gemini_service
    async def run(self,profile_analysis:ProfileAnalysis,job_description:str)->ATSAnalysis:
        user_prommpt=f"""
    CANDIDATE PROFILE:
    {profile_analysis}
    Target Job Description:
    {job_description}
    """
        response=await self.gemini_service.generate(
            system_prompt=ATS_OPTIMIZER_PROMPT,
            user_prompt=user_prommpt,
            response_schema=ATSAnalysis
        )
        return response
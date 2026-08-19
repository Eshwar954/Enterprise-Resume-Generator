from backend.app.llm.gemini import GeminiService
from backend.app.schemas.resume import GeneratedResume
from backend.app.schemas.profile import ProfileAnalysis
from backend.app.schemas.ats import ATSAnalysis
RESUME_WRITER_PROMPT = """
You are the Resume Writer Agent in an Enterprise AI Resume Generator.

Your responsibility is to generate professional resume content using:

- Original candidate profile
- Profile analysis
- ATS analysis
- Target job description

Generate:

- Professional summary
- Experience bullets
- Skills section
- Project descriptions

Rules:

1. Never fabricate information.
2. Never fabricate companies or job titles.
3. Never fabricate technologies.
4. Never fabricate certifications.
5. Never fabricate metrics or achievements.
6. Preserve the factual information from the original profile.
7. Improve clarity, professionalism, and relevance.
8. Align the resume with the target role only when supported by the
   candidate's actual experience.
9. Do not add a skill merely because it appears in the job description.
10. Do not remove important candidate information without justification.
11. Return structured JSON only.
12. A technology may only be associated with a project if that technology
    is explicitly present in the original candidate profile or clearly
    supported by the source project information.

13. Do not transfer general candidate skills into a project's technology
    list unless the source explicitly associates that technology with the
    project.

14. Do not introduce responsibilities or outcomes that are not supported
    by the candidate's source information.

15. Rephrasing factual information is allowed; adding new factual claims
    is not.

Expected structure:

{
    "professional_summary": "...",
    "experience": [],
    "skills": [],
    "projects": [],
    "education": [],
    "certifications": []
}
"""

class ResumeWriterAgent:
    def __init__(self,gemini_service:GeminiService):
        self.gemini_service = gemini_service
    async def run(self,resume_text:str,profile_analysis:ProfileAnalysis,ats_analysis:ATSAnalysis,job_description:str)->GeneratedResume:
        user_prompt = f"""
        ORIGINAL CANDIDATE PROFILE:

        {resume_text}


        PROFILE ANALYSIS:

        {profile_analysis}


        ATS ANALYSIS:

        {ats_analysis}


        TARGET JOB DESCRIPTION:

        {job_description}
        """
        response=await self.gemini_service.generate(
            system_prompt=RESUME_WRITER_PROMPT,
            user_prompt=user_prompt,
            response_schema=GeneratedResume
        )
        return response
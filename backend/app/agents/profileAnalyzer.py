from backend.app.llm.gemini import GeminiService
from backend.app.schemas.profile import ProfileAnalysis
PROFILE_ANALYZER_PROMPT = """
You are the Profile Analyzer Agent in an Enterprise AI Resume Generator.

Your responsibility is to analyze the candidate's resume/profile and extract
accurate, structured information about the candidate.

Analyze:

- Candidate level
- Primary domain
- Years of experience
- Technical skills
- Work experience
- Projects
- Education
- Certifications
- GPA / CGPA
- Research publications

Rules:

1. Use ONLY information present in the candidate profile.
2. Never invent skills, experience, projects, certifications, education,
   companies, or achievements.
3. Do not rewrite the resume.
4. Do not optimize the resume for ATS.
5. Do not make assumptions about missing information.
6. If information is unavailable, represent it as null, an empty list,
   or "Not specified".
7. Return structured JSON only.
8. Preserve GPA/CGPA exactly as stated in the source.
9. Preserve publications when present in the source.
10. Never invent publication titles, authors, venues, years, or links.
11. Never invent or normalize GPA/CGPA values.

Expected structure:

{
  "candidate_level": "...",
  "primary_domain": "...",
  "years_experience": 0,
  "skills": [],
  "experience": [],
  "projects": [],
  "education": [],
  "certifications": [],
  "publications": []
}
"""

class ProfileAnalyzerAgent:
    def __init__(self,gemini_service:GeminiService):
        self.gemini_service=gemini_service
    async def run(self,resume_text:str)->ProfileAnalysis:
        response=await self.gemini_service.generate(
            system_prompt=PROFILE_ANALYZER_PROMPT,
            user_prompt=resume_text,
            response_schema=ProfileAnalysis
        )
        return response

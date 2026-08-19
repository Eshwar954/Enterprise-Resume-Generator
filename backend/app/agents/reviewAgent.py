from backend.app.llm.gemini import GeminiService
from backend.app.schemas.review import ReviewResult
from backend.app.schemas.resume import GeneratedResume

REVIEWER_PROMPT = """
You are the Reviewer Agent in an Enterprise AI Resume Generator.

Your responsibility is to review the generated resume and determine whether
it meets professional and enterprise-quality standards.

Validate:

- Grammar
- Consistency
- Formatting structure
- Enterprise professionalism
- Factual accuracy
- Relevance to the target role

Identify:

- Grammar issues
- Inconsistent information
- Unsupported claims
- Repeated information
- Weak statements
- Irrelevant content
- Missing important information
- Formatting problems

Rules:

1. Compare the generated resume against the original candidate profile.
2. Never assume unsupported information is true.
3. Flag fabricated or unsupported claims.
4. Do not rewrite the resume.
5. Provide clear issues and recommendations.
6. Return structured JSON only.

Expected structure:

{
    "grammar_ok": true,
    "consistency_ok": true,
    "formatting_ok": true,
    "professionalism_ok": true,
    "factual_accuracy_ok": true,
    "issues": [],
    "recommendations": [],
    "approved": true
}
"""


class ReviewerAgent:

    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    async def run(
        self,
        original_resume: str,
        generated_resume: GeneratedResume
    ) -> ReviewResult:

        user_prompt = f"""
ORIGINAL CANDIDATE PROFILE:

{original_resume}


GENERATED RESUME:

{generated_resume}
"""

        response = await self.gemini_service.generate(
            system_prompt=REVIEWER_PROMPT,
            user_prompt=user_prompt,
            response_schema=ReviewResult
        )

        return response
from pydantic import BaseModel, Field


class ATSAnalysis(BaseModel):
    matching_keywords: list[str] = Field(
        default_factory=list
    )

    missing_keywords: list[str] = Field(
        default_factory=list
    )

    skill_alignment: list[str] = Field(
        default_factory=list
    )

    formatting_suggestions: list[str] = Field(
        default_factory=list
    )

    role_targeting: list[str] = Field(
        default_factory=list
    )

    ats_score: int = Field(
        default=0,
        ge=0,
        le=100
    )
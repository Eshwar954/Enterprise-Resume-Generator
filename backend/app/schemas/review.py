from pydantic import BaseModel, Field


class ReviewResult(BaseModel):
    grammar_ok: bool = False

    consistency_ok: bool = False

    formatting_ok: bool = False

    professionalism_ok: bool = False

    factual_accuracy_ok: bool = False

    issues: list[str] = Field(
        default_factory=list
    )

    recommendations: list[str] = Field(
        default_factory=list
    )

    approved: bool = False
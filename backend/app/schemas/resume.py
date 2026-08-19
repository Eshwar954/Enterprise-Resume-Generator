from pydantic import BaseModel, Field


class ResumeExperience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    bullets: list[str] = Field(default_factory=list)


class ResumeProject(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)


class ResumeEducation(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    duration: str | None = None


class GeneratedResume(BaseModel):
    professional_summary: str

    experience: list[ResumeExperience] = Field(
        default_factory=list
    )

    skills: list[str] = Field(
        default_factory=list
    )

    projects: list[ResumeProject] = Field(
        default_factory=list
    )

    education: list[ResumeEducation] = Field(
        default_factory=list
    )

    certifications: list[str] = Field(
        default_factory=list
    )
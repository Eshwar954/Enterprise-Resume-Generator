from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    description: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    name: str
    description: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    url: str | None = None


class EducationItem(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    duration: str | None = None
    cgpa: str | None = None


class PublicationItem(BaseModel):
    title: str
    authors: str | None = None
    venue: str | None = None
    year: str | None = None
    status: str | None = None
    url: str | None = None
    description: str | None = None


class ProfileAnalysis(BaseModel):
    candidate_level: str | None = None
    primary_domain: str | None = None
    years_experience: int = 0

    skills: list[str] = Field(
        default_factory=list
    )

    experience: list[ExperienceItem] = Field(
        default_factory=list
    )

    projects: list[ProjectItem] = Field(
        default_factory=list
    )

    education: list[EducationItem] = Field(
        default_factory=list
    )

    certifications: list[str] = Field(
        default_factory=list
    )

    publications: list[PublicationItem] = Field(
        default_factory=list
    )

    achievements: list[str] = Field(
        default_factory=list
    )
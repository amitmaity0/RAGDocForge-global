from pydantic import BaseModel, Field, computed_field


class QualityDimensionScore(BaseModel):
    name: str
    score: int
    max_score: int = 5
    explanation: str


class QualityReport(BaseModel):
    doc_id: str
    source_file: str
    raw_score: int | None = None
    overall_score: int
    readiness_level: str
    dimensions: list[QualityDimensionScore]
    strengths: list[str] = Field(default_factory=list)
    blocking_issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)
    score_cap_reasons: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def final_score(self) -> int:
        return self.overall_score

from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from src.constants import CandidateLevel


class CodeReviewBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        json_encoders={Enum: lambda v: v.name.lower()},
    )


class ReviewResponse(CodeReviewBase):
    found_files: List[str]
    comments: List[str]
    rating: float
    conclusion: str


class ReviewRequest(CodeReviewBase):
    assigment_description: str = Field(
        ..., description='Description of the coding assignment'
    )
    github_repo_url: str = Field(
        ..., description='URL of the GitHub repository to review'
    )
    candidate_level: CandidateLevel = Field(
        ..., description="The candidate's skill level (Junior, Middle, or Senior)"
    )


class TextFile(CodeReviewBase):
    path: str
    content: str = None


class ReviewInAI(CodeReviewBase):
    assigment_description: str
    candidate_level: CandidateLevel
    text_files: List[TextFile]

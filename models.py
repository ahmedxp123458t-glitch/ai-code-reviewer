from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Language(str, Enum):
    python = "python"
    javascript = "javascript"


class ReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000)
    language: Language


class BugIssue(BaseModel):
    line: int
    message: str
    severity: str  # high, medium, low
    type: str


class SecurityIssue(BaseModel):
    line: int
    message: str
    severity: str
    cwe: Optional[str] = None


class Suggestion(BaseModel):
    line: Optional[int] = None
    message: str
    category: str


class ComplexityReport(BaseModel):
    cyclomatic_complexity: int
    lines_of_code: int
    num_functions: int
    num_classes: int
    max_nesting_depth: int
    complexity_score: str  # low, moderate, high, very high


class RefactoringSuggestion(BaseModel):
    line: Optional[int] = None
    message: str
    rationale: str


class ReviewResult(BaseModel):
    id: str
    language: str
    bugs: List[BugIssue] = []
    security_issues: List[SecurityIssue] = []
    optimizations: List[Suggestion] = []
    complexity: Optional[ComplexityReport] = None
    refactoring: List[RefactoringSuggestion] = []
    overall_summary: str = ""
    created_at: str = ""


class ReportRequest(BaseModel):
    format: str = "html"  # html or pdf

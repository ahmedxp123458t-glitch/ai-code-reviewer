import uuid
from datetime import datetime
from services.bug_detector import detect_bugs
from services.security_checker import check_security
from services.optimization_service import suggest_optimizations
from services.complexity_analyzer import analyze_complexity
from services.report_service import generate_report
from database import save_review, get_review
from models import ReviewResult, ReportRequest
from openai import OpenAI
import os


SYSTEM_SUMMARY_PROMPT = """You are a code review summarizer. Given the review results below, provide a concise overall summary (2-3 sentences) of the code quality, highlighting the most critical issues found."""


def review_code(code: str, language: str) -> ReviewResult:
    review_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    bugs = detect_bugs(code, language)
    security_issues = check_security(code, language)
    optimizations = suggest_optimizations(code, language)
    complexity = analyze_complexity(code, language)

    refactoring = _get_refactoring_suggestions(code, language, bugs, security_issues, complexity)

    summary = _generate_summary(code, language, bugs, security_issues, complexity)

    result = ReviewResult(
        id=review_id,
        language=language,
        bugs=[bug for bug in bugs],
        security_issues=[sec for sec in security_issues],
        optimizations=[opt for opt in optimizations],
        complexity=complexity,
        refactoring=[ref for ref in refactoring],
        overall_summary=summary,
        created_at=created_at,
    )

    save_review(review_id, language, code, result.model_dump())
    return result


def _get_refactoring_suggestions(code: str, language: str, bugs: list, security: list, complexity: dict) -> list[dict]:
    suggestions = []
    if complexity["max_nesting_depth"] > 4:
        suggestions.append({
            "line": 0,
            "message": f"Reduce nesting depth (currently {complexity['max_nesting_depth']} levels deep)",
            "rationale": "Deep nesting reduces readability and maintainability. Extract nested blocks into separate functions."
        })
    if complexity["cyclomatic_complexity"] > 20:
        suggestions.append({
            "line": 0,
            "message": f"High cyclomatic complexity ({complexity['cyclomatic_complexity']})",
            "rationale": "Split complex functions into smaller, focused functions to improve testability and readability."
        })
    if complexity["num_functions"] > 15 and complexity["lines_of_code"] > 300:
        suggestions.append({
            "line": 0,
            "message": f"Consider splitting into modules ({complexity['num_functions']} functions in one file)",
            "rationale": "Large files with many functions should be organized into separate modules."
        })
    if language == "python":
        if any("for " in line for line in code.split("\n")):
            suggestions.append({
                "line": 0,
                "message": "Consider using generator expressions for memory efficiency",
                "rationale": "Generators use lazy evaluation, reducing memory usage for large collections."
            })
    return suggestions


def _generate_summary(code: str, language: str, bugs: list, security: list, complexity: dict) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            review_data = {
                "bugs": len(bugs),
                "security_issues": len(security),
                "complexity": complexity["complexity_score"],
                "loc": complexity["lines_of_code"],
            }
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_SUMMARY_PROMPT},
                    {"role": "user", "content": f"Review results: {review_data}"},
                ],
                temperature=0.3,
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass

    bug_count = len(bugs)
    sec_count = len(security)
    comp = complexity["complexity_score"]
    return (
        f"Found {bug_count} bug(s), {sec_count} security issue(s). "
        f"Complexity level: {comp}. "
        f"{'High priority: address security issues first.' if sec_count > 0 else ''}"
    )


def get_review_result(review_id: str) -> dict | None:
    return get_review(review_id)


def generate_report_for_review(review_id: str, fmt: str = "html") -> tuple[str, str, str]:
    data = get_review(review_id)
    if data is None:
        raise ValueError("Review not found")
    content, content_type, filename = generate_report(data, fmt)
    return content, content_type, filename

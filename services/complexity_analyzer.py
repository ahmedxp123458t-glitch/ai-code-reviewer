import re


def analyze_complexity(code: str, language: str) -> dict:
    lines = code.split("\n")
    lines_of_code = _count_loc(lines)
    num_functions = _count_functions(code, language)
    num_classes = _count_classes(code, language)
    cyclomatic = _calculate_cyclomatic(code, language)
    max_nesting = _calculate_nesting_depth(lines)
    complexity_score = _score_complexity(cyclomatic, lines_of_code, num_functions)

    return {
        "cyclomatic_complexity": cyclomatic,
        "lines_of_code": lines_of_code,
        "num_functions": num_functions,
        "num_classes": num_classes,
        "max_nesting_depth": max_nesting,
        "complexity_score": complexity_score,
    }


def _count_loc(lines: list) -> int:
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("//") and not stripped.startswith("/*") and not stripped.startswith("*") and not stripped.startswith("--"):
            count += 1
    return count


def _count_functions(code: str, language: str) -> int:
    if language == "python":
        pattern = r"^\s*def\s+\w+\s*\("
    else:
        pattern = r"(?:function\s+\w+\s*\(|\w+\s*=\s*function\s*\(|\(\s*[^)]*\s*\)\s*=>|\w+\s*\([^)]*\)\s*\{)"
    return len(re.findall(pattern, code, re.MULTILINE))


def _count_classes(code: str, language: str) -> int:
    if language == "python":
        pattern = r"^\s*class\s+\w+"
    else:
        pattern = r"^\s*class\s+\w+"
    return len(re.findall(pattern, code, re.MULTILINE))


def _calculate_cyclomatic(code: str, language: str) -> int:
    base = 1
    keywords = {
        "python": [r"\bif\b", r"\belif\b", r"\bfor\b", r"\bwhile\b", r"\band\b", r"\bor\b",
                   r"\btry\b", r"\bexcept\b", r"\bwith\b", r"\bassert\b"],
        "javascript": [r"\bif\b", r"\belse if\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b",
                       r"\bcatch\b", r"\b\?\s*\.?\s*:", r"\b\&\&\b", r"\b\|\|\b"],
    }
    patterns = keywords.get(language, keywords["python"])
    for pattern in patterns:
        matches = re.findall(pattern, code)
        base += len(matches)
    return base


def _calculate_nesting_depth(lines: list) -> int:
    max_depth = 0
    current_depth = 0
    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            continue
        open_braces = stripped.count("{")
        close_braces = stripped.count("}")
        open_colons = stripped.count(":")
        indent = len(line) - len(line.lstrip())
        depth_from_indent = indent // 4 if indent > 0 else 0
        current_depth = max(0, depth_from_indent)
        if current_depth > max_depth:
            max_depth = current_depth
    return max_depth


def _score_complexity(cyclomatic: int, loc: int, funcs: int) -> str:
    if cyclomatic <= 10 and loc <= 100 and funcs <= 5:
        return "low"
    elif cyclomatic <= 20 and loc <= 300 and funcs <= 10:
        return "moderate"
    elif cyclomatic <= 40 and loc <= 500 and funcs <= 20:
        return "high"
    else:
        return "very high"

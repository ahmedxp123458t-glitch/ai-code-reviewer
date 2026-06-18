from openai import OpenAI
import os


SYSTEM_PROMPT = """You are an expert code reviewer. Analyze the given code and identify ALL bugs and potential errors.
For each bug found, provide:
- line number (approximate if exact is unclear, otherwise 0)
- clear description of the bug
- severity (high/medium/low)
- type (e.g., logic_error, syntax_error, runtime_error, type_error, null_pointer, race_condition, etc.)

Respond ONLY with a valid JSON array. Example:
[
  {"line": 15, "message": "Variable 'x' used before assignment", "severity": "high", "type": "runtime_error"}
]
If no bugs are found, return an empty array [].
"""


def detect_bugs(code: str, language: str) -> list[dict]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_rule_based(code, language)

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Language: {language}\n\nCode:\n```\n{code}\n```"},
            ],
            temperature=0.1,
            max_tokens=2000,
        )
        content = response.choices[0].message.content.strip()
        content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        import json
        return json.loads(content)
    except Exception:
        return _fallback_rule_based(code, language)


def _fallback_rule_based(code: str, language: str) -> list[dict]:
    bugs = []
    lines = code.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if language == "python":
            if "== None" in stripped or "!= None" in stripped:
                bugs.append({
                    "line": i, "message": "Use 'is None' instead of '== None'",
                    "severity": "low", "type": "style"
                })
            if "except:" in stripped and not stripped.endswith("# noqa"):
                bugs.append({
                    "line": i, "message": "Bare except clause catches all exceptions",
                    "severity": "medium", "type": "error_handling"
                })
            if "import *" in stripped:
                bugs.append({
                    "line": i, "message": "Wildcard imports are discouraged",
                    "severity": "low", "type": "style"
                })
        elif language == "javascript":
            if "==" in stripped and "!=" not in stripped and "===" not in stripped:
                bugs.append({
                    "line": i, "message": "Use === instead of == for strict equality",
                    "severity": "low", "type": "style"
                })
            if "var " in stripped:
                bugs.append({
                    "line": i, "message": "Use let or const instead of var",
                    "severity": "low", "type": "style"
                })

    return bugs

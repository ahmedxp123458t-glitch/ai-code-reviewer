from openai import OpenAI
import os


SYSTEM_PROMPT = """You are a performance optimization expert. Analyze the given code and suggest performance improvements.
For each suggestion, provide:
- line number (approximate, 0 if general)
- clear suggestion message
- category (performance, memory, i/o, algorithmic, database, network, rendering)

Respond ONLY with a valid JSON array. Example:
[
  {"line": 25, "message": "Use list comprehension instead of for-loop for better performance", "category": "performance"},
  {"line": 0, "message": "Consider adding caching for database query results", "category": "database"}
]
If no optimization needed, return empty array [].
"""


def suggest_optimizations(code: str, language: str) -> list[dict]:
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
    suggestions = []
    lines = code.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if language == "python":
            if "for " in stripped and "range(len(" in stripped:
                suggestions.append({
                    "line": i, "message": "Use direct iteration instead of range(len(...))",
                    "category": "performance"
                })
            if ".append(" in stripped and "for " in stripped:
                suggestions.append({
                    "line": i, "message": "Consider using list comprehension instead of loop with append",
                    "category": "performance"
                })
            if "while True:" in stripped or "while 1:" in stripped:
                suggestions.append({
                    "line": i, "message": "Ensure while True loop has a proper break condition",
                    "category": "algorithmic"
                })
        elif language == "javascript":
            if "for (var " in stripped or "for(let " in stripped or "for(const " in stripped:
                if "; " not in stripped and ".length" not in stripped:
                    suggestions.append({
                        "line": i, "message": "Consider caching array.length in for loop condition",
                        "category": "performance"
                    })
            if ".innerHTML +=" in stripped:
                suggestions.append({
                    "line": i, "message": "Avoid multiple innerHTML assignments; build string then assign once",
                    "category": "performance"
                })

    return suggestions

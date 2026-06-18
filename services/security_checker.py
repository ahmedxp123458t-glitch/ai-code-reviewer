from openai import OpenAI
import os


SYSTEM_PROMPT = """You are a security code review expert. Analyze the given code for ALL security vulnerabilities.
For each issue found, provide:
- line number (approximate, 0 if unknown)
- clear description of the security issue
- severity (high/medium/low)
- CWE identifier if applicable (optional)

Respond ONLY with a valid JSON array. Example:
[
  {"line": 42, "message": "SQL injection vulnerability: raw query concatenation", "severity": "high", "cwe": "CWE-89"},
  {"line": 10, "message": "Hardcoded API key detected", "severity": "high", "cwe": "CWE-798"}
]
If no issues are found, return an empty array [].
"""


def check_security(code: str, language: str) -> list[dict]:
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
    issues = []
    lines = code.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip().lower()

        secrets_patterns = ["api_key", "api-secret", "password", "secret", "token", "auth", "credentials"]
        for pat in secrets_patterns:
            if pat in stripped and "=" in stripped and ("sk-" in stripped or "eyJ" in stripped):
                issues.append({
                    "line": i, "message": f"Possible hardcoded secret detected: '{pat}'",
                    "severity": "high", "cwe": "CWE-798"
                })

        if language == "python":
            if "eval(" in stripped or "exec(" in stripped:
                issues.append({
                    "line": i, "message": "Use of eval/exec allows arbitrary code execution",
                    "severity": "high", "cwe": "CWE-95"
                })
            if "pickle.load" in stripped:
                issues.append({
                    "line": i, "message": "Unsafe deserialization with pickle",
                    "severity": "high", "cwe": "CWE-502"
                })
            if "sqlite3" in stripped and "?" not in stripped and "%s" not in stripped:
                if any(kw in stripped for kw in ["execute(", "executemany("]):
                    issues.append({
                        "line": i, "message": "Possible SQL injection: use parameterized queries",
                        "severity": "high", "cwe": "CWE-89"
                    })
            if "input(" in stripped:
                issues.append({
                    "line": i, "message": "Using input() in Python 2 is dangerous (eval). In Python 3, validate input.",
                    "severity": "medium", "cwe": "CWE-20"
                })
            if "shell=True" in stripped:
                issues.append({
                    "line": i, "message": "Shell=True enables shell injection attacks",
                    "severity": "high", "cwe": "CWE-78"
                })

        elif language == "javascript":
            if "innerHTML" in stripped:
                issues.append({
                    "line": i, "message": "Using innerHTML can lead to XSS attacks",
                    "severity": "high", "cwe": "CWE-79"
                })
            if "document.write" in stripped:
                issues.append({
                    "line": i, "message": "document.write can lead to XSS vulnerabilities",
                    "severity": "high", "cwe": "CWE-79"
                })
            if "localStorage" in stripped and "password" in stripped:
                issues.append({
                    "line": i, "message": "Storing passwords in localStorage is insecure",
                    "severity": "high", "cwe": "CWE-312"
                })

    return issues

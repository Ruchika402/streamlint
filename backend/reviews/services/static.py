import subprocess
import json
import logging

logger = logging.getLogger(__name__)

def run_ruff(code: str, language: str) -> list:
    if language not in ["python", "django"]:
        return []

    try:
        # Run ruff via stdin (we never save the pasted code to disk)
        result = subprocess.run(
            ["ruff", "check", "--output-format", "json", "--stdin-filename", "snippet.py", "-"],
            input=code,
            text=True,
            capture_output=True,
            timeout=5,
        )
        
        if not result.stdout.strip():
            return []

        findings = json.loads(result.stdout)
        clean_findings = []
        for f in findings:
            clean_findings.append({
                "line": f.get("location", {}).get("row", 0),
                "code": f.get("code", ""),
                "message": f.get("message", "")
            })
        return clean_findings

    except subprocess.TimeoutExpired:
        logger.warning("Ruff timed out.")
        return []
    except Exception as e:
        logger.error(f"Ruff error: {e}")
        return []
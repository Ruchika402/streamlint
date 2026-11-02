import json
import logging

logger = logging.getLogger(__name__)

def parse_stream_chunk(chunk: str, buffer: str) -> tuple[list, str]:
    buffer += chunk
    valid_issues = []
    
    lines = buffer.split("\n")
    buffer = lines.pop()
    
    for line in lines:
        line = line.strip()
        if line.startswith("```json"):
            line = line[7:]
        if line.startswith("```"):
            line = line[3:]
        if not line:
            continue
            
        try:
            data = json.loads(line)
            if "summary" in data:
                valid_issues.append({"type": "summary", "data": data})
            elif "line" in data and "severity" in data:
                valid_issues.append({"type": "issue", "data": data})
        except json.JSONDecodeError:
            logger.debug(f"Skipped bad JSON line: {line}")
            continue
            
    return valid_issues, buffer
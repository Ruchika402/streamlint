def status_event(review_id, state, seq=1):
    return {
        "type": "status",
        "review_id": review_id,
        "seq": seq,
        "payload": {"state": state},
    }

def issue_event(review_id, line, severity, category, message, suggestion, seq=1):
    return {
        "type": "issue",
        "review_id": review_id,
        "seq": seq,
        "payload": {
            "line": line,
            "severity": severity,
            "category": category,
            "message": message,
            "suggestion": suggestion,
        },
    }

def presence_event(review_id, count, seq=1):
    return {
        "type": "presence",
        "review_id": review_id,
        "seq": seq,
        "payload": {"viewers": count},
    }
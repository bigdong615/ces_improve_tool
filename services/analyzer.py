"""AI reason analysis using keyword-based rule engine."""

RULES = {
    "slow_response": ["slow", "wait", "long time", "delay", "week", "month", "days"],
    "unresolved": [
        "not resolved",
        "still broken",
        "doesn't work",
        "not fixed",
        "same issue",
        "still open",
    ],
    "poor_communication": [
        "no update",
        "didn't explain",
        "unclear",
        "no response",
        "ignored",
        "never heard",
    ],
    "lack_expertise": [
        "didn't understand",
        "wrong solution",
        "not qualified",
        "incorrect",
        "inexperienced",
    ],
    "process_issue": [
        "transferred",
        "escalation",
        "bounced around",
        "multiple teams",
        "passed around",
    ],
    "expectation_mismatch": [
        "expected",
        "promised",
        "should have",
        "disappointed",
        "misleading",
    ],
}


def analyze_comment(comment):
    """Analyze a survey comment and return (category, confidence).

    Returns:
        tuple: (category_code: str, confidence: float)
    """
    if not comment:
        return "other", 0.0

    text = comment.lower()
    hits = {}

    for category, keywords in RULES.items():
        count = 0
        for keyword in keywords:
            if keyword in text:
                count += 1
        if count > 0:
            hits[category] = count

    if not hits:
        return "other", 0.0

    total_hits = sum(hits.values())
    best_category = max(hits, key=hits.get)
    confidence = round(hits[best_category] / total_hits, 2)

    return best_category, confidence
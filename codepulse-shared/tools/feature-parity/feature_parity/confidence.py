"""Conservative confidence factors; review approval is a separate axis."""

LEVEL_BOUNDARIES = {"low": 0.0, "medium": 0.5, "high": 0.8}


def confidence_level(score):
    if score >= LEVEL_BOUNDARIES["high"]:
        return "high"
    if score >= LEVEL_BOUNDARIES["medium"]:
        return "medium"
    return "low"


def declaration_confidence():
    return {
        "level": "low", "score": 0.25,
        "reasons": ["Documentation declaration only; implementation not verified"],
    }


def lexical_endpoint_confidence():
    return {
        "level": "low", "score": 0.4,
        "reasons": ["HTTP syntax found in C# code; framework registration and behavior not resolved"],
    }


def syntax_declaration_confidence():
    return {
        "level": "low", "score": 0.35,
        "reasons": ["Template or registration syntax observed; business contract and reachability unresolved"],
    }


def admitted(confidence, threshold):
    return confidence["score"] >= LEVEL_BOUNDARIES[threshold]
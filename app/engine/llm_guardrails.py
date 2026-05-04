from __future__ import annotations

import re

LLM_DATA_GUARDRAILS = (
    "Use ONLY the provided structured data. Do NOT invent or infer facts not present in the data.\n"
    "Do NOT contradict numerical or categorical values in the input.\n"
    "If uncertain, say: 'Based on the current system state...'\n"
    "Do not use first-person recommendation phrasing. Use 'The system recommends...' when referring to recommendations."
)

_THREAT_LEVEL_RE = re.compile(r"\b(LOW|MEDIUM|HIGH|CRITICAL)\b", re.IGNORECASE)
_ENTITY_REF_RE = re.compile(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)+\b")
_COA_REF_RE = re.compile(r"\b(?:COA|OPT|TGT)-[A-Z0-9-]+\b")
_PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
_DISTANCE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:nm|km|nautical miles?)", re.IGNORECASE)

_SANITIZER_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bI recommend\b", re.IGNORECASE), "The system recommends"),
    (re.compile(r"\bI suggest\b", re.IGNORECASE), "The system indicates"),
    (re.compile(r"\bI advise\b", re.IGNORECASE), "The system indicates"),
    (re.compile(r"\bWe should\b", re.IGNORECASE), "The system indicates"),
    (re.compile(r"\bYou must\b", re.IGNORECASE), "The system indicates"),
    (re.compile(r"\bIt is recommended that\b", re.IGNORECASE), "The system indicates that"),
    (re.compile(r"\bThe optimal action is\b", re.IGNORECASE), "The system-recommended action is"),
]


def sanitize_llm_text(text: str) -> str:
    for pattern, replacement in _SANITIZER_RULES:
        text = pattern.sub(replacement, text)
    return text


def explanation_references_match(
    text: str,
    *,
    threat_level: str | None = None,
    valid_target_ids: set[str] | None = None,
    valid_coa_ids: set[str] | None = None,
    valid_coa_titles: set[str] | None = None,
    numeric_ground_truth: dict[str, float] | None = None,
) -> bool:
    if not text:
        return False

    normalized = sanitize_llm_text(text)

    # Threat level: if the text mentions specific levels, the actual level must be among them
    mentioned_levels = {match.upper() for match in _THREAT_LEVEL_RE.findall(normalized)}
    if threat_level and mentioned_levels and threat_level.upper() not in mentioned_levels:
        return False

    target_ids = valid_target_ids or set()
    coa_ids = valid_coa_ids or set()

    # Entity references: only validate IDs that look like our system IDs (XX-YYY pattern)
    # Skip generic uppercase words that happen to match the regex
    for entity_id in _ENTITY_REF_RE.findall(normalized):
        if entity_id.startswith(("COA-", "OPT-", "TGT-")):
            # Validate COA/TGT references strictly
            if coa_ids and entity_id not in coa_ids:
                return False
            continue
        # For entity IDs: only reject if target_ids is populated AND the ID
        # matches our known prefix patterns (VES-, UAV-, CON-, SUB- etc.)
        if target_ids and _looks_like_system_entity_id(entity_id):
            if entity_id not in target_ids:
                return False

    # COA references: validate against known COA IDs
    for coa_id in _COA_REF_RE.findall(normalized):
        if coa_ids and coa_id not in coa_ids:
            return False

    # Numeric guardrail: validate percentages against ground truth
    if numeric_ground_truth:
        if not _numeric_claims_match(normalized, numeric_ground_truth):
            return False

    return True


# Known system entity ID prefixes used in scenarios
_SYSTEM_ENTITY_PREFIXES = (
    "VES-", "UAV-", "CON-", "SUB-", "ISR-", "SIG-",
    "RAD-", "SAT-", "BLU-", "FRD-", "NEU-", "CIV-",
    "CABLE-", "INFRA-",
)


def _looks_like_system_entity_id(entity_id: str) -> bool:
    """Check if an entity ID looks like one of our system-generated IDs."""
    return entity_id.upper().startswith(_SYSTEM_ENTITY_PREFIXES)


_NUMERIC_KEYS: dict[str, list[str]] = {
    "success_probability": ["success", "probability"],
    "threat_probability": ["threat probability", "threat prob"],
    "escalation_probability": ["escalation probability", "escalation prob"],
    "risk_to_second_cable": ["cable risk", "second cable"],
    "missed_detection_probability": ["detection probability", "missed detection"],
}

_NUMERIC_TOLERANCE = 0.05


def _numeric_claims_match(text: str, ground_truth: dict[str, float]) -> bool:
    """Check that percentage claims in text are within tolerance of ground truth values."""
    text_lower = text.lower()
    mentioned_percents = _PERCENT_RE.findall(text_lower)
    if not mentioned_percents:
        return True

    claimed_values = [float(v) for v in mentioned_percents]
    allowed_values: set[float] = set()

    for key, value in ground_truth.items():
        pct = value * 100.0
        allowed_values.add(round(pct, 1))
        lo = round((value - _NUMERIC_TOLERANCE) * 100.0, 1)
        hi = round((value + _NUMERIC_TOLERANCE) * 100.0, 1)
        for step in range(int(lo), int(hi) + 2):
            allowed_values.add(float(step))
            allowed_values.add(float(step) + 0.5)

    for key, keywords in _NUMERIC_KEYS.items():
        if key not in ground_truth:
            continue
        for kw in keywords:
            if kw in text_lower:
                truth_pct = round(ground_truth[key] * 100.0, 1)
                lo_pct = round((ground_truth[key] - _NUMERIC_TOLERANCE) * 100.0, 1)
                hi_pct = round((ground_truth[key] + _NUMERIC_TOLERANCE) * 100.0, 1)
                for claimed in claimed_values:
                    if lo_pct - 1 <= claimed <= hi_pct + 1:
                        break
                else:
                    return False

    return True

"""
Safety Filter Service for Fix It Yourself (DIY Assistant)
Enforces the mandatory safety rule:
NEVER teach risky work (electrical wiring, sockets, switchboards, MCB/fuse,
gas/LPG lines, water heaters/geysers, structural/wall-cutting, heights/roofs,
fire, chemicals, or high pressure).

Checks keywords in English, common Tamil, and common Hindi before any AI call.
"""

import re

# Comprehensive hazard keyword patterns
HAZARD_CATEGORIES = {
    "Electrical Hazards": {
        "keywords": [
            # English
            r"\b(electrical|electricity|electric|wiring|wire|wires|socket|sockets|plug|plugs)\b",
            r"\b(switchboard|switch\s*board|mcb|fuse|fuse\s*box|breaker|circuit\s*breaker)\b",
            r"\b(spark|sparking|sparks|short\s*circuit|shock|electric\s*shock|electrocution)\b",
            r"\b(main\s*board|meter\s*box|high\s*voltage|live\s*wire|earthing|grounding)\b",
            r"\b(transformer|phase|ac\s*current|dc\s*current|voltage)\b",
            # Tamil
            r"\b(current|min\s*saram|theepori|fuse\s*pona|current\s*shock|adikkuthu)\b",
            # Hindi
            r"\b(bijli|bijlee|taar|bijli\s*ka\s*jhatka|current\s*lagna)\b"
        ],
        "warning": "Working with electrical wiring, sockets, switchboards, or high voltage carries severe risk of electrocution, fire, and permanent injury."
    },
    "Gas & LPG Hazards": {
        "keywords": [
            # English
            r"\b(gas|lpg|cylinder|gas\s*leak|gas\s*smell|smell\s*gas|stove\s*leak|burner\s*leak)\b",
            r"\b(pipeline|gas\s*pipe|regulator|gas\s*stove\s*leak|flame\s*leak)\b",
            # Tamil
            r"\b(gas\s*aduppu|cylinder\s*leak|gas\s*vaasanai)\b",
            # Hindi
            r"\b(gas\s*risav|gas\s*cylinder|gas\s*ki\s*badboo)\b"
        ],
        "warning": "LPG gas leaks pose an immediate danger of explosion, rapid fire, and asphyxiation. Turn off the regulator and ventilate immediately."
    },
    "Water Heaters & Geysers": {
        "keywords": [
            # English
            r"\b(geyser|water\s*heater|water\s*geyser|immersion\s*rod|boiler|hot\s*water\s*tank)\b",
            r"\b(geyser\s*not\s*heating|geyser\s*shock|geyser\s*leak)\b",
            # Tamil & Hindi
            r"\b(geyser\s*repair|pani\s*heater)\b"
        ],
        "warning": "Water heaters combine high-voltage electric elements with pressurized water, creating severe hazards of electric shock, scalding, and tank ruptures."
    },
    "Structural & Demolition": {
        "keywords": [
            # English
            r"\b(structural|wall\s*cutting|wall\s*breaking|demolition|concrete\s*drilling)\b",
            r"\b(pillar|beam|load\s*bearing|crack\s*in\s*pillar|ceiling\s*collapse)\b",
            # Tamil
            r"\b(suvar\s*idithal|katti\s*velai|suvar\s*vetruthal)\b",
            # Hindi
            r"\b(deewar\s*todna|structure\s*todna)\b"
        ],
        "warning": "Cutting or modifying structural walls, pillars, or beams can compromise building stability and lead to catastrophic collapse."
    },
    "Roofing & Heights": {
        "keywords": [
            # English
            r"\b(roof|roofing|roof\s*leak|terrace\s*edge|working\s*at\s*height|scaffolding)\b",
            r"\b(tall\s*ladder|chimney|gutter\s*roof|asbestos)\b",
            # Tamil & Hindi
            r"\b(koorai|chhat|chhat\s*ka\s*kaam)\b"
        ],
        "warning": "Working at heights or on rooftops without professional safety harnesses poses serious risks of life-threatening falls."
    },
    "Fire, High Pressure & Chemicals": {
        "keywords": [
            # English
            r"\b(fire|flame|burning|smoke|explosion|blast)\b",
            r"\b(chemical|acid|muriatic\s*acid|drain\s*acid|toxic|fumes|pesticide)\b",
            r"\b(high\s*pressure|pressure\s*vessel|compressor\s*tank)\b",
            # Tamil & Hindi
            r"\b(theey|neruppu|aag|dhuaan|tezab)\b"
        ],
        "warning": "Handling toxic chemicals, open flames, or pressurized vessels can cause chemical burns, poison inhalation, and explosive damage."
    }
}


def check_safety_blocklist(problem_text):
    """
    Evaluates the problem text against all safety keyword blocklists.
    Returns:
        (is_risky: bool, category: str, warning_message: str)
    """
    if not problem_text:
        return False, None, None

    normalized_text = problem_text.lower().strip()

    for category, data in HAZARD_CATEGORIES.items():
        for pattern in data["keywords"]:
            if re.search(pattern, normalized_text, re.IGNORECASE):
                return True, category, data["warning"]

    return False, None, None

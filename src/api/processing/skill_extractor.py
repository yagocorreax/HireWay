import re
from src.api.processing.skills_list import SKILLS


SKILL_PATTERNS = [
    (skill, re.compile(rf"(?<![a-z0-9]){re.escape(skill)}(?![a-z0-9])"))
    for skill in SKILLS
]

def extract_skills(text: str):
    if not text:
        return []

    normalized_text = re.sub(r"\s+", " ", text.lower())

    return [
        skill
        for skill, pattern in SKILL_PATTERNS
        if pattern.search(normalized_text)
    ]

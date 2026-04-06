from src.api.processing.skills_list import SKILLS

def extract_skills(text: str):
    text = text.lower()
    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))

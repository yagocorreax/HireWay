from src.api.ingestion.material_loader import load_materials

LEVEL_ORDER = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3
}


SKILL_ALIASES = {
    "gcp": ["gcp", "google cloud"],
    "google cloud": ["gcp", "google cloud"],
    "postgres": ["postgres", "postgresql"],
    "postgresql": ["postgres", "postgresql"],
    "powerbi": ["powerbi", "power bi"],
    "power bi": ["powerbi", "power bi"],
    "pyspark": ["pyspark", "spark"],
    "spark": ["spark", "pyspark"],
    "data pipeline": ["data pipeline", "etl", "data ingestion"],
    "etl": ["etl", "data pipeline", "data ingestion"],
    "data lakehouse": ["lakehouse", "delta lake", "databricks"],
    "lakehouse": ["lakehouse", "delta lake", "databricks"],
    "mongodb": ["mongodb", "mongo db", "nosql"],
    "mongo db": ["mongodb", "mongo db", "nosql"],
    "snowflake": ["snowflake", "data warehouse"],
    "databricks": ["databricks", "spark", "pyspark", "delta lake", "lakehouse"]
}


def normalize_skill(skill: str) -> str:
    return skill.lower().strip()


def expand_skill_terms(skill: str) -> set[str]:
    normalized = normalize_skill(skill)
    aliases = SKILL_ALIASES.get(normalized, [normalized])
    return set(normalize_skill(alias) for alias in aliases)


def material_matches_gap(material: dict, gap: str) -> bool:
    gap_terms = expand_skill_terms(gap)
    material_skills = set(
        normalize_skill(skill)
        for skill in material.get("skills", [])
    )

    return bool(gap_terms.intersection(material_skills))


def group_materials_by_level(materials: list[dict]) -> dict:
    grouped = {
        "beginner": [],
        "intermediate": [],
        "advanced": []
    }

    for material in materials:
        level = material.get("level", "beginner")

        item = {
            "title": material.get("title"),
            "provider": material.get("provider"),
            "type": material.get("type"),
            "level": level,
            "url": material.get("url"),
            "description": material.get("description"),
            "prerequisites": material.get("prerequisites", []),
            "next_topics": material.get("next_topics", [])
        }

        if level in grouped:
            grouped[level].append(item)

    return grouped


def recommend_learning_paths_for_gaps(
    missing_skills: list[str],
    max_per_level: int = 3
) -> dict:
    materials = load_materials()
    recommendations = {}

    for gap in missing_skills:
        matched_materials = [
            material
            for material in materials
            if material_matches_gap(material, gap)
        ]

        matched_materials = sorted(
            matched_materials,
            key=lambda material: LEVEL_ORDER.get(material.get("level", "beginner"), 1)
        )

        grouped = group_materials_by_level(matched_materials)

        for level in grouped:
            grouped[level] = grouped[level][:max_per_level]

        recommendations[gap] = {
            "learning_path": grouped,
            "total_materials_found": len(matched_materials),
            "recommendation_strategy": "matched_by_skill_alias_and_level"
        }

    return recommendations
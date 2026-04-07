def match_skills(resume_skills: list, job_skills: list):
    resume_set = set(resume_skills)
    job_set = set(job_skills)

    matched = list(resume_set.intersection(job_set))
    missing = list(job_set.difference(resume_set))

    if len(job_set) == 0:
        score = 0
    else:
        score = len(matched) / len(job_set)
    
    return {
        "match_score": round(score, 2),
        "matched_skills": matched,
        "missing_skills": missing
    }
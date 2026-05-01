def match_skills(resume_skills: list, job_skills: list):
    resume_set = set(resume_skills)
    ordered_job_skills = list(dict.fromkeys(job_skills))

    matched = [skill for skill in ordered_job_skills if skill in resume_set]
    missing = [skill for skill in ordered_job_skills if skill not in resume_set]

    if len(ordered_job_skills) == 0:
        score = 0
    else:
        score = len(matched) / len(ordered_job_skills)
    
    return {
        "match_score": round(score, 2),
        "matched_skills": matched,
        "missing_skills": missing
    }

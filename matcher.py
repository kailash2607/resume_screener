import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import (clean_text, extract_skills, extract_education,
                   extract_experience_years, extract_name)

TEXT_WEIGHT = 0.6    # importance of overall text similarity
SKILL_WEIGHT = 0.4   # importance of required-skill match


def rank_candidates(jd_text, resumes, text_weight=0.6):    
    """
    jd_text : the job description as a string
    resumes : a dictionary like {"aarav_sharma.txt": "resume text...", ...}
    Returns a table (DataFrame) of candidates sorted from best to worst.
    """
    if not resumes:
        return pd.DataFrame()

    filenames = list(resumes.keys())
    texts = [resumes[f] for f in filenames]

    # --- Part 1: TF-IDF + cosine similarity ---
    documents = [clean_text(jd_text)] + [clean_text(t) for t in texts]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(documents)
    # compare the job description (row 0) with every resume (rows 1 onwards)
    text_scores = cosine_similarity(matrix[0:1], matrix[1:])[0]

    # --- Part 2: skill matching ---
    required_skills = extract_skills(jd_text)

    rows = []
    for i, filename in enumerate(filenames):
        text = texts[i]
        candidate_skills = extract_skills(text)

        matched = [s for s in required_skills if s in candidate_skills]
        missing = [s for s in required_skills if s not in candidate_skills]
        skill_score = len(matched) / len(required_skills) if required_skills else 0

        text_norm = min(text_scores[i] / 0.4, 1.0)   # similarity of 0.4 counts as a full match
        final = text_weight * text_norm + (1 - text_weight) * skill_score
                
        rows.append({
            "Candidate": extract_name(text, fallback=filename),
            "Score": round(final * 100, 1),
            "Text Match": round(text_norm * 100, 1),            "Skill Match": round(skill_score * 100, 1),
            "Matched Skills": ", ".join(matched),
            "Missing Skills": ", ".join(missing),
            "Education": extract_education(text)[0],
            "Experience (yrs)": extract_experience_years(text),
        })

    df = pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)
    df.index = df.index + 1          # ranks start at 1, not 0
    df.index.name = "Rank"
    return df
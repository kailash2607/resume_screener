import os
from utils import extract_text
from matcher import rank_candidates

jd = extract_text("sample_data/job_description.txt")

folder = "sample_data/resumes"
resumes = {}
for filename in os.listdir(folder):
    resumes[filename] = extract_text(os.path.join(folder, filename))

result = rank_candidates(jd, resumes)

print(result[["Candidate", "Score", "Text Match", "Skill Match"]].to_string())
print()
print("Missing skills for each candidate:")
for rank, row in result.iterrows():
    print(f"{rank}. {row['Candidate']}: {row['Missing Skills']}")
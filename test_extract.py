import os
from utils import (extract_text, extract_skills, extract_education,
                   extract_experience_years, extract_name)

jd = extract_text("sample_data/job_description.txt")
print("JOB DESCRIPTION SKILLS:", extract_skills(jd))
print("=" * 60)

folder = "sample_data/resumes"
for filename in os.listdir(folder):
    text = extract_text(os.path.join(folder, filename))
    print("Name:      ", extract_name(text))
    print("Skills:    ", extract_skills(text))
    print("Education: ", extract_education(text)[0])
    print("Experience:", extract_experience_years(text), "years")
    print("-" * 60)
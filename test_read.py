import os
from utils import extract_text

jd = extract_text("sample_data/job_description.txt")
print("JOB DESCRIPTION (first 150 characters):")
print(jd[:150])
print("-" * 40)

folder = "sample_data/resumes"
for filename in os.listdir(folder):
    text = extract_text(os.path.join(folder, filename))
    print(filename, "->", len(text), "characters")
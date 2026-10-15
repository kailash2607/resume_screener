# 📄 AI Resume Screening System

An AI-powered decision-support tool that analyzes resumes, compares them with a job description using NLP and machine learning techniques, and ranks candidates by how well they match the job.

## Problem Statement

Companies receive a large number of resumes for every job opening. Reviewing and comparing them manually is time-consuming, repetitive and prone to human error, and recruiters may miss qualified candidates when screening hundreds of applications. This project builds a system that automatically analyzes resumes against a job description, calculates a matching score for each candidate and ranks them, so recruiters can quickly identify the most suitable candidates.

## Features

- Accepts a job description (upload a PDF or TXT file, or paste text) and multiple resumes (PDF or TXT)
- Extracts skills, education level, years of experience and the candidate's name from each resume
- Identifies the required skills mentioned in the job description
- Calculates a matching score for every candidate and ranks them from best to worst
- Shows which required skills each candidate has and which are missing
- Leaderboard with score rings and fit labels (Excellent, Good, Fair, Low)
- Analytics tab with a score breakdown chart and a radar chart comparing the top 3 candidates
- Skill gap heatmap showing every candidate against every required skill
- Recommendation summary for the top candidate
- Adjustable weighting between text similarity and skill match
- Downloadable results as a CSV file
- Built-in sample data for an instant demo

## How It Works

1. **Reading files:** text is extracted from PDF files with `pdfplumber` and from TXT files directly.
2. **Cleaning:** text is lowercased and symbols are removed.
3. **Information extraction:** a skills list is matched against the text. Education level is found from keywords such as B.Tech or M.Sc, experience from phrases like "2 years" or "6 months", and the name from the first suitable line of the resume.
4. **Text similarity (TF-IDF and cosine similarity):** the job description and every resume are converted to TF-IDF vectors, which give more weight to meaningful words and less to common ones. Cosine similarity then measures how close each resume is to the job description, from 0 to 1.
5. **Skill match:** the share of the job's required skills that the candidate has.
6. **Final score:** a weighted mix of the two, 60% text similarity and 40% skill match by default. The text similarity is scaled so that a similarity of 0.4 counts as a full match, because short resumes rarely score higher against a long job description.
7. **Ranking:** candidates are sorted by final score.

## Tech Stack

- Python 3
- scikit-learn (TF-IDF, cosine similarity)
- pandas (tables)
- pdfplumber (reading PDF resumes)
- Plotly (charts)
- Streamlit (web interface)

## Project Structure

```
resume_screener/
├── app.py              # Streamlit web interface
├── utils.py            # file reading, cleaning, skill/education/experience/name extraction
├── matcher.py          # TF-IDF matching, scoring and ranking
├── sample_data/
│   ├── job_description.txt
│   └── resumes/        # sample resumes
├── .streamlit/
│   └── config.toml     # theme colors
└── README.md
```

## How to Run

```bash
python -m venv venv
venv\Scripts\activate
python -m pip install pandas scikit-learn pdfplumber nltk streamlit plotly
python -m streamlit run app.py
```

Then open http://localhost:8501 in your browser. To try it quickly, turn on **Use built-in sample data** in the sidebar and click **Screen Candidates**.

## Example Output

| Rank | Candidate | Score | Text Match | Skill Match |
|---|---|---|---|---|
| 1 | Aarav Sharma | 65.8 | 55.1% | 81.8% |
| 2 | Priya Nair | 43.5 | 42.1% | 45.5% |
| 3 | Vikram Rao | 16.8 | 9.8% | 27.3% |
| 4 | Rohan Mehta | 12.9 | 9.3% | 18.2% |
| 5 | Sneha Iyer | 1.6 | 2.7% | 0.0% |

These are the results for the bundled sample job description (Machine Learning Engineer) and five sample resumes, using the default 60/40 weighting. Numbers change with the weights chosen in the sidebar.

## Limitations and Future Work

- Skills are found from a fixed list, so a skill that is not in the list is not detected. The list can be extended easily.
- Scanned PDFs (images) cannot be read without OCR.
- Education and experience are found with simple pattern matching and may miss unusual wording.
- Matching is based on words, not meaning. Sentence embeddings would let the system understand synonyms such as "ML" and "machine learning".
- The tool is meant to support recruiters, not replace them. Final hiring decisions should always involve a human.

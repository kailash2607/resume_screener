import re
import pdfplumber

# ---------- 1. Reading files (from Step 2) ----------

def extract_text(file):
    """Read text from a PDF or TXT file (path or uploaded file)."""
    name = getattr(file, "name", str(file)).lower()

    if name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        return text

    if name.endswith(".txt"):
        if hasattr(file, "read"):  # uploaded file
            return file.read().decode("utf-8", errors="ignore")
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    return ""


# ---------- 2. Cleaning text ----------

def clean_text(text):
    """Lowercase the text and remove symbols so the ML model sees only words."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#\s]", " ", text)  # keep letters, numbers, + and #
    text = re.sub(r"\s+", " ", text).strip()   # collapse extra spaces
    return text


# ---------- 3. Skills ----------

SKILLS = [
    # programming
    "python", "java", "javascript", "c++", "html", "css", "react",
    # data and ML
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "machine learning", "deep learning", "nlp", "statistics",
    "data visualization", "data analysis", "matplotlib", "seaborn",
    # databases and tools
    "sql", "mysql", "mongodb", "git", "github", "docker",
    "tableau", "power bi", "excel", "streamlit",
    # cloud
    "aws", "azure", "cloud",
    # IoT and electronics
    "iot", "arduino", "embedded systems",
    # finance
    "tally", "financial accounting", "gst", "bookkeeping",
        # more tools
    "flask", "django", "fastapi", "opencv", "spacy", "nltk", "linux",
    "typescript", "node.js", "figma", "jira", "rest api",
]


def extract_skills(text):
    """Return the list of known skills that appear in the text."""
    text = text.lower()
    found = []
    for skill in SKILLS:
        # the pattern makes sure 'sql' is not matched inside 'mysql'
        pattern = r"(?<![a-z0-9+#])" + re.escape(skill) + r"(?![a-z0-9+#])"
        if re.search(pattern, text):
            found.append(skill)
    return found


# ---------- 4. Education ----------

EDUCATION_LEVELS = [
    # (label, rank, patterns that indicate it)
    ("PhD", 4, [r"\bph\.?d\b", r"\bdoctorate\b"]),
    ("Master's", 3, [r"\bm\.?tech\b", r"\bm\.?sc\b", r"\bm\.?e\b(?=\s+in)", r"\bmba\b", r"\bmca\b",
                     r"\bmaster", r"\bpost graduate\b"]),
    ("Bachelor's", 2, [r"\bb\.?tech\b", r"\bb\.e\b", r"\bb\.?sc\b", r"\bb\.?com\b", r"\bbca\b",
                       r"\bbachelor"]),
    ("Diploma", 1, [r"\bdiploma\b"]),
]


def extract_education(text):
    """Return (label, rank) of the highest education level found."""
    text = text.lower()
    best = ("Not found", 0)
    for label, rank, patterns in EDUCATION_LEVELS:
        for p in patterns:
            if re.search(p, text) and rank > best[1]:
                best = (label, rank)
    return best


# ---------- 5. Experience ----------

def extract_experience_years(text):
    """Find mentions like '2 years' or '6 months' and return the largest in years."""
    text = text.lower()
    years = [float(n) for n in re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", text)]
    months = [float(n) / 12 for n in re.findall(r"(\d+(?:\.\d+)?)\s*months?", text)]
    values = years + months
    return round(max(values), 1) if values else 0.0


# ---------- 6. Candidate name ----------

def extract_name(text, fallback="Unknown"):
    """Pick the first line that looks like a person's name."""
    skip_words = ("resume", "curriculum vitae", "cv", "profile", "contact",
                  "summary", "objective")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower() in skip_words:       # headings like "RESUME"
            continue
        if "@" in line or any(ch.isdigit() for ch in line):   # emails, phone numbers
            continue
        if len(line.split()) > 5:            # too long to be a name
            continue
        return line.title() if line.isupper() else line
    return fallback
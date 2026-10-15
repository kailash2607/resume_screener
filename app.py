import os
from html import escape

import streamlit as st
import plotly.graph_objects as go

from utils import extract_text, extract_skills
from matcher import rank_candidates

st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="wide")

SAMPLE_DIR = "sample_data"

# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
.stApp {font-family: 'Inter', sans-serif; background: #F5F7FB;}
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 1.5rem; max-width: 1200px;}

.hero {background: linear-gradient(120deg, #4338CA 0%, #7C3AED 55%, #DB2777 100%);
       padding: 2.4rem 2.6rem; border-radius: 22px; margin-bottom: 1.4rem;
       box-shadow: 0 12px 30px rgba(79,70,229,.25);}
.hero-title {color: #fff; font-size: 2.3rem; font-weight: 800; margin: 0;}
.hero-sub {color: #E0E7FF; font-size: 1.05rem; margin: .5rem 0 0 0; max-width: 760px;}
.hero-badges span {display: inline-block; background: rgba(255,255,255,.18); color: #fff;
       padding: 5px 14px; border-radius: 999px; font-size: .82rem; margin: 16px 8px 0 0;}

.kpi {background: #fff; border: 1px solid #E8ECF4; border-radius: 16px;
      padding: 1.1rem 1.3rem; box-shadow: 0 2px 10px rgba(15,23,42,.06);}
.kpi-label {color: #64748B; font-size: .85rem; font-weight: 500;}
.kpi-value {color: #0F172A; font-size: 1.6rem; font-weight: 700; margin-top: 2px;}

.reco {background: linear-gradient(120deg, #EEF2FF, #FAF5FF); border: 1px solid #DDD6FE;
       border-radius: 16px; padding: 1.1rem 1.4rem; margin: 1rem 0; color: #312E81;}

.cand {display: flex; align-items: center; gap: 1.2rem; background: #fff;
       border: 1px solid #E8ECF4; border-radius: 18px; padding: 1.1rem 1.4rem;
       margin-bottom: .9rem; box-shadow: 0 2px 10px rgba(15,23,42,.05); transition: .2s;}
.cand:hover {transform: translateY(-2px); box-shadow: 0 10px 24px rgba(79,70,229,.14);}
.cand-rank {font-size: 1.7rem; min-width: 46px; text-align: center; font-weight: 700; color: #94A3B8;}
.ring {width: 84px; height: 84px; min-width: 84px; border-radius: 50%; position: relative;
       background: conic-gradient(var(--c) calc(var(--p) * 1%), #E2E8F0 0);
       display: flex; align-items: center; justify-content: center;}
.ring::before {content: ""; position: absolute; inset: 8px; background: #fff; border-radius: 50%;}
.ring span {position: relative; font-weight: 800; font-size: 1.1rem; color: #0F172A;}
.cand-name {font-size: 1.15rem; font-weight: 700; color: #0F172A;}
.cand-meta {color: #64748B; font-size: .88rem; margin: .2rem 0 .5rem;}
.pill {padding: 3px 12px; border-radius: 999px; font-size: .75rem; font-weight: 600;
       margin-left: 8px; vertical-align: middle;}
.chip {display: inline-block; padding: 3px 11px; margin: 3px 4px 3px 0;
       border-radius: 999px; font-size: .8rem; font-weight: 500;}
.chip-green {background: #DCFCE7; color: #166534;}
.chip-red {background: #FEE2E2; color: #991B1B;}
.chip-blue {background: #E0E7FF; color: #3730A3;}
.chip-label {font-size: .75rem; font-weight: 600; color: #64748B; margin-right: 6px;}

.step {background: #fff; border: 1px solid #E8ECF4; border-radius: 16px; padding: 1.3rem;
       box-shadow: 0 2px 10px rgba(15,23,42,.05); height: 100%;}
.step-num {display: inline-block; background: #4F46E5; color: #fff; width: 30px; height: 30px;
       border-radius: 50%; text-align: center; line-height: 30px; font-weight: 700; margin-bottom: 8px;}

[data-testid="stBaseButton-primary"], button[kind="primary"] {
    background: linear-gradient(120deg, #4F46E5, #7C3AED) !important; border: none !important;
    padding: .7rem 2rem !important; font-weight: 600 !important; border-radius: 12px !important;
    box-shadow: 0 6px 16px rgba(79,70,229,.35);}

/* ---------- input cards ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #fff; border: 1px solid #E8ECF4 !important; border-radius: 20px !important;
    box-shadow: 0 6px 24px rgba(79,70,229,.08); padding: .5rem .7rem;}
.card-head {display: flex; align-items: center; gap: 14px; margin-bottom: .8rem;}
.card-icon {width: 52px; height: 52px; min-width: 52px; border-radius: 15px; display: flex;
            align-items: center; justify-content: center; font-size: 1.6rem;}
.card-step {font-size: .72rem; font-weight: 700; letter-spacing: .08em; color: #7C3AED; margin: 0;}
.card-title {font-size: 1.25rem; font-weight: 700; color: #0F172A; margin: 0; line-height: 1.3;}
.card-sub {font-size: .85rem; color: #64748B; margin: 0;}

[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed #A5B4FC !important; border-radius: 16px !important;
    background: linear-gradient(135deg, #EEF2FF, #FAF5FF) !important;
    padding: 1.6rem 1rem !important; transition: .2s;}
[data-testid="stFileUploaderDropzone"]:hover {border-color: #4F46E5 !important; background: #EEF2FF !important;}
[data-testid="stFileUploaderDropzone"] button {
    border: 1.5px solid #4F46E5 !important; color: #4F46E5 !important;
    border-radius: 10px !important; font-weight: 600 !important;}
textarea {border-radius: 12px !important;}

.status {display: inline-block; padding: 5px 16px; border-radius: 999px; font-size: .82rem;
         font-weight: 600; margin-top: .6rem;}
.status-ok {background: #DCFCE7; color: #166534;}
.status-wait {background: #F1F5F9; color: #64748B;}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {background: linear-gradient(180deg, #1E1B4B 0%, #312E81 55%, #4338CA 100%);}
[data-testid="stSidebar"] * {color: #E0E7FF;}
[data-testid="stSidebar"] hr {border-color: rgba(255,255,255,.15) !important;}
[data-testid="stSidebar"] [role="slider"] {background-color: #FFFFFF !important; box-shadow: 0 0 0 4px rgba(165,180,252,.45) !important;}
[data-testid="stSidebar"] [data-testid="stSliderThumbValue"] {color: #FFFFFF !important; font-weight: 700;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {color: #A5B4FC !important; font-size: .8rem;}

.sb-brand {display: flex; align-items: center; gap: 12px; padding: .4rem 0 1rem;}
.sb-logo {width: 46px; height: 46px; border-radius: 14px; font-size: 1.5rem;
          background: linear-gradient(135deg, #7C3AED, #DB2777);
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 6px 16px rgba(0,0,0,.3);}
.sb-name {font-size: 1.25rem; font-weight: 800; color: #FFFFFF !important; margin: 0; line-height: 1.2;}
.sb-tag {font-size: .78rem; color: #A5B4FC !important; margin: 0;}
.sb-label {font-size: .7rem; font-weight: 700; letter-spacing: .12em; color: #A5B4FC !important;
           margin: 1.1rem 0 .3rem;}

.wbar {display: flex; height: 12px; border-radius: 999px; overflow: hidden; margin-top: .2rem;
       background: rgba(255,255,255,.12);}
.wbar-text {background: #A5B4FC; transition: width .3s;}
.wbar-skill {background: #F472B6; transition: width .3s;}
.wlegend {display: flex; justify-content: space-between; font-size: .78rem; margin-top: .45rem;}
.wlegend i {display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px;}

.sb-card {background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14);
          border-radius: 14px; padding: .8rem 1rem; margin-bottom: .6rem; font-size: .82rem;
          line-height: 1.45;}
.sb-card b {color: #FFFFFF !important; font-size: .9rem;}
.sb-tip {background: linear-gradient(120deg, rgba(124,58,237,.45), rgba(219,39,119,.35));
         border-radius: 14px; padding: .85rem 1rem; font-size: .82rem; margin-top: 1rem; line-height: 1.45;}
.sb-foot {text-align: center; font-size: .72rem; color: #818CF8 !important; margin-top: 1.4rem;}
</style>
""", unsafe_allow_html=True)


# ---------- Helper functions ----------
def read_upload(uploaded_file):
    uploaded_file.seek(0)
    return extract_text(uploaded_file)


def load_sample():
    jd = extract_text(os.path.join(SAMPLE_DIR, "job_description.txt"))
    folder = os.path.join(SAMPLE_DIR, "resumes")
    resumes = {f: extract_text(os.path.join(folder, f)) for f in sorted(os.listdir(folder))}
    return jd, resumes


def fit_info(score):
    """Returns (label, text color, background color)."""
    if score >= 60:
        return "Excellent fit", "#15803D", "#DCFCE7"
    if score >= 40:
        return "Good fit", "#1D4ED8", "#DBEAFE"
    if score >= 20:
        return "Fair fit", "#B45309", "#FEF3C7"
    return "Low fit", "#B91C1C", "#FEE2E2"


def split_skills(text):
    return [s for s in text.split(", ") if s]


def chips(skills, css_class):
    if not skills:
        return '<span class="chip-label">none</span>'
    return "".join(f'<span class="chip {css_class}">{escape(s)}</span>' for s in skills)


def candidate_card(rank, row):
    label, color, bg = fit_info(row["Score"])
    medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
    matched = split_skills(row["Matched Skills"])
    missing = split_skills(row["Missing Skills"])
    return (
        '<div class="cand">'
        f'<div class="cand-rank">{medal}</div>'
        f'<div class="ring" style="--p:{row["Score"]};--c:{color}"><span>{row["Score"]:.0f}%</span></div>'
        '<div style="flex:1">'
        f'<div class="cand-name">{escape(row["Candidate"])}'
        f'<span class="pill" style="background:{bg};color:{color}">{label}</span></div>'
        f'<div class="cand-meta">🎓 {row["Education"]} &nbsp;·&nbsp; 💼 {row["Experience (yrs)"]} yrs '
        f'&nbsp;·&nbsp; Skill match {row["Skill Match"]:.0f}% &nbsp;·&nbsp; Text match {row["Text Match"]:.0f}%</div>'
        f'<div><span class="chip-label">MATCHED</span>{chips(matched, "chip-green")}</div>'
        f'<div><span class="chip-label">MISSING</span>{chips(missing, "chip-red")}</div>'
        '</div></div>'
    )


def kpi(label, value):
    return f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>'


def card_head(icon, bg, step, title, sub):
    return (f'<div class="card-head"><div class="card-icon" style="background:{bg}">{icon}</div>'
            f'<div><p class="card-step">{step}</p><p class="card-title">{title}</p>'
            f'<p class="card-sub">{sub}</p></div></div>')


def status(ok, text):
    css = "status-ok" if ok else "status-wait"
    return f'<span class="status {css}">{text}</span>'


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(
        '<div class="sb-brand"><div class="sb-logo">📄</div>'
        '<div><p class="sb-name">ResumeAI</p><p class="sb-tag">Smart screening assistant</p></div></div>',
        unsafe_allow_html=True)

    st.markdown('<p class="sb-label">⚖️ SCORING BALANCE</p>', unsafe_allow_html=True)
    text_pct = st.slider("Text similarity weight (%)", 0, 100, 60, 5, label_visibility="collapsed")
    st.markdown(
        f'<div class="wbar"><div class="wbar-text" style="width:{text_pct}%"></div>'
        f'<div class="wbar-skill" style="width:{100 - text_pct}%"></div></div>'
        f'<div class="wlegend"><span><i style="background:#A5B4FC"></i>Text {text_pct}%</span>'
        f'<span><i style="background:#F472B6"></i>Skills {100 - text_pct}%</span></div>',
        unsafe_allow_html=True)

    st.markdown('<p class="sb-label">🧪 DEMO MODE</p>', unsafe_allow_html=True)
    use_sample = st.toggle("Use built-in sample data", value=False)
    st.caption("Try the app instantly without uploading anything.")

    st.divider()
    st.markdown('<p class="sb-label">🧠 HOW SCORING WORKS</p>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sb-card"><b>🔤 Text match</b><br>TF-IDF + cosine similarity between the job and each resume.</div>'
        '<div class="sb-card"><b>🎯 Skill match</b><br>Share of the required skills the candidate has.</div>'
        '<div class="sb-card"><b>🏁 Final score</b><br>A weighted mix of both, controlled by the slider above.</div>'
        '<div class="sb-tip">💡 <b>Tip:</b> raise the skill weight when specific tools are mandatory for the role.</div>'
        '<p class="sb-foot">Built with Python · scikit-learn · Streamlit</p>',
        unsafe_allow_html=True)

# ---------- Hero ----------
st.markdown("""
<div class="hero">
<p class="hero-title">📄 AI Resume Screening System</p>
<p class="hero-sub">Upload a job description and a stack of resumes. Every candidate is scored with NLP,
ranked, and explained, so recruiters can shortlist in seconds.</p>
<div class="hero-badges"><span>TF-IDF</span><span>Cosine Similarity</span><span>Skill Extraction</span><span>Instant Ranking</span></div>
</div>
""", unsafe_allow_html=True)

# ---------- Inputs ----------
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown(card_head("🎯", "#E0E7FF", "STEP 1", "Job Description",
                              "What role are you hiring for?"), unsafe_allow_html=True)
        tab_up, tab_paste = st.tabs(["📁 Upload file", "✏️ Paste text"])
        with tab_up:
            jd_file = st.file_uploader("Drag and drop the job description here (PDF or TXT)",
                                       type=["pdf", "txt"], key="jd")
        with tab_paste:
            jd_pasted = st.text_area("Paste the job description", height=150,
                                     placeholder="Looking for a Machine Learning Engineer with Python, SQL...")
        if jd_file is not None:
            st.markdown(status(True, f"✅ {jd_file.name} ready"), unsafe_allow_html=True)
        elif jd_pasted.strip():
            st.markdown(status(True, f"✅ Pasted text ready ({len(jd_pasted.split())} words)"),
                        unsafe_allow_html=True)
        else:
            st.markdown(status(False, "⏳ Waiting for job description"), unsafe_allow_html=True)

with col2:
    with st.container(border=True):
        st.markdown(card_head("👥", "#FCE7F3", "STEP 2", "Candidate Resumes",
                              "Add as many resumes as you like."), unsafe_allow_html=True)
        resume_files = st.file_uploader("Drag and drop resumes here (PDF or TXT)",
                                        type=["pdf", "txt"], accept_multiple_files=True)
        if resume_files:
            st.markdown(status(True, f"✅ {len(resume_files)} resume(s) ready"), unsafe_allow_html=True)
        else:
            st.markdown(status(False, "⏳ Waiting for resumes"), unsafe_allow_html=True)

st.write("")

if st.button("🔍 Screen Candidates", type="primary"):
    if use_sample:
        jd_text, resumes = load_sample()
    else:
        jd_text = read_upload(jd_file) if jd_file is not None else jd_pasted
        resumes = {f.name: read_upload(f) for f in resume_files} if resume_files else {}

    if not jd_text.strip():
        st.error("Please upload or paste a job description first (or turn on the sample data).")
    elif not resumes:
        st.error("Please upload at least one resume.")
    else:
        for name in [n for n, t in resumes.items() if not t.strip()]:
            st.warning(f"Could not read text from {name}, so it was skipped.")
            del resumes[name]
        if resumes:
            st.session_state["result"] = rank_candidates(jd_text, resumes, text_pct / 100)
            st.session_state["required"] = extract_skills(jd_text)
            st.session_state["weight"] = text_pct / 100

# ---------- Results ----------
if "result" in st.session_state:
    result = st.session_state["result"]
    required = st.session_state["required"]
    weight = st.session_state["weight"]
    best = result.iloc[0]
    n_matched = len(split_skills(best["Matched Skills"]))
    best_missing = split_skills(best["Missing Skills"])

    st.markdown("## 📊 Results")
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(kpi("Candidates screened", len(result)), unsafe_allow_html=True)
    k2.markdown(kpi("Top candidate", escape(best["Candidate"])), unsafe_allow_html=True)
    k3.markdown(kpi("Top score", f"{best['Score']}%"), unsafe_allow_html=True)
    k4.markdown(kpi("Strong matches", int((result["Score"] >= 40).sum())), unsafe_allow_html=True)

    gaps = f" Main gaps: <b>{', '.join(best_missing)}</b>." if best_missing else " No required skills are missing."
    st.markdown(
        f'<div class="reco">💡 <b>Recommendation:</b> <b>{escape(best["Candidate"])}</b> is the strongest match '
        f'with a score of <b>{best["Score"]}%</b>, covering <b>{n_matched} of {len(required)}</b> required skills.{gaps}</div>',
        unsafe_allow_html=True)

    st.markdown("**Skills required by the job**")
    st.markdown(chips(required, "chip-blue"), unsafe_allow_html=True)
    st.write("")

    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Leaderboard", "📊 Analytics", "🧩 Skill Gap", "📋 Data"])

    with tab1:
        for rank, row in result.iterrows():
            st.markdown(candidate_card(rank, row), unsafe_allow_html=True)

    with tab2:
        names = result["Candidate"].tolist()
        st.markdown("##### Score breakdown")
        fig = go.Figure()
        fig.add_bar(y=names, x=[weight * t for t in result["Text Match"]], orientation="h",
                    name="Text similarity", marker_color="#A5B4FC")
        fig.add_bar(y=names, x=[(1 - weight) * s for s in result["Skill Match"]], orientation="h",
                    name="Skill match", marker_color="#4F46E5")
        fig.update_layout(barmode="stack", height=340, xaxis_title="Score (points)",
                          yaxis=dict(autorange="reversed"), legend=dict(orientation="h", y=1.15),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig)

        st.markdown("##### Top 3 candidates compared")
        edu_map = {"Not found": 0, "Diploma": 25, "Bachelor's": 50, "Master's": 75, "PhD": 100}
        cats = ["Skill Match", "Text Match", "Experience", "Education", "Overall"]
        radar = go.Figure()
        for _, row in result.head(3).iterrows():
            vals = [row["Skill Match"], row["Text Match"],
                    min(row["Experience (yrs)"] / 5, 1) * 100,
                    edu_map.get(row["Education"], 0), row["Score"]]
            radar.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=cats + [cats[0]],
                                            fill="toself", name=row["Candidate"], opacity=0.6))
        radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            height=430, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(radar)
        st.caption("Experience is scaled so that 5 years or more = 100.")

    with tab3:
        st.markdown("##### Which candidate has which required skill?")
        z = [[1 if s in split_skills(row["Matched Skills"]) else 0 for s in required]
             for _, row in result.iterrows()]
        heat = go.Figure(go.Heatmap(z=z, x=required, y=result["Candidate"].tolist(),
                                    colorscale=[[0, "#FEE2E2"], [1, "#22C55E"]],
                                    showscale=False, xgap=4, ygap=4,
                                    hovertemplate="%{y}<br>%{x}: %{z}<extra></extra>"))
        heat.update_layout(height=120 + 60 * len(result), yaxis=dict(autorange="reversed"),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(heat)
        st.caption("Green = candidate has the skill. Red = missing.")

    with tab4:
        table = result[["Candidate", "Score", "Skill Match", "Text Match", "Education", "Experience (yrs)"]]
        st.dataframe(table, column_config={
            "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.1f"),
            "Skill Match": st.column_config.ProgressColumn("Skill Match", min_value=0, max_value=100, format="%.0f%%"),
            "Text Match": st.column_config.ProgressColumn("Text Match", min_value=0, max_value=100, format="%.0f%%"),
        })
        st.download_button("⬇️ Download results (CSV)", result.to_csv().encode("utf-8"),
                           file_name="candidate_ranking.csv", mime="text/csv")
else:
    st.markdown("### How it works")
    s1, s2, s3 = st.columns(3)
    s1.markdown('<div class="step"><div class="step-num">1</div><br><b>Add the job</b><br>Upload or paste the job description.</div>', unsafe_allow_html=True)
    s2.markdown('<div class="step"><div class="step-num">2</div><br><b>Add resumes</b><br>Upload as many PDF or TXT resumes as you like.</div>', unsafe_allow_html=True)
    s3.markdown('<div class="step"><div class="step-num">3</div><br><b>Get the ranking</b><br>See scores, skill gaps and a recommendation instantly.</div>', unsafe_allow_html=True)

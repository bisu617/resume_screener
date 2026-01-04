import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath("src"))
from text_extraction import extract_text_from_pdf
from preprocessing import clean_text
from similarity import calculate_similarity
from scorer import score_resume


st.title("📄 ML Resume Screener")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_text = st.text_area("Paste Job Description")

if resume_file and jd_text:
    with open("temp_resume.pdf", "wb") as f:
        f.write(resume_file.read())

    resume_text = extract_text_from_pdf("temp_resume.pdf")

    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)

    similarity = calculate_similarity(resume_clean, jd_clean)
    score = score_resume(similarity)

    st.metric("Resume Match Score", f"{score}%")

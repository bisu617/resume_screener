import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath("src"))

from text_extraction import extract_text_from_pdf
from preprocessing import clean_text, extract_keywords_from_both
from similarity import calculate_combined_score
from scorer import score_resume, get_score_category, generate_feedback, get_recommendations

st.set_page_config(
    page_title="AI Resume Screener", 
    page_icon="", 
    layout="wide"
)

st.title(" AI Resume Screener")
st.markdown("### Analyze how well your resume matches a job description")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📎 Upload Your Resume")
    resume_file = st.file_uploader(
        "Upload Resume (PDF)", 
        type=["pdf"],
        help="Upload your resume in PDF format"
    )

with col2:
    st.subheader(" Job Description")
    jd_text = st.text_area(
        "Paste the job description here",
        height=250,
        placeholder="Paste the complete job description..."
    )

st.markdown("---")


show_debug = st.checkbox(" Show Debug Output", help="Display detailed analysis")

analyze_button = st.button(
    " Analyze Match", 
    type="primary", 
    use_container_width=True
)

if analyze_button:
    if not resume_file:
        st.error(" Please upload your resume")
    elif not jd_text or len(jd_text.strip()) < 100:
        st.error(" Please paste a complete job description (minimum 100 characters)")
    else:
        with st.spinner(" Analyzing your resume..."):
            try:
           
                temp_file = "temp_resume.pdf"
                with open(temp_file, "wb") as f:
                    f.write(resume_file.read())
                
                resume_text = extract_text_from_pdf(temp_file)
                
                if not resume_text or len(resume_text.strip()) < 50:
                    st.error(" Could not extract text from PDF")
                    os.remove(temp_file)
                    st.stop()
                
                if show_debug:
                    st.write(f"**Debug:** Extracted {len(resume_text)} chars, {len(resume_text.split())} words from resume")
                    st.write(f"**Debug:** JD has {len(jd_text)} chars, {len(jd_text.split())} words")
                
              
                print("\n>>> Step 1: Extracting keywords from ORIGINAL text")
                keyword_data = extract_keywords_from_both(resume_text, jd_text)
                
                if show_debug:
                    st.write(f"**Debug:** Extracted {len(keyword_data['jd_keywords'])} JD keywords")
                    st.write(f"**Debug:** Found {len(keyword_data['matching'])} matches")
                    st.write(f"**Debug:** Sample JD keywords: {keyword_data['jd_keywords'][:10]}")
                
                
                print("\n>>> Step 2: Cleaning text for TF-IDF")
                resume_clean = clean_text(resume_text)
                jd_clean = clean_text(jd_text)
                
                if show_debug:
                    st.write(f"**Debug:** Cleaned resume: {len(resume_clean)} chars, {len(resume_clean.split())} words")
                    st.write(f"**Debug:** Cleaned JD: {len(jd_clean)} chars, {len(jd_clean.split())} words")
                    st.write(f"**Debug:** Resume sample: {resume_clean[:200]}")
                
               
                if len(resume_clean.split()) < 20 or len(jd_clean.split()) < 20:
                    st.error("❌ Text cleaning removed too much content!")
                    st.write(f"Resume words: {len(resume_clean.split())}, JD words: {len(jd_clean.split())}")
                    st.stop()
                
                
                print("\n>>> Step 3: Calculating similarity with CLEANED text")
                scores = calculate_combined_score(resume_clean, jd_clean, keyword_data)
            
                
                final_score = score_resume(scores['combined_score'])
                category, emoji = get_score_category(final_score)
                
              
                st.success("✅ Analysis Complete!")
                st.markdown("---")
                
                
                col1, col2, col3 = st.columns([2, 2, 3])
                
                with col1:
                    st.metric(
                        "Match Score", 
                        f"{final_score}%",
                        help="Overall compatibility"
                    )
                
                with col2:
                    st.metric(
                        "Category", 
                        f"{emoji} {category}",
                        help="Match strength"
                    )
                
                with col3:
                  
                    if final_score >= 60:
                        color = "green"
                    elif final_score >= 40:
                        color = "orange"
                    else:
                        color = "red"
                    
                    st.markdown(f"""
                    <div style='background-color: #f0f2f6; padding: 15px; border-radius: 5px;'>
                        <div style='background-color: #e0e0e0; border-radius: 10px; height: 20px;'>
                            <div style='background-color: {color}; width: {final_score}%; height: 20px; border-radius: 10px;'></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Debug output
                if show_debug:
                    st.markdown("### 🔧 Debug Information")
                    st.json({
                        "TF-IDF Score": round(scores['tfidf_score'], 4),
                        "Keyword Score": round(scores['keyword_score'], 4),
                        "Boost": round(scores.get('boost_applied', 0), 4),
                        "Combined": round(scores['combined_score'], 4),
                        "Final %": final_score,
                        "Keywords Matched": f"{scores['matching_count']}/{scores['total_jd_keywords']}"
                    })
                    
                    st.write("**Sample Matches:**", keyword_data['matching'][:15])
                    st.write("**Sample Missing:**", keyword_data['missing'][:15])
                
               
                feedback_text = generate_feedback(
                    scores, 
                    keyword_data['matching'], 
                    keyword_data['missing']
                )
                st.markdown(feedback_text)
                
                
                recommendations = get_recommendations(final_score, scores)
                if recommendations:
                    st.markdown("---")
                    st.markdown("###  Recommendations")
                    for rec in recommendations:
                        st.markdown(rec)
                
           
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
            except Exception as e:
                st.error(f" An error occurred: {str(e)}")
                
                if show_debug:
                    import traceback
                    st.code(traceback.format_exc())
                
                if os.path.exists("temp_resume.pdf"):
                    os.remove("temp_resume.pdf")


with st.sidebar:
    st.markdown("### ℹ About")
    st.markdown("""
    **How it works:**
    1. Extracts keywords from job description
    2. Matches them against your resume
    3. Calculates semantic similarity
    4. Combines both for final score
    
    **Score Guide:**
    - 70%+: Exceptional 
    - 60-70%: Strong 
    - 50-60%: Good 
    - 40-50%: Moderate 
    - <40%: Needs work 
    """)
def score_resume(similarity_score):
    """Convert similarity score (0-1) to percentage (0-100)"""
    return round(similarity_score * 100, 2)

def get_score_category(score):
    """
    Categorize score into realistic bands based on industry standards
    
    Real-world ATS and resume matching systems typically see:
    - 70%+: Exceptional match (rare, almost perfect alignment)
    - 60-70%: Strong match (very good candidate, definite interview)
    - 50-60%: Good match (solid candidate, worth considering)
    - 40-50%: Moderate match (some fit, needs careful review)
    - 30-40%: Weak match (significant gaps)
    - Below 30%: Poor match (major misalignment)
    """
    if score >= 70:
        return "Exceptional Match", "🟢"
    elif score >= 60:
        return "Strong Match", "🟢"
    elif score >= 50:
        return "Good Match", "🟡"
    elif score >= 40:
        return "Moderate Match", "🟠"
    elif score >= 30:
        return "Weak Match", "🔴"
    else:
        return "Poor Match", "🔴"

def generate_feedback(scores, matching_keywords, missing_keywords):
    """Generate detailed, actionable feedback based on analysis results"""
    feedback = []
    
    # Calculate percentages
    tfidf_pct = round(scores['tfidf_score'] * 100, 1)
    keyword_pct = round(scores['keyword_score'] * 100, 1)
    combined_pct = round(scores['combined_score'] * 100, 1)
    
    # Overall assessment
    feedback.append(f"### 🎯 Overall Assessment\n")
    
    if combined_pct >= 70:
        feedback.append("**Excellent match!** Your resume strongly aligns with this position. You appear to be a highly qualified candidate.")
        feedback.append("\n✨ **What this means:** Your background, skills, and experience closely match what the employer is looking for. Your application has a strong chance of getting past ATS systems and catching a recruiter's attention.\n")
    elif combined_pct >= 60:
        feedback.append("**Strong match!** Your resume shows good alignment with the job requirements.")
        feedback.append("\n👍 **What this means:** You have most of the qualifications needed. With minor improvements, your application should perform well in ATS systems.\n")
    elif combined_pct >= 50:
        feedback.append("**Good match.** Your resume has solid alignment with the role.")
        feedback.append("\n👌 **What this means:** You meet many requirements, but emphasizing relevant experience more prominently could improve your chances.\n")
    elif combined_pct >= 40:
        feedback.append("**Moderate match.** There's some alignment, but gaps exist.")
        feedback.append("\n⚠️ **What this means:** You may want to tailor your resume more specifically to this role or focus on highlighting transferable skills.\n")
    else:
        feedback.append("**Limited match.** Significant gaps between your resume and job requirements.")
        feedback.append("\n⚠️ **What this means:** This role may not be the best fit, or your resume needs substantial revision to highlight relevant experience.\n")
    
    # Score breakdown
    feedback.append("---")
    feedback.append("### 📊 Score Breakdown\n")
    feedback.append(f"**Overall Match Score:** {combined_pct}%\n")
    
    feedback.append(f"**1. Semantic Similarity: {tfidf_pct}%**")
    feedback.append("   - This measures how well your resume content aligns with the job description's overall meaning and context.")
    
    if tfidf_pct >= 50:
        feedback.append("   - ✅ Strong semantic alignment - your experience narrative fits the role well")
    elif tfidf_pct >= 35:
        feedback.append("   - ⚠️ Moderate alignment - consider restructuring to better match job requirements")
    else:
        feedback.append("   - ❌ Weak alignment - significant content gaps exist")
    
    feedback.append(f"\n**2. Keyword Match: {keyword_pct}%**")
    feedback.append(f"   - Found **{scores['matching_count']} out of {scores['total_jd_keywords']}** critical keywords from the job description.")
    
    if keyword_pct >= 60:
        feedback.append("   - ✅ Excellent keyword coverage - ATS systems will likely score you highly")
    elif keyword_pct >= 45:
        feedback.append("   - ⚠️ Good coverage, but adding missing keywords could improve ATS performance")
    else:
        feedback.append("   - ❌ Limited keyword coverage - ATS systems may filter out your resume")
    
    feedback.append("")
    
    # Strengths
    if matching_keywords:
        feedback.append("---")
        feedback.append("### ✅ Your Strengths (Matching Keywords)\n")
        feedback.append("These terms from the job description appear in your resume:\n")
        
        # Sort by relevance (shorter terms first, then alphabetically)
        sorted_matches = sorted(matching_keywords, key=lambda x: (len(x.split()), x))
        
        # Group into single words and phrases
        single_words = [kw for kw in sorted_matches if ' ' not in kw]
        phrases = [kw for kw in sorted_matches if ' ' in kw]
        
        # Display top matches
        display_count = min(30, len(matching_keywords))
        display_matches = sorted_matches[:display_count]
        
        # Format nicely
        feedback.append("**Skills & Technologies:**")
        feedback.append(", ".join(display_matches))
        
        if len(matching_keywords) > display_count:
            feedback.append(f"\n*...plus {len(matching_keywords) - display_count} more matching terms*")
        
        feedback.append(f"\n💪 **Keep emphasizing these strengths** in your resume and cover letter!\n")
    
    # Missing keywords/areas for improvement
    if missing_keywords:
        feedback.append("---")
        feedback.append("### ⚠️ Areas to Strengthen (Missing Keywords)\n")
        feedback.append("These important terms from the job description are not clearly present in your resume:\n")
        
        # Prioritize and sort
        sorted_missing = sorted(missing_keywords, key=lambda x: (len(x.split()), x))
        
        # Display top missing terms
        display_count = min(25, len(missing_keywords))
        display_missing = sorted_missing[:display_count]
        
        feedback.append("**Skills & Keywords to Add:**")
        feedback.append(", ".join(display_missing))
        
        if len(missing_keywords) > display_count:
            feedback.append(f"\n*...and {len(missing_keywords) - display_count} more terms*")
        
        feedback.append("\n")
        feedback.append("#### 💡 Action Steps:")
        feedback.append("1. **If you have this experience:** Add these keywords naturally to your resume")
        feedback.append("   - Include them in your skills section")
        feedback.append("   - Weave them into your job descriptions and achievements")
        feedback.append("   - Use them in context with concrete examples")
        feedback.append("\n2. **If you lack this experience:** Consider:")
        feedback.append("   - Highlighting transferable skills that relate to these areas")
        feedback.append("   - Taking online courses or certifications to gain these skills")
        feedback.append("   - Looking for roles that better match your current skillset")
    
    # Additional tips based on score components
    feedback.append("\n---")
    feedback.append("### 📝 Specific Recommendations\n")
    
    if keyword_pct < 45 and tfidf_pct > 50:
        feedback.append("**Keyword Optimization Needed:**")
        feedback.append("- Your resume has good overall content, but lacks specific terminology")
        feedback.append("- Add exact keywords from the job description throughout your resume")
        feedback.append("- Update your skills section to match the job requirements")
        feedback.append("- Use industry-standard terms and acronyms mentioned in the JD\n")
    
    if tfidf_pct < 45 and keyword_pct > 50:
        feedback.append("**Content Expansion Needed:**")
        feedback.append("- You have the right keywords, but need more context and detail")
        feedback.append("- Expand on your relevant experiences with concrete examples")
        feedback.append("- Quantify achievements (e.g., 'increased efficiency by 30%')")
        feedback.append("- Better align your narrative with the job responsibilities\n")
    
    if tfidf_pct < 45 and keyword_pct < 45:
        feedback.append("**Major Revision Recommended:**")
        feedback.append("- Consider tailoring this resume more specifically for this role")
        feedback.append("- Reorganize to highlight most relevant experience first")
        feedback.append("- Add a summary statement that mirrors the job description")
        feedback.append("- Focus on achievements that relate directly to this position\n")
    
    # General tips
    feedback.append("#### ✨ General Resume Tips:")
    feedback.append("- **Use exact phrasing** from the job description when truthful")
    feedback.append("- **Quantify everything** - use numbers, percentages, timeframes")
    feedback.append("- **Prioritize relevance** - put most relevant experience first")
    feedback.append("- **Be specific** - vague terms like 'worked on' are less impactful")
    feedback.append("- **Update for each job** - customize your resume for every application")
    
    return "\n".join(feedback)

def get_recommendations(score, scores):
    """
    Provide specific, prioritized recommendations based on score analysis
    Returns list of actionable items
    """
    recommendations = []
    
    tfidf_pct = scores['tfidf_score'] * 100
    keyword_pct = scores['keyword_score'] * 100
    
    # Critical issues (address first)
    if keyword_pct < 35:
        recommendations.append("🔴 **CRITICAL:** Add more relevant keywords from the job description. Your current keyword match is very low, which means ATS systems are likely to filter out your resume.")
    
    if tfidf_pct < 30:
        recommendations.append("🔴 **CRITICAL:** Restructure your resume to better align with job requirements. The overall content relevance is currently weak.")
    
    # High priority improvements
    if keyword_pct < 50 and keyword_pct >= 35:
        recommendations.append("🟠 **HIGH PRIORITY:** Incorporate more specific technical terms and tools mentioned in the job description throughout your resume (especially in skills and experience sections).")
    
    if tfidf_pct < 45 and tfidf_pct >= 30:
        recommendations.append("🟠 **HIGH PRIORITY:** Expand on relevant experiences with concrete examples and quantifiable achievements that match the job responsibilities.")
    
    # Medium priority improvements
    if keyword_pct > 60 and tfidf_pct < 50:
        recommendations.append("🟡 **MEDIUM PRIORITY:** While you have good keyword coverage, add more context and detail around your relevant skills to strengthen your candidacy.")
    
    if tfidf_pct > 60 and keyword_pct < 50:
        recommendations.append("🟡 **MEDIUM PRIORITY:** Your content is strong, but add more specific technical terms, certifications, and industry-standard tools mentioned in the JD.")
    
    # Optimization tips (for already decent scores)
    if score >= 50 and score < 70:
        recommendations.append("🟢 **OPTIMIZATION:** Fine-tune your resume by reordering bullet points to highlight most relevant achievements first.")
        recommendations.append("🟢 **OPTIMIZATION:** Add a tailored summary statement at the top that mirrors key requirements from the job description.")
    
    # General recommendations for low scores
    if score < 50:
        recommendations.append("💡 **CONSIDER:** Review the job requirements carefully and honestly assess if this role aligns with your experience. If yes, significant resume tailoring is needed. If no, consider roles that better match your background.")
    
    # Always include these
    if score < 70:
        recommendations.append("📊 **TRACK PROGRESS:** Use this tool to re-analyze after making changes. Aim for a score above 60% for strong consideration.")
    
    return recommendations
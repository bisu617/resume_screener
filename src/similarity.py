from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def calculate_similarity(resume_text, jd_text):
    """
    Calculate TF-IDF similarity
    CRITICAL: Ensure resume_text and jd_text are properly cleaned before calling
    """
    
    if not resume_text or not jd_text:
        print("⚠️ WARNING: Empty text provided to calculate_similarity")
        return 0.0
    
    # Verify we have actual content
    resume_words = len(resume_text.split())
    jd_words = len(jd_text.split())
    
    print(f"\n=== TF-IDF SIMILARITY ===")
    print(f"Resume: {resume_words} words")
    print(f"JD: {jd_words} words")
    
    if resume_words < 10 or jd_words < 10:
        print(f"⚠️ WARNING: Very short text (Resume: {resume_words}, JD: {jd_words})")
        print("This will likely result in low similarity scores")
    
    # Optimized TF-IDF settings - NO max_features limit!
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),      # 1-2 word phrases
        min_df=1,                 # Keep all terms (we have only 2 docs)
        max_df=1.0,               # Don't filter any terms (only 2 docs)
        lowercase=True,           # Already lowercase, but ensure it
        token_pattern=r'\b[\w\+\#\.\-]{2,}\b',  # Min 2 chars, keep tech symbols
        sublinear_tf=True,        # Log scaling
        norm='l2',                # L2 normalization
        # NO max_features - let it use all terms!
    )
    
    try:
        # Fit and transform
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        vocab_size = len(vectorizer.vocabulary_)
        
        print(f"Vocabulary: {vocab_size} unique terms")
        
        if vocab_size == 0:
            print("❌ ERROR: Empty vocabulary - no terms passed tokenization!")
            print("Check if text cleaning removed all content")
            return 0.0
        
        if vocab_size < 30:
            print(f"⚠️ WARNING: Very small vocabulary ({vocab_size} terms)")
            print("This suggests aggressive text cleaning or very short documents")
        
        # Get vectors
        resume_vector = tfidf_matrix[0].toarray()[0]
        jd_vector = tfidf_matrix[1].toarray()[0]
        
        # Analyze overlap
        resume_nonzero = np.sum(resume_vector > 0)
        jd_nonzero = np.sum(jd_vector > 0)
        overlap = np.sum((resume_vector > 0) & (jd_vector > 0))
        
        print(f"Resume: {resume_nonzero} terms, JD: {jd_nonzero} terms")
        print(f"Overlap: {overlap} terms ({overlap/jd_nonzero*100 if jd_nonzero > 0 else 0:.1f}% of JD)")
        
        if overlap == 0:
            print("❌ WARNING: Zero overlap - completely different vocabularies!")
        
        # Show top terms for debugging
        feature_names = vectorizer.get_feature_names_out()
        jd_top_idx = jd_vector.argsort()[-10:][::-1]
        jd_top = [feature_names[i] for i in jd_top_idx if jd_vector[i] > 0][:5]
        print(f"Top JD terms: {jd_top}")
        
        # Calculate similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        raw_score = float(similarity[0][0])
        
        print(f"Raw cosine similarity: {raw_score:.4f} ({raw_score*100:.1f}%)")
        
        return raw_score
        
    except Exception as e:
        print(f"❌ TF-IDF Error: {e}")
        import traceback
        traceback.print_exc()
        return 0.0

def calculate_keyword_match(matching_keywords, jd_keywords):
    """Calculate keyword match with weighted scoring"""
    
    if not jd_keywords:
        return 0.0
    
    # Basic match rate
    match_rate = len(matching_keywords) / len(jd_keywords)
    
    # Weight multi-word phrases more heavily (they're more specific)
    if matching_keywords:
        weighted_score = 0
        total_weight = 0
        
        for kw in jd_keywords:
            weight = len(kw.split())  # Single words = 1, phrases = 2+
            total_weight += weight
            
            if kw in matching_keywords:
                weighted_score += weight
        
        weighted_rate = weighted_score / total_weight if total_weight > 0 else 0
        final_rate = (match_rate + weighted_rate) / 2
        
        print(f"\nKeyword match: {len(matching_keywords)}/{len(jd_keywords)}")
        print(f"Basic: {match_rate:.4f}, Weighted: {weighted_rate:.4f}, Final: {final_rate:.4f}")
        
        return final_rate
    
    return match_rate

def calculate_combined_score(resume_text, jd_text, keyword_data):
    """
    Combined scoring
    
    CRITICAL: resume_text and jd_text should be CLEANED text, not raw text!
    """
    
    print("\n" + "="*60)
    print("CALCULATING COMBINED SCORE")
    print("="*60)
    
    # Verify inputs
    if not resume_text or not jd_text:
        print("❌ ERROR: Empty text provided!")
        return {
            'tfidf_score': 0.0,
            'keyword_score': 0.0,
            'combined_score': 0.0,
            'matching_count': 0,
            'total_jd_keywords': len(keyword_data.get('jd_keywords', [])),
            'boost_applied': 0.0
        }
    
    # Calculate scores
    tfidf_score = calculate_similarity(resume_text, jd_text)
    keyword_score = calculate_keyword_match(
        keyword_data['matching'], 
        keyword_data['jd_keywords']
    )
    
    # Adaptive weighting
    num_keywords = len(keyword_data['jd_keywords'])
    
    if num_keywords >= 50:
        tfidf_weight = 0.55
        keyword_weight = 0.45
    elif num_keywords >= 30:
        tfidf_weight = 0.60
        keyword_weight = 0.40
    else:
        tfidf_weight = 0.65
        keyword_weight = 0.35
    
    print(f"\nWeights: TF-IDF={tfidf_weight}, Keywords={keyword_weight} (based on {num_keywords} JD keywords)")
    
    # Base score
    base_score = (tfidf_score * tfidf_weight) + (keyword_score * keyword_weight)
    
    # Smart boosting
    boost = 0
    if tfidf_score >= 0.35 and keyword_score >= 0.45:
        boost = 0.05
        print(f"Boost: +{boost:.2f} (strong synergy)")
    elif keyword_score >= 0.60 and tfidf_score >= 0.25:
        boost = 0.03
        print(f"Boost: +{boost:.2f} (strong keywords)")
    elif tfidf_score >= 0.40:
        boost = 0.02
        print(f"Boost: +{boost:.2f} (strong semantic)")
    
    combined_score = min(base_score + boost, 1.0)
    
    print(f"\n{'='*60}")
    print("SCORE BREAKDOWN")
    print(f"{'='*60}")
    print(f"TF-IDF:   {tfidf_score:.4f} × {tfidf_weight} = {tfidf_score*tfidf_weight:.4f}")
    print(f"Keywords: {keyword_score:.4f} × {keyword_weight} = {keyword_score*keyword_weight:.4f}")
    print(f"Boost:    +{boost:.4f}")
    print(f"{'-'*60}")
    print(f"COMBINED: {combined_score:.4f} ({combined_score*100:.1f}%)")
    print(f"{'='*60}\n")
    
    return {
        'tfidf_score': tfidf_score,
        'keyword_score': keyword_score,
        'combined_score': combined_score,
        'matching_count': len(keyword_data['matching']),
        'total_jd_keywords': len(keyword_data['jd_keywords']),
        'boost_applied': boost
    }
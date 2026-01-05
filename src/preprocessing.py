import re
import nltk
from nltk.corpus import stopwords

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def clean_text(text):
    """
    Clean text with extensive debugging
    """
    print("\n" + "="*60)
    print("DIAGNOSTIC: TEXT CLEANING")
    print("="*60)
    
    if not text:
        print("❌ ERROR: Empty input text!")
        return ""
    
    print(f"\n1. ORIGINAL TEXT:")
    print(f"   Length: {len(text)} characters")
    print(f"   Word count: {len(text.split())} words")
    print(f"   First 150 chars: {text[:150]}")
    
    # Convert to lowercase
    text = text.lower()
    print(f"\n2. AFTER LOWERCASE:")
    print(f"   First 150 chars: {text[:150]}")
    
    # Replace multiple spaces/newlines with single space
    original_len = len(text)
    text = re.sub(r'\s+', ' ', text)
    print(f"\n3. AFTER WHITESPACE NORMALIZATION:")
    print(f"   Length changed: {original_len} → {len(text)}")
    print(f"   First 150 chars: {text[:150]}")
    
    # Keep alphanumeric, spaces, and common tech symbols
    original_len = len(text)
    text = re.sub(r'[^a-z0-9\s\+\#\.\-]', ' ', text)
    print(f"\n4. AFTER SPECIAL CHARACTER REMOVAL:")
    print(f"   Length changed: {original_len} → {len(text)}")
    print(f"   Characters removed: {original_len - len(text)}")
    print(f"   First 150 chars: {text[:150]}")
    
    # Remove extra spaces
    original_len = len(text)
    text = ' '.join(text.split())
    print(f"\n5. AFTER FINAL CLEANUP:")
    print(f"   Length changed: {original_len} → {len(text)}")
    print(f"   Final word count: {len(text.split())} words")
    print(f"   First 150 chars: {text[:150]}")
    
    if len(text.split()) < 20:
        print(f"\n   ⚠️ WARNING: Very short cleaned text ({len(text.split())} words)")
        print(f"   This may cause TF-IDF issues!")
    
    print("="*60 + "\n")
    return text

def extract_keywords_advanced(text, max_keywords=150):
    """Extract keywords with detailed debugging"""
    
    print("\n" + "="*60)
    print("DIAGNOSTIC: KEYWORD EXTRACTION")
    print("="*60)
    
    if not text:
        print("❌ ERROR: Empty input text!")
        return []
    
    print(f"\n1. INPUT TEXT:")
    print(f"   Length: {len(text)} characters")
    print(f"   Word count: {len(text.split())} words")
    
    # Get stop words
    stop_words = set(stopwords.words('english'))
    stop_words = {w for w in stop_words if len(w) > 2}
    
    additional_stops = {
        'will', 'can', 'must', 'may', 'able', 'need', 'needs',
        'required', 'preferred', 'including', 'such', 'well',
        'within', 'across', 'through', 'using', 'based'
    }
    stop_words.update(additional_stops)
    
    print(f"\n2. STOP WORDS:")
    print(f"   Total stop words: {len(stop_words)}")
    print(f"   Sample: {list(stop_words)[:10]}")
    
    # Extract words
    words = text.lower().split()
    print(f"\n3. WORD EXTRACTION:")
    print(f"   Total words: {len(words)}")
    
    # Count frequencies
    word_freq = {}
    filtered_count = 0
    for word in words:
        if len(word) >= 2 and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        else:
            filtered_count += 1
    
    print(f"   Words kept: {len(word_freq)}")
    print(f"   Words filtered: {filtered_count}")
    print(f"   Top 10 by frequency: {sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]}")
    
    # Extract bigrams
    bigrams = []
    for i in range(len(words) - 1):
        if words[i] not in stop_words or words[i+1] not in stop_words:
            bigram = f"{words[i]} {words[i+1]}"
            if len(bigram) >= 5:
                bigrams.append(bigram)
    
    print(f"\n4. BIGRAM EXTRACTION:")
    print(f"   Total bigrams: {len(bigrams)}")
    
    # Count bigram frequencies
    bigram_freq = {}
    for bigram in bigrams:
        bigram_freq[bigram] = bigram_freq.get(bigram, 0) + 1
    
    print(f"   Unique bigrams: {len(bigram_freq)}")
    print(f"   Top 10: {sorted(bigram_freq.items(), key=lambda x: x[1], reverse=True)[:10]}")
    
    # Combine
    all_terms = list(word_freq.keys()) + list(bigram_freq.keys())
    all_freq = {**word_freq, **bigram_freq}
    
    sorted_terms = sorted(all_terms, key=lambda x: all_freq[x], reverse=True)
    final_keywords = sorted_terms[:max_keywords]
    
    print(f"\n5. FINAL KEYWORDS:")
    print(f"   Total combined terms: {len(all_terms)}")
    print(f"   Returning top {len(final_keywords)} keywords")
    print(f"   Sample (first 15): {final_keywords[:15]}")
    
    print("="*60 + "\n")
    return final_keywords

def smart_keyword_match(keyword, text):
    """Smart matching with debugging for problem cases"""
    text = text.lower()
    keyword = keyword.lower()
    
    # Single word matching
    if ' ' not in keyword:
        # Exact match
        if re.search(r'\b' + re.escape(keyword) + r'\b', text):
            return True
        # Plural
        if re.search(r'\b' + re.escape(keyword) + r's\b', text):
            return True
        # Without 's'
        if keyword.endswith('s'):
            base = keyword[:-1]
            if re.search(r'\b' + re.escape(base) + r'\b', text):
                return True
        # Verb variations
        if re.search(r'\b' + re.escape(keyword) + r'(ed|ing|er|ers)\b', text):
            return True
        return False
    
    # Multi-word phrase matching
    words = keyword.split()
    
    # Exact phrase
    if keyword in text:
        return True
    
    # Proximity matching
    text_words = text.split()
    
    for i in range(len(text_words)):
        first_match = False
        if text_words[i] == words[0]:
            first_match = True
        elif text_words[i] == words[0] + 's' or text_words[i] == words[0] + 'ed':
            first_match = True
        elif words[0].endswith('s') and text_words[i] == words[0][:-1]:
            first_match = True
        
        if first_match:
            window_end = min(i + 10, len(text_words))
            window = text_words[i:window_end]
            
            matches = 1
            for word in words[1:]:
                if word in window or word + 's' in window or word + 'ed' in window:
                    matches += 1
                elif word.endswith('s') and word[:-1] in window:
                    matches += 1
            
            if matches >= len(words) * 0.7:
                return True
    
    return False

def extract_keywords_from_both(resume_text, jd_text):
    """Extract and match keywords with extensive debugging"""
    
    print("\n" + "="*80)
    print("MAIN DIAGNOSTIC: KEYWORD EXTRACTION FROM BOTH DOCUMENTS")
    print("="*80)
    
    print("\n>>> CLEANING RESUME TEXT...")
    resume_clean = clean_text(resume_text)
    
    print("\n>>> CLEANING JD TEXT...")
    jd_clean = clean_text(jd_text)
    
    print("\n>>> EXTRACTING JD KEYWORDS...")
    jd_keywords = extract_keywords_advanced(jd_clean, max_keywords=100)
    
    print("\n>>> EXTRACTING RESUME KEYWORDS...")
    resume_keywords = extract_keywords_advanced(resume_clean, max_keywords=150)
    
    # Match keywords
    print("\n" + "="*60)
    print("KEYWORD MATCHING PROCESS")
    print("="*60)
    
    matching = []
    missing = []
    
    resume_lower = resume_text.lower()
    
    print(f"\nChecking {len(jd_keywords)} JD keywords against resume...")
    
    match_count = 0
    for i, keyword in enumerate(jd_keywords):
        if smart_keyword_match(keyword, resume_lower):
            matching.append(keyword)
            match_count += 1
            if i < 10:  # Show first 10 matches
                print(f"  ✓ Match #{match_count}: '{keyword}'")
        else:
            missing.append(keyword)
            if len(missing) <= 10:  # Show first 10 misses
                print(f"  ✗ Miss: '{keyword}'")
    
    match_rate = len(matching) / len(jd_keywords) if jd_keywords else 0
    
    print(f"\n" + "="*60)
    print("KEYWORD MATCHING SUMMARY")
    print("="*60)
    print(f"Total JD keywords: {len(jd_keywords)}")
    print(f"Matched: {len(matching)} ({match_rate*100:.1f}%)")
    print(f"Missing: {len(missing)} ({(1-match_rate)*100:.1f}%)")
    print(f"\nTop 10 matches: {matching[:10]}")
    print(f"Top 10 missing: {missing[:10]}")
    print("="*60 + "\n")
    
    return {
        'jd_keywords': jd_keywords,
        'resume_keywords': resume_keywords,
        'matching': matching,
        'missing': missing
    }
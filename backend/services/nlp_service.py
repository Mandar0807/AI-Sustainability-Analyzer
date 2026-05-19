import re
import time
import nltk
import numpy as np
import textstat
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer

# ─────────────────────────────────────────────────────
# FILLER PHRASES — remove entirely
# ─────────────────────────────────────────────────────
FILLER_PHRASES = [
    "can you please", "could you please", "could you kindly",
    "i would really like to", "i would like to", "i want to",
    "i am curious about", "i am interested in",
    "could you help me understand", "help me understand",
    "please help me", "please explain to me",
    "i need to know", "i need you to",
    "i was wondering if you could", "i was wondering",
    "would you be able to", "would you mind",
    "if you dont mind", "if possible",
    "as best as you can", "as much as possible",
    "in your own words", "to the best of your ability"
]

# ─────────────────────────────────────────────────────
# REDUNDANT QUALIFIERS — replace or remove
# ─────────────────────────────────────────────────────
REDUNDANT_QUALIFIERS = {
    "in great detail": "in detail",
    "in complete detail": "in detail",
    "in great depth": "in depth",
    "very thoroughly": "",
    "completely and fully": "",
    "in a complete manner": "",
    "in a comprehensive manner": "",
    "in a detailed manner": "in detail",
    "step by step in detail": "step by step",
    "as detailed as possible": "in detail",
    "as thoroughly as possible": "thoroughly",
    "in great detail and depth": "in depth",
    "with full explanation": "",
    "with complete explanation": "",
    "with all details": "",
    "tell me everything about": "explain",
    "tell me all about": "explain",
    "give me a detailed explanation of": "explain",
    "give me a complete overview of": "overview of",
    "provide me with": "",
    "provide a detailed": "provide",
}

# ─────────────────────────────────────────────────────
# VERBOSE STARTERS — replace with imperative
# ─────────────────────────────────────────────────────
VERBOSE_STARTERS = {
    "i want to understand": "explain",
    "i want to know": "what is",
    "i would like to understand": "explain",
    "i would like to know": "what is",
    "can you explain": "explain",
    "could you explain": "explain",
    "can you describe": "describe",
    "could you describe": "describe",
    "can you tell me": "tell me",
    "could you tell me": "tell me",
    "can you help me understand": "explain",
    "could you help me understand": "explain",
    "please provide information on": "explain",
    "please provide information about": "explain",
    "please give me information about": "explain",
    "i need information about": "explain",
    "i need information on": "explain",
}

# ─────────────────────────────────────────────────────
# STOP WORDS for TF-IDF
# ─────────────────────────────────────────────────────
STOP_WORDS = set(stopwords.words('english'))

# POS tags to always keep (nouns, verbs, adjectives, question words)
IMPORTANT_POS = {
    'NN', 'NNS', 'NNP', 'NNPS',  # Nouns
    'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',  # Verbs
    'JJ', 'JJR', 'JJS',  # Adjectives
    'WP', 'WRB', 'WDT',  # Question words (who, what, where, when)
    'CD',  # Numbers
}


def detect_issues(prompt: str) -> list:
    """
    Detect all inefficiency issues in the prompt.
    Returns list of issues with type, found text, tokens wasted.
    """
    issues = []
    prompt_lower = prompt.lower()

    # Check filler phrases
    for phrase in FILLER_PHRASES:
        if phrase in prompt_lower:
            # Estimate tokens (roughly 1 token per word)
            tokens_wasted = len(phrase.split())
            issues.append({
                "type": "filler_phrase",
                "found": phrase,
                "tokens_wasted": tokens_wasted,
                "suggestion": "Remove entirely — adds no meaning",
                "severity": "high"
            })

    # Check redundant qualifiers
    for phrase, replacement in REDUNDANT_QUALIFIERS.items():
        if phrase in prompt_lower:
            tokens_wasted = len(phrase.split()) - len(replacement.split()) if replacement else len(phrase.split())
            issues.append({
                "type": "redundant_qualifier",
                "found": phrase,
                "tokens_wasted": max(tokens_wasted, 1),
                "suggestion": f"Replace with '{replacement}'" if replacement else "Remove entirely",
                "severity": "medium"
            })

    # Check verbose starters
    for phrase, replacement in VERBOSE_STARTERS.items():
        if prompt_lower.startswith(phrase) or f" {phrase}" in prompt_lower:
            tokens_wasted = len(phrase.split()) - len(replacement.split())
            issues.append({
                "type": "verbose_starter",
                "found": phrase,
                "tokens_wasted": max(tokens_wasted, 1),
                "suggestion": f"Replace with '{replacement}'",
                "severity": "high"
            })

    # Check for repeated concepts
    words = word_tokenize(prompt_lower)
    word_freq = {}
    for word in words:
        if word.isalpha() and word not in STOP_WORDS and len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1

    for word, count in word_freq.items():
        if count > 1:
            issues.append({
                "type": "word_repetition",
                "found": f"'{word}' used {count} times",
                "tokens_wasted": count - 1,
                "suggestion": f"Use '{word}' only once",
                "severity": "low"
            })

    return issues


def rule_based_clean(prompt: str) -> tuple:
    """
    Apply rule-based cleaning.
    Returns cleaned prompt and list of changes made.
    """
    cleaned = prompt.strip()
    changes = []

    # Apply verbose starters first
    cleaned_lower = cleaned.lower()
    for phrase, replacement in VERBOSE_STARTERS.items():
        if cleaned_lower.startswith(phrase):
            original_part = cleaned[:len(phrase)]
            cleaned = replacement.capitalize() + cleaned[len(phrase):]
            changes.append(f"Replaced '{original_part}' with '{replacement}'")
            cleaned_lower = cleaned.lower()
            break

    # Apply filler phrases
    for phrase in FILLER_PHRASES:
        if phrase in cleaned.lower():
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            cleaned = pattern.sub('', cleaned)
            changes.append(f"Removed filler: '{phrase}'")

    # Apply redundant qualifiers
    for phrase, replacement in REDUNDANT_QUALIFIERS.items():
        if phrase in cleaned.lower():
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            cleaned = pattern.sub(replacement, cleaned)
            if replacement:
                changes.append(f"Replaced '{phrase}' with '{replacement}'")
            else:
                changes.append(f"Removed redundant qualifier: '{phrase}'")

    # Clean up extra spaces and punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = re.sub(r'\s([?.!,])', r'\1', cleaned)

    # Capitalize first letter
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]

    return cleaned, changes


def tfidf_importance_scoring(prompt: str) -> dict:
    """
    Score each word by TF-IDF importance.
    LLMLingua inspired — low scoring words are candidates for removal.
    """
    words = word_tokenize(prompt.lower())

    if len(words) < 5:
        # Too short to apply TF-IDF meaningfully
        return {word: 1.0 for word in words}

    try:
        # Create a small corpus from the prompt sentences
        # This simulates how LLMLingua scores token importance
        sentences = sent_tokenize(prompt)
        if len(sentences) < 2:
            # Single sentence — duplicate with variations for TF-IDF
            sentences = [prompt, ' '.join(words[::2]), ' '.join(words[1::2])]

        vectorizer = TfidfVectorizer(
            token_pattern=r'\b[a-zA-Z]{2,}\b',
            stop_words=None
        )
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()

        # Get scores for first sentence (original prompt)
        scores = dict(zip(
            feature_names,
            np.asarray(tfidf_matrix[0].todense()).flatten()
        ))

        return scores

    except Exception:
        return {word: 1.0 for word in words}


def llmlingua_style_compress(prompt: str, compression_ratio: float = 0.7) -> tuple:
    """
    LLMLingua inspired compression.
    
    Real LLMLingua uses a small LM to score token perplexity.
    Our version uses TF-IDF scores + POS tags to determine
    which tokens are most important to preserve.
    
    compression_ratio: target ratio to keep (0.7 = keep 70% of tokens)
    """
    words = word_tokenize(prompt)

    if len(words) <= 5:
        return prompt, [], 0

    # Get TF-IDF importance scores
    tfidf_scores = tfidf_importance_scoring(prompt)

    # Get POS tags for each word
    pos_tags = pos_tag(words)

    # Score each word
    word_scores = []
    for i, (word, pos) in enumerate(pos_tags):
        word_lower = word.lower()
        score = tfidf_scores.get(word_lower, 0.0)

        # Boost score for important POS tags
        if pos in IMPORTANT_POS:
            score += 0.5

        # Boost score for words not in stopwords
        if word_lower not in STOP_WORDS:
            score += 0.3

        # Always keep first and last word
        if i == 0 or i == len(words) - 1:
            score += 1.0

        # Boost question words
        if word_lower in ['what', 'how', 'why', 'when', 'where', 'who', 'which']:
            score += 0.8

        # Penalize pure stopwords with no POS importance
        if word_lower in STOP_WORDS and pos not in IMPORTANT_POS:
            score -= 0.2

        word_scores.append((word, score, pos, i))

    # Determine how many words to keep
    target_length = max(3, int(len(words) * compression_ratio))

    # Sort by score, keep top N, then reorder by original position
    sorted_by_score = sorted(word_scores, key=lambda x: x[1], reverse=True)
    words_to_keep = set([item[3] for item in sorted_by_score[:target_length]])

    # Reconstruct prompt keeping original order
    compressed_words = []
    removed_words = []

    for i, (word, score, pos, idx) in enumerate(word_scores):
        if idx in words_to_keep:
            compressed_words.append(word)
        else:
            removed_words.append(word)

    compressed = ' '.join(compressed_words)

    # Clean up
    compressed = re.sub(r'\s+', ' ', compressed).strip()
    if compressed:
        compressed = compressed[0].upper() + compressed[1:]

    tokens_removed = len(words) - len(compressed_words)

    return compressed, removed_words, tokens_removed


def calculate_efficiency_grade(efficiency_score: float) -> str:
    """Calculate letter grade from efficiency score."""
    if efficiency_score >= 90:
        return "A"
    elif efficiency_score >= 80:
        return "B"
    elif efficiency_score >= 65:
        return "C"
    elif efficiency_score >= 50:
        return "D"
    else:
        return "F"


def calculate_readability(text: str) -> dict:
    """Calculate readability metrics."""
    try:
        flesch = textstat.flesch_reading_ease(text)
        fog = textstat.gunning_fog(text)
        return {
            "flesch_reading_ease": round(flesch, 1),
            "gunning_fog_index": round(fog, 1),
            "reading_level": textstat.text_standard(text, float_output=False)
        }
    except Exception:
        return {
            "flesch_reading_ease": 0,
            "gunning_fog_index": 0,
            "reading_level": "Unknown"
        }


def analyze_and_optimize(prompt: str) -> dict:
    """
    Main function — full NLP analysis and optimization pipeline.
    
    Pipeline:
    1. Detect all issues
    2. Rule-based cleaning (filler, qualifiers, starters)
    3. LLMLingua-style TF-IDF compression
    4. Calculate metrics and grade
    """
    start_time = time.time()

    original_word_count = len(prompt.split())
    original_token_estimate = len(word_tokenize(prompt))

    # ── Stage 1: Issue Detection ──────────────────────
    issues = detect_issues(prompt)

    # ── Stage 2: Rule-Based Cleaning ─────────────────
    rule_cleaned, rule_changes = rule_based_clean(prompt)
    rule_token_count = len(word_tokenize(rule_cleaned))
    rule_tokens_saved = original_token_estimate - rule_token_count

    # ── Stage 3: LLMLingua-Style Compression ─────────
    # Apply compression on the rule-cleaned version
    # Target: keep 75% of tokens (aggressive but readable)
    llmlingua_compressed, removed_words, llmlingua_tokens_removed = llmlingua_style_compress(
        rule_cleaned,
        compression_ratio=0.75
    )
    llmlingua_token_count = len(word_tokenize(llmlingua_compressed))

    # ── Stage 4: Final Metrics ────────────────────────
    total_tokens_saved = original_token_estimate - llmlingua_token_count
    total_percent_saved = round(
        (total_tokens_saved / original_token_estimate) * 100, 1
    ) if original_token_estimate > 0 else 0

    # Efficiency score — inverse of waste ratio
    efficiency_score = round(
        (llmlingua_token_count / original_token_estimate) * 100
    ) if original_token_estimate > 0 else 100

    # Flip it — higher score = more efficient original
    original_efficiency = 100 - round(total_percent_saved)

    grade = calculate_efficiency_grade(original_efficiency)

    # Readability of original vs optimized
    original_readability = calculate_readability(prompt)
    optimized_readability = calculate_readability(llmlingua_compressed)

    processing_time = round(time.time() - start_time, 4)

    return {
        # Original
        "original_prompt": prompt,
        "original_word_count": original_word_count,
        "original_token_count": original_token_estimate,
        "original_readability": original_readability,
        "original_efficiency_score": original_efficiency,
        "original_grade": grade,

        # Issues detected
        "issues": issues,
        "total_issues_found": len(issues),

        # Stage 2 — Rule based result
        "rule_based_result": {
            "prompt": rule_cleaned,
            "changes_made": rule_changes,
            "tokens_saved": rule_tokens_saved,
            "token_count": rule_token_count
        },

        # Stage 3 — LLMLingua style result (final)
        "optimized_prompt": llmlingua_compressed,
        "optimized_token_count": llmlingua_token_count,
        "optimized_readability": optimized_readability,
        "removed_words": removed_words[:10],  # show first 10

        # Summary
        "total_tokens_saved": total_tokens_saved,
        "total_percent_saved": total_percent_saved,
        "rule_based_tokens_saved": rule_tokens_saved,
        "llmlingua_additional_tokens_saved": llmlingua_tokens_removed,

        # Meta
        "processing_time_seconds": processing_time,
        "api_cost": 0.0,
        "method": "Rule-based + TF-IDF LLMLingua-style compression"
    }
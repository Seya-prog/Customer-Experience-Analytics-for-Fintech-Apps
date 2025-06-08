# Notebooks README

## Purpose
This directory contains Jupyter notebooks for the analysis and exploration of customer experience data for Ethiopian fintech apps.

## Task 2: Sentiment and Thematic Analysis

### Methodology
- **Sentiment Analysis:**
  - Uses `distilbert-base-uncased-finetuned-sst-2-english` (Hugging Face Transformers) to assign sentiment scores (positive/negative/neutral) to each review.
  - Sentiment scores are signed: positive for positive sentiment, negative for negative sentiment, and zero for neutral.
- **Thematic Analysis:**
  - Extracts significant keywords and n-grams using TF-IDF.
  - Manually groups keywords/phrases into 3–5 overarching themes per bank (e.g., 'Account Access Issues', 'Transaction Performance', 'User Interface & Experience', 'Customer Support', 'Feature Requests').
  - Assigns themes to reviews based on the presence of these keywords/phrases.

### How to Use
1. Open the sentiment and thematic analysis notebook in this directory.
2. Run all cells in order:
   - Load the cleaned data from Task 1.
   - Perform sentiment analysis.
   - Extract keywords and assign themes.
   - Save the final results as a new CSV.
3. Review the documented grouping logic and adjust keyword lists as needed for your analysis.

---

For more details, see the notebook itself or contact the project maintainer.

# Notebooks Directory

This directory contains Jupyter notebooks essential for the analytical phases of the project, including sentiment analysis, thematic analysis, insights generation, and visualizations.

## Notebooks Overview

### `sentiment_and_thematic_analysis.ipynb`
*   **Purpose:** Performs detailed sentiment and thematic analysis on the collected bank reviews.
*   **Methodology:**
    *   **Sentiment Analysis:** Utilizes `distilbert-base-uncased-finetuned-sst-2-english` (Hugging Face Transformers) to assign sentiment labels and signed scores.
    *   **Thematic Analysis:** Extracts keywords using TF-IDF and manually groups them into actionable themes (e.g., 'Account Access Issues', 'Transaction Performance').
    *   Saves the enriched dataset to `data/bank_reviews_with_sentiment_and_themes.csv`.

### `insights_and_recommendations.ipynb`
*   **Purpose:** Derives key business insights and formulates practical recommendations based on the combined sentiment and thematic analysis.
*   **Methodology:**
    *   **Insights:** Identifies drivers of satisfaction and pain points, and compares banks based on sentiment and thematic distributions.
    *   **Visualizations:** Generates various plots (e.g., sentiment distribution, theme distribution by bank, keyword clouds) using Matplotlib and Seaborn.
    *   **Recommendations:** Provides actionable suggestions for app improvements, including bank-specific advice, directly addressing identified pain points and leveraging drivers of satisfaction.
    *   **Ethics:** Discusses potential biases and ethical considerations in the data and analysis.

## How to Use

1.  Ensure all project dependencies are installed (`pip install -r requirements.txt`).
2.  Open the desired notebook in a Jupyter environment (e.g., Jupyter Lab, VS Code with Jupyter extension).
3.  Run all cells sequentially to execute the analysis and generate outputs.
4.  For detailed instructions on running the full project pipeline, refer to the main `README.md`.

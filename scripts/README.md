# Scripts Directory

This directory contains Python scripts essential for the project's data pipeline, including data collection, preprocessing, and database interaction.

## Scripts Overview

### `scrape_and_preprocess.py`
*   **Purpose:** Orchestrates the data collection from Google Play Store and initial preprocessing steps.
*   **Functionality:**
    *   Scrapes user reviews for Commercial Bank of Ethiopia, Bank of Abyssinia, and Dashen Bank using `google_play_scraper`.
    *   Performs data cleaning: removes duplicates, handles missing values, and normalizes date formats.
    *   Saves the cleaned and preprocessed data to `data/bank_reviews_cleaned.csv`.

### `insert_to_oracle.py`
*   **Purpose:** Manages the insertion of processed review data into an Oracle XE database.
*   **Functionality:**
    *   Connects to the specified Oracle XE instance using `cx_Oracle`.
    *   Reads the `bank_reviews_with_sentiment_and_themes.csv` file, which contains the enriched data from sentiment and thematic analysis.
    *   Inserts bank information into the `banks` table (handling existing entries).
    *   Inserts individual review records into the `reviews` table.

## How to Use

Refer to the main `README.md` for detailed instructions on running each script as part of the overall project workflow.

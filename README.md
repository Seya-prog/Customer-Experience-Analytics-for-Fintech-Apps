# Customer Experience Analytics for Fintech Apps

This project analyzes customer reviews for Ethiopian fintech applications, deriving insights into user satisfaction and pain points to inform app improvements.

## Project Structure

```
.github/             # GitHub Actions workflows
data/                # Stores raw and processed data (CSV files, SQL dumps)
notebooks/           # Jupyter notebooks for analysis and visualization
scripts/             # Python scripts for data processing, scraping, and database interaction
test/                # Placeholder for unit tests
requirements.txt     # Python dependencies
README.md            # Project overview and instructions
```

## Task 1: Data Collection and Preprocessing

### Methodology

1. **Data Collection**
   - Scraped user reviews from the Google Play Store for three major Ethiopian banks:
     - Commercial Bank of Ethiopia (`com.combanketh.mobilebanking`)
     - Bank of Abyssinia (`com.boa.boaMobileBanking`)
     - Dashen Bank (`com.dashen.dashensuperapp`)
   - Utilized the `google_play_scraper` Python package to collect over 1,200 reviews (400+ per bank).
   - Collected review text, rating, date, bank name, and source.

2. **Preprocessing**
   - Removed duplicate reviews.
   - Handled missing data by dropping rows with missing review text, rating, or date.
   - Normalized dates to `YYYY-MM-DD` format.
   - Saved the cleaned dataset as `data/bank_reviews_cleaned.csv` with columns: `review`, `rating`, `date`, `bank`, `source`.

### How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the data collection and preprocessing script:
   ```bash
   python scripts/scrape_and_preprocess.py
   ```
3. The cleaned dataset will be saved to `data/bank_reviews_cleaned.csv`.

### Output
- A CSV file with at least 1,200 reviews, <5% missing data, and the required columns.

## Task 2: Sentiment and Thematic Analysis

### Methodology

1. **Sentiment Analysis**
   - Utilized the `distilbert-base-uncased-finetuned-sst-2-english` model from Hugging Face Transformers to assign sentiment scores (positive, negative, neutral) to each review.
   - Sentiment scores were normalized to be signed: positive for positive sentiment, negative for negative, and zero for neutral.

2. **Thematic Analysis**
   - Extracted significant keywords and n-grams using TF-IDF.
   - Manually grouped keywords/phrases into overarching themes such as 'Account Access Issues', 'Transaction Performance', 'User Interface & Experience', 'Customer Support', and 'Feature Requests'.
   - Assigned these themes to reviews based on keyword presence.

### How to Run

1. Ensure all dependencies are installed (`pip install -r requirements.txt`).
2. Open `notebooks/sentiment_and_thematic_analysis.ipynb` in a Jupyter environment.
3. Run all cells sequentially to perform sentiment analysis, thematic analysis, and save the results.
4. The enriched dataset is saved as `data/bank_reviews_with_sentiment_and_themes.csv` with columns: `review_id`, `review_text`, `sentiment_label`, `sentiment_score`, `identified_theme(s)`, `rating`, `date`, `bank`, `source`.

## Task 3: Store Cleaned Data in Oracle

### Methodology

1. **Oracle XE Database Setup**
   - Designed and implemented a relational database schema (`banks` and `reviews` tables) in Oracle XE to persistently store the cleaned and processed review data.
   - A dedicated user (`bank_reviews_user`) was created with appropriate privileges.

2. **Data Insertion**
   - Developed a Python script (`scripts/insert_to_oracle.py`) using `cx_Oracle` to connect to the Oracle database.
   - Inserted bank information into the `banks` table and the processed review data from `bank_reviews_with_sentiment_and_themes.csv` into the `reviews` table.

3. **SQL Dump**
   - Generated an SQL Data Pump dump (`.dmp`) of the `bank_reviews_user` schema, containing both schema definition and populated data.

### How to Run

1. **Oracle Setup:** Ensure Oracle XE is installed and running, and the `bank_reviews_user` with necessary privileges is set up.
2. **Create Schema:** Run the DDL scripts for `banks` and `reviews` tables in your Oracle SQL client.
3. **Insert Data:** Update `scripts/insert_to_oracle.py` with your Oracle credentials and run:
   ```bash
   python scripts/insert_to_oracle.py
   ```
4. **Generate SQL Dump:** From your OS command line (ensure `expdp` is in PATH or navigate to Oracle bin directory):
   ```bash
   expdp bank_reviews_user/your_password@XE DUMPFILE=bank_reviews_dump.dmp DIRECTORY=DATA_PUMP_DIR SCHEMAS=bank_reviews_user LOGFILE=expdp_bank_reviews.log
   ```

## Task 4: Insights and Recommendations

### Methodology

1. **Insight Generation**
   - Identified key drivers of customer satisfaction (e.g., strong UI/UX, positive brand perception) and pain points (e.g., transaction performance issues, account access problems) by analyzing sentiment scores per theme and theme prevalence.
   - Compared the three banks (Dashen, Bank of Abyssinia, CBE) based on their sentiment distribution and dominant themes, highlighting their relative strengths and weaknesses.

2. **Visualization**
   - Created various plots (sentiment distribution, theme distribution, keyword clouds) using Matplotlib and Seaborn to visually represent key findings.

3. **Recommendations**
   - Formulated practical, data-backed improvement suggestions for the banking apps, including both general and bank-specific recommendations targeting identified pain points.

4. **Ethical Considerations**
   - Noted potential biases in review data, such as negative skew, sampling bias, and subjectivity of language.

### How to Run

1. Ensure all dependencies are installed (`pip install -r requirements.txt`).
2. Open `notebooks/insights_and_recommendations.ipynb` in a Jupyter environment.
3. Run all cells sequentially to perform the analysis, generate visualizations, and review the detailed insights and recommendations.

---

For more detailed information on each task, refer to the respective scripts in `scripts/` and notebooks in `notebooks/`. 
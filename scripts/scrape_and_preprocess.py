from google_play_scraper import reviews, Sort
import pandas as pd
from datetime import datetime
from dateutil import parser
import os

def fetch_reviews(app_id, bank_name, n_reviews=400):
    all_reviews = []
    next_token = None
    count = 0
    while count < n_reviews:
        batch, next_token = reviews(
            app_id,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=min(200, n_reviews - count),
            continuation_token=next_token
        )
        for entry in batch:
            all_reviews.append({
                'review': entry.get('content', ''),
                'rating': entry.get('score', None),
                'date': entry.get('at').strftime('%Y-%m-%d') if entry.get('at') else '',
                'bank': bank_name,
                'source': 'Google Play'
            })
        count += len(batch)
        if not next_token or len(batch) == 0:
            break
    return pd.DataFrame(all_reviews)

def preprocess_and_save():
    banks = [
        {'name': 'Commercial Bank of Ethiopia', 'app_id': 'com.combanketh.mobilebanking'},
        {'name': 'Bank of Abyssinia', 'app_id': 'com.boa.boaMobileBanking'},
        {'name': 'Dashen Bank', 'app_id': 'com.dashen.dashensuperapp'}
    ]
    all_reviews = []
    for bank in banks:
        print(f"Fetching reviews for {bank['name']}...")
        df = fetch_reviews(bank['app_id'], bank['name'], n_reviews=400)
        print(f"Fetched {len(df)} reviews for {bank['name']}")
        all_reviews.append(df)
    df = pd.concat(all_reviews, ignore_index=True)
    print("Columns after concat:", df.columns)
    print("Shape after concat:", df.shape)
    print(df.head())
    # Check for expected columns
    expected_cols = {'review', 'rating'}
    if not expected_cols.issubset(df.columns) or df.empty:
        print("Error: DataFrame is missing expected columns or is empty. Please check scraping function and app IDs.")
        return
    # Remove duplicates
    df = df.drop_duplicates(subset=['review', 'bank'])
    # Handle missing data (drop rows with missing review or rating)
    df = df.dropna(subset=['review', 'rating'])
    # Normalize dates
    df['date'] = df['date'].apply(lambda x: parser.parse(x).strftime('%Y-%m-%d') if x else None)
    # Drop rows with missing/invalid dates
    df = df.dropna(subset=['date'])
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/bank_reviews_cleaned.csv', index=False)
    print(f"Saved {len(df)} cleaned reviews to data/bank_reviews_cleaned.csv")

if __name__ == '__main__':
    preprocess_and_save() 
import pytest
import pandas as pd
import os
import sys
from unittest.mock import patch, MagicMock

# Add the scripts directory to the Python path so we can import the scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

# Mock the google_play_scraper module for testing
class MockReviewsResult:
    def __init__(self, content, score, at):
        self.content = content
        self.score = score
        self.at = at

    def get(self, key, default=None):
        if key == 'content':
            return self.content
        elif key == 'score':
            return self.score
        elif key == 'at':
            return self.at
        return default

# Test for scrape_and_preprocess.py
@patch('scrape_and_preprocess.reviews')
def test_scrape_and_preprocess(mock_reviews, tmp_path):
    # Mock the return value of reviews function
    mock_reviews.return_value = ([
        MockReviewsResult('Great app!', 5, pd.Timestamp('2023-01-01')),
        MockReviewsResult('Bad experience', 1, pd.Timestamp('2023-01-02')),
        MockReviewsResult('Good UI', 4, pd.Timestamp('2023-01-03')),
        MockReviewsResult('Bad experience', 1, pd.Timestamp('2023-01-02')) # Duplicate for same bank in real run
    ], None) # No continuation token needed for simple test

    # Temporarily change the working directory to the project root for file paths
    original_cwd = os.getcwd()
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    try:
        # Import the script after changing CWD to correctly resolve relative paths
        import scrape_and_preprocess
        scrape_and_preprocess.preprocess_and_save()

        # Verify the output CSV
        # The script creates 'data/bank_reviews_cleaned.csv' in the project root
        assert os.path.exists('data/bank_reviews_cleaned.csv')

        df_cleaned = pd.read_csv('data/bank_reviews_cleaned.csv')

        # The mock returns 4 reviews per bank, for 3 banks = 12 total.
        # drop_duplicates(subset=['review', 'bank']) will remove 1 duplicate for each bank,
        # so 3 * 3 = 9 unique (review, bank) pairs will remain.
        assert len(df_cleaned) == 9 # <--- CORRECTED ASSERTION
        assert 'review' in df_cleaned.columns
        assert 'rating' in df_cleaned.columns
        assert 'date' in df_cleaned.columns
        assert 'bank' in df_cleaned.columns
        assert 'source' in df_cleaned.columns
        assert (df_cleaned['date'] == pd.to_datetime(df_cleaned['date']).dt.strftime('%Y-%m-%d')).all()

        # Clean up the generated file and directory
        os.remove('data/bank_reviews_cleaned.csv')
        # os.rmdir('data') # This might fail if other files are present or if it's not empty
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


# Test for insert_to_oracle.py
@patch('pandas.read_csv') # <--- ADDED patch for pandas.read_csv
@patch('insert_to_oracle.cx_Oracle')
def test_insert_to_oracle(mock_cx_Oracle, mock_read_csv, tmp_path):
    # Create a dummy CSV for testing
    test_data = {
        'review_id': [1, 2],
        'review_text': ['Great app for banking', 'Slow transfer'],
        'sentiment_label': ['POSITIVE', 'NEGATIVE'],
        'sentiment_score': [0.9, -0.7],
        'identified_theme(s)': ['User Interface & Experience', 'Transaction Performance'],
        'rating': [5, 2],
        'date': ['2023-01-01', '2023-01-02'],
        'bank': ['Commercial Bank of Ethiopia', 'Bank of Abyssinia'],
        'source': ['Google Play', 'Google Play']
    }
    dummy_df = pd.DataFrame(test_data)

    # Mock pandas.read_csv to return our dummy DataFrame
    mock_read_csv.return_value = dummy_df # <--- MOCKED read_csv

    # Mock cx_Oracle connection and cursor
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cx_Oracle.connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    # Mock fetchone to simulate bank existence and new bank_id creation
    # First call for CBE (None means not exists, then (1,) as new ID)
    # Second call for BOA (None means not exists, then (2,) as new ID)
    mock_cur.fetchone.side_effect = [None, (1,), None, (2,), None, None] 

    # Temporarily change the working directory to the project root for file paths
    original_cwd = os.getcwd()
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    try:
        # Import the script after changing CWD
        import insert_to_oracle

        # Call the main function of the script
        insert_to_oracle.main() # <--- No need to patch csv_path directly anymore

        # Verify connection and cursor calls
        mock_cx_Oracle.connect.assert_called_once()
        mock_conn.cursor.assert_called_once()

        # Verify bank insertions/checks (2 SELECTs for existence, 2 INSERTs for new banks, 2 SELECTs to get ID)
        # It will be 4 calls to execute related to banks.
        assert mock_cur.execute.call_count >= 6 # At least 2 selects, 2 inserts for banks, 2 inserts for reviews

        # Verify review insertions (2 reviews)
        # Check the last two execute calls are for reviews INSERT
        insert_calls = [call.args[0] for call in mock_cur.execute.call_args_list if "INSERT INTO reviews" in call.args[0]]
        assert len(insert_calls) == 2

        # Verify commits
        mock_conn.commit.assert_called() # Check if commit was called at least once
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    finally:
        os.chdir(original_cwd) 
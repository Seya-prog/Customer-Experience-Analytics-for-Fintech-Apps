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
        MockReviewsResult('Bad experience', 1, pd.Timestamp('2023-01-02')) # Duplicate
    ], None) # No continuation token needed for simple test

    # Temporarily change the working directory to the project root for file paths
    original_cwd = os.getcwd()
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    try:
        # Import the script after changing CWD to correctly resolve relative paths
        import scrape_and_preprocess
        scrape_and_preprocess.preprocess_and_save()

        # Verify the output CSV
        output_file = os.path.join(tmp_path, 'data', 'bank_reviews_cleaned.csv')
        # Since the script creates its own data directory, we'll verify from there.
        # The script saves to 'data/bank_reviews_cleaned.csv' relative to its execution, which is project root in this test.
        assert os.path.exists('data/bank_reviews_cleaned.csv')

        df_cleaned = pd.read_csv('data/bank_reviews_cleaned.csv')

        assert len(df_cleaned) == 3 # 4 reviews, 1 duplicate removed
        assert 'review' in df_cleaned.columns
        assert 'rating' in df_cleaned.columns
        assert 'date' in df_cleaned.columns
        assert 'bank' in df_cleaned.columns
        assert 'source' in df_cleaned.columns
        assert (df_cleaned['date'] == pd.to_datetime(df_cleaned['date']).dt.strftime('%Y-%m-%d')).all()

        # Clean up the generated file for testing. (Important for CI/CD)
        os.remove('data/bank_reviews_cleaned.csv')
        os.rmdir('data') # Remove the empty data directory if it was created
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


# Test for insert_to_oracle.py
@patch('insert_to_oracle.cx_Oracle')
def test_insert_to_oracle(mock_cx_Oracle, tmp_path):
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

    # Ensure the dummy CSV is in the expected path relative to the script
    test_data_dir = os.path.join(tmp_path, 'data')
    os.makedirs(test_data_dir, exist_ok=True)
    dummy_csv_path = os.path.join(test_data_dir, 'bank_reviews_with_sentiment_and_themes.csv')
    dummy_df.to_csv(dummy_csv_path, index=False)

    # Mock cx_Oracle connection and cursor
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cx_Oracle.connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    # Mock fetchone to simulate bank existence and new bank_id creation
    mock_cur.fetchone.side_effect = [None, (1,), None, (2,)] # For banks check and then getting ID

    # Temporarily change the working directory to the project root for file paths
    original_cwd = os.getcwd()
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    try:
        # Import the script after changing CWD
        import insert_to_oracle

        # Patch the hardcoded CSV path in the script for the test
        with patch('insert_to_oracle.csv_path', dummy_csv_path):
            insert_to_oracle.main() # Assuming insert_to_oracle has a main function to run it

        # Verify connection and cursor calls
        mock_cx_Oracle.connect.assert_called_once()
        mock_conn.cursor.assert_called_once()

        # Verify bank insertions/checks
        assert mock_cur.execute.call_count >= 2 # At least 2 for bank checks
        # For each unique bank, we expect a SELECT then an INSERT (if not exists) then another SELECT to get ID
        # In our mock, we expect 2 SELECTs for banks, and 2 INSERTs for banks (since we mock them not existing initially)
        # Followed by 2 INSERTs for reviews.

        # Verify review insertions (2 reviews)
        assert mock_cur.execute.call_args_list[-1].args[0].strip().startswith("INSERT INTO reviews") # Check the last call
        assert mock_cur.execute.call_args_list[-2].args[0].strip().startswith("INSERT INTO reviews") # Check the second to last call

        # Verify commits
        assert mock_conn.commit.call_count >= 1 # At least one commit
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    finally:
        os.chdir(original_cwd) 
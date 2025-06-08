import pandas as pd
import cx_Oracle
import os

# === CONFIGURATION ===
username = "bank_reviews_user"      
password = "bankreviews321"          
host = "localhost"
port = 1521
sid = "XE"                          

def main():
    # === CONNECT TO ORACLE XE ===
    dsn = cx_Oracle.makedsn(host, port, sid=sid)
    conn = cx_Oracle.connect(user=username, password=password, dsn=dsn)
    cur = conn.cursor()

    # === READ THE PROCESSED CSV ===
    script_dir = os.path.dirname(__file__)
    csv_path = os.path.join(script_dir, "..", "data", "bank_reviews_with_sentiment_and_themes.csv")
    df = pd.read_csv(csv_path)

    # === INSERT BANKS AND GET THEIR IDs ===
    banks = df['bank'].unique()
    bank_id_map = {}

    for bank in banks:
        # Check if bank already exists
        cur.execute("SELECT bank_id FROM banks WHERE bank_name = :1", [bank])
        result = cur.fetchone()
        if result:
            bank_id = result[0]
        else:
            # Insert new bank and get its ID
            cur.execute("INSERT INTO banks (bank_name) VALUES (:1)", [bank])
            conn.commit()
            cur.execute("SELECT bank_id FROM banks WHERE bank_name = :1", [bank])
            bank_id = cur.fetchone()[0]
        bank_id_map[bank] = bank_id

    # === INSERT REVIEWS ===
    for _, row in df.iterrows():
        # Check if review already exists (optional, for idempotency)
        cur.execute("SELECT 1 FROM reviews WHERE review_id = :1", [int(row['review_id'])])
        if cur.fetchone():
            continue  # Skip if already inserted

        cur.execute("""
            INSERT INTO reviews (
                review_id, review_text, sentiment_label, sentiment_score, identified_theme, rating, review_date, bank_id, source
            ) VALUES (
                :1, :2, :3, :4, :5, :6, TO_DATE(:7, 'YYYY-MM-DD'), :8, :9
            )
        """, (
            int(row['review_id']),
            row['review_text'],
            row['sentiment_label'],
            float(row['sentiment_score']),
            row['identified_theme(s)'],
            int(row['rating']),
            row['date'],
            bank_id_map[row['bank']],
            row['source']
        ))

    conn.commit()
    cur.close()
    conn.close()
    print("Data inserted successfully!")

if __name__ == '__main__':
    main()
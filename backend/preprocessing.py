import pandas as pd

def load_sample_data():
    """Create simple sample financial transaction data for testing"""
    data = {
        'transaction_id': [1, 2, 3, 4, 5],
        'amount': [100.50, -250.75, 300.0, 50.25, -120.0],
        'category': ['groceries', 'salary', 'rent', 'transport', 'entertainment'],
        'timestamp': ['2026-01-01', '2026-01-02', '2026-01-03', '2026-01-04', '2026-01-05']
    }
    return pd.DataFrame(data)

def preprocess_data(df):
    """Basic preprocessing: clean, normalize, and add simple features"""
    # Fill any missing values
    df = df.fillna({'amount': 0, 'category': 'unknown'})
    
    # Convert timestamp to proper datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Simple min-max normalization for amount
    if df['amount'].max() != df['amount'].min():
        df['normalized_amount'] = (df['amount'] - df['amount'].min()) / (df['amount'].max() - df['amount'].min())
    else:
        df['normalized_amount'] = 0.0
    
    # Add basic feature
    df['is_positive'] = df['amount'] > 0
    
    print("✅ Preprocessing completed successfully!")
    return df

if __name__ == "__main__":
    print("🚀 Testing backend/preprocessing.py")
    df = load_sample_data()
    print("\nOriginal sample data:")
    print(df)
    
    processed_df = preprocess_data(df)
    print("\nProcessed data:")
    print(processed_df)
    
    print("\n✅ backend/preprocessing.py is ready and working!")
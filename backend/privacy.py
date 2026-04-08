import pandas as pd
import numpy as np
from preprocessing import load_sample_data, preprocess_data

def anonymize_transaction_ids(df):
    """Replace transaction_id with anonymous IDs (simple hashing)"""
    df = df.copy()
    # Student-friendly anonymous ID generation
    df['anonymous_id'] = [f"anon_{abs(hash(str(i))) % 1000000}" for i in range(len(df))]
    if 'transaction_id' in df.columns:
        df = df.drop('transaction_id', axis=1, errors='ignore')
    return df

def add_laplace_noise(df, epsilon=1.0):
    """Add Laplace noise to 'amount' column (basic differential privacy simulation)"""
    df = df.copy()
    if 'amount' not in df.columns:
        return df
    
    sensitivity = 1.0  # Simple assumption for demo
    scale = sensitivity / epsilon
    noise = np.random.laplace(loc=0, scale=scale, size=len(df))
    
    df['noisy_amount'] = df['amount'] + noise
    print(f"✅ Laplace noise added (privacy budget ε={epsilon})")
    return df

def apply_privacy_preservation(df, epsilon=1.0):
    """Apply full privacy pipeline"""
    df = anonymize_transaction_ids(df)
    df = add_laplace_noise(df, epsilon)
    print("✅ Privacy preservation completed successfully!")
    return df

if __name__ == "__main__":
    print("🚀 Testing backend/privacy.py")
    df = load_sample_data()
    print("\nOriginal sample data:")
    print(df)
    
    df = preprocess_data(df)
    print("\nAfter preprocessing:")
    print(df)
    
    private_df = apply_privacy_preservation(df, epsilon=0.5)
    print("\nPrivacy-preserved data (key columns):")
    print(private_df[['anonymous_id', 'noisy_amount', 'category', 'is_positive']])
    
    print("\n✅ backend/privacy.py is ready and working!")
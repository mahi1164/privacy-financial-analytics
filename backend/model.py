import pandas as pd
from sklearn.cluster import KMeans
from preprocessing import load_sample_data, preprocess_data
from privacy import apply_privacy_preservation

def train_clustering_model(df, n_clusters=3):
    """Train simple KMeans model on privacy-preserved noisy_amount"""
    df = df.copy()
    
    # Use only noisy_amount (privacy-safe feature) for clustering
    X = df[['noisy_amount']].values.reshape(-1, 1)
    
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['cluster'] = model.fit_predict(X)
    
    print(f"✅ Clustering model trained with {n_clusters} clusters")
    return df, model

def predict_cluster(model, amount):
    """Predict cluster for a new transaction amount"""
    return model.predict([[amount]])[0]

if __name__ == "__main__":
    print("🚀 Testing backend/model.py")
    
    # Full pipeline: load → preprocess → privacy → model
    df = load_sample_data()
    df = preprocess_data(df)
    private_df = apply_privacy_preservation(df, epsilon=0.5)
    
    clustered_df, model = train_clustering_model(private_df)
    
    print("\nClustered data (key columns):")
    print(clustered_df[['anonymous_id', 'noisy_amount', 'category', 'cluster']])
    
    # Test prediction
    test_amount = 150.0
    cluster = predict_cluster(model, test_amount)
    print(f"\nTest prediction: New transaction of ₹{test_amount} belongs to cluster {cluster}")
    
    print("\n✅ backend/model.py is ready and working!")
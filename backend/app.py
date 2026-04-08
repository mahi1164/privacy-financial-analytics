# backend/app.py
# COMPLETE & RUNNABLE Flask app with CORS fix - Updated for cross-origin requests from Live Server (port 5500)

from flask import Flask
from routes import routes   # Import the routes we created earlier

app = Flask(__name__)

# ====================== CORS FIX (this solves the "Could not reach backend" error) ======================
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Register all API routes
app.register_blueprint(routes)

# ====================== BASIC TEST ROUTE (backup) ======================
@app.route('/test', methods=['GET'])
def test():
    return {"status": "healthy", "message": "PrivacyGuard Backend is running ✅"}

from flask import jsonify
import sqlite3

@app.route('/get-transactions', methods=['GET'])
def get_transactions():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT anonymous_id, noisy_amount, category, cluster, is_positive FROM transactions")
        rows = cursor.fetchall()
        
        transactions = []
        for row in rows:
            transactions.append({
                "anonymous_id": row[0],
                "noisy_amount": row[1],
                "category": row[2],
                "cluster": row[3],
                "is_positive": row[4]
            })
        
        conn.close()
        
        return jsonify({
            "status": "success",
            "data": transactions
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

# 👇 KEEP THIS AT THE VERY END
if __name__ == '__main__':
    print("🚀 Starting PrivacyGuard Backend on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
from flask import Flask

try:
    from .routes import routes
except ImportError:
    from routes import routes


app = Flask(__name__)


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response


app.register_blueprint(routes)


if __name__ == "__main__":
    print("Starting PrivacyGuard Backend on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)

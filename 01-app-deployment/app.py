from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "message": "Cloud & Infrastructure DevSecOps Lab API",
        "environment": os.getenv("APP_ENV", "production")
    })

@app.route('/healthz')
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "healthy", "message": "Backend API running on OpenShift!"})

@app.route('/healthz')
def health():
    return jsonify({"status": "OK"}), 200  # Used by OpenShift livenessProbe

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
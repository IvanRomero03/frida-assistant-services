import logging

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/test")
def test():
    return jsonify({"message": "Hello World!"})

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

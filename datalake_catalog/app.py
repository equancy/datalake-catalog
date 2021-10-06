from flask import Flask, jsonify

app = Flask(__name__)

@app.errorhandler(404)
def error_404(error):
    return jsonify(message="Not found"), 404


@app.errorhandler(400)
def error_400(error):
    return jsonify(message="Bad request"), 400


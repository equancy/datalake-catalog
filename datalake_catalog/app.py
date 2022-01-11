from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

app = Flask(__name__)


@app.errorhandler(HTTPException)
def handle_exception(error):
    if error.code >= 500:  # pragma: no cover
        app.logger.error(error)

    return jsonify(message=error.name), error.code

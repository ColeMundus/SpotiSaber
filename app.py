from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

#configuraration
DEBUG = True

# instantiation
app = Flask(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# sanity check route
@app.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify("pong!")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()

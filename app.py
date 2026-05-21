import random
from flask import Flask, jsonify, render_template, request
from data import QUESTIONS

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/quiz")
def quiz():
    return render_template("index.html")


@app.route("/api/questions")
def get_questions():
    cat_filter = request.args.get("cat")
    pool = [q for q in QUESTIONS if q[1] == cat_filter] if cat_filter else QUESTIONS
    sample = random.sample(pool, min(10, len(pool)))
    result = []
    for abbr, cat, correct, wrongs in sample:
        options = [correct] + list(wrongs)
        random.shuffle(options)
        result.append({"abbr": abbr, "cat": cat, "correct": correct, "options": options})
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

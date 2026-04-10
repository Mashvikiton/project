from flask import Flask, request, jsonify, render_template
from executor import CodeExecutor
from db import (
    get_all_students,
    get_all_datasets,
    assign_dataset,
    ensure_initialized,
    get_student_dataset
)

ensure_initialized()

app = Flask(__name__)

executor = CodeExecutor()

print("APP STARTED")


# =========================
# HTML страницы sssssss
# =========================

@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/tasks")
def tasks_page():
    return render_template("tasks.html")


# =========================
# API
# =========================

@app.route("/run_code", methods=["POST"])
def run_code():
    data = request.get_json()

    if not data:
        return jsonify({"error": "no data provided"}), 400

    code = data.get("code")
    student_id = data.get("student_id")

    # валидация
    if not code:
        return jsonify({"error": "empty code"}), 400

    if student_id is None:
        return jsonify({"error": "student_id required"}), 400

    print(f"[RUN_CODE] student_id={student_id}")

    result = executor.execute(code, student_id)

    return jsonify(result)


@app.route("/students", methods=["GET"])
def students():
    print("[GET] students")
    return jsonify(get_all_students())


@app.route("/datasets", methods=["GET"])
def datasets():
    print("[GET] datasets")
    return jsonify(get_all_datasets())


@app.route("/select_dataset", methods=["POST"])
def select_dataset():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "no data"}), 400

    student_id = data.get("student_id")
    dataset_id = data.get("dataset_id")

    if student_id is None or dataset_id is None:
        return jsonify({"success": False, "error": "missing fields"}), 400

    print(f"[SELECT_DATASET] student={student_id}, dataset={dataset_id}")

    result = assign_dataset(student_id, dataset_id)

    return jsonify(result)


# =========================
# ДОПОЛНИТЕЛЬНЫЕ (важно на будущее)
# =========================

@app.route("/student/<int:student_id>", methods=["GET"])
def get_student(student_id):
    students = get_all_students()

    for s in students:
        if s["id"] == student_id:
            return jsonify(s)

    return jsonify({"error": "student not found"}), 404


@app.route("/dataset_preview/<int:student_id>", methods=["GET"])
def dataset_preview(student_id):
    df = get_student_dataset(student_id)

    if df is None:
        return jsonify({"error": "dataset not found"}), 400

    preview = df.head().to_dict(orient="records")

    return jsonify(preview)


# =========================

if __name__ == "__main__":
    app.run(debug=True)
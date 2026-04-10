import requests

BASE_URL = "http://127.0.0.1:5000"


def safe_json(response):
    try:
        return response.json()
    except Exception:
        return {
            "error": "Invalid JSON response",
            "status_code": response.status_code,
            "text": response.text[:300]
        }


# 1. Получаем студентов
resp = requests.get(f"{BASE_URL}/students")
print(resp.status_code)
students = safe_json(resp)
print(students)

if not students:
    print("No students found")
    exit()

student_id = students[0]["id"]


# 2. Назначаем dataset (один раз)
resp = requests.post(
    f"{BASE_URL}/select_dataset",
    json={"student_id": student_id, "dataset_id": 1}
)
print(resp.status_code)
print(safe_json(resp))


# 3. Запуск кода
resp = requests.post(
    f"{BASE_URL}/run_code",
    json={
        "student_id": student_id,
        "code": "print(df.head())"
    }
)

print(resp.status_code)
print(safe_json(resp))
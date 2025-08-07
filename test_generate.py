import requests

url = "http://localhost:8000/generate"

payload = {
    "data": [
        [5.1, 3.5, 1.4, 0.2, 0],
        [4.9, 3.0, 1.4, 0.2, 0],
        [6.2, 3.4, 5.4, 2.3, 2],
        [5.9, 3.0, 5.1, 1.8, 2],
        [5.5, 2.3, 4.0, 1.3, 1],
        [6.5, 2.8, 4.6, 1.5, 1]
    ],
    "columns": ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"],
    "label_index": 4
}

response = requests.post(url, json=payload)

print("Status:", response.status_code)
try:
    print("Response:")
    print(response.json())
except Exception:
    print(response.text)  # Vis HTML-feil eller traceback

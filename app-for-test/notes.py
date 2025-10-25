import requests

url = "http://localhost:5000/api/whiteboard/upload_note"
headers = {
    "X-Board-ID": "1TNT0FEL",
    "X-Secret-Key": "LOCJRy2GjXn9LlNj"
}

files = {
    "file": ("test.pdf", open("app-for-test/test.pdf", "rb"), "application/pdf")
}

data = {
    "title": "数学笔记",
    "description": "关于二次函数的笔记",
    "tags": "数学,函数,笔记"
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
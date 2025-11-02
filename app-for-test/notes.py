import requests

url = "http://localhost:5000/api/whiteboard/upload_note"
headers = {
    "X-Board-ID": "CBJSH5QG",
    "X-Secret-Key": "QZ1LfLjH0YIoVhrS"
}

files = {
    "file": ("test.jpg", open("app-for-test/v2-12f8da92883cc63efc28682aba59c973_1440w.jpg", "rb"), "application/pdf")
}

data = {
    "title": "数学笔记",
    "description": "关于二次函数的笔记",
    "tags": "数学,函数,笔记"
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
import requests

def get_user_whiteboards(app_id, app_secret, user_token):
    url = "http://localhost:5000/api/whiteboard/framework/auth-with-token"
    payload = {
        "app_id": app_id,
        "app_secret": app_secret,
        "user_token": user_token
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(data)
            return data['whiteboards']
        else:
            print("获取失败:", data.get('error'))
    else:
        print("请求失败，状态码:", response.status_code)
    
    return None

# 使用示例
whiteboards = get_user_whiteboards(
    "app_fXCxzyV0GbRb0zAhNyicGQ", 
    "rxBtBUSC8q-idIPhP9zQYelsUSG6hxV1HQso4mnKlVg",
    "98eINUv2j9xBj3Io8mjJdgLGgcBfYlGjxCKNeLyeBTEJjlredZB5DPJ7wDTdDLku"
)
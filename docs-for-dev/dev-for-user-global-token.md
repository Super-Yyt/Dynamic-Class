### 🧩 Token 获取与认证接口

#### 1. 生成用户Token

生成一个可用于API访问的用户令牌。此令牌代表当前登录教师身份，可访问其所有班级的白板。

- **接口**：`POST /settings/generate-user-token`
- **权限**：需教师身份登录
- **请求体**：无
- **响应示例**：
```json
{
  "success": true,
  "message": "用户令牌生成成功！",
  "user_token": "u6dIh6r2A8x9qL0pV3sW2bN1mK7jR5tG0zX9fE4..."
}
```
- **示例代码 (JavaScript)**:
```javascript
// 在设置页面点击生成令牌按钮触发
async function generateUserToken() {
  const response = await fetch('/settings/generate-user-token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    }
  });
  
  if (response.ok) {
    const result = await response.json();
    console.log('生成的令牌:', result.user_token);
    // 页面将刷新显示新生成的令牌
    location.reload();
  }
}
```

#### 2. 通过用户Token获取白板列表

第三方应用使用开发者凭证和用户Token获取该教师所有可访问的白板信息。

- **接口**：`POST /api/whiteboard/framework/auth-with-token`
- **权限**：开发者应用凭证 + 用户Token
- **请求参数**：

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| app_id | String | 是 | 开发者应用ID  |
| app_secret | String | 是 | 开发者应用密钥  |
| user_token | String | 是 | 用户令牌 |

- **请求示例**：
```json
{
  "app_id": "your_developer_app_id",
  "app_secret": "your_developer_app_secret", 
  "user_token": "u6dIh6r2A8x9qL0pV3sW2bN1mK7jR5tG0zX9fE4..."
}
```
- **响应示例**：
```json
{
  "success": true,
  "whiteboards": [
    {
      "id": 123,
      "name": "三年级二班数学白板",
      "board_id": "wb_5f8a2d1c3b",
      "secret_key": "sk_9e7f5a3b1d",
      "class_name": "三年级二班",
      "class_id": 45,
      "is_online": true,
      "last_heartbeat": "2025-11-01 14:30:25",
      "created_at": "2025-10-15 09:00:00"
    }
  ],
  "count": 1,
  "user": {
    "id": 789,
    "username": "张老师",
    "email": "zhang@example.com"
  }
}
```
- **示例代码 (Python)**:
```python
import requests

def get_user_whiteboards(app_id, app_secret, user_token):
    url = "https://dlass.tech/api/whiteboard/framework/auth-with-token"
    payload = {
        "app_id": app_id,
        "app_secret": app_secret,
        "user_token": user_token
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            return data['whiteboards']
        else:
            print("获取失败:", data.get('error'))
    else:
        print("请求失败，状态码:", response.status_code)
    
    return None

# 使用示例
whiteboards = get_user_whiteboards(
    "your_app_id", 
    "your_app_secret",
    "u6dIh6r2A8x9qL0pV3sW2bN1mK7jR5tG0zX9fE4..."
)
```

### 🔐 Token 管理接口

#### 3. 重置用户Token

使现有令牌失效并生成新令牌。

- **接口**：`POST /settings/reset-user-token`
- **权限**：需教师身份登录
- **示例代码**：
```javascript
// 前端调用重置令牌
function resetUserToken() {
  if (confirm('重置令牌将使现有令牌立即失效，确定要继续吗？')) {
    fetch('/settings/reset-user-token', { method: 'POST' })
      .then(() => location.reload());
  }
}
```

#### 4. 撤销用户Token

完全撤销用户令牌，禁用API访问。

- **接口**：`POST /settings/revoke-user-token`
- **权限**：需教师身份登录
- **示例代码**：
```javascript
// 前端调用撤销令牌
function revokeUserToken() {
  if (confirm('撤销令牌将立即禁用API访问，确定要继续吗？')) {
    fetch('/settings/revoke-user-token', { method: 'POST' })
      .then(() => location.reload());
  }
}
```

### 📡 使用Token访问数据接口

#### 5. 使用用户Token调用白板API

使用用户Token直接访问白板数据接口，可代替单个白板的密钥。

- **接口**：`GET /api/whiteboard/assignments` (示例)
- **认证方式**：在请求头中添加用户Token
- **请求头**：
```
X-User-Token: u6dIh6r2A8x9qL0pV3sW2bN1mK7jR5tG0zX9fE4...
```
- **示例代码 (cURL)**:
```bash
# 获取作业数据
curl -X GET "https://dlass.tech/api/whiteboard/{id}/assignments?date=2025-11-01" \
  -H "X-User-Token: u6dIh6r2A8x9qL0pV3sW2bN1mK7jR5tG0zX9fE4..."
```
- **示例代码 (JavaScript)**:
```javascript
async function getWhiteboardAssignments(userToken, date) {
  const response = await fetch(`/api/whiteboard/assignments?date=${date}`, {
    method: 'GET',
    headers: {
      'X-User-Token': userToken
    }
  });
  
  if (response.ok) {
    return await response.json();
  } else {
    throw new Error('获取数据失败');
  }
}

// 使用示例
getWhiteboardAssignments('u6dIh6r2A8x9qL0pV3sW2bN1mK7jR5tG0zX9fE4...', '2025-11-01')
  .then(data => console.log(data));
```

### 💡 使用流程说明

1. **生成Token**：教师用户在设置页面生成个人API令牌
2. **应用认证**：第三方应用使用开发者凭证+用户Token获取白板列表 
3. **API调用**：使用用户Token直接调用各种白板API接口 

### ⚠️ 安全提示

- 用户Token具有与教师账户相同的权限，请妥善保管
- 建议通过HTTPS传输令牌 
- 定期轮换令牌以增强安全性
- 在不需要时及时撤销令牌
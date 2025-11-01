# 框架认证 API 接口文档

## 概述

框架认证接口允许第三方应用通过应用凭证和白板 token 获取白板的访问密钥，用于集成到其他框架或系统中。

---

## 1. 框架认证接口

### 接口信息
- **URL**: `/api/whiteboard/framework/auth`
- **方法**: `POST`
- **认证**: 应用凭证认证
- **内容类型**: `application/json`

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_id` | string | 是 | 开发者应用ID |
| `app_secret` | string | 是 | 开发者应用密钥 |
| `id` | integer | 是 | 白板ID |
| `token` | string | 是 | 白板访问令牌 |

### 请求示例
```json
{
  "app_id": "your_app_id",
  "app_secret": "your_app_secret",
  "id": 123,
  "token": "whiteboard_token"
}
```

### 响应参数

#### 成功响应 (200)
```json
{
  "success": true,
  "board_id": "wb_abc123",
  "secret_key": "sk_xyz789",
  "whiteboard_name": "一年级一班白板",
  "class_name": "一年级一班"
}
```

#### 错误响应
- **400 Bad Request** - 缺少必要参数
```json
{
  "error": "缺少必要参数"
}
```

- **401 Unauthorized** - 认证失败
```json
{
  "error": "应用认证失败"
}
```

- **401 Unauthorized** - 白板token无效
```json
{
  "error": "白板token无效"
}
```

---

## 2. 重置白板密钥接口

### 接口信息
- **URL**: `/api/whiteboard/reset-secret`
- **方法**: `POST`
- **认证**: 白板token认证
- **内容类型**: `application/json`

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | integer | 是 | 白板ID |
| `token` | string | 是 | 白板访问令牌 |

### 请求示例
```json
{
  "id": 123,
  "token": "whiteboard_token"
}
```

### 响应参数

#### 成功响应 (200)
```json
{
  "success": true,
  "message": "白板密钥重置成功",
  "new_secret_key": "sk_new_secret_456",
  "whiteboard_id": 123,
  "whiteboard_name": "一年级一班白板"
}
```

#### 错误响应
- **400 Bad Request** - 缺少必要参数
```json
{
  "error": "缺少必要参数：id 和 token"
}
```

- **401 Unauthorized** - 认证失败
```json
{
  "error": "白板ID或token无效"
}
```

- **500 Internal Server Error** - 服务器错误
```json
{
  "error": "重置密钥时发生错误"
}
```

---

## 3. 认证流程说明

### 3.1 应用注册流程
1. 开发者在开发者控制台注册应用
2. 获取 `app_id` 和 `app_secret`
3. 应用状态需为 `approved` 才能使用

### 3.2 白板认证流程
1. 班主任在白板设置中生成 token
2. 第三方应用通过以下方式获取白板凭证：
   - 使用 `app_id` 和 `app_secret` 进行应用认证
   - 使用白板 `id` 和 `token` 进行白板认证
3. 获取 `board_id` 和 `secret_key` 用于白板接入

### 3.3 安全重置流程
1. 当怀疑密钥泄露时，可调用重置接口
2. 使用白板 `id` 和当前 `token` 进行认证
3. 系统生成新的 `secret_key`，旧的立即失效

---

## 4. 使用示例

### 4.1 Python 示例
```python
import requests

def framework_auth(app_id, app_secret, whiteboard_id, token):
    url = "https://dlass.tech/api/whiteboard/framework/auth"
    data = {
        "app_id": app_id,
        "app_secret": app_secret,
        "id": whiteboard_id,
        "token": token
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        return result['board_id'], result['secret_key']
    else:
        raise Exception(f"认证失败: {response.json().get('error')}")

def reset_secret(whiteboard_id, token):
    url = "https://dlass.tech/api/whiteboard/reset-secret"
    data = {
        "id": whiteboard_id,
        "token": token
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['new_secret_key']
    else:
        raise Exception(f"重置失败: {response.json().get('error')}")
```

### 4.2 JavaScript 示例
```javascript
async function frameworkAuth(appId, appSecret, whiteboardId, token) {
    const response = await fetch('/api/whiteboard/framework/auth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            app_id: appId,
            app_secret: appSecret,
            id: whiteboardId,
            token: token
        })
    });
    
    const result = await response.json();
    if (response.ok) {
        return {
            boardId: result.board_id,
            secretKey: result.secret_key
        };
    } else {
        throw new Error(result.error);
    }
}

async function resetSecret(whiteboardId, token) {
    const response = await fetch('/api/whiteboard/reset-secret', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: whiteboardId,
            token: token
        })
    });
    
    const result = await response.json();
    if (response.ok) {
        return result.new_secret_key;
    } else {
        throw new Error(result.error);
    }
}
```

---

## 5. 错误代码说明

| 错误代码 | 说明 | 解决方案 |
|----------|------|----------|
| 400 | 请求参数缺失或格式错误 | 检查请求参数是否完整且格式正确 |
| 401 | 认证失败 | 检查应用凭证或白板token是否正确 |
| 404 | 资源不存在 | 检查白板ID是否正确，白板是否被删除 |
| 500 | 服务器内部错误 | 联系系统管理员 |

---

## 6. 相关模型

### DeveloperApp (开发者应用)
- `app_id`: 应用唯一标识
- `app_secret`: 应用密钥
- `status`: 应用状态 (approved/pending/rejected)

### Whiteboard (白板)
- `id`: 白板ID
- `board_id`: 白板标识符
- `secret_key`: 白板密钥
- `token`: 访问令牌
- `is_active`: 是否激活
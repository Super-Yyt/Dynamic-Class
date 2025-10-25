# 白板笔记API完整文档

## 基础信息

### 认证方式
- **白板端认证**: 使用请求头 `X-Board-ID` 和 `X-Secret-Key`
- **Web端认证**: 需要用户登录会话

### 基础URL
- 白板端: `/api/whiteboard`
- Web端: `/web/notes`

### 通用响应格式

#### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  ...其他数据
}
```

#### 错误响应
```json
{
  "error": "错误描述",
  ...其他信息
}
```

## 白板端API（通过白板ID和密钥认证）

### 1. 上传笔记文件

上传一个笔记文件到指定的白板。

- **URL**: `/api/whiteboard/upload_note`
- **方法**: `POST`
- **认证**: 需要白板认证头
- **Content-Type**: `multipart/form-data`

#### 请求头
| 头字段 | 必填 | 描述 |
|--------|------|------|
| X-Board-ID | 是 | 白板ID |
| X-Secret-Key | 是 | 白板密钥 |

#### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| file | File | 是 | 要上传的文件 |
| title | String | 否 | 笔记标题，如不提供则使用文件名 |
| description | String | 否 | 笔记描述 |
| tags | String | 否 | 笔记标签，多个用逗号分隔 |

#### 响应示例
```json
{
  "success": true,
  "message": "文件上传成功",
  "note_id": 1,
  "filename": "数学笔记.pdf",
  "file_path": "1/2024/12/25/数学笔记_1735123456.pdf",
  "file_url": "/uploads/1/1/2024/12/25/数学笔记_1735123456.pdf",
  "file_size": 2048000,
  "uploaded_at": "2024-12-25 10:30:45",
  "class_id": 1,
  "whiteboard_id": 1
}
```

#### 错误状态码
- `400`: 缺少文件、文件类型不支持、文件过大
- `401`: 认证失败
- `500`: 上传失败

### 2. 获取笔记列表

获取白板下的笔记列表，支持分页、筛选和排序。

- **URL**: `/api/whiteboard/notes`
- **方法**: `GET`
- **认证**: 需要白板认证头

#### 请求头
| 头字段 | 必填 | 描述 |
|--------|------|------|
| X-Board-ID | 是 | 白板ID |
| X-Secret-Key | 是 | 白板密钥 |

#### 查询参数
| 参数名 | 类型 | 必填 | 描述 | 默认值 |
|--------|------|------|------|--------|
| page | Integer | 否 | 页码 | 1 |
| per_page | Integer | 否 | 每页数量 | 20 |
| file_type | String | 否 | 按文件类型筛选，如pdf、png | - |
| tag | String | 否 | 按标签筛选 | - |
| search | String | 否 | 搜索关键词，匹配标题、描述、文件名 | - |
| sort_by | String | 否 | 排序字段：filename, file_size, download_count, created_at | created_at |
| sort_order | String | 否 | 排序顺序：asc, desc | desc |

#### 响应示例
```json
{
  "success": true,
  "notes": [
    {
      "id": 1,
      "filename": "数学笔记_1735123456.pdf",
      "original_filename": "数学笔记.pdf",
      "file_path": "1/2024/12/25/数学笔记_1735123456.pdf",
      "file_url": "/uploads/1/1/2024/12/25/数学笔记_1735123456.pdf",
      "file_size": 2048000,
      "file_size_formatted": "2.0 MB",
      "file_type": "pdf",
      "mime_type": "application/pdf",
      "whiteboard_id": 1,
      "class_id": 1,
      "uploaded_by": 1,
      "uploader_name": "张老师",
      "title": "数学笔记",
      "description": "关于二次函数的笔记",
      "tags": "数学,函数,笔记",
      "tags_list": ["数学", "函数", "笔记"],
      "is_public": true,
      "download_count": 5,
      "created_at": "2024-12-25 10:30:45",
      "updated_at": "2024-12-25 10:30:45",
      "whiteboard_name": "高一(1)班白板",
      "class_name": "高一(1)班"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_prev": false,
    "has_next": true
  },
  "filters": {
    "file_type": "pdf",
    "tag": "数学",
    "search": "笔记",
    "sort_by": "created_at",
    "sort_order": "desc"
  }
}
```

### 3. 获取笔记详情

获取指定笔记的详细信息。

- **URL**: `/api/whiteboard/notes/<note_id>`
- **方法**: `GET`
- **认证**: 需要白板认证头

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| note_id | Integer | 是 | 笔记ID |

#### 响应示例
```json
{
  "success": true,
  "note": {
    "id": 1,
    "filename": "数学笔记_1735123456.pdf",
    "original_filename": "数学笔记.pdf",
    "file_path": "1/2024/12/25/数学笔记_1735123456.pdf",
    "file_url": "/uploads/1/1/2024/12/25/数学笔记_1735123456.pdf",
    "file_size": 2048000,
    "file_size_formatted": "2.0 MB",
    "file_type": "pdf",
    "mime_type": "application/pdf",
    "whiteboard_id": 1,
    "class_id": 1,
    "uploaded_by": 1,
    "uploader_name": "张老师",
    "title": "数学笔记",
    "description": "关于二次函数的笔记",
    "tags": "数学,函数,笔记",
    "tags_list": ["数学", "函数", "笔记"],
    "is_public": true,
    "download_count": 5,
    "created_at": "2024-12-25 10:30:45",
    "updated_at": "2024-12-25 10:30:45",
    "whiteboard_name": "高一(1)班白板",
    "class_name": "高一(1)班"
  }
}
```

#### 错误状态码
- `404`: 笔记不存在

### 4. 更新笔记信息

更新笔记的元数据信息（标题、描述、标签等）。

- **URL**: `/api/whiteboard/notes/<note_id>`
- **方法**: `PUT`
- **认证**: 需要白板认证头
- **Content-Type**: `application/json`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| note_id | Integer | 是 | 笔记ID |

#### 请求体
```json
{
  "title": "更新后的标题",
  "description": "更新后的描述",
  "tags": "新标签1,新标签2",
  "is_public": true
}
```

#### 响应示例
```json
{
  "success": true,
  "message": "笔记更新成功",
  "note": {
    // 更新后的笔记详情
  }
}
```

#### 错误状态码
- `404`: 笔记不存在
- `500`: 更新失败

### 5. 删除笔记

删除指定笔记，包括数据库记录和物理文件。

- **URL**: `/api/whiteboard/notes/<note_id>`
- **方法**: `DELETE`
- **认证**: 需要白板认证头

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| note_id | Integer | 是 | 笔记ID |

#### 响应示例
```json
{
  "success": true,
  "message": "笔记删除成功"
}
```

#### 错误状态码
- `404`: 笔记不存在
- `500`: 删除失败

### 6. 下载笔记文件

下载笔记文件。

- **URL**: `/api/whiteboard/notes/<note_id>/download`
- **方法**: `GET`
- **认证**: 需要白板认证头

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| note_id | Integer | 是 | 笔记ID |

#### 响应
- 返回文件流，Content-Type为文件的MIME类型
- Content-Disposition为附件，使用原始文件名

#### 错误状态码
- `404`: 笔记不存在或文件不存在

### 7. 获取笔记统计

获取白板笔记的统计信息。

- **URL**: `/api/whiteboard/notes/stats`
- **方法**: `GET`
- **认证**: 需要白板认证头

#### 响应示例
```json
{
  "success": true,
  "stats": {
    "total_notes": 50,
    "total_size": 10485760,
    "total_size_formatted": "10.0 MB",
    "file_types": {
      "pdf": 30,
      "png": 15,
      "jpg": 5
    },
    "recent_notes": [
      {
        "id": 50,
        "title": "最新笔记",
        "original_filename": "最新笔记.pdf",
        "file_type": "pdf",
        "created_at": "2024-12-25 15:30:00",
        "file_size_formatted": "2.1 MB"
      }
    ]
  }
}
```

## Web端API（教师使用，需要登录）

### 8. 获取班级笔记列表

获取指定班级的所有笔记（跨白板），供教师管理使用。

- **URL**: `/web/notes/classes/<class_id>/notes`
- **方法**: `GET`
- **认证**: 需要用户登录会话，且用户必须是该班级的班主任或授课教师。

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| class_id | Integer | 是 | 班级ID |

#### 查询参数
| 参数名 | 类型 | 必填 | 描述 | 默认值 |
|--------|------|------|------|--------|
| page | Integer | 否 | 页码 | 1 |
| per_page | Integer | 否 | 每页数量 | 20 |
| whiteboard_id | Integer | 否 | 按白板筛选 | - |
| file_type | String | 否 | 按文件类型筛选 | - |
| search | String | 否 | 搜索关键词 | - |

#### 响应示例
```json
{
  "success": true,
  "notes": [
    {
      "id": 1,
      "filename": "数学笔记_1735123456.pdf",
      "original_filename": "数学笔记.pdf",
      "file_path": "1/2024/12/25/数学笔记_1735123456.pdf",
      "file_url": "/uploads/1/1/2024/12/25/数学笔记_1735123456.pdf",
      "file_size": 2048000,
      "file_size_formatted": "2.0 MB",
      "file_type": "pdf",
      "mime_type": "application/pdf",
      "whiteboard_id": 1,
      "class_id": 1,
      "uploaded_by": 1,
      "uploader_name": "张老师",
      "title": "数学笔记",
      "description": "关于二次函数的笔记",
      "tags": "数学,函数,笔记",
      "tags_list": ["数学", "函数", "笔记"],
      "is_public": true,
      "download_count": 5,
      "created_at": "2024-12-25 10:30:45",
      "updated_at": "2024-12-25 10:30:45",
      "whiteboard_name": "高一(1)班白板",
      "class_name": "高一(1)班"
    }
  ],
  "whiteboards": [
    {
      "id": 1,
      "name": "高一(1)班白板"
    },
    {
      "id": 2,
      "name": "高一(1)班作业板"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

#### 错误状态码
- `403`: 无权限访问该班级的笔记

### 9. 删除班级笔记

删除指定班级的笔记（教师使用）。

- **URL**: `/web/notes/notes/<note_id>`
- **方法**: `DELETE`
- **认证**: 需要用户登录会话，且用户必须是该班级的班主任或授课教师。

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| note_id | Integer | 是 | 笔记ID |

#### 响应示例
```json
{
  "success": true,
  "message": "笔记删除成功"
}
```

#### 错误状态码
- `403`: 无权限删除该笔记
- `404`: 笔记不存在
- `500`: 删除失败

## 文件访问API

### 10. 访问上传的文件

通过URL访问上传的文件，需要相应的班级访问权限。

- **URL**: `/uploads/<class_id>/<path:filename>`
- **方法**: `GET`
- **认证**: 需要用户登录会话，且用户有该班级的访问权限。

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| class_id | Integer | 是 | 班级ID |
| filename | String | 是 | 文件路径 |

#### 响应
- 返回文件流

#### 错误状态码
- `403`: 无权限访问该班级的文件
- `404`: 文件不存在

## 技术规格

### 文件限制
- **最大文件大小**: 10MB
- **允许的文件类型**:
  - 图片: png, jpg, jpeg, gif, bmp
  - 文档: pdf, txt, md
  - Office: ppt, pptx, doc, docx
  - 压缩文件: zip, rar

### 文件存储结构
```
uploads/
├── {class_id}/           # 班级ID
│   └── {whiteboard_id}/  # 白板ID
│       └── {year}/       # 年
│           └── {month}/  # 月（两位数）
│               └── {day}/ # 日（两位数）
│                   └── {filename}_{timestamp}.{ext}
```

### 分页参数
- 默认每页20条记录
- 最大每页100条记录（可配置）

## 使用示例

### Python requests 示例

#### 上传笔记
```python
import requests

url = "http://localhost:5000/api/whiteboard/upload_note"
headers = {
    "X-Board-ID": "your_whiteboard_id",
    "X-Secret-Key": "your_secret_key"
}

files = {
    "file": ("数学笔记.pdf", open("数学笔记.pdf", "rb"), "application/pdf")
}

data = {
    "title": "数学笔记",
    "description": "关于二次函数的笔记",
    "tags": "数学,函数,笔记"
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

#### 获取笔记列表
```python
import requests

url = "http://localhost:5000/api/whiteboard/notes"
headers = {
    "X-Board-ID": "your_whiteboard_id",
    "X-Secret-Key": "your_secret_key"
}

params = {
    "page": 1,
    "per_page": 20,
    "file_type": "pdf",
    "search": "数学",
    "sort_by": "created_at",
    "sort_order": "desc"
}

response = requests.get(url, headers=headers, params=params)
print(response.json())
```

#### 下载笔记
```python
import requests

url = "http://localhost:5000/api/whiteboard/notes/1/download"
headers = {
    "X-Board-ID": "your_whiteboard_id",
    "X-Secret-Key": "your_secret_key"
}

response = requests.get(url, headers=headers, stream=True)

with open("下载的笔记.pdf", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
```
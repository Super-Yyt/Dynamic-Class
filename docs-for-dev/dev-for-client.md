# 白板客户端与服务端通信文档

## 概述

本文档描述了白板客户端与服务端之间的完整通信协议，包括 RESTful API 和 Socket.IO 实时通信。

## 基础信息

- **服务端地址**: `https://dlass.tech`
- **API 前缀**: `/api/whiteboard`
- **Socket.IO 路径**: `/socket.io`
- **认证方式**: 白板凭证认证

## 1. 认证方式

### 1.1 白板凭证
每个白板都有唯一的认证凭证：
- `board_id`: 白板唯一标识 (20位字符串)
- `secret_key`: 白板密钥 (50位字符串)

### 1.2 Socket.IO 连接认证
```javascript
const socket = io('https://dlass.tech', {
  query: {
    board_id: 'your_board_id',
    secret_key: 'your_secret_key'
  }
});
```

### 1.3 REST API 认证
使用 HTTP 头进行认证：
```javascript
headers: {
  'X-Board-ID': 'your_board_id',
  'X-Secret-Key': 'your_secret_key'
}
```

## 2. RESTful API 接口

### 2.1 获取作业列表
**端点**: `GET /api/whiteboard/assignments`

**请求头**:
```
X-Board-ID: your_board_id
X-Secret-Key: your_secret_key
```

**查询参数**:
- `date` (可选): 过滤日期，格式 `YYYY-MM-DD`
- `subject` (可选): 学科名称

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "数学作业",
      "description": "完成第1-5页习题",
      "subject": "数学",
      "due_date": "2024-01-15 23:59:00",
      "created_at": "2024-01-10 10:00:00"
    },
    {
      "id": 2,
      "title": "语文作文",
      "description": "写一篇关于春天的作文",
      "subject": "语文",
      "due_date": "2024-01-16 23:59:00",
      "created_at": "2024-01-10 11:00:00"
    }
  ],
  "count": 2
}
```

**错误响应**:
```json
{
  "error": "认证失败"
}
```

### 2.2 获取任务列表
**端点**: `GET /api/whiteboard/tasks`

**请求头**:
```
X-Board-ID: your_board_id
X-Secret-Key: your_secret_key
```

**查询参数**:
- `date` (可选): 过滤日期，格式 `YYYY-MM-DD`
- `priority` (可选): 优先级 (1-3)
- `status` (可选): 状态 (`pending`, `completed`)

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "打扫卫生",
      "description": "打扫教室卫生",
      "priority": 1,
      "action_id": 0,
      "due_date": "2024-01-15 17:00:00",
      "is_acknowledged": false,
      "is_completed": false,
      "created_at": "2024-01-10 09:00:00"
    },
    {
      "id": 2,
      "title": "收作业",
      "description": "收集数学作业",
      "priority": 3,
      "action_id": 1,
      "due_date": "2024-01-15 12:00:00",
      "is_acknowledged": true,
      "is_completed": false,
      "created_at": "2024-01-10 08:00:00"
    }
  ],
  "count": 2
}
```

### 2.3 获取公告列表
**端点**: `GET /api/whiteboard/announcements`

**请求头**:
```
X-Board-ID: your_board_id
X-Secret-Key: your_secret_key
```

**查询参数**:
- `date` (可选): 过滤日期，格式 `YYYY-MM-DD`
- `long_term` (可选): 是否长期公告 (`true`/`false`)

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "重要通知",
      "content": "明天放假一天",
      "is_long_term": false,
      "created_at": "2024-01-10 08:00:00"
    },
    {
      "id": 2,
      "title": "校规校纪",
      "content": "请同学们遵守校规校纪",
      "is_long_term": true,
      "created_at": "2024-01-01 00:00:00"
    }
  ],
  "count": 2
}
```

### 2.4 获取所有内容
**端点**: `GET /api/whiteboard/all`

**请求头**:
```
X-Board-ID: your_board_id
X-Secret-Key: your_secret_key
```

**查询参数**:
- `date` (可选): 过滤日期，格式 `YYYY-MM-DD`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "type": "task",
      "id": 1,
      "title": "打扫卫生",
      "description": "打扫教室卫生",
      "priority": 1,
      "action_id": 0,
      "due_date": "2024-01-15 17:00:00",
      "is_acknowledged": false,
      "is_completed": false,
      "created_at": "2024-01-10 09:00:00"
    },
    {
      "type": "announcement",
      "id": 1,
      "title": "重要通知",
      "content": "明天放假一天",
      "is_long_term": false,
      "created_at": "2024-01-10 08:00:00"
    },
    {
      "type": "assignment",
      "id": 1,
      "title": "数学作业",
      "description": "完成第1-5页习题",
      "subject": "数学",
      "due_date": "2024-01-15 23:59:00",
      "created_at": "2024-01-10 10:00:00"
    }
  ],
  "count": 3,
  "tasks_count": 1,
  "announcements_count": 1,
  "assignments_count": 1
}
```

### 2.5 确认任务
**端点**: `POST /api/whiteboard/tasks/{task_id}/acknowledge`

**请求头**:
```
X-Board-ID: your_board_id
X-Secret-Key: your_secret_key
```

**响应示例**:
```json
{
  "success": true
}
```

**错误响应**:
```json
{
  "error": "任务不存在"
}
```

### 2.6 完成任务
**端点**: `POST /api/whiteboard/tasks/{task_id}/complete`

**请求头**:
```
X-Board-ID: your_board_id
X-Secret-Key: your_secret_key
```

**响应示例**:
```json
{
  "success": true
}
```

### 2.7 心跳检测
**端点**: `POST /api/whiteboard/heartbeat`

**请求头**:
```
X-Board-ID: your_board_id
X-Secret-Key: your_secret_key
```

**响应示例**:
```json
{
  "success": true,
  "message": "心跳接收成功"
}
```

## 3. Socket.IO 事件

### 3.1 连接事件

#### 客户端连接
```javascript
const socket = io('https://dlass.tech', {
  query: {
    board_id: 'your_board_id',
    secret_key: 'your_secret_key'
  }
});
```

#### 连接成功响应
**事件**: `connected`
```json
{
  "status": "success",
  "message": "认证成功"
}
```

#### 连接失败响应
```json
{
  "status": "error",
  "message": "认证失败"
}
```

### 3.2 心跳事件

#### 发送心跳
**事件**: `heartbeat`
```javascript
socket.emit('heartbeat', {
  board_id: 'your_board_id'
});
```

**频率建议**: 每15-20秒发送一次

### 3.3 接收实时数据

#### 新任务
**事件**: `new_task`
```json
{
  "id": 1,
  "title": "新任务标题",
  "description": "任务描述",
  "priority": 1,
  "action_id": 0,
  "subject": "数学",
  "due_date": "2024-01-15 17:00:00",
  "created_at": "2024-01-10 09:00:00",
  "teacher_name": "张老师"
}
```

#### 新作业
**事件**: `new_assignment`
```json
{
  "id": 1,
  "title": "数学作业",
  "description": "完成习题",
  "subject": "数学",
  "due_date": "2024-01-15 23:59:00",
  "created_at": "2024-01-10 10:00:00",
  "teacher_name": "李老师"
}
```

#### 更新作业
**事件**: `update_assignment`
```json
{
  "id": 1,
  "title": "更新的作业标题",
  "description": "更新的作业描述",
  "subject": "数学",
  "due_date": "2024-01-16 23:59:00",
  "updated_at": "2024-01-10 11:00:00",
  "teacher_name": "李老师"
}
```

#### 新公告
**事件**: `new_announcement`
```json
{
  "id": 1,
  "title": "重要通知",
  "content": "通知内容",
  "is_long_term": false,
  "created_at": "2024-01-10 08:00:00",
  "teacher_name": "王老师"
}
```

#### 删除任务
**事件**: `delete_task`
```json
{
  "task_id": 1
}
```

#### 删除作业
**事件**: `delete_assignment`
```json
{
  "assignment_id": 1
}
```

#### 删除公告
**事件**: `delete_announcement`
```json
{
  "announcement_id": 1
}
```

#### 任务状态更新
**事件**: `task_updated`
```json
{
  "id": 1,
  "title": "任务标题",
  "is_acknowledged": true,
  "is_completed": false
}
```

#### 白板状态更新
**事件**: `whiteboard_status_update`
```json
{
  "whiteboard_id": 1,
  "is_online": true,
  "last_heartbeat": "2024-01-10 10:30:00"
}
```

### 3.4 客户端发送事件

#### 确认任务
**事件**: `task_acknowledged`
```javascript
socket.emit('task_acknowledged', {
  task_id: 1
});
```

#### 完成任务
**事件**: `task_completed`
```javascript
socket.emit('task_completed', {
  task_id: 1
});
```

## 4. 完整 Python 客户端实现

```python
import socketio
import requests
import json
import time
import threading
import argparse
from datetime import datetime
import sys

class WhiteboardClient:
    def __init__(self, server_url, board_id, secret_key):
        self.server_url = server_url
        self.board_id = board_id
        self.secret_key = secret_key
        self.sio = None
        self.is_connected = False
        self.heartbeat_interval = 15  # 秒
        
    def connect(self):
        """连接到白板服务器"""
        try:
            # 初始化Socket.IO客户端
            self.sio = socketio.Client()
            
            # 设置事件处理器
            self.setup_event_handlers()
            
            print(f"正在连接到白板服务器 {self.server_url}...")
            
            # 使用查询参数连接
            self.sio.connect(
                f"{self.server_url}?board_id={self.board_id}&secret_key={self.secret_key}"
            )
            
            # 等待连接建立
            time.sleep(2)
            
            if self.is_connected:
                print("✓ 连接成功！输入 'help' 查看可用命令")
            else:
                print("✗ 连接失败")
                
        except Exception as e:
            print(f"连接失败: {e}")
    
    def setup_event_handlers(self):
        """设置Socket.IO事件处理器"""
        
        @self.sio.event
        def connect():
            self.is_connected = True
            print("✓ Socket.IO 连接已建立")
            
        @self.sio.event
        def disconnect():
            self.is_connected = False
            print("✗ 与服务器断开连接")
            self.stop_heartbeat()
            
        @self.sio.event
        def connected(data):
            if data.get('status') == 'success':
                print("✓ 白板认证成功")
                self.start_heartbeat()
            else:
                print(f"✗ 认证失败: {data.get('message')}")
                
        @self.sio.event
        def new_task(data):
            print("\n" + "="*50)
            print("📋 收到新任务!")
            self._print_task(data)
            print("="*50)
            
        @self.sio.event
        def new_assignment(data):
            print("\n" + "="*50)
            print("📚 收到新作业!")
            self._print_assignment(data)
            print("="*50)
            
        @self.sio.event
        def update_assignment(data):
            print("\n" + "="*50)
            print("🔄 作业已更新!")
            self._print_assignment(data)
            print("="*50)
            
        @self.sio.event
        def new_announcement(data):
            print("\n" + "="*50)
            print("📢 收到新公告!")
            self._print_announcement(data)
            print("="*50)
            
        @self.sio.event
        def delete_task(data):
            task_id = data.get('task_id')
            print(f"\n🗑️  任务已删除: ID {task_id}")
            
        @self.sio.event
        def delete_assignment(data):
            assignment_id = data.get('assignment_id')
            print(f"\n🗑️  作业已删除: ID {assignment_id}")
            
        @self.sio.event
        def delete_announcement(data):
            announcement_id = data.get('announcement_id')
            print(f"\n🗑️  公告已删除: ID {announcement_id}")
            
        @self.sio.event
        def task_updated(data):
            print(f"\n🔄 任务状态更新:")
            print(f"   ID: {data.get('id')}")
            print(f"   标题: {data.get('title')}")
            print(f"   已确认: {data.get('is_acknowledged')}")
            print(f"   已完成: {data.get('is_completed')}")
            
        @self.sio.event
        def whiteboard_status_update(data):
            status = "在线" if data.get('is_online') else "离线"
            last_heartbeat = data.get('last_heartbeat', '未知')
            print(f"\n📊 白板状态更新: {status}")
            print(f"   最后心跳: {last_heartbeat}")
            
        @self.sio.event
        def connect_error(data):
            print(f"连接错误: {data}")
            
        @self.sio.event
        def error(data):
            print(f"Socket.IO 错误: {data}")
    
    def start_heartbeat(self):
        """启动心跳线程"""
        def heartbeat_loop():
            while self.is_connected:
                try:
                    if hasattr(self.sio, 'connected') and self.sio.connected:
                        self.sio.emit('heartbeat', {
                            'board_id': self.board_id
                        })
                        # print("❤️  心跳发送成功")
                    time.sleep(self.heartbeat_interval)
                except Exception as e:
                    print(f"心跳发送失败: {e}")
                    break
                    
        self.heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
    
    def stop_heartbeat(self):
        """停止心跳"""
        if hasattr(self, 'heartbeat_thread'):
            self.heartbeat_thread = None
    
    def _print_task(self, task):
        """打印任务信息"""
        print(f"ID: {task.get('id')}")
        print(f"标题: {task.get('title')}")
        print(f"描述: {task.get('description', '无')}")
        print(f"优先级: {task.get('priority')}")
        print(f"截止时间: {task.get('due_date')}")
        print(f"创建时间: {task.get('created_at')}")
        print(f"教师: {task.get('teacher_name', '未知')}")
        
    def _print_assignment(self, assignment):
        """打印作业信息"""
        print(f"ID: {assignment.get('id')}")
        print(f"标题: {assignment.get('title')}")
        print(f"描述: {assignment.get('description', '无')}")
        print(f"学科: {assignment.get('subject')}")
        print(f"截止时间: {assignment.get('due_date')}")
        created_at = assignment.get('created_at') or assignment.get('updated_at')
        print(f"时间: {created_at}")
        print(f"教师: {assignment.get('teacher_name', '未知')}")
        
    def _print_announcement(self, announcement):
        """打印公告信息"""
        print(f"ID: {announcement.get('id')}")
        print(f"标题: {announcement.get('title')}")
        print(f"内容: {announcement.get('content')}")
        print(f"长期公告: {'是' if announcement.get('is_long_term') else '否'}")
        print(f"创建时间: {announcement.get('created_at')}")
        print(f"教师: {announcement.get('teacher_name', '未知')}")
    
    def _get_api_headers(self):
        """获取API认证头"""
        return {
            'X-Board-ID': self.board_id,
            'X-Secret-Key': self.secret_key
        }
    
    def _make_api_request(self, endpoint, params=None):
        """发送API请求"""
        try:
            url = f"{self.server_url}/api/whiteboard/{endpoint}"
            response = requests.get(url, params=params, headers=self._get_api_headers())
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text}")
                return None
                
        except Exception as e:
            print(f"API请求失败: {e}")
            return None
    
    def _make_api_post(self, endpoint):
        """发送POST API请求"""
        try:
            url = f"{self.server_url}/api/whiteboard/{endpoint}"
            response = requests.post(url, headers=self._get_api_headers())
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text}")
                return None
                
        except Exception as e:
            print(f"API请求失败: {e}")
            return None
    
    def get_assignments(self, date=None, subject=None):
        """获取作业列表"""
        params = {}
        if date:
            params['date'] = date
        if subject:
            params['subject'] = subject
            
        result = self._make_api_request('assignments', params)
        if result and result.get('success'):
            assignments = result.get('data', [])
            print(f"\n📚 作业列表 (共{len(assignments)}个):")
            for assignment in assignments:
                print("-" * 30)
                self._print_assignment(assignment)
        else:
            error_msg = result.get('error', '未知错误') if result else '请求失败'
            print(f"获取作业列表失败: {error_msg}")
    
    def get_tasks(self, date=None, priority=None, status=None):
        """获取任务列表"""
        params = {}
        if date:
            params['date'] = date
        if priority:
            params['priority'] = priority
        if status:
            params['status'] = status
            
        result = self._make_api_request('tasks', params)
        if result and result.get('success'):
            tasks = result.get('data', [])
            print(f"\n📋 任务列表 (共{len(tasks)}个):")
            for task in tasks:
                print("-" * 30)
                self._print_task(task)
        else:
            error_msg = result.get('error', '未知错误') if result else '请求失败'
            print(f"获取任务列表失败: {error_msg}")
    
    def get_announcements(self, date=None, long_term=None):
        """获取公告列表"""
        params = {}
        if date:
            params['date'] = date
        if long_term is not None:
            params['long_term'] = str(long_term).lower()
            
        result = self._make_api_request('announcements', params)
        if result and result.get('success'):
            announcements = result.get('data', [])
            print(f"\n📢 公告列表 (共{len(announcements)}个):")
            for announcement in announcements:
                print("-" * 30)
                self._print_announcement(announcement)
        else:
            error_msg = result.get('error', '未知错误') if result else '请求失败'
            print(f"获取公告列表失败: {error_msg}")
    
    def get_all(self, date=None):
        """获取所有内容"""
        params = {}
        if date:
            params['date'] = date
            
        result = self._make_api_request('all', params)
        if result and result.get('success'):
            items = result.get('data', [])
            print(f"\n📊 所有内容 (共{len(items)}个):")
            
            for item in items:
                item_type = item.get('type')
                print("-" * 40)
                if item_type == 'task':
                    print("📋 任务:")
                    self._print_task(item)
                elif item_type == 'assignment':
                    print("📚 作业:")
                    self._print_assignment(item)
                elif item_type == 'announcement':
                    print("📢 公告:")
                    self._print_announcement(item)
        else:
            error_msg = result.get('error', '未知错误') if result else '请求失败'
            print(f"获取所有内容失败: {error_msg}")
    
    def acknowledge_task(self, task_id):
        """确认任务"""
        result = self._make_api_post(f'tasks/{task_id}/acknowledge')
        if result and result.get('success'):
            print(f"✓ 任务 {task_id} 确认成功")
            # 同时发送Socket事件
            if hasattr(self.sio, 'connected') and self.sio.connected:
                self.sio.emit('task_acknowledged', {'task_id': task_id})
        else:
            error_msg = result.get('error', '未知错误') if result else '请求失败'
            print(f"确认任务失败: {error_msg}")
    
    def complete_task(self, task_id):
        """完成任务"""
        result = self._make_api_post(f'tasks/{task_id}/complete')
        if result and result.get('success'):
            print(f"✓ 任务 {task_id} 完成成功")
            # 同时发送Socket事件
            if hasattr(self.sio, 'connected') and self.sio.connected:
                self.sio.emit('task_completed', {'task_id': task_id})
        else:
            error_msg = result.get('error', '未知错误') if result else '请求失败'
            print(f"完成任务失败: {error_msg}")
    
    def send_heartbeat(self):
        """手动发送心跳"""
        if hasattr(self.sio, 'connected') and self.sio.connected:
            self.sio.emit('heartbeat', {'board_id': self.board_id})
            print("❤️  心跳已发送")
        else:
            print("未连接到服务器")
    
    def show_status(self):
        """显示连接状态"""
        status = "已连接" if self.is_connected else "未连接"
        print(f"连接状态: {status}")
        print(f"白板ID: {self.board_id}")
        print(f"服务器: {self.server_url}")
    
    def disconnect(self):
        """断开连接"""
        if self.sio:
            self.sio.disconnect()
            self.is_connected = False
            print("已断开连接")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
可用命令:
  status           - 显示连接状态
  assignments      - 获取作业列表
  tasks            - 获取任务列表
  announcements    - 获取公告列表
  all              - 获取所有内容
  ack <task_id>    - 确认任务
  complete <task_id> - 完成任务
  heartbeat        - 发送心跳
  help             - 显示此帮助
  exit             - 退出程序

示例:
  assignments 2024-01-15
  tasks pending
  ack 123
  complete 123

参数说明:
  date: YYYY-MM-DD 格式的日期
  priority: 1-5 的数字
  status: pending(待处理) 或 completed(已完成)
  long_term: true(长期) 或 false(短期)
        """
        print(help_text)


def main():
    parser = argparse.ArgumentParser(description='白板命令行客户端')
    parser.add_argument('--board-id', required=True, help='白板ID')
    parser.add_argument('--secret-key', required=True, help='白板密钥')
    parser.add_argument('--server', default='https://dlass.tech', help='服务器地址')
    
    args = parser.parse_args()
    
    # 创建客户端实例
    client = WhiteboardClient(args.server, args.board_id, args.secret_key)
    
    # 连接服务器
    client.connect()
    
    # 命令行交互循环
    try:
        while True:
            try:
                command = input("\n白板> ").strip().split()
                if not command:
                    continue
                    
                cmd = command[0].lower()
                
                if cmd == 'exit' or cmd == 'quit':
                    break
                elif cmd == 'status':
                    client.show_status()
                elif cmd == 'assignments':
                    date = command[1] if len(command) > 1 else None
                    subject = command[2] if len(command) > 2 else None
                    client.get_assignments(date, subject)
                elif cmd == 'tasks':
                    date = command[1] if len(command) > 1 else None
                    priority = command[2] if len(command) > 2 else None
                    status = command[3] if len(command) > 3 else None
                    client.get_tasks(date, priority, status)
                elif cmd == 'announcements':
                    date = command[1] if len(command) > 1 else None
                    long_term = command[2] if len(command) > 2 else None
                    client.get_announcements(date, long_term)
                elif cmd == 'all':
                    date = command[1] if len(command) > 1 else None
                    client.get_all(date)
                elif cmd == 'ack':
                    if len(command) > 1:
                        client.acknowledge_task(command[1])
                    else:
                        print("请提供任务ID: ack <task_id>")
                elif cmd == 'complete':
                    if len(command) > 1:
                        client.complete_task(command[1])
                    else:
                        print("请提供任务ID: complete <task_id>")
                elif cmd == 'heartbeat':
                    client.send_heartbeat()
                elif cmd == 'help':
                    client.show_help()
                else:
                    print("未知命令。输入 'help' 查看可用命令")
                    
            except KeyboardInterrupt:
                print("\n正在退出...")
                break
            except Exception as e:
                print(f"命令执行错误: {e}")
                
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
```

## 5. 安装和运行

### 5.1 安装依赖
```bash
pip install socketio requests
```

### 5.2 运行客户端
```bash
python whiteboard_client.py --board-id YOUR_BOARD_ID --secret-key YOUR_SECRET_KEY
```

### 5.3 测试命令
```bash
# 获取所有内容
all

# 获取今天的作业
assignments $(date +%Y-%m-%d)

# 获取待处理的任务
tasks pending

# 确认任务ID为1的任务
ack 1
```
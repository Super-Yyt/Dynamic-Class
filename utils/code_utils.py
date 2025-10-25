import random
import string

def generate_class_code():
    """生成班级代码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_whiteboard_credentials():
    """生成白板ID和密钥"""
    board_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return board_id, secret_key
from datetime import datetime
import pytz

# 时区配置
china_tz = pytz.timezone('Asia/Shanghai')  # UTC+8

def get_china_time():
    """获取当前北京时间（无时区信息）"""
    return datetime.now(china_tz).replace(tzinfo=None)

def format_china_time(dt):
    """格式化时间为北京时间字符串"""
    if dt is None:
        return None
    try:
        # 如果时间没有时区信息，假设它是北京时间
        if dt.tzinfo is None:
            # 直接格式化，不进行时区转换
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            # 如果有时区信息，转换为北京时间
            china_dt = dt.astimezone(china_tz)
            return china_dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None

def parse_china_time(time_str):
    """解析时间字符串为北京时间"""
    if not time_str:
        return None
    try:
        # 尝试解析ISO格式
        if 'T' in time_str:
            if time_str.endswith('Z'):
                dt = datetime.fromisoformat(time_str[:-1] + '+00:00')
            else:
                dt = datetime.fromisoformat(time_str)
        else:
            # 解析普通日期时间格式
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']:
                try:
                    dt = datetime.strptime(time_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"无法解析时间格式: {time_str}")
        
        # 假设输入时间是北京时间，直接返回
        return dt
    except Exception as e:
        raise ValueError(f"时间格式无效: {time_str}")
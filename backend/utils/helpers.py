import random
import string
from datetime import datetime

def generate_user_id() -> str:
    """生成10位用户ID"""
    timestamp = str(int(datetime.now().timestamp()))[-6:]  # 取时间戳后6位
    random_chars = ''.join(random.choices(string.digits, k=4))  # 4位随机数字
    return timestamp + random_chars

def generate_product_id() -> str:
    """生成12位商品ID"""
    timestamp = str(int(datetime.now().timestamp()))[-7:]  # 取时间戳合7位
    random_chars = ''.join(random.choices(string.digits, k=4))  # 4位随机数字
    return 'P' + timestamp + random_chars  # P + 7 + 4 = 12

def generate_transaction_id() -> str:
    """生成15位交易ID"""
    timestamp = str(int(datetime.now().timestamp()))[-10:]  # 取时间戳后10位
    random_chars = ''.join(random.choices(string.digits, k=4))  # 4位随机数字
    return 'T' + timestamp + random_chars

def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    return len(phone) == 11 and phone.startswith('1') and phone.isdigit()

def validate_campus_card(campus_card: str) -> bool:
    """验证校园卡号格式"""
    return len(campus_card) <= 20 and len(campus_card) > 0 and campus_card.replace(' ', '').isalnum()
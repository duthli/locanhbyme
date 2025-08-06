import os

def create_directory(path):
    """Tạo thư mục nếu chưa tồn tại"""
    if not os.path.exists(path):
        os.makedirs(path)

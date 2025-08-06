import os
import shutil
import easyocr
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
import re

# Tạo đối tượng EasyOCR
reader = easyocr.Reader(['en'])

def preprocess_image(image_path):
    """Tiền xử lý ảnh để dễ dàng nhận diện mã"""
    try:
        img = Image.open(image_path)
        img = img.convert('L')  # Chuyển ảnh thành đen trắng

        # Thêm bước Thresholding (ngưỡng phân đoạn) để làm cho các chữ nổi bật hơn
        img = ImageOps.invert(img)  # Đảo ngược ảnh để làm nền trắng và chữ đen
        img = img.point(lambda p: p > 180 and 255)  # Tạo ngưỡng trắng đen để làm nổi bật chữ

        # Tăng cường độ tương phản mạnh mẽ hơn
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(5)  # Điều chỉnh độ tương phản mạnh mẽ

        # Làm sắc nét ảnh để dễ dàng nhận diện ký tự
        img = img.filter(ImageFilter.SHARPEN)
        
        return img
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

def recognize_code_with_easyocr(image_path):
    """Nhận diện mã số từ ảnh sử dụng EasyOCR"""
    try:
        # Tiền xử lý ảnh trước khi nhận diện
        img = preprocess_image(image_path)
        if img is None:
            return ""

        # Lưu ảnh đã xử lý vào file tạm thời
        preprocessed_image_path = 'temp_processed_image.jpg'
        img.save(preprocessed_image_path)

        # Dùng EasyOCR để nhận diện (truyền đường dẫn file ảnh đã xử lý)
        result = reader.readtext(preprocessed_image_path)
        recognized_text = [text[1] for text in result]

        # In ra kết quả nhận diện để kiểm tra
        print(f"Recognized text for {image_path}: {recognized_text}")

        # Xóa ảnh tạm sau khi xử lý
        os.remove(preprocessed_image_path)

        # Sử dụng regex để chỉ lấy mã tên file (có thể là bất kỳ mã nào như HUN_1234)
        code = ' '.join(recognized_text)
        match = re.search(r'(HUN_\d+)', code)  # Tìm mã có định dạng HUN_XXXX
        if match:
            return match.group(0)  # Trả về mã tìm được (chỉ lấy phần tên file, ví dụ: HUN_1234)
        else:
            return ""  # Trả về rỗng nếu không tìm thấy

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return ""

def filter_and_copy_images(image_folder, target_code, raw_folder, save_folder):
    """Lọc ảnh raw theo mã số và sao chép vào thư mục mới"""
    matched_images = []
    unmatched_images = []

    # Lọc theo tất cả ảnh có mã trùng
    for filename in os.listdir(image_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, filename)
            code = recognize_code_with_easyocr(image_path)
            print(f"File: {filename}, Code: {code}")  # In ra mã nhận diện từ ảnh

            # Nếu mã số trùng khớp
            if target_code in code:  # Kiểm tra xem mã nhận diện có chứa mã tìm kiếm không
                # Tạo tên file trùng với mã nhận diện (loại bỏ đuôi mở rộng như .CR3, .CR2, ...)
                base_name = os.path.splitext(code)[0]  # Lấy phần tên file mà không có đuôi mở rộng
                raw_image_path = os.path.join(raw_folder, base_name + ".CR3")  # Tìm file trong raw folder

                # Kiểm tra xem file raw có tồn tại không và sao chép vào thư mục đích
                if os.path.exists(raw_image_path):
                    shutil.copy(raw_image_path, save_folder)  # Sao chép ảnh vào thư mục lưu trữ
                    matched_images.append(filename)
            else:
                unmatched_images.append(filename)

    return matched_images, unmatched_images

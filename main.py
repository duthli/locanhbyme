import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from image_recognition import filter_and_copy_images
from utils import create_directory
import os
import easyocr
from PIL import Image, ImageEnhance, ImageFilter

class ImageFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Filter App")
        self.root.geometry("600x500")
        
        self.image_folder = ""
        self.raw_folder = ""
        self.save_folder = ""
        self.target_code = ""  # Mã mà người dùng nhập vào

        # Label and buttons
        self.lbl_image_folder = tk.Label(self.root, text="Select Folder with Images")
        self.lbl_image_folder.pack(pady=10)
        
        self.btn_select_image_folder = tk.Button(self.root, text="Browse...", command=self.select_image_folder)
        self.btn_select_image_folder.pack(pady=5)
        
        self.lbl_selected_image_folder = tk.Label(self.root, text="")
        self.lbl_selected_image_folder.pack(pady=5)
        
        self.lbl_raw_folder = tk.Label(self.root, text="Select Folder with RAW Images")
        self.lbl_raw_folder.pack(pady=10)
        
        self.btn_select_raw_folder = tk.Button(self.root, text="Browse...", command=self.select_raw_folder)
        self.btn_select_raw_folder.pack(pady=5)
        
        self.lbl_selected_raw_folder = tk.Label(self.root, text="")
        self.lbl_selected_raw_folder.pack(pady=5)
        
        self.lbl_image_count = tk.Label(self.root, text="Images in Selected Folder: 0")
        self.lbl_image_count.pack(pady=5)

        # Ô nhập mã
        self.lbl_target_code = tk.Label(self.root, text="Enter Target Code (e.g., HUN_)")
        self.lbl_target_code.pack(pady=10)

        self.entry_target_code = tk.Entry(self.root)
        self.entry_target_code.pack(pady=5)

        # Progressbar to show processing status
        self.progress = Progressbar(self.root, length=300, mode='indeterminate')
        self.progress.pack(pady=10)

        self.btn_process = tk.Button(self.root, text="Start Processing", command=self.process_images)
        self.btn_process.pack(pady=20)
    
    def select_image_folder(self):
        """Chọn thư mục chứa ảnh cần lọc"""
        self.image_folder = filedialog.askdirectory(title="Select Image Folder")
        self.lbl_selected_image_folder.config(text=f"Selected Image Folder: {self.image_folder}")
        image_count = len([f for f in os.listdir(self.image_folder) if os.path.isfile(os.path.join(self.image_folder, f))])
        self.lbl_image_count.config(text=f"Images in Selected Folder: {image_count}")
        
        # Tạo thư mục con bên trong thư mục gốc để lưu ảnh đã lọc
        self.save_folder = os.path.join(self.image_folder, 'filtered_images')
        create_directory(self.save_folder)

    def select_raw_folder(self):
        """Chọn thư mục chứa ảnh raw"""
        self.raw_folder = filedialog.askdirectory(title="Select RAW Image Folder")
        self.lbl_selected_raw_folder.config(text=f"Selected RAW Folder: {self.raw_folder}")
    
    def process_images(self):
        """Xử lý ảnh, nhận diện mã số và sao chép ảnh raw vào thư mục mới"""
        if not self.image_folder or not self.raw_folder or not self.save_folder:
            messagebox.showerror("Error", "Please fill in all fields!")
            return

        # Lấy mã target_code từ ô nhập
        self.target_code = self.entry_target_code.get().strip()
        
        if not self.target_code:
            messagebox.showerror("Error", "Please enter a valid target code!")
            return
        
        # Hiển thị thanh trạng thái
        self.progress.start()

        # Dùng EasyOCR để nhận diện mã số từ ảnh
        reader = easyocr.Reader(['en'])
        
        try:
            # Xử lý các ảnh trong thư mục
            matched_images, unmatched_images = filter_and_copy_images(self.image_folder, self.target_code, self.raw_folder, self.save_folder)
            
            self.progress.stop()  # Dừng thanh trạng thái khi hoàn thành

            if matched_images:
                messagebox.showinfo("Success", f"Found {len(matched_images)} images and moved them to the save folder.")
                print("Matched images:", matched_images)
            else:
                messagebox.showinfo("No Matches", "No images found with the target code.")

            if unmatched_images:
                print("Unmatched images:", unmatched_images)

        except Exception as e:
            self.progress.stop()  # Dừng thanh trạng thái khi có lỗi
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def recognize_code_with_easyocr(self, image_path, reader):
        """Nhận diện mã số từ ảnh sử dụng EasyOCR"""
        # Tiền xử lý ảnh trước khi nhận diện
        img = Image.open(image_path)
        img = img.convert('L')
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)
        img = img.filter(ImageFilter.SHARPEN)
        
        # Dùng EasyOCR để nhận diện
        result = reader.readtext(img)
        recognized_text = [text[1] for text in result]
        
        # Trả về mã số nhận diện (nếu có)
        return ' '.join(recognized_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageFilterApp(root)
    root.mainloop()

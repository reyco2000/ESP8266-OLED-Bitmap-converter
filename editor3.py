########################################################################
# BITMAP CONVERVER FOR EMBEEDED
# Useful to create C bitmap array for SD1306
# Allows to manipulate the images and once ready to create the c Array
# Created by Reinaldo Torres reyco2000@gmail.com
# V0.3 July 2024
#
#   ____                     ____   ___   ___   ___  
#  |  _ \ ___ _   _  ___ ___|___ \ / _ \ / _ \ / _ \ 
#  | |_) / _ \ | | |/ __/ _ \ __) | | | | | | | | | |
#  |  _ <  __/ |_| | (_| (_) / __/| |_| | |_| | |_| |
#  |_| \_\___|\__, |\___\___/_____|\___/ \___/ \___/ 
#              |___/                                  
##########################################################################

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
from typing import Optional

class ImageEditor:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Image Editor")

        self.image: Optional[Image.Image] = None
        self.img_path: Optional[str] = None
        self.tk_image: Optional[ImageTk.PhotoImage] = None

        self.canvas = tk.Canvas(root, width=500, height=500)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)

        buttons = [
            ("Open Image", self.open_image),
            ("Black & White", self.to_black_and_white),
            ("Center Image", self.center_image),
            ("Resize to 128x64", self.resize_image),
            ("Invert Colors", self.invert_image),
            ("Transparent to White", self.transparent_to_white),
            ("Auto Crop", self.auto_crop),
            ("Save Image", self.save_image)
        ]

        for text, command in buttons:
            tk.Button(button_frame, text=text, command=command).pack(fill=tk.X)

        self.keep_aspect = tk.IntVar()
        tk.Checkbutton(button_frame, text="Keep Aspect Ratio", variable=self.keep_aspect).pack(fill=tk.X)

    def open_image(self):
        try:
            self.img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.bmp;*.png;*.jpg")])
            if self.img_path:
                self.image = Image.open(self.img_path)
                self.display_image(self.image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {str(e)}")

    def display_image(self, img: Image.Image):
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, 
                                 image=self.tk_image, anchor=tk.CENTER)

    def to_black_and_white(self):
        if self.image:
            self.image = self.image.convert("1")
            self.display_image(self.image)

    def center_image(self):
        if self.image and self.tk_image:
            self.display_image(self.image)

    def resize_image(self):
        if self.image:
            size = (128, 64)
            self.image = self.image.copy()
            if self.keep_aspect.get():
                self.image.thumbnail(size)
            else:
                self.image = self.image.resize(size)
            self.display_image(self.image)

    def invert_image(self):
        if self.image:
            self.image = ImageOps.invert(self.image.convert("RGB"))
            self.display_image(self.image)

    def transparent_to_white(self):
        if self.image and self.image.mode in ('RGBA', 'LA'):
            new_image = Image.new("RGBA", self.image.size, "WHITE")
            new_image.paste(self.image, (0, 0), self.image)
            self.image = new_image.convert("RGB")
            self.display_image(self.image)

    def auto_crop(self):
        if self.image:
            bbox = self.image.getbbox()
            if bbox:
                self.image = self.image.crop(bbox)
                self.display_image(self.image)

    def save_image(self):
        if self.image:
            filetypes = [
                ("Black & White BMP", "*.bmp"),
                ("PNG", "*.png"),
                ("XBM C Header", "*.xbm")
            ]
            save_path = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=filetypes)
            if save_path:
                try:
                    if save_path.endswith('.bmp'):
                        self.image.convert("1").save(save_path)
                    elif save_path.endswith('.png'):
                        self.image.save(save_path)
                    elif save_path.endswith('.xbm'):
                        self.image.convert("1").save(save_path)
                        self.convert_to_xbm(save_path)
                    messagebox.showinfo("Save Image", f"Image saved successfully: {save_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image: {str(e)}")

    def convert_to_xbm(self, filepath: str):
        try:
            with open(filepath, 'r') as file:
                data = file.readlines()

            filename = filepath.split('/')[-1].split('.')[0]
            width, height = self.image.size
            header_comment = f"// Bitmap image data ({width}x{height} pixels)\n"
            header = f"const unsigned char {filename} [] PROGMEM = {{\n"
            data = ''.join(data[3:-1]).replace('0x', '').replace(',', '').replace('\n', '').strip()
            
            octets = [f"0x{data[i:i+2].zfill(2)}" for i in range(0, len(data), 2)]
            lines = [', '.join(octets[i:i+16]) for i in range(0, len(octets), 16)]
            content = header_comment + header + ',\n'.join(lines) + '\n};'

            new_filepath = filepath.replace('.xbm', '.h')
            with open(new_filepath, 'w') as file:
                file.write(content)
            messagebox.showinfo("Save Image", f"Image saved as C header file: {new_filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert to XBM: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")

        self.image = None
        self.img_path = None

        self.canvas = tk.Canvas(root, width=500, height=500)
        self.canvas.pack(side=tk.LEFT)

        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.btn_open = tk.Button(button_frame, text="Open Image", command=self.open_image)
        self.btn_open.pack(fill=tk.X)

        self.btn_bw = tk.Button(button_frame, text="Black & White", command=self.to_black_and_white)
        self.btn_bw.pack(fill=tk.X)

        self.btn_center = tk.Button(button_frame, text="Center Image", command=self.center_image)
        self.btn_center.pack(fill=tk.X)

        self.btn_resize = tk.Button(button_frame, text="Resize to 128x64", command=self.resize_image)
        self.btn_resize.pack(fill=tk.X)

        self.keep_aspect = tk.IntVar()
        self.chk_aspect = tk.Checkbutton(button_frame, text="Keep Aspect Ratio", variable=self.keep_aspect)
        self.chk_aspect.pack(fill=tk.X)

        self.btn_invert = tk.Button(button_frame, text="Invert Colors", command=self.invert_image)
        self.btn_invert.pack(fill=tk.X)

        self.btn_transparent_to_white = tk.Button(button_frame, text="Transparent to White", command=self.transparent_to_white)
        self.btn_transparent_to_white.pack(fill=tk.X)

        self.btn_auto_crop = tk.Button(button_frame, text="Auto Crop", command=self.auto_crop)
        self.btn_auto_crop.pack(fill=tk.X)

        self.btn_save = tk.Button(button_frame, text="Save Image", command=self.save_image)
        self.btn_save.pack(fill=tk.X)

    def open_image(self):
        self.img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.bmp;*.png;*.jpg")])
        if self.img_path:
            self.image = Image.open(self.img_path)
            self.display_image(self.image)

    def display_image(self, img):
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(250, 250, image=self.tk_image, anchor=tk.CENTER)

    def to_black_and_white(self):
        if self.image:
            self.image = self.image.convert("1")
            self.display_image(self.image)

    def center_image(self):
        if self.image:
            width, height = self.image.size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            new_x = (canvas_width - width) // 2
            new_y = (canvas_height - height) // 2
            self.canvas.create_image(new_x, new_y, image=self.tk_image, anchor=tk.NW)

    def resize_image(self):
        if self.image:
            if self.keep_aspect.get():
                self.image.thumbnail((128, 64))
            else:
                self.image = self.image.resize((128, 64))
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
                if save_path.endswith('.bmp'):
                    self.image.convert("1").save(save_path)
                elif save_path.endswith('.png'):
                    self.image.save(save_path)
                elif save_path.endswith('.xbm'):
                    self.image.convert("1").save(save_path)
                    self.convert_to_xbm(save_path)

    def convert_to_xbm(self, filepath):
        with open(filepath, 'r') as file:
            data = file.readlines()

        filename = filepath.split('/')[-1].split('.')[0]
        width, height = self.image.size
        header_comment = f"// Bitmap image data ({width}x{height} pixels)\n"
        header = f"const unsigned char {filename} [] PROGMEM = {{\n"
        data = data[3:-1]  # Skip the first three lines and the last line
        data = ''.join(data).replace('0x', '').replace(',', '').replace('\n', '').strip()
        
        octets = [f"0x{data[i:i+2].zfill(2)}" for i in range(0, len(data), 2)]
        lines = [', '.join(octets[i:i+16]) for i in range(0, len(octets), 16)]
        content = header_comment + header + ',\n'.join(lines) + '\n};'

        new_filepath = filepath.replace('.xbm', '.h')
        with open(new_filepath, 'w') as file:
            file.write(content)
        messagebox.showinfo("Save Image", f"Image saved as C header file: {new_filepath}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()


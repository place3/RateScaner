import customtkinter as ctk
from tkinter import filedialog
import CORE.APP_WORKERS.uploader as core

class UploadWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.title("Upload")

        self.geometry("600x400")
        self.resizable(False, False)
        self._build_ui()


        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        self.upload_frame = ctk.CTkFrame(self, 400, 300)
        self.upload_frame.pack(expand = True, fill = "both")

        self._build_info()
        self._buid_files_box()
        self._buid_buttons()

    def _build_info(self):
        self.info_widget = ctk.CTkLabel(self.upload_frame,
                                        text="Upload File",
                                        font=("Segoe UI", 14)).pack(anchor="w", pady=(0, 10))


    def _buid_files_box(self):
        self.files_box = ctk.CTkTextbox(self.upload_frame,
                                        state = 'disabled',
                                        height = 180)
        self.files_box.pack(side = 'left', expand = True, fill = 'both')

    def _buid_buttons(self):
        self.buttons_frame = ctk.CTkFrame(self.upload_frame,width=500, height=400)
        self.buttons_frame.pack()

        self.select_button = ctk.CTkButton(self.buttons_frame,
                                           text = "Select File",
                                           command = self.select_files)
        self.select_button.pack(side="top", expand = True, fill = 'both',  pady = 5)

        self.upload_button = ctk.CTkButton(self.buttons_frame,
                                           text = "Upload File",
                                           command = self.upload_files,
                                           state = "disabled"
                                           )
        self.upload_button.pack(side = 'bottom',expand = True, fill = 'both', pady = 5)

    def upload_files(self):
        if not self.selected_files:
            return
        core.upload(self.selected_files)
        self._clear()


    def select_files(self):
        files = filedialog.askopenfilenames(
            title = "Upload Files",
            filetypes = [("Image", "*.jpg *.jpeg *.png *.bmp")],
        )
        if not files:
            return

        self._set_selected_file(files)

    #--------------
    def _set_selected_file(self, files):
        self.selected_files = list(files)

        self.files_box.configure(state = 'normal')
        self.files_box.delete("1.0", "end")

        for file in files:
            self.files_box.insert("end", file+"\n")

        self.files_box.configure(state = 'disabled')
        self.upload_button.configure(state = 'normal')

    def _clear(self):
        self.selected_files.clear()
        self.files_box.configure(state = 'normal')
        self.files_box.delete("1.0", "end")
        self.files_box.configure(state = 'disabled')
        self.upload_button.configure(state = 'disabled')

    def on_close(self):
        self.master.upload_dialog = None
        self.destroy()
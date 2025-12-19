import tkinter as tk
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

from GUI.pages.HomePage import HomeFrame
from GUI.pages.ManagePage import ManageFrame
from GUI.pages.UploadPage import UploadFrame
from GUI.pages.ProcessPage import ProcessFrame


#обновление фреймов и отображение их на одной странице
class App(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.geometry("900x600")
        self.title("SCANER APP")

        self.project_files = []
        self.output_data = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for page in (HomeFrame, UploadFrame, ProcessFrame,ManageFrame):
            page_name = page.__name__
            self.frames[page_name] = page(self)
            self.frames[page_name].grid(row=0, column=0, sticky="nsew")

        self.show_page("Home")

    def show_page(self, page_name:str):
        self.mapping = {
            "Home": "HomeFrame",
            "Upload": "UploadFrame",
            "Process": "ProcessFrame",
            "Manage": "ManageFrame",
        }
        frame = self.frames.get(self.mapping[page_name])
        frame.tkraise()

        if hasattr(frame, "on_show"):
            frame.on_show(page_name)

if __name__ == "__main__":
    app = App()
    app.focus_force()
    app.mainloop()

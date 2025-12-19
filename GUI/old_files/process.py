import customtkinter as ctk

class ProcessWindow(ctk.CTkToplevel):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.title("Process")
        self.geometry("400x500")


    def _build_ui(self):
        pass

    def create_progressBar(self):
        self.progressBar = ctk.CTkProgressBar()
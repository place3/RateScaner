import customtkinter as ctk
from GUI.old_files.manage import ManageWindow
from GUI.old_files.process import ProcessWindow
from GUI.old_files.upload import UploadWindow

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Scanner App")
        self.geometry("800x600")
        self.configure(fg_color='#1B4752')

        self.upload_dialog = None
        self.manage_dialog = None
        self.process_dialog = None

        self._build_ui()

    def _build_ui(self):
        self.but_frame = ctk.CTkFrame(self)
        self.but_frame.pack(expand=True, fill="both", padx=(250, 250), pady=(40,40))

        ctk.CTkLabel(self.but_frame, text="SCAN DOCS",
                     font=("Segoe UI", 22, "bold")).pack(pady=(20,20))

        self.upload_but = ctk.CTkButton(self.but_frame,
                                        height=45, width=400,
                                        text="загрузить изображения", font = ("Arial", 20, ),
                                        command=self.open_upload)
        self.upload_but.pack(fill="x",padx= (10, 10), pady=10)

        self.manage_but = ctk.CTkButton(self.but_frame,
                                        height=45, width=400,
                                        text="Управлять данными", font = ("Arial", 20, ),
                                        command=self.open_manage)
        self.manage_but.pack(fill="x", padx= (10, 10), pady=10)

        self.process_but = ctk.CTkButton(self.but_frame,
                                        height=45, width=400,
                                        text="Перейти к сканированию", font=("Arial", 20,),
                                        command=self.open_process)
        self.process_but.pack(fill="x", padx=(10, 10), pady=10)



    def open_upload(self):
        if self.upload_dialog is None or not self.upload_dialog.winfo_exists():
            self.upload_dialog = UploadWindow(self)
        else:
            self.upload_dialog.focus()

    def open_manage(self):
        if self.manage_dialog is None:
            self.manage_dialog = ManageWindow(self)
        else:
            self.manage_dialog.focus()

    def open_process(self):
        if self.process_dialog is None:
            self.process_dialog = ProcessWindow(self)
        else:
            self.process_dialog.focus()




app = MainWindow()
app.mainloop()


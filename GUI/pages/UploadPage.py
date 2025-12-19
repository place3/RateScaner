from tkinter import filedialog
import os
import customtkinter as ctk
from tkinterdnd2 import DND_FILES
from GUI.Utiles import parse_dropped_files

class UploadFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.selected_files = []

        self.grid_columnconfigure((0, 2), weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(1, weight=4)

        #----Header--------------'
        back_but = ctk.CTkButton(self, text=" <- Back",
                                 command=lambda: master.show_page("Home")
                                 , width=20)
        back_but.grid(row=0, column=0)

        lable = ctk.CTkLabel(master=self,text="Upload your file",
                             font = ("Arial", 20, "bold"), padx = 20)
        lable.grid(row=0, column=1, sticky="ew")

        # ---DND----
        self.dnd_area = ctk.CTkLabel(master=self,text="Upload your file here",
                                height = 300, width = 300, font = ("Arial", 20, "bold"),
                                padx = 20, fg_color="grey",
                                corner_radius=15)
        self.dnd_area.grid(row=1,column =1)

        self.dnd_area.drop_target_register(DND_FILES)
        self.dnd_area.dnd_bind("<<Drop>>", self.on_drop)

        #---КНОПКИ УПРАВЛЕНИЯ-----
        self.button_frame = ctk.CTkFrame(self, bg_color="grey")
        self.button_frame.grid(row=2, column=1, sticky="ew",pady=(10,50))
        self.browse_but = ctk.CTkButton(master=self.button_frame, text="Browse",
                                        command=self.browse_files,)
        self.browse_but.grid(row=0, column=1, sticky="ew")

        self.upload_status = ctk.CTkLabel(master=self.button_frame,text="there are not many files",
                                          font = ("Arial", 20, "bold"),
                                          fg_color="black",
                                          text_color = 'red')
        self.upload_status.grid(row=0, column=2, sticky="ew")



        self.save_but = ctk.CTkButton(self.button_frame, text="Save files",
                                      state="disabled", command=self.save_files_to_sys)
        self.save_but.grid(row=2, column=0,columnspan=2, sticky="ew")


    def save_files(self):
        pass

    def on_drop(self, event):
        files = parse_dropped_files(event.data)
        self.add_files(files)

    def browse_files(self):
        files = filedialog.askopenfilenames()
        if files:
            self.add_files(list(files))

    def add_files(self, files):
        for f in files:
            if f not in self.selected_files:
                self.selected_files.append(f)

        self.upload_status.configure(text=f"Выбранно файлов: {len(self.selected_files)}")
        self.save_but.configure(state = "normal")

        self.drop_zone.configure(fg_color=("gray80", "gray35"), text=f"Последний: {os.path.basename(files[-1])}")

    def save_files_to_sys(self):
        #Тут логика загрузки изображений в папку проекта
        count_files = 0
        for f in self.selected_files:
            if os.path.exists(f):
                count_files += 1



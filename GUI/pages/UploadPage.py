from idlelib.debugger_r import frametable
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

        #self.grid_columnconfigure((0, 2), weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        #----Header--------------'
        self.header = ctk.CTkFrame(self, bg_color="grey")
        self.header.grid(row=0, column=0, sticky="ew", columnspan=3)

        self.header.grid_columnconfigure(1, weight=1)

        back_but = ctk.CTkButton(self.header, text=" <- Back",
                                 command=lambda: master.show_page("Home")
                                 , width=20)
        back_but.grid(row=0, column=0, sticky="ew")

        lable = ctk.CTkLabel(master=self.header, text="Upload your file",
                             font = ("Arial", 20, "bold"), padx = 10)
        lable.grid(row=0, column=1, sticky="ew")

        # ---DND----
        self.dnd_area = ctk.CTkScrollableFrame(master=self,
                                label_text="Upload your file here",
                                label_font = ("Arial", 20, "bold"),
                                fg_color="grey",
                                corner_radius=12, border_width=10,
                                border_color="grey")
        self.dnd_area.grid(row=1,column =0, columnspan=3, sticky="nsew", padx=30)

        self.dnd_area.drop_target_register(DND_FILES)
        self.dnd_area.dnd_bind("<<Drop>>", self.on_drop)

        # Список выбранных файлов (в состоянии пустова списка)
        self.placeholder_label = ctk.CTkLabel(master=self.dnd_area,
                                              text="Upload your file",
                                              font = ("Arial", 20, "bold"),
                                              text_color = 'grey50')
        self.placeholder_label.pack(expand=True, fill="both", pady = 50)

        #---КНОПКИ УПРАВЛЕНИЯ-----
        self.button_frame = ctk.CTkFrame(self, fg_color="grey30")
        self.button_frame.grid(row=2, column=1,columnspan = 3, sticky="ew",pady=(30,50), padx=30)
        self.button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.browse_but = ctk.CTkButton(master=self.button_frame, text="Browse",
                                        command=self.browse_files,)
        self.browse_but.grid(row=0, column=0, sticky="ew", padx = 10)

        self.upload_status = ctk.CTkLabel(master=self.button_frame,text="there are not many files",
                                          font = ("Arial", 20, "bold"),
                                          fg_color="grey30",
                                          text_color = 'black')
        self.upload_status.grid(row=0, column=2, sticky="ew")

        self.save_but = ctk.CTkButton(self.button_frame, text="Save files",
                                      state="disabled", command=self.save_files_to_sys)
        self.save_but.grid(row=0, column=4, sticky="ew", padx = (10, 10))


    #----------Логика

    def on_drop(self, event):
        files = parse_dropped_files(event.data)
        self.add_files(files)

    def browse_files(self):
        files = filedialog.askopenfilenames()
        if files:
            self.add_files(list(files))

    def add_files(self, files):
        if files:
            self.placeholder_label.pack_forget()

        for f in files:
            if f not in self.selected_files:
                self.selected_files.append(f)
                self._create_file_item(f)

        self.upload_status.configure(text=f"Выбранно файлов: {len(self.selected_files)}")
        self.save_but.configure(state="normal")

    def _create_file_item(self, file_path):
        file_name = os.path.basename(file_path)

        file_frame = ctk.CTkFrame(self.dnd_area, bg_color="grey30")
        file_frame.pack(expand=True, fill="both", pady = 10, padx = 10)

        file_name_label = ctk.CTkLabel(master=file_frame,
                                       text=file_name, font = ("Arial", 14, "bold")
                                    )
        file_name_label.pack(side = 'left', padx = 10, pady = 10)

        close_but = ctk.CTkButton(file_frame, fg_color="red",
                                    text_color = "white", text="X",
                                  width=10,height=10,
                                    command=lambda:self._remove_file_item(file_path, file_frame))
        close_but.pack(side = "right", padx=(10, 10))



    def _remove_file_item(self, file_path, file_frame):
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            file_frame.destroy()

            self.upload_status.configure(f'Выбранно файлов: {len(self.selected_files)}')
            if not self.selected_files:
                self.save_but.configure(state="disabled")

                self.upload_status.configure(text="Нету файлов")


    def save_files_to_sys(self):
        #Тут логика загрузки изображений в папку проекта
        count_files = 0
        for f in self.selected_files:
            if os.path.exists(f):
                count_files += 1



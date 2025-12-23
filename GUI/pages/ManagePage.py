import customtkinter as ctk

class ManageFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.grid_rowconfigure(1, weight=2)
        self.grid_columnconfigure(0, weight=1)

        self.check_boxes = {}

        #---------Header------------
        self.header_frame = ctk.CTkFrame(master=self,)
        self.header_frame.grid(row=0, column=0, sticky="nsew")

        self.back_but = ctk.CTkButton(self.header_frame, text="Back", command=lambda:self.master.show_page('Home'))
        self.back_but.grid(row=0, column=0, sticky="nsew", padx=(30, 10))

        self.head_lable = ctk.CTkLabel(self.header_frame, text="Project Files")
        self.head_lable.grid(row=0, column=2, sticky="nsew")

        self.open_folder_button = ctk.CTkButton(self.header_frame, text="Open Folder")
        self.open_folder_button.grid(row=0, column=4, sticky="nsew", padx=(10, 30))

        self.header_frame.grid_columnconfigure(2, weight=1)
        #---------Body--------------
        self.manager_bar = ctk.CTkScrollableFrame(master=self,
                                            fg_color="grey30", corner_radius=10,
                                            border_width=1)
        self.manager_bar.grid(row=1, column=0, sticky="nsew",
                              padx=30, pady=10)

        self.manager_bar.grid_columnconfigure(1, weight=1)

        #--------Buttons-Controll------
        self.footer_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, sticky="nsew",)

        self.delete_all_but = ctk.CTkButton(self.footer_frame, text="delete all")
        self.delete_all_but.grid(row=0, column=0, sticky="nsew", padx=(10, 30))

        self.delete_selected_but = ctk.CTkButton(self.footer_frame, text="delete selected",
                                                 command=self._delete_selected_files)
        self.delete_selected_but.grid(row=0, column=1, sticky="nsew", padx=(30, 10))

        self.dir_info = ctk.CTkLabel(self.footer_frame, text="Файлов нету(( ")
        self.dir_info.grid(row=0, column=2, sticky="nsew")

    #---------Funcs-----------------

    def _on_show(self):
        self._refrash_page()


    def _refresh_page(self):
        for widget in self.manager_bar.winfo_children():
            widget.destroy()
        self.check_boxes.clear()

        files = getattr(self.master, "project_files", [])

        if not files:
            self.dir_info.configure(text="Ничего нету")


    def _delete_all_files(self):
        pass

    def _delete_selected_files(self):
        pass

    def delete_single(self, path):
        if path in self.master.project_files:
            self.master.project_files.remove(path)
            self._refresh_page()
import customtkinter as ctk


class ManageWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x400")
        self.title("Manage")
        self._build_ui()

    def _build_ui(self):
        self.manage_frame = ctk.CTkFrame(self,width=500, height=400)
        self.manage_frame.pack(fill="both", expand=True)

        self._buid_info()
        self._build_file_box()
        self._build_buttons()

    def _build_file_box(self):
        self.file_box = ctk.CTkTextbox(self.manage_frame, height=220)
        self.file_box.pack(fill="both", expand=True)
        #self.files_box.bind("<ButtonRelease-1>", self._on_select)

    def _build_buttons(self):
        self.button_frame = ctk.CTkFrame(self.manage_frame, width=500, height=400)
        self.button_frame.pack(fill="both", expand=True)

        self.delete_selected_button = ctk.CTkButton(master=self.button_frame, text="Clear Selected",
                                            command=self._delete_files())
        self.delete_selected_button.pack(side="left", expand = True)

        self.delete_all_button = ctk.CTkButton(self.button_frame, text="Clear All",
                                               command=self._clear_dir)
        self.delete_all_button.pack(side="side"
                                         , expand=True, fill="x")

        self.open_folder_button = ctk.CTkButton(master=self.button_frame, text="Open Folder",
                                                command=self._open_folder
                                                )
        self.open_folder_button.pack(side="right", expand=True, fill="x")

    ## -------FUNCTION FOR BUTTONS-------------

    def _clear_dir(self):
        if all:
            pass
        pass

    def _delete_files(self):
        pass

    def _open_folder(self):
        pass

    def _buid_info(self):
        pass


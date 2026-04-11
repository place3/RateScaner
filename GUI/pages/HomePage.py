import customtkinter as  ctk

class HomeFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)

        self.logo_placeholder = ctk.CTkLabel(self,
                                             text="Logo",
                                             corner_radius=20,
                                             )
        self.logo_placeholder.pack(pady=10)

        #----buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="grey")
        self.button_frame.pack(pady=10)


        btn_settings = {"width":220, "height":50, "font":("Roboto",16) }
        self.upload_but = ctk.CTkButton(self.button_frame, text="Upload File",
                                        command=lambda:master.show_page("Upload"), **btn_settings)
        self.upload_but.pack(pady=10)

        self.manage_but = ctk.CTkButton(self.button_frame, text="Manage",
                                        command=lambda:master.show_page("Manage"), **btn_settings)
        self.manage_but.pack(pady=10)

        self.process_but = ctk.CTkButton(self.button_frame, text="Upload File",
                                        command=lambda:master.show_page("Process"), **btn_settings)
        self.process_but.pack(pady=10)
import tkinter as tk


class SelectCatagoryPopup(tk.Frame):
    previous_popup = None

    def __init__(self, parent):
        if self.__class__.previous_popup is not None:
            self.__class__.previous_popup.destroy()
        tk.Frame.__init__(self, parent)
        self.__class__.previous_popup = self

        b = tk.Button(self, text="Popip")
        b.pack()

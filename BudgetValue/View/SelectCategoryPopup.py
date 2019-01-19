import TM_CommonPy as TM  # noqa
import tkinter as tk


class SelectCategoryPopup(tk.Frame):
    previous_popup = None

    def __init__(self, parent, vModel, vClosingHandler, *args):
        tk.Frame.__init__(self, parent, borderwidth=2, background="black")
        self.vModel = vModel
        self.vClosingHandler = vClosingHandler
        self.args = args
        # Delete old popup
        if self.__class__.previous_popup is not None:
            self.__class__.previous_popup.destroy()
        self.__class__.previous_popup = self
        # Position myself
        self.place(x=0, y=0)
        self.tkraise()

        for vCategory in vModel.Categories.values():
            b = tk.Button(self, text=vCategory.name,
                          command=lambda vCategory=vCategory: self.SelectCategory(vCategory))
            b.pack(fill=tk.BOTH, expand=True)

    def SelectCategory(self, vCategory):
        self.vClosingHandler(vCategory, *self.args)
        self.destroy()

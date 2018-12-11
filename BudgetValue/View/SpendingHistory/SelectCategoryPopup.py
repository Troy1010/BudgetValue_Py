import TM_CommonPy as TM  # noqa
import tkinter as tk


class SelectCategoryPopup(tk.Frame):
    previous_popup = None

    def __init__(self, cell, vModel):
        tk.Frame.__init__(self, cell.parent, borderwidth=2, background="black")
        self.vModel = vModel
        self.parent = cell.parent
        self.destroy = self.DestoyDecorator(self.destroy, cell)
        # Delete old popup
        if self.__class__.previous_popup is not None:
            self.__class__.previous_popup.destroy()
        self.__class__.previous_popup = self
        # Position myself
        self.place(x=0 + cell.winfo_width(), y=0)
        self.tkraise()
        # Highlight cell
        cell.config(background="grey")

        for vCategory in vModel.Categories:
            b = tk.Button(self, text=vCategory.name,
                          command=lambda vCategory=vCategory, cell=cell, self=self: self.SelectCategory(vCategory, cell))
            b.pack(fill=tk.BOTH, expand=True)

    class DestoyDecorator:
        def __init__(self, method, cell):
            self.cell = cell
            self.method = method

        def __call__(self, *args, **kwargs):
            try:
                self.cell.config(background="SystemButtonFace")
            except tk.TclError:  # cell doesn't exist
                pass
            self.method(*args, **kwargs)

    def SelectCategory(self, vCategory, cell):
        self.parent.Update((cell.grid_info()['row'], "Category"), vCategory.name)
        self.destroy()

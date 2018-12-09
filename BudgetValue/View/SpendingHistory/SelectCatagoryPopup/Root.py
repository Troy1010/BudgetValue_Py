import TM_CommonPy as TM  # noqa
import tkinter as tk


class Root(tk.Frame):
    previous_popup = None

    def __init__(self, parent, cell, vModel):
        tk.Frame.__init__(self, parent, borderwidth=2, background="black")
        # Delete old popup
        if self.__class__.previous_popup is not None:
            self.__class__.previous_popup.destroy()
        self.__class__.previous_popup = self

        for vItem in vModel.Catagories.main_list:
            b = tk.Button(self, text=vItem,
                          command=lambda vItem=vItem, cell=cell, self=self: self.SelectCatagory(vItem, cell))
            b.pack(fill=tk.BOTH, expand=True)

    def SelectCatagory(self, catagory, cell):
        cell.config(state="normal")
        cell.delete("1.0", tk.END)
        cell.insert(1.0, catagory)
        cell.config(state="disabled")
        cell.config(background="SystemButtonFace")
        self.destroy()

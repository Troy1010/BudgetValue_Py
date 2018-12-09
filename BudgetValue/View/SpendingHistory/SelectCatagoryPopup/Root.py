import TM_CommonPy as TM  # noqa
import tkinter as tk


class Root(tk.Frame):
    previous_popup = None

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent, borderwidth=2, background="black")
        # Delete old popup
        if self.__class__.previous_popup is not None:
            self.__class__.previous_popup.destroy()
        self.__class__.previous_popup = self

        for vItem in vModel.Catagories.main_list:
            b = tk.Button(self, text=vItem,
                          command=lambda vItem=vItem, self=self: self.SelectCatagory(vItem))
            b.pack(fill=tk.BOTH, expand=True)

    def SelectCatagory(self, catagory):
        print(TM.FnName() + " " + catagory)

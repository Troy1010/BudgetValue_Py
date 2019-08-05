import TM_CommonPy as TM  # noqa
import tkinter as tk
from tkinter import ttk
from BudgetValue._Logger import Log  # noqa
import BudgetValue as BV  # noqa


class Popup_SelectFromList(tk.Frame):
    previous_popup = None

    def __init__(self, parent, handler, selection_list, cPos=None, vDestroyHandler=None):
        tk.Frame.__init__(self, parent, borderwidth=2, background="black")
        # Hook destroy handlers

        def ForgetPrevPopup():
            self.__class__.previous_popup = None
        self.destroy = TM.Hook(self.destroy, vDestroyHandler, ForgetPrevPopup, bPrintAndQuitOnError=True)
        # Delete old popup
        if self.__class__.previous_popup is not None:
            self.__class__.previous_popup.destroy()
        self.__class__.previous_popup = self
        # Position myself
        if not cPos:
            x, y = parent.winfo_pointerx() - parent.winfo_rootx(), parent.winfo_pointery() - parent.winfo_rooty()
        else:
            x, y = cPos[0], cPos[1]
        self.place(x=x, y=y)
        self.tkraise()
        # Pick category type
        combobox_value = tk.StringVar()
        combo_box = ttk.Combobox(self)
        combo_box.config(textvariable=combobox_value, state="readonly")
        combo_box.config(values=selection_list)
        combo_box.pack()
        # Bind Escape to exit
        self.winfo_toplevel().bind("<Escape>", lambda event: self.destroy(), add='+')
        # Bind Return to accept

        def OnReturn(event):
            value = combobox_value.get() if combobox_value.get() != "" else None
            handler(value)
            self.destroy()
        self.winfo_toplevel().bind("<Return>", OnReturn, add='+')

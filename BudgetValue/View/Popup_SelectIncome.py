import TM_CommonPy as TM  # noqa
import tkinter as tk
from BudgetValue._Logger import Log  # noqa
import rx  # noqa
from . import WidgetFactories as WF  # noqa


class Popup_SelectIncome(tk.Frame):
    previous_popup = None

    def __init__(self, parent, transaction_handler, cPos=None, vDestroyHandler=None):
        tk.Frame.__init__(self, parent, borderwidth=2, background="black")
        # Hook DestroyHandler

        def ForgetPrevPopup():
            self.__class__.previous_popup = None
        self.destroy = TM.Hook(self.destroy, vDestroyHandler, ForgetPrevPopup, bPrintAndQuitOnError=True)
        # Bind Escape to exit
        self.winfo_toplevel().bind("<Escape>", lambda event: self.destroy(), add='+')
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
        # Show Income Transactions
        self.MakeEntry((0, 0), "zood")
        self.transaction = None
        # Bind Return to accept

        def OnReturn(event):
            if isinstance(event.widget, tk.Entry):
                return
            transaction_handler(self.transaction)
            self.destroy()
        self.winfo_toplevel().bind("<Return>", OnReturn, add='+')

    def MakeEntry(self, cRowColumnPair, text, validation=None):
        return WF.MakeEntry(self, cRowColumnPair, text=text, validation=validation, bFocusNothingOnReturn=True)

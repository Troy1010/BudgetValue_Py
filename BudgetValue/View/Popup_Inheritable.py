import TM_CommonPy as TM  # noqa
import tkinter as tk
from BudgetValue._Logger import Log  # noqa
import rx  # noqa
from . import WidgetFactories as WF  # noqa
import BudgetValue as BV  # noqa
from .Misc import DisposableTkBind


class Popup_Inheritable(tk.Frame):
    previous_popup = None

    def __init__(self, parent, handler, cPos=None, vDestroyHandler=None):
        #
        tk.Frame.__init__(self, parent, borderwidth=2, background="black")
        self.disposable_binds = list()
        self.handler = handler
        # Hook DestroyHandler

        def ForgetPrevPopup():
            self.__class__.previous_popup = None

        def DisposeBinds():
            for disposable_bind in self.disposable_binds:
                disposable_bind.Dispose()
        self.destroy = TM.Hook(self.destroy, vDestroyHandler, ForgetPrevPopup, DisposeBinds, bPrintAndQuitOnError=True)
        # Bind Escape to exit
        self.disposable_binds.append(DisposableTkBind(self.winfo_toplevel(), "<Escape>", self.winfo_toplevel().bind("<Escape>", lambda event: self.destroy(), add='+')))
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
        # Bind Return to accept

        def OnReturn(event):
            if isinstance(event.widget, tk.Entry):
                return
            self.handler(self.GetInputValue())
            self.destroy()
        self.disposable_binds.append(DisposableTkBind(self.winfo_toplevel(), "<Return>", self.winfo_toplevel().bind("<Return>", OnReturn, add='+')))

    def GetInputValue(self):
        return None

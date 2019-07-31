import TM_CommonPy as TM  # noqa
import tkinter as tk
from BudgetValue._Logger import Log  # noqa
import rx  # noqa
from . import WidgetFactories as WF  # noqa


class Popup_AddCategory(tk.Frame):
    previous_popup = None

    def __init__(self, parent, handler, cPos=None, vDestroyHandler=None):
        #
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
        # Show Entry box
        WF.MakeEntry_ReadOnly(self, (0, 0), text="Input Category Name:")
        self.text_stream = rx.subjects.BehaviorSubject("")  # FIX: leaking?
        WF.MakeEntry(self, (0, 1), stream=self.text_stream, width=10)
        # Bind Return to accept

        def OnReturn(event):
            if isinstance(event.widget, tk.Entry):
                return
            handler(self.text_stream.value)
            self.destroy()
        self.winfo_toplevel().bind("<Return>", OnReturn, add='+')

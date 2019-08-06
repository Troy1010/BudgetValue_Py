import TM_CommonPy as TM  # noqa
from BudgetValue._Logger import Log  # noqa
import rx  # noqa
from . import WidgetFactories as WF  # noqa
from .Popup_Inheritable import Popup_Inheritable
import tkinter as tk


class Popup_InputText(Popup_Inheritable):
    previous_popup = None

    def __init__(self, parent, handler, cPos=None, vDestroyHandler=None, sPrompt=None):
        super().__init__(parent, handler, cPos=cPos, vDestroyHandler=vDestroyHandler)
        # Show Entry box
        if sPrompt is not None:
            WF.MakeEntry_ReadOnly(self, (0, 0), text=sPrompt)
        self.text_stream = rx.subjects.BehaviorSubject("")  # FIX: leaking?
        WF.MakeEntry(self, (0, 1), stream=self.text_stream, width=10)

    def OnReturn(self, event):
        if isinstance(event.widget, tk.Entry):
            return
        super().OnReturn(event)

    def GetInputValue(self):
        return self.text_stream.value

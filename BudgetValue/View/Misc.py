import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import rx  # noqa
from .Skin import vSkin  # noqa
import BudgetValue as BV
from . import WidgetFactories as WF  # noqa


class ModelTable(TM.tk.TableFrame):
    iFirstDataColumn = 0
    iFirstDataRow = 1

    def __init__(self, parent, vModel):
        super().__init__(parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.parent = parent
        self.cDisposables = []

    def Refresh(self):
        # remove old
        for child in self.winfo_children():
            try:
                if not child.bPerminent:
                    child.grid_forget()
                    child.destroy()
            except AttributeError:
                child.grid_forget()
                child.destroy()
        if hasattr(self, 'cDisposables'):
            for disposable in self.cDisposables:
                disposable.dispose()
        self.cDisposables = []


class DisposableTkBind():
    def __init__(self, widget, key, bind_id):
        self.widget = widget
        self.key = key
        self.bind_id = bind_id

    def Dispose(self):
        self.widget.unbind(self.key, self.bind_id)

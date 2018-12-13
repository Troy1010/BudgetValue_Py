import tkinter as tk
from .TableData import TableData
from .TableHeader import TableHeader
from .TableBalance import TableBalance


class Table(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent
        # Header
        self.vHeader = TableHeader(self)
        self.vHeader.pack(side=tk.TOP, fill='x')
        # TableData Canvas
        self.vCanvas = tk.Canvas(self, highlightthickness=0, background='grey')
        self.vCanvas.pack(side=tk.TOP, fill='x', anchor='nw')
        self.vTableData = TableData(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTableData, anchor='nw')
        self.vTableData.pack(anchor='nw')
        # Balance
        self.vBalance = TableBalance(self, vModel)
        self.vBalance.pack(side=tk.TOP, fill='x')

    def Refresh(self):
        self.vTableData.Refresh()

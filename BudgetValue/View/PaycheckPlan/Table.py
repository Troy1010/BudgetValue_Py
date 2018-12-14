import tkinter as tk
from .TableData import TableData


class Table(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent
        # TableData Canvas
        self.vCanvas = tk.Canvas(self, highlightthickness=0)
        self.vCanvas.pack(side=tk.TOP, fill='x', anchor='nw')
        self.vTableData = TableData(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTableData, anchor='nw')
        self.vTableData.pack(anchor='nw')

    def Refresh(self):
        self.vTableData.Refresh()

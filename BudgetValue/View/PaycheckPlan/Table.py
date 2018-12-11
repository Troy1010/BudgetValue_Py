import tkinter as tk
from .TableData import TableData
from .TableHeader import TableHeader


class Table(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent
        # Header
        self.vHeader = TableHeader(self)
        self.vHeader.pack(side=tk.TOP, fill="x")
        # Canvas
        self.vCanvas = tk.Canvas(self, highlightthickness=0)
        self.vCanvas.pack(side=tk.TOP, expand=True, fill="both")
        #  Assign TableData to Canvas
        self.vTableData = TableData(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTableData, anchor='nw')

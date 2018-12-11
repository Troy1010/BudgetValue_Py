import tkinter as tk
from .TableDataFrame import TableDataFrame


class Table(tk.Canvas):
    def __init__(self, parent, vModel):
        tk.Canvas.__init__(self, parent, highlightthickness=0)
        self.vModel = vModel
        self.parent = parent
        # Assign TableDataFrame to Canvas
        self.vTableDataFrame = TableDataFrame(self, vModel)
        self.create_window((0, 0), window=self.vTableDataFrame, anchor='nw')

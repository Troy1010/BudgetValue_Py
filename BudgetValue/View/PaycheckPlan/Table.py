import tkinter as tk
from .TableWindow import TableWindow


class Table(tk.Canvas):
    def __init__(self, parent, vModel):
        tk.Canvas.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent
        # Assign TableWindow to Canvas
        self.vTableWindow = TableWindow(self, vModel)
        self.create_window((0, 0), window=self.vTableWindow, anchor='nw')

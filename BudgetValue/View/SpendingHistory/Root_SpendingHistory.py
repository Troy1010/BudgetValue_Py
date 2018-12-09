import tkinter as tk
import tkinter.filedialog  # noqa
from tkinter import ttk
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import BudgetValue as BV
import itertools


class Root(tk.Frame):
    name = "Spending History"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        # ButtonBar
        self.vButtonFrame = tk.Frame(self)
        self.vButtonFrame.pack(side=tk.TOP, anchor='w')
        # TableFrame
        self.vTableFrame = tk.Frame(self, background='lightgrey')
        self.vTableFrame.pack(side=tk.TOP, expand=True, fill="both")
        self.vTableFrame.grid_rowconfigure(1, weight=1)
        self.vTableFrame.grid_columnconfigure(0, weight=1)
        self.vTableFrame.parent = self
        #  Header
        self.vHeader = BV.View.SpendingHistory.Header(self.vTableFrame, vModel)
        self.vHeader.grid(row=0, column=0, sticky="NSEW")
        #  Table
        self.vTable = BV.View.SpendingHistory.Table(self.vTableFrame, vModel)
        self.vTable.grid(row=1, column=0, sticky="NSEW")
        #  Scrollbars
        vScrollbar_Y = tk.Scrollbar(self.vTableFrame)
        vScrollbar_Y.grid(row=0, rowspan=2, column=1, sticky="ns")
        self.vTable.config(yscrollcommand=vScrollbar_Y.set)
        vScrollbar_Y.config(command=self.vTable.yview)
        vScrollbar_X = tk.Scrollbar(self.vTableFrame, orient=tk.HORIZONTAL)
        vScrollbar_X.grid(row=2, column=0, sticky="ew")
        self.vTable.config(xscrollcommand=vScrollbar_X.set)
        vScrollbar_X.config(command=self.vTable.xview)
        # ButtonBar - continued
        vButton_ImportHistory = ttk.Button(self.vButtonFrame, text="Import Spending History",
                                           command=lambda self=self: self.ImportHistory())
        vButton_ImportHistory.pack(side=tk.LEFT, anchor='w')
        #
        self.Refresh()

    def Refresh(self):
        self.vTableFrame.cColWidths = self.GetColWidths(self.vModel)
        self.vHeader.Refresh()
        self.vTable.Refresh()

    def ImportHistory(self):
        # Prompt which file
        vFile = tk.filedialog.askopenfile()
        # Import
        if vFile is not None:
            self.vModel.SpendingHistory.Import(vFile.name)
        # Refresh view
        self.vTable.Refresh()

    def GetColWidths(self, vModel):
        cColWidths = {}
        for row in itertools.chain([vModel.SpendingHistory.GetHeader()], vModel.SpendingHistory.GetTable()):
            for j, vItem in enumerate(row):
                cColWidths[j] = max(cColWidths.get(j, 0), len(str(vItem)) + 1)
                if j < len(row) - 1:
                    cColWidths[j] = min(30, cColWidths[j])
        return cColWidths

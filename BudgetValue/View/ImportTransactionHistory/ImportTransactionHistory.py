import tkinter as tk
import tkinter.filedialog  # noqa
from tkinter import ttk
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import itertools
import tkinter.messagebox  # noqa
import rx
from .Table import Table
from .Header import Header


class ImportTransactionHistory(tk.Frame):
    name = "Import Transaction History"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')
        # TableFrame
        self.vTableFrame = tk.Frame(self, background='lightgrey')
        self.vTableFrame.pack(side=tk.TOP, expand=True, fill="both")
        self.vTableFrame.grid_rowconfigure(1, weight=1)
        self.vTableFrame.grid_columnconfigure(0, weight=1)
        self.vTableFrame.parent = self
        #  Header
        self.vHeader = Header(self.vTableFrame, vModel)
        self.vHeader.grid(row=0, column=0, sticky="NSEW")
        #  Table
        self.vTable = Table(self.vTableFrame, vModel)
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
        vButton_ImportHistory = ttk.Button(self.vButtonBar, text="Import Spending History", command=lambda self=self: self.ImportHistory())
        vButton_ImportHistory.pack(side=tk.LEFT, anchor='w')
        vButton_Pop = ttk.Button(self.vButtonBar, text="Pop", command=lambda self=self: self.Pop())
        vButton_Pop.pack(side=tk.LEFT, anchor='w')
        self.vButton_PopView = ttk.Button(self.vButtonBar, text='0')
        self.vButton_PopView.pack(side=tk.LEFT, anchor='w')
        self.stream = rx.subjects.Subject()
        self.stream.subscribe(lambda value, self=self: self.StreamOnNextHandler(value))
        self.stream.on_next(4)
        #
        self.Refresh()

    def StreamOnNextHandler(self, value):
        self.vButton_PopView.config(text=str(value))

    def Pop(self):
        self.stream.on_next(int(self.vButton_PopView.cget("text")) + 1)

    def Refresh(self):
        self.vTableFrame.cColWidths = self.GetColWidths(self.vModel)
        self.vHeader.Refresh()
        self.vTable.Refresh()

    def ImportHistory(self):
        # Prompt which file
        vFile = tk.filedialog.askopenfile()
        # Import
        if vFile is not None:
            self.vModel.ImportTransactionHistory.Import(vFile.name)
        # Refresh view
        self.vTable.Refresh()

    def GetColWidths(self, vModel):
        cColWidths = {}
        for row in itertools.chain([vModel.ImportTransactionHistory.GetHeader()], vModel.ImportTransactionHistory.GetTable()):
            for j, vItem in enumerate(row[1:]):
                cColWidths[j] = max(cColWidths.get(j, 0), len(str(vItem)) + 1)
                if vItem != row[-1]:
                    cColWidths[j] = min(30, cColWidths[j])
        return cColWidths
import tkinter as tk
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
from .Table import Table  # noqa
import BudgetValue as BV
from .. import WidgetFactories as WF
from ..BudgetedTable import BudgetedTable  # noqa
from ..Popup_InputAmount import Popup_InputAmount  # noqa


class SpendHistory(tk.Frame):
    name = "Spend From Categories"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')
        WF.MakeButton(self.vButtonBar, text="zoop")
        # Frame of tables
        self.vFrameOfTables = tk.Frame(self)
        self.vFrameOfTables.pack(side=tk.TOP, expand=True, fill="both")
        self.vFrameOfTables.grid_rowconfigure(1, weight=1)
        self.vFrameOfTables.grid_columnconfigure(0, weight=1)
        # BudgetedTable
        self.vBTCanvas = tk.Canvas(self.vFrameOfTables, highlightthickness=0)
        self.vBTCanvas.pack(side=tk.LEFT, fill='x', anchor='nw')
        self.vBTTable = BudgetedTable(self.vBTCanvas, vModel)
        self.vBTCanvas.create_window((0, 0), window=self.vBTTable, anchor='nw')
        self.vBTTable.pack(anchor='nw')
        self.vBTTable.Refresh()
        # Verticle Separator
        self.vVerticleSeparator = tk.Frame(self.vFrameOfTables, width=20)
        self.vVerticleSeparator.pack(side=tk.LEFT, anchor='nw', fill='both')
        # Scrollbar Frame
        self.vScrollbarFrame = tk.Frame(self.vFrameOfTables, background='lightgrey')
        self.vScrollbarFrame.grid_rowconfigure(0, weight=1)
        self.vScrollbarFrame.grid_columnconfigure(0, weight=1)
        self.vScrollbarFrame.pack(side=tk.LEFT, anchor='nw', fill='both', expand=True)
        # Table
        self.vCanvas = tk.Canvas(self.vScrollbarFrame, highlightthickness=0)
        self.vCanvas.grid(row=0, column=0, sticky="NSEW")
        self.vTable = Table(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTable, anchor='nw')
        self.vTable.Refresh()
        # Scrollbars
        vScrollbar_Y = tk.Scrollbar(self.vScrollbarFrame)
        vScrollbar_Y.grid(row=0, column=1, sticky="ns")
        self.vCanvas.config(yscrollcommand=vScrollbar_Y.set)
        vScrollbar_Y.config(command=self.vCanvas.yview)
        vScrollbar_X = tk.Scrollbar(self.vScrollbarFrame, orient=tk.HORIZONTAL)
        vScrollbar_X.grid(row=1, column=0, sticky="ew")
        self.vCanvas.config(xscrollcommand=vScrollbar_X.set)
        vScrollbar_X.config(command=self.vCanvas.xview)
        # Scroll Events
        self.vScrollbarFrame.bind('<Configure>', lambda event: self.vCanvas.config(scrollregion=self.vCanvas.bbox("all")))

        def onMousewheel(event):
            self.vCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.vScrollbarFrame.bind('<Enter>', lambda event: self.bind_all("<MouseWheel>", onMousewheel))
        self.vScrollbarFrame.bind('<Leave>', lambda event: self.unbind_all("<MouseWheel>"))
        # ButtonBar Buttons

        def AddSpend(amount):
            self.vModel.TransactionHistory.AddTransaction(amount=-amount, bSpend=True, description="nonverified spend")
            self.vTable.Refresh()
        WF.MakeButton(self.vButtonBar, text="Add Unverified Spend", command=lambda: AddSpend(0))
        WF.MakeButton(self.vButtonBar, text="Refresh", command=self.Refresh)
        WF.MakeButton(self.vButtonBar, text="Update", command=lambda: self.Update_())
        WF.MakeButton(self.vButtonBar, text="Try YView", command=lambda: self.try_yview())
        WF.MakeButton(self.vButtonBar, text="Print bbox", command=lambda: self.PrintBBox())

    def PrintBBox(self):
        print("table bbox('all'):"+str(self.vTable.bbox("all")))
        print("canvas bbox('all'):"+str(self.vCanvas.bbox("all")))

    def Update_(self):
        self.update()

    def try_yview(self):
        self.vCanvas.yview("moveto", 0.1)

    def Refresh(self):
        self.vBTTable.Refresh()
        self.vTable.Refresh()

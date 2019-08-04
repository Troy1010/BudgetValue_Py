import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
import tkinter.filedialog  # noqa
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
from .Table import Table
import BudgetValue as BV
import rx
from .. import WidgetFactories as WF
from ..Skin import vSkin
from ...Model.Categories import Categories  # noqa
from ..Popup_InputAmount import Popup_InputAmount
from .. import BudgetedTable


class SplitMoneyIntoCategories(tk.Frame):
    name = "Split Money Into Categories"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')

        def CreateTransaction(amount):
            self.vModel.TransactionHistory.AddTransaction(bSpend=False, amount=amount)
            self.vTable.Refresh()
        vButton_SplitPaycheck = ttk.Button(self.vButtonBar, text="Add Unverified Income",
                                           command=lambda: Popup_InputAmount(self, self.vModel, lambda amount: CreateTransaction(amount)))
        vButton_SplitPaycheck.pack(side=tk.LEFT, anchor='w')
        # Button_SplitDifference
        vSplitDifferenceText_stream = rx.subjects.BehaviorSubject("")
        self.vModel.Balance.balance_stream.map(
            lambda balance: "Add Unverified Income - Difference (" + str(balance) + ")"
        ).subscribe(vSplitDifferenceText_stream)

        def SplitDifference():
            self.vModel.TransactionHistory.AddTransaction(amount=-self.vModel.Balance.balance_stream.value, bSpend=False)
            self.vTable.Refresh()
        vButton_SplitDifference = WF.MakeButton(self.vButtonBar, stream=vSplitDifferenceText_stream,
                                                command=lambda self=self: SplitDifference())

        def HighlightBalanceButton(balance):
            if balance:
                vButton_SplitDifference.config(background=vSkin.BG_BAD)
            else:
                vButton_SplitDifference.config(background=vSkin.BG_DEFAULT)
        self.vModel.Balance.balance_stream.subscribe(HighlightBalanceButton)
        # Scrollbar Frame
        self.vScrollbarFrame = tk.Frame(self, background='lightgrey')
        self.vScrollbarFrame.grid_rowconfigure(1, weight=1)  # allows expansion
        self.vScrollbarFrame.grid_columnconfigure(1, weight=1)  # allows expansion
        self.vScrollbarFrame.pack(side=tk.LEFT, anchor='nw', fill='both', expand=True)
        # Row Header Canvas
        self.vRowHeaderCanvas = tk.Canvas(self.vScrollbarFrame, highlightthickness=0)
        self.vRowHeaderCanvas.grid(row=1, column=0, sticky="NSEW")
        self.vRowHeaderTable = BudgetedTable.BudgetedTable(self.vRowHeaderCanvas, vModel)
        self.vRowHeaderCanvas.create_window((0, 0), window=self.vRowHeaderTable, anchor='nw')
        self.vRowHeaderTable.Refresh()
        self.vRowHeaderTable.RefreshParent = self.Refresh
        # resize RowHeaderCanvas width on RowHeaderFrame resize
        self.vRowHeaderTable.bind('<Configure>', lambda event: (
            self.vRowHeaderCanvas.config(width=self.vRowHeaderTable.winfo_width())
        ))
        # Table
        self.vCanvas = tk.Canvas(self.vScrollbarFrame, highlightthickness=0)
        self.vCanvas.grid(row=1, column=1, sticky="NSEW")
        self.vTable = Table(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTable, anchor='nw')
        # self.vTable.pack(anchor='nw') # this line causes vCanvas bbox not to match
        self.vTable.Refresh()
        # Scrollbars
        vScrollbar_Y = tk.Scrollbar(self.vScrollbarFrame)
        vScrollbar_Y.grid(row=0, column=2, rowspan=2, sticky="ns")
        self.vCanvas.config(yscrollcommand=vScrollbar_Y.set)
        vScrollbar_Y.config(command=self.vCanvas.yview)
        vScrollbar_X = tk.Scrollbar(self.vScrollbarFrame, orient=tk.HORIZONTAL)
        vScrollbar_X.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.vCanvas.config(xscrollcommand=vScrollbar_X.set)

        def ScrollHeaderAndData(*args):
            self.vCanvas.xview(*args)
        vScrollbar_X.config(command=ScrollHeaderAndData)
        # If scrollbar frame is resized, match the canvas's scroll region
        self.vScrollbarFrame.bind('<Configure>', lambda event: self.vCanvas.config(scrollregion=self.vCanvas.bbox("all")), add='+')
        # ButtonBar More
        WF.MakeButton(self.vButtonBar, text="Print bbox", command=lambda: self.PrintBBox())
        WF.MakeButton(self.vButtonBar, text="Print Rowheader bbox", command=lambda: self.PrintRowHeaderBBox())

        def PrintCategories():
            for var in self.vModel.Categories.Select():
                print(str(var.type.name) + " " + var.name)
        WF.MakeButton(self.vButtonBar, text="Print Categories", command=lambda: PrintCategories())
        WF.MakeButton(self.vButtonBar, text="Refresh", command=lambda: self.Refresh())

        def Import():
            # Prompt which file
            vFile = tk.filedialog.askopenfile()
            # Import
            if vFile is not None:
                self.vModel.TransactionHistory.Import(vFile.name)
        WF.MakeButton(self.vButtonBar, text="Import Transactions", command=lambda: Import())

    def Refresh(self):
        self.vRowHeaderTable.Refresh()
        self.vTable.Refresh()

    def PrintRowHeaderBBox(self):
        print("table bbox('all'):"+str(self.vRowHeaderTable.bbox("all")))
        print("canvas bbox('all'):"+str(self.vRowHeaderCanvas.bbox("all")))

    def PrintBBox(self):
        print("table bbox('all'):"+str(self.vTable.bbox("all")))
        print("canvas bbox('all'):"+str(self.vCanvas.bbox("all")))

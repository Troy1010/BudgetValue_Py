import tkinter as tk
from tkinter import ttk
import tkinter.filedialog  # noqa
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import tkinter.messagebox  # noqa
from .Table import Table
import BudgetValue as BV
import rx
from .. import WidgetFactories as WF
from ..Skin import vSkin


class SplitMoneyIntoCategories(tk.Frame):
    name = "Split Money Into Categories"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.bind("<Destroy>", lambda event: self._destroy())
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')
        vButton_AddRow = ttk.Button(self.vButtonBar, text="Split",
                                    command=lambda self=self: self.AddSplitMoneyHistoryColumn())
        vButton_AddRow.pack(side=tk.LEFT, anchor='w')
        vButton_SplitPaycheck = ttk.Button(self.vButtonBar, text="Split Paycheck",
                                           command=lambda self=self: self.SplitPaycheck())
        vButton_SplitPaycheck.pack(side=tk.LEFT, anchor='w')
        # Button_SplitBalance
        vSplitBalanceText_stream = rx.subjects.BehaviorSubject("Split Balance")
        self.vModel.Balance.balance_stream.map(
            lambda balance: "Split Balance (" + str(balance) + ")"
        ).subscribe(vSplitBalanceText_stream)
        vButton_SplitBalance = WF.MakeButton(self.vButtonBar, text=vSplitBalanceText_stream,
                                             command=lambda self=self: self.SplitBalance())

        def HighlightBalanceButton(balance):
            if balance:
                vButton_SplitBalance.config(background=vSkin.BG_BAD)
            else:
                vButton_SplitBalance.config(background=vSkin.BG_DEFAULT)
        self.vModel.Balance.balance_stream.subscribe(HighlightBalanceButton)
        vButton_SplitAccounts = ttk.Button(self.vButtonBar, text="Split Accounts",
                                           command=lambda self=self: self.buttonPressed.on_next(None))
        vButton_SplitAccounts.pack(side=tk.LEFT, anchor='w')
        self.buttonPressed = rx.subjects.Subject()
        self.buttonPressed.with_latest_from(
            self.vModel.Accounts.total_stream,
            lambda pressEvent, total: total
        ).subscribe(lambda x: self.SplitAccounts(x))
        #
        vButton_Print = ttk.Button(self.vButtonBar, text="Print",
                                   command=lambda self=self: self.Print())
        vButton_Print.pack(side=tk.LEFT, anchor='w')
        # Table
        self.vCanvas = tk.Canvas(self, highlightthickness=0)
        self.vCanvas.pack(side=tk.TOP, fill='x', anchor='nw')
        self.vTable = Table(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTable, anchor='nw')
        self.vTable.pack(anchor='nw')
        self.vTable.Refresh()
        # ButtonBar More
        vButton_Refresh = ttk.Button(self.vButtonBar, text="Refresh",
                                     command=lambda self=self: self.vTable.Refresh())
        vButton_Refresh.pack(side=tk.LEFT, anchor='w')

    def Print(self):
        print("self.vModel.SplitMoneyHistory..")
        for i, cColumn in enumerate(self.vModel.SplitMoneyHistory):
            print(" Column "+str(i))
            for vEntry in cColumn:
                print("  "+vEntry.category.name+" - "+str(vEntry.amount))

    def _destroy(self):
        self.vModel.SplitMoneyHistory.Save()

    def SplitBalance(self):
        self.vModel.SplitMoneyHistory.AddColumn()
        self.vModel.SplitMoneyHistory.AddEntry(-1, "Income", amount=self.vModel.Balance.balance_stream.value)
        self.vTable.Refresh()

    def SplitPaycheck(self):
        self.vModel.SplitMoneyHistory.AddColumn()
        for categoryName, paycheckPlan_row in self.vModel.PaycheckPlan.items():
            if categoryName != "<Default Category>":
                self.vModel.SplitMoneyHistory.AddEntry(-1, categoryName, amount=paycheckPlan_row.amount)
        self.vTable.Refresh()

    def SplitAccounts(self, amount):
        self.vModel.SplitMoneyHistory.AddColumn()
        self.vModel.SplitMoneyHistory.AddEntry(-1, "Net Worth", amount=amount)
        self.vTable.Refresh()

    def AddSplitMoneyHistoryColumn(self):
        self.vModel.SplitMoneyHistory.AddColumn()
        self.vTable.Refresh()

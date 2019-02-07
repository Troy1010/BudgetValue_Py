import TM_CommonPy as TM  # noqa
import tkinter as tk
from BudgetValue._Logger import Log  # noqa
import rx  # noqa
from . import WidgetFactories as WF  # noqa
import BudgetValue as BV
from .Popup_InputAmount import Popup_InputAmount


class Popup_SelectIncome(tk.Frame):
    previous_popup = None

    def __init__(self, parent, vModel, handler, cPos=None, vDestroyHandler=None):
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        #
        tk.Frame.__init__(self, parent, borderwidth=2, background="black")
        # Hook DestroyHandler

        def ForgetPrevPopup():
            self.__class__.previous_popup = None
        self.destroy = TM.Hook(self.destroy, vDestroyHandler, ForgetPrevPopup, bPrintAndQuitOnError=True)
        # Bind Escape to exit
        self.winfo_toplevel().bind("<Escape>", lambda event: self.destroy(), add='+')
        # Delete old popup
        if self.__class__.previous_popup is not None:
            self.__class__.previous_popup.destroy()
        self.__class__.previous_popup = self
        # Position myself
        if not cPos:
            x, y = parent.winfo_pointerx() - parent.winfo_rootx(), parent.winfo_pointery() - parent.winfo_rooty()
        else:
            x, y = cPos[0], cPos[1]
        self.place(x=x, y=y)
        self.tkraise()
        # Show Income Transactions
        self.transaction = None

        def MakeNewTransaction(amount):
            self.transaction = self.vModel.TransactionHistory.AddTransaction(amount=amount, description="Unverified Paycheck")
        WF.MakeButton(self, pos=(0, 0), text="Create unverified paycheck",
                      command=lambda: Popup_InputAmount(self.winfo_toplevel(), self.vModel, MakeNewTransaction)
                      )
        for row, transaction in enumerate(vModel.TransactionHistory.Iter_Income(), 1):
            assert isinstance(transaction, BV.Model.Transaction)
            WF.MakeEntry_ReadOnly(self, (row, 0), transaction.timestamp, display=BV.DisplayTimestamp)
            WF.MakeEntry_ReadOnly(self, (row, 1), transaction.amount)

            def AssignTransaction(transaction):
                self.transaction = transaction
            WF.MakeX(self, (row, 2), lambda transaction=transaction: AssignTransaction(transaction))
        # Bind Return to accept

        def OnReturn(event):
            if isinstance(event.widget, tk.Entry):
                return
            handler(self.transaction)
            self.destroy()
        self.winfo_toplevel().bind("<Return>", OnReturn, add='+')

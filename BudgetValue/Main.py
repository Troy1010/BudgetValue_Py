import BudgetValue as BV

vModel = BV.Model.Model()
app = BV.View.View(vModel)
vModel.LoadAndHookSaves()
app.mainloop()

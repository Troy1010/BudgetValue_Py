import BudgetValue as BV
import time

vModel = BV.Model.Model()
app = BV.View.View(vModel)
s = "Mainloop begins. time_elapsed:"+str(time.time()-vModel.start_time)
print(s)
app.mainloop()

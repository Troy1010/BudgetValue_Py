import BudgetValue as BV
import time
import atexit

vModel = BV.Model.Model()
app = BV.View.View(vModel)
vModel.PaycheckPlan.Load()
atexit.register(vModel.PaycheckPlan.Save)
s = "Mainloop begins. time_elapsed:"+str(time.time()-vModel.start_time)
print(s)
app.mainloop()

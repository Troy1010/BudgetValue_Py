import BudgetValue as BV
import time

vModel = BV.Model.Model()
app = BV.View.View(vModel)
vModel.LoadAndHookSaves()
print("LoadAndHookSaves. time_elapsed:"+str(time.time()-vModel.start_time))
app.mainloop()

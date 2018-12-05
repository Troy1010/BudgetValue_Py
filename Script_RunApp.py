import sys
import os
import TM_CommonPy as TM
# Settings
bPause = False


try:
    os.chdir("BudgetValue")
    TM.Run("python Main.py")
except Exception as e:
    TM.DisplayException(e)
    sys.exit(1)
if bPause:
    TM.DisplayDone()

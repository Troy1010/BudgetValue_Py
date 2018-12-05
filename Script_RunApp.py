import sys
import TM_CommonPy as TM
# Settings
bPause = False


try:
    TM.Run("python BudgetValue/Main.py")
except Exception as e:
    TM.DisplayException(e)
    sys.exit(1)
if bPause:
    TM.DisplayDone()

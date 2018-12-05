##region Settings
import os
bWriteLog = True
sLogFile = os.path.join(__file__,'..','BVLog.log')
##endregion
##region LogInit
import logging
BVLog = logging.getLogger(__name__)
BVLog.setLevel(logging.DEBUG)
try:
    os.remove(sLogFile)
except (PermissionError,FileNotFoundError):
    pass
if bWriteLog:
    bLogFileIsOpen = False
    try:
        os.rename(sLogFile,sLogFile)
    except PermissionError:
        bLogFileIsOpen = True
    except FileNotFoundError:
        pass
    if not bLogFileIsOpen:
        BVLog.addHandler(logging.FileHandler(sLogFile))
##endregion

import logging
import os
# Settings
bWriteLog = True
sLogFile = os.path.join(__file__, '..', 'BVLog.log')

BVLog = logging.getLogger(__name__)
BVLog.setLevel(logging.DEBUG)
try:
    os.remove(sLogFile)
except (PermissionError, FileNotFoundError):
    pass
if bWriteLog:
    bLogFileIsOpen = False
    try:
        os.rename(sLogFile, sLogFile)
    except PermissionError:
        bLogFileIsOpen = True
    except FileNotFoundError:
        pass
    if not bLogFileIsOpen:
        BVLog.addHandler(logging.FileHandler(sLogFile))

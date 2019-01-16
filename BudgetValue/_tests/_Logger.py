import os
import logging
# Settings
bWriteLogFile = True
sLogFile = os.path.join(__file__, '..', 'BVLog_LogTests.log')
vMasterThreshold = logging.DEBUG
vConsoleHandlerThreshold = logging.WARNING
vFileHandlerThreshold = logging.DEBUG

BVLog_LogTests = logging.getLogger(__name__)
# BVLog_LogTests.info = TM.LoggingHeaderDecorator(BVLog_LogTests.info)
# BVLog_LogTests.debug = TM.LoggingHeaderDecorator(BVLog_LogTests.debug)
BVLog_LogTests.setLevel(vMasterThreshold)
vFormatter = logging.Formatter('%(message)s')
# ---ConsoleHandler
vConsoleHandler = logging.StreamHandler()
vConsoleHandler.setLevel(vConsoleHandlerThreshold)
vConsoleHandler.setFormatter(vFormatter)
BVLog_LogTests.addHandler(vConsoleHandler)
# ---FileHandler
try:
    os.remove(sLogFile)
except (PermissionError, FileNotFoundError):
    pass
if bWriteLogFile:
    bLogFileIsOpen = False
    try:
        os.rename(sLogFile, sLogFile)
    except PermissionError:
        bLogFileIsOpen = True
    except FileNotFoundError:
        pass
    if not bLogFileIsOpen:
        vFileHandler = logging.FileHandler(sLogFile)
        vFileHandler.setFormatter(vFormatter)
        vFileHandler.setLevel(vFileHandlerThreshold)
        BVLog_LogTests.addHandler(vFileHandler)

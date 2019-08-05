import logging
import os
# Settings
bWriteLog = True
sLogFile = os.path.join(__file__, '..', 'BVLog.log')

BVLog = logging.getLogger(__name__)
BVLog.setLevel(logging.DEBUG)
try:
    os.remove(sLogFile)
except FileNotFoundError:
    pass
if bWriteLog:
    BVLog.addHandler(logging.FileHandler(sLogFile))


def Log(*args, bPrint=False, **kwargs):
    BVLog.debug(*args, **kwargs)
    if bPrint:
        print(args[0])
